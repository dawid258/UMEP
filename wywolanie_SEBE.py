import os
from funkcje_SEBE import *
import glob, psutil
from qgis.core import QgsProcessingFeedback
import processing

# -------------------------------------------------------------------------
# 1) GŁÓWNE KATALOGI
# -------------------------------------------------------------------------
BASE_DIR           = r"C:/Users/dawids/Desktop/PRACA/PROJEKTY/7_PILA/SEBE_V3_pipeline_test"
RAW_DIR            = os.path.join(BASE_DIR, '1_dane')             # folder z danymi wyjściowymi
WORK_DIR           = os.path.join(BASE_DIR, 'pipeline_work')      # folder na wyniki pośrednie
TILES_DIR          = os.path.join(WORK_DIR, 'tiles')             # kafle NMPT
MOSAIC_TIF         = os.path.join(WORK_DIR, 'pila_mozaika.tif')
CLIPPED_MOSAIC_TIF = os.path.join(WORK_DIR, 'pila_solar_cut.tif')
DSM_TIF            = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/rzeszow_NMPT_przyciete.tif"#os.path.join(RAW_DIR, 'DSM', 'pila_DSM.tif') # lub zmień na właściwy plik
MASK_VECTOR_GPKG   = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/maska_przyciecia.gpkg"

# -------------------------------------------------------------------------
# 2) KATALOGI UMEP / SEBE
# -------------------------------------------------------------------------
UMEP_HEIGHT_DIR  = os.path.join(WORK_DIR, 'umep_height')
UMEP_ASPECT_DIR  = os.path.join(WORK_DIR, 'umep_aspect')
SEBE_SKY_DIR     = os.path.join(WORK_DIR, 'sky_irr')
SEBE_OUTPUT_DIR  = os.path.join(WORK_DIR, 'roof_irr')

# -------------------------------------------------------------------------
# 3) Pozostałe wyjścia
# -------------------------------------------------------------------------
SLOPE_TIF            = os.path.join(WORK_DIR, 'slope_deg.tif')
AREA_TIF             = os.path.join(WORK_DIR, 'actual_area.tif')
ENERGY_RAW_TIF       = CLIPPED_MOSAIC_TIF
ENERGY_CORRECTED_TIF = os.path.join(WORK_DIR, 'energy_corrected.tif')
RAD_CLASS_TIF        = os.path.join(WORK_DIR, 'radiation_class.tif')
BUILDINGS_GPKG       = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/bdot_przyciety.gpkg"#os.path.join(RAW_DIR, 'wektor', 'budynki_v2_roof_height_v2.gpkg')
BUILDINGS_CLASS_GPKG = os.path.join(WORK_DIR, 'buildings_classified.gpkg')
BUILDINGS_BUF_GPKG   = os.path.join(WORK_DIR, 'buildings_buffer.gpkg')
ENERGY_BUILD_TIF     = os.path.join(WORK_DIR, 'energy_corrected_building.tif')
SEBE_METEO_FILE      = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/SEBE/solar_Rzeszow_2023.txt"

# -------------------------------------------------------------------------
# 4) Uruchomienie pipeline
# -------------------------------------------------------------------------
os.makedirs(TILES_DIR,           exist_ok=True)
os.makedirs(UMEP_HEIGHT_DIR,     exist_ok=True)
os.makedirs(UMEP_ASPECT_DIR,     exist_ok=True)
os.makedirs(SEBE_SKY_DIR,        exist_ok=True)
os.makedirs(SEBE_OUTPUT_DIR,     exist_ok=True)
os.makedirs(os.path.dirname(MOSAIC_TIF), exist_ok=True)

# 0) Preprocessing
NMPT_PATH = os.path.join("C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/rzeszow_NMPT_przyciete.tif")
preprocess_nmpt_tiles(
    nmpt_path=NMPT_PATH,
    out_dir=TILES_DIR,
    margin=20,
    max_pixels=500_000
)

# 1) UMEP: wall height i aspect
feedback = QgsProcessingFeedback()
for tif in glob.glob(os.path.join(TILES_DIR, '*.tif')):
    base = os.path.splitext(os.path.basename(tif))[0]
    processing.run(
        'umep:Urban Geometry: Wall Height and Aspect',
        {
            'INPUT': tif,
            'INPUT_LIMIT': 3,
            'OUTPUT_HEIGHT': os.path.join(UMEP_HEIGHT_DIR, f'{base}_wall_height.tif'),
            'OUTPUT_ASPECT': os.path.join(UMEP_ASPECT_DIR, f'{base}_wall_aspect.tif')
        },
        feedback=feedback
    )

# 2) SEBE: roof irradiation
for tif in glob.glob(os.path.join(TILES_DIR, '*.tif')):
    base = os.path.splitext(os.path.basename(tif))[0]
    out_f = os.path.join(SEBE_OUTPUT_DIR, base)
    os.makedirs(out_f, exist_ok=True)
    processing.run(
        'umep:Solar Radiation: Solar Energy of Builing Envelopes (SEBE)',
        {
            'INPUT_DSM': tif,
            'INPUT_HEIGHT': os.path.join(UMEP_HEIGHT_DIR, f'{base}_wall_height.tif'),
            'INPUT_ASPECT': os.path.join(UMEP_ASPECT_DIR, f'{base}_wall_aspect.tif'),
            'INPUTMET': SEBE_METEO_FILE,
            'OUTPUT_ROOF': os.path.join(out_f, f'roof_irr_{base}.tif'),
            'IRR_FILE': os.path.join(SEBE_SKY_DIR, f'sky_irr_{base}.txt'),
            'OUTPUT_DIR': out_f
        },
        feedback=feedback
    )

# 3) Mozaika
feather = 40
mem, w, h = estimate_memory_requirements(SEBE_OUTPUT_DIR, feather)
tile_sz = 1024 if mem > psutil.virtual_memory().available/(1024**3)*0.8 else 2048
mosaic_with_gauss_grid(SEBE_OUTPUT_DIR, MOSAIC_TIF, feather_px=feather, tile_size=tile_sz)

# # 4) Przycinanie
clip_raster_to_mask(MOSAIC_TIF, MASK_VECTOR_GPKG, output_path=CLIPPED_MOSAIC_TIF)

# 5) Nachylenie i korekta
create_slope_raster(DSM_TIF, SLOPE_TIF)
compute_actual_area(SLOPE_TIF, AREA_TIF)
compute_corrected_energy(ENERGY_RAW_TIF, SLOPE_TIF, ENERGY_CORRECTED_TIF)
reclassify_radiation(ENERGY_CORRECTED_TIF, RAD_CLASS_TIF)

# 6) Zonal stats i bufor
zonal_mean_radiation(BUILDINGS_GPKG, ENERGY_CORRECTED_TIF, BUILDINGS_CLASS_GPKG)
processing.run('native:buffer', {
    'INPUT': f"{BUILDINGS_CLASS_GPKG}|layername=buildings_classified",
    'DISTANCE': 5, 'SEGMENTS': 5, 'END_CAP_STYLE': 1,
    'JOIN_STYLE': 1, 'MITER_LIMIT': 2, 'DISSOLVE': True,
    'OUTPUT': BUILDINGS_BUF_GPKG
})
processing.run('gdal:cliprasterbymasklayer', {
    'INPUT': ENERGY_CORRECTED_TIF,
    'MASK': f"{BUILDINGS_BUF_GPKG}|layername=buildings_buffer",
    'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': True,
    'OUTPUT': ENERGY_BUILD_TIF
})

print('Pipeline completed.')
