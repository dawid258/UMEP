import os
import glob
import math
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.transform import from_origin
from rasterio.warp import reproject
from rasterio.enums import Resampling
import tempfile
import shutil
from tqdm import tqdm
import psutil
import gc
import geopandas as gpd
from rasterstats import zonal_stats
from osgeo import gdal
from math import pi
from qgis.core import QgsProcessingFeedback
import processing

# -----------------------------------------------------------------------------
# FUNKCJE
# -----------------------------------------------------------------------------
#test
def preprocess_nmpt_tiles(
    nmpt_path: str,
    out_dir: str,
    margin: int = 20,
    max_pixels: int = 3_000_000
):
    """
    Dzieli plik NMPT na kafelki o maksymalnej liczbie pikseli, z marginesem.

    Args:
        nmpt_path: ścieżka do pliku DSM
        out_dir: katalog wyjściowy dla kafelków
        margin: margines w pikselach
        max_pixels: maksymalna liczba pikseli na kafelek z marginesem
    """
    os.makedirs(out_dir, exist_ok=True)

    def compute_max_tile_size(mrg, max_px):
        size = int(math.floor(math.sqrt(max_px)))
        while (size + 2*mrg)**2 > max_px:
            size -= 1
        return size

    tile_size = compute_max_tile_size(margin, max_pixels)
    print(f"Preprocessing: tile size={tile_size}, margin={margin} px")

    with rasterio.open(nmpt_path) as src:
        W, H = src.width, src.height
        row_idx = 0
        for top in range(0, H, tile_size):
            h = min(tile_size, H - top)
            col_idx = 0
            for left in range(0, W, tile_size):
                w = min(tile_size, W - left)
                t_m = margin if top > 0 else 0
                l_m = margin if left > 0 else 0
                b_m = margin if (top+h) < H else 0
                r_m = margin if (left+w) < W else 0
                win = Window(
                    max(left-l_m, 0),
                    max(top-t_m, 0),
                    w + l_m + r_m,
                    h + t_m + b_m
                )
                if win.width * win.height > max_pixels:
                    col_idx += 1
                    continue
                transform = src.window_transform(win)
                profile = src.profile.copy()
                profile.update({
                    'height': int(win.height),
                    'width': int(win.width),
                    'transform': transform
                })
                fname = f"tile_r{row_idx:03d}_c{col_idx:03d}.tif"
                out_fp = os.path.join(out_dir, fname)
                with rasterio.open(out_fp, 'w', **profile) as dst:
                    dst.write(src.read(1, window=win), 1)
                col_idx += 1
            row_idx += 1
    print("✅ Preprocessing done: tiles saved.")


def _initialize_temp_files(sum_weighted_path, sum_weights_path, height, width):
    sum_weighted = np.memmap(sum_weighted_path, dtype='float64', mode='w+', shape=(height, width))
    sum_weights  = np.memmap(sum_weights_path, dtype='float64', mode='w+', shape=(height, width))
    block = 1024
    for i in range(0, height, block):
        end = min(i + block, height)
        sum_weighted[i:end, :] = 0.0
        sum_weights[i:end, :]  = 0.0
    del sum_weighted, sum_weights


def _process_tile(fn, sum_weighted_path, sum_weights_path, height, width,
                  nodata, feather_px, sigma, x_min, y_max, res, tile_size):
    with rasterio.open(fn) as src:
        arr = src.read(1).astype('float64')
        mask = arr == nodata
        arr[mask] = 0.0
        h, w = src.shape
        yy = np.arange(h).reshape(h, 1); xx = np.arange(w).reshape(1, w)
        d_x = np.minimum(xx, w-1-xx); d_y = np.minimum(yy, h-1-yy)
        dist = np.minimum(d_x, d_y).astype('float64')
        wmat = np.ones_like(dist)
        if feather_px > 0:
            zone = dist < feather_px
            wmat[zone] = np.exp(-((feather_px - dist[zone])**2)/(2*(sigma**2)))
        wmat[mask] = 0.0
        c_off = int((src.bounds.left - x_min)/res) + feather_px
        r_off = int((y_max - src.bounds.top)/res) + feather_px
        r0, c0 = r_off, c_off
        sum_wt = np.memmap(sum_weighted_path, dtype='float64', mode='r+', shape=(height, width))
        sum_ws = np.memmap(sum_weights_path, dtype='float64', mode='r+', shape=(height, width))
        bh = min(tile_size, h); bw = min(tile_size, w)
        for i in range(0, h, bh):
            for j in range(0, w, bw):
                ei, ej = i+bh, j+bw
                arr_blk = arr[i:ei, j:ej]; w_blk = wmat[i:ei, j:ej]
                r1 = r0 + i; c1 = c0 + j
                sum_wt[r1:r1+arr_blk.shape[0], c1:c1+arr_blk.shape[1]] += arr_blk * w_blk
                sum_ws[r1:r1+arr_blk.shape[0], c1:c1+arr_blk.shape[1]] += w_blk
        del sum_wt, sum_ws, arr, wmat


def _create_final_mosaic(sum_weighted_path, sum_weights_path, output_path,
                         height, width, dtype, nodata, crs, transform, tile_size):
    sw = np.memmap(sum_weighted_path, dtype='float64', mode='r', shape=(height, width))
    ws = np.memmap(sum_weights_path, dtype='float64', mode='r', shape=(height, width))
    profile = dict(driver='GTiff', dtype=dtype, count=1, crs=crs,
                   transform=transform, width=width, height=height,
                   nodata=nodata, compress='lzw', tiled=True,
                   blockxsize=512, blockysize=512)
    with rasterio.open(output_path, 'w', **profile) as dst:
        for i in range(0, height, tile_size):
            ei = min(i+tile_size, height)
            for j in range(0, width, tile_size):
                ej = min(j+tile_size, width)
                wblk = ws[i:ei, j:ej]; swblk = sw[i:ei, j:ej]
                res = np.full((ei-i, ej-j), nodata, dtype='float64')
                valid = wblk > 0
                res[valid] = swblk[valid] / wblk[valid]
                dst.write(res.astype(dtype), 1, window=rasterio.windows.Window(j, i, ej-j, ei-i))
    del sw, ws


def mosaic_with_gauss_grid(input_folder, output_path,
                           feather_px=20, tile_size=2048, cleanup_temp=True):
    # Przeszukiwanie folderów z wzorcem "tile_*"
    pattern = os.path.join(input_folder, '**', 'roof_irr_tile_*.tif')
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        raise ValueError(f"Brak plików .tif w folderze: {pattern}")
    # Parametry z pierwszego pliku
    with rasterio.open(files[0]) as src0:
        crs, dtype, res, nodata, b0 = src0.crs, src0.dtypes[0], src0.res[0], src0.nodata, src0.bounds
    x_min, x_max = b0.left, b0.right; y_min, y_max = b0.bottom, b0.top
    # Globalne granice
    for fn in files[1:]:
        with rasterio.open(fn) as src:
            b = src.bounds
            x_min, x_max = min(x_min, b.left), max(x_max, b.right)
            y_min, y_max = min(y_min, b.bottom), max(y_max, b.top)
    # Bufor + wymiary
    width = int(np.ceil((x_max-x_min)/res)) + 2*feather_px
    height = int(np.ceil((y_max-y_min)/res)) + 2*feather_px
    transform = from_origin(x_min - feather_px*res, y_max + feather_px*res, res, res)
    sum_wt_p = os.path.join(tempfile.mkdtemp(prefix='mosaic_temp_'), 'sum_wt.dat')
    sum_ws_p = os.path.join(os.path.dirname(sum_wt_p), 'sum_ws.dat')
    _initialize_temp_files(sum_wt_p, sum_ws_p, height, width)
    sigma = feather_px/2.0
    for i, fn in enumerate(files):
        _process_tile(fn, sum_wt_p, sum_ws_p, height, width, nodata,
                      feather_px, sigma, x_min, y_max, res, tile_size)
        if i % 10 == 0 and psutil.virtual_memory().percent > 85:
            gc.collect()
    _create_final_mosaic(sum_wt_p, sum_ws_p, output_path,
                         height, width, dtype, nodata, crs, transform, tile_size)
    if cleanup_temp:
        shutil.rmtree(os.path.dirname(sum_wt_p))


def get_memory_usage():
    return psutil.virtual_memory().used / (1024**3)

def estimate_memory_requirements(input_folder, feather_px=20):
    files = sorted(glob.glob(os.path.join(input_folder, '*.tif')))
    if not files: return 0,0,0
    with rasterio.open(files[0]) as src0:
        res, b0 = src0.res[0], src0.bounds
    x_min, x_max = b0.left, b0.right; y_min, y_max = b0.bottom, b0.top
    for fn in files[1:]:
        b = rasterio.open(fn).bounds
        x_min, x_max = min(x_min, b.left), max(x_max, b.right)
        y_min, y_max = min(y_min, b.bottom), max(y_max, b.top)
    width = int(np.ceil((x_max-x_min)/res)) + 2*feather_px
    height = int(np.ceil((y_max-y_min)/res)) + 2*feather_px
    size_gb = (width * height * 8 * 2) / (1024**3)
    return size_gb, width, height


def clip_raster_to_mask(raster_path, mask_path, layer=None, output_path=None):
    mask = gpd.read_file(mask_path, layer=layer).geometry.values
    with rasterio.open(raster_path) as src:
        out_img, out_tr = rasterio.mask.mask(src, mask, crop=True)
        out_meta = src.meta.copy()
    out_meta.update(driver='GTiff', height=out_img.shape[1], width=out_img.shape[2], transform=out_tr)
    if not output_path:
        output_path = raster_path.replace('.tif', '_clipped.tif')
    with rasterio.open(output_path, 'w', **out_meta) as dst:
        dst.write(out_img)
    return output_path


def create_slope_raster(dsm_fp, slope_fp):
    gdal.DEMProcessing(slope_fp, dsm_fp, 'slope', format='GTiff', slopeFormat='degree')


def compute_actual_area(slope_fp, out_fp):
    # Otwórz dataset i od razu pobierz profil
    with rasterio.open(slope_fp) as src:
        slope = src.read(1)
        profile = src.profile
        PIXEL_AREA = abs(src.transform.a * src.transform.e)
    # Przelicz nachylenie na radiany
    slope_rad = np.deg2rad(np.where((slope < 0) | np.isnan(slope), 0, slope))
    with np.errstate(divide='ignore', invalid='ignore'):
        actual = PIXEL_AREA / np.cos(slope_rad)
        actual[np.isnan(actual) | (actual > 100)] = 0
    profile.update(dtype='float32', count=1)
    with rasterio.open(out_fp, 'w', **profile) as dst:
        dst.write(actual.astype('float32'), 1)


def reproject_raster(src_fp, target_meta, out_shape, resampling=Resampling.bilinear):
    with rasterio.open(src_fp) as src:
        src_arr = src.read(1)
        dst = np.zeros(out_shape, dtype='float32')
        reproject(source=src_arr, destination=dst,
                  src_transform=src.transform, src_crs=src.crs,
                  dst_transform=target_meta['transform'], dst_crs=target_meta['crs'],
                  resampling=resampling)
    return dst


def compute_corrected_energy(energy_fp, slope_fp, out_fp):
    with rasterio.open(energy_fp) as erk:
        energy, meta = erk.read(1), erk.meta
    slope = reproject_raster(slope_fp, meta, energy.shape)
    mask = (slope < 65) * slope
    rad = np.deg2rad(mask)
    with np.errstate(divide='ignore', invalid='ignore'):
        corr = energy / np.cos(rad)
        corr[np.isnan(corr)|(corr>1e6)] = 0
    meta.update(dtype='float32', count=1)
    with rasterio.open(out_fp, 'w', **meta) as dst:
        dst.write(corr.astype('float32'), 1)


def reclassify_radiation(in_fp, out_fp):
    with rasterio.open(in_fp) as src:
        data, profile = src.read(1), src.profile
    cls = np.zeros_like(data, dtype='uint8')
    cls[(data>0)&(data<=800)] = 1
    cls[(data>800)&(data<=1000)] = 2
    cls[data>1000] = 3
    profile.update(dtype='uint8', count=1, nodata=0)
    with rasterio.open(out_fp, 'w', **profile) as dst:
        dst.write(cls, 1)


def zonal_mean_radiation(buildings_fp, energy_fp, corrected_energy_fp, out_fp):
    """Compute zonal stats: mean from raw energy raster, sum from corrected raster."""
    # policz powierzchnię piksela na podstawie rastra oryginalnego
    import rasterio
    with rasterio.open(energy_fp) as src:
        transform = src.transform
        pixel_area = abs(transform.a * transform.e)

    # wczytaj budynki
    import geopandas as gpd
    from rasterstats import zonal_stats
    gdf = gpd.read_file(buildings_fp)

    # średnia z rastra surowego
    stats_mean = zonal_stats(
        gdf, energy_fp,
        stats=['mean'],
        geojson_out=False,
        all_touched=False
    )

    # suma z rastra skorygowanego
    stats_sum = zonal_stats(
        gdf, corrected_energy_fp,
        stats=['sum'],
        geojson_out=False,
        all_touched=False
    )

    # przypisz wyniki
    gdf['mean_kwh_m2'] = [s.get('mean', 0) or 0 for s in stats_mean]
    gdf['sum_kwh']     = [(s.get('sum', 0) or 0) * pixel_area for s in stats_sum]

    # klasyfikacja
    def cls(val):
        if   val <= 800:  return 1
        elif val <=1000:  return 2
        else:             return 3

    gdf['class'] = gdf['mean_kwh_m2'].apply(cls)
    gdf.to_file(out_fp, driver='GPKG')

