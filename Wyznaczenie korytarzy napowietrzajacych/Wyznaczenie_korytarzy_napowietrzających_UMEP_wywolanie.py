import os
import numpy as np
import pandas as pd
from Wyznaczenie_korytarzy_napowietrzających_UMEP_funkcje import *

    
    # Ścieżki i pola
csv_path = r"C:/Users/dawids/Desktop/dane_meteo_Stalowa_Wola_2021.csv"
dir_col = "wind_dir_10m:d"
spd_col = "wind_speed_10m:ms"
    
dir_output = r"C:/Users/dawids/Desktop/Dawid/STALOWA_WOLA/CALE_MIASTO/urock_output/"
buildings_path = r"C:/Users/dawids/Desktop/Dawid/STALOWA_WOLA/CALE_MIASTO/uproszczona_geometria_v4.gpkg"
height_field_build = 'ROOF_HEIGHT'
vegetation_path = r"C:/Users/dawids/Desktop/Dawid/STALOWA_WOLA/CALE_MIASTO/obrysy_koron_uproszczone_v4.gpkg"
veg_crown_top_field = 'tree_h'
veg_crown_base_field = ''
attenuation_field = ''
input_profile_file = ''
input_profile_type = 1
input_wind_height = 2
horizontal_resolution = 512
vertical_resolution = 6
wind_height_ref = '2'
base_output_dir = os.path.join(dir_output, f"RES_{horizontal_resolution}v_{vertical_resolution}")
save_raster, save_vector, save_netcdf, load_output = False, True, False, True

city_mask = r"C:/Users/dawids/Desktop/Dawid/STALOWA_WOLA/obszar_opracowania.gpkg"
subfolders = ['wind_speed', 'wind_direction']

# Parametry korytarzy
speed_near_ground = 32
threshold_to_corridor = 0.5
min_width_m, min_length_m = 50.0, 1000.0
min_prune_length_m = 100.0
angle_tol_deg = 60

# 1. Wczytaj meteo
df = load_meteo(csv_path, dir_col, spd_col)
# 2. Średnie prędkości
speeds = compute_mean_speeds(df, directions, dir_col, spd_col)
print(directions, speeds)

# 3. UROCK
run_urock_all(
        buildings_path, height_field_build, vegetation_path,
        veg_crown_top_field, veg_crown_base_field, attenuation_field,
        input_profile_file, input_profile_type, input_wind_height,
        directions, speeds,
        horizontal_resolution, vertical_resolution,
        wind_height_ref, base_output_dir,
        save_raster, save_vector,
        save_netcdf, load_output
)

# 4. Rasteryzacja
raster_root = rasterize_all(base_output_dir, horizontal_resolution)

# 5. Cięcie
cut_dir = clip_all(city_mask, raster_root, subfolders, horizontal_resolution)

#6. Korytarze
corridor_dir = find_corridors(
        base_output_dir, cut_dir, subfolders,
        directions, speed_near_ground,
        threshold_to_corridor, horizontal_resolution,
        vertical_resolution, min_width_m,
        min_length_m, min_prune_length_m,
        angle_tol_deg
)

# 7. Wizualizacja
plot_results(raster_root, directions, dir_output, horizontal_resolution, vertical_resolution)

# 8. Navier-Stokes
run_navier(
        corridor_dir, raster_root, directions,
        horizontal_resolution, vertical_resolution,
        dx=32, dy=32, dt=1e-4, dxd=32, dyd=32,
        p0=101300, rho=1.247, nu=15.6e-6, g=1,
        target_epsg=3007, v0=3
)
print('— Pipeline zakończony —')