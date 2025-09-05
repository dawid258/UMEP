# -*- coding: utf-8 -*-
"""
=============================================================================
=== KOMPLETNY PIPELINE ANALIZY KOMFORTU TERMICZNEGO (WERSJA ZUNIFIKOWANA) ===
=============================================================================

Ten skrypt stanowi kompletny, zautomatyzowany zestaw do przeprowadzenia analizy
komfortu termicznego, łącząc wszystkie niezbędne kroki w jeden logiczny ciąg.

STRUKTURA PROJEKTU:
-------------------
Wszystkie ścieżki są generowane z jednego katalogu głównego (BASE_DIR).
Oczekiwana struktura folderów przed uruchomieniem:

BASE_DIR
└─── 00_dane_wejsciowe
     +--- canopy_res5_Pila.tif
     +--- dsm_dem_buildings_res_5_Pila.tif
     +--- NMT_2025_res5_epsg_2177_Pila.tif
     +--- LC_2025_res5_Pila.tif
     +--- urock_raster_rest_5_dir_135.tif
     +--- (inne pliki, np. era5_Pila_hot_day_2023.txt)

INSTRUKCJA:
-----------
1. Ustaw poprawną ścieżkę do swojego katalogu głównego w zmiennej `BASE_DIR`.
2. Upewnij się, że wszystkie pliki wejściowe znajdują się w podfolderze `00_dane_wejsciowe`.
3. Uruchom skrypt w środowisku z dostępem do bibliotek QGIS i Rasterio.

"""
import os
import math
import glob
import tempfile
from contextlib import ExitStack

# --- Bloki try-except dla importów, aby upewnić się, że środowisko jest gotowe ---
try:
    import rasterio
    from rasterio.windows import Window
    from qgis.core import (
        QgsApplication, QgsProcessingFeedback, QgsRasterLayer, QgsVectorLayer,
        QgsFeature, QgsGeometry, QgsVectorFileWriter
    )
    import processing
except ImportError as e:
    print(f"BŁĄD KRYTYCZNY: Brak wymaganej biblioteki: {e}")
    print("Upewnij się, że skrypt jest uruchamiany w środowisku Python z zainstalowanym QGIS i Rasterio.")
    exit()

# =============================================================================
# 1. KONFIGURACJA GŁÓWNA
#    (JEDYNE MIEJSCE DO EDYCJI PRZEZ UŻYTKOWNIKA)
# =============================================================================

# --- ŚCIEŻKA DO INSTALACJI QGIS (dla skryptów standalone) ---
QGIS_PREFIX_PATH = r"C:/Program Files/QGIS 3.28/apps/qgis"

# --- GŁÓWNY KATALOG PROJEKTU ---
# Wszystkie inne foldery zostaną utworzone wewnątrz tej lokalizacji.
BASE_DIR = r"C:/Users/dawids/Desktop/PRACA/PROJEKTY/7_PILA/2025/THERMAL_COMFORT/pipeline_test"

# --- NAZWY PLIKÓW I FOLDERÓW ---
# Folder z danymi wejściowymi (musi istnieć wewnątrz BASE_DIR)
INPUT_DATA_SUBDIR = "00_dane_wejsciowe"

# Nazwy wejściowych plików rastrowych (muszą znajdować się w folderze INPUT_DATA_SUBDIR)
RASTER_CANOPY = "canopy_res5_Pila.tif"
RASTER_BUILDINGS_DSM = "dsm_dem_buildings_res_5_Pila.tif"
RASTER_DEM = "NMT_2025_res5_epsg_2177_Pila.tif"
RASTER_LAND_COVER = "LC_2025_res5_Pila.tif"
RASTER_UROCK = "urock_raster_rest_5_dir_135.tif"
METEO_FILE = "era5_Pila_hot_day_2023.txt"

# Nazwy folderów wyjściowych dla poszczególnych etapów (zostaną utworzone automatycznie)
TILES_CANOPY_DIR_NAME = "01_tiles_canopy"
TILES_BUILDINGS_DIR_NAME = "01_tiles_buildings_dsm"
TILES_DEM_DIR_NAME = "01_tiles_dem"
TILES_LC_DIR_NAME = "01_tiles_land_cover"
TILES_UROCK_DIR_NAME = "01_tiles_urock"
SVF_OUTPUT_DIR_NAME = "02_svf_output"
WALL_HEIGHT_DIR_NAME = "03_wall_height"
WALL_ASPECT_DIR_NAME = "03_wall_aspect"
SOLWEIG_OUTPUT_DIR_NAME = "04_solweig_output"
THERMAL_COMFORT_DIR_NAME = "05_thermal_comfort_PET"

# --- PARAMETRY PRZETWARZANIA ---
# Etap 1: Kafelkowanie
TILING_MAX_PIXELS = 300000
TILING_MARGIN_PX = 20

# Etap 2: Sky View Factor
SVF_PARAMS = {
    'TRANS_VEG': 3, 'INPUT_TDSM': None, 'INPUT_THEIGHT': 25, 'ANISO': True,
    'WALL_SCHEME': False, 'KMEANS': True, 'CLUSTERS': 5,
    'INPUT_SVFHEIGHT': 1, 'OUTPUT_FILE': 'TEMPORARY_OUTPUT'
}

# Etap 3: Geometria ścian
WALL_GEOMETRY_LIMIT = 3

# Etap 4: SOLWEIG (pamiętając o logice ze skryptu nr 4, który mi pokazałeś)
SOLWEIG_PARAMS = {
    'TRANS_VEG': 3, 'LEAF_START': 97, 'LEAF_END': 300, 'CONIFER_TREES': False,
    'INPUT_TDSM': None, 'INPUT_THEIGHT': 25, 'USE_LC_BUILD': False, 'SAVE_BUILD': False,
    'INPUT_ANISO': '', 'INPUT_WALLSCHEME': '', 'WALLTEMP_NETCDF': False, 'WALL_TYPE': 1,
    'ALBEDO_WALLS': 0.2, 'ALBEDO_GROUND': 0.15, 'EMIS_WALLS': 0.9, 'EMIS_GROUND': 0.95,
    'ABS_S': 0.7, 'ABS_L': 0.95, 'POSTURE': 0, 'CYL': True, 'ONLYGLOBAL': False, 'UTC': 0,
    'AGE': 35, 'ACTIVITY': 80, 'CLO': 0.9, 'WEIGHT': 75, 'HEIGHT': 180, 'SEX': 0,
    'SENSOR_HEIGHT': 10, 'OUTPUT_TMRT': True, 'OUTPUT_KDOWN': False, 'OUTPUT_KUP': False,
    'OUTPUT_LDOWN': False, 'OUTPUT_LUP': False, 'OUTPUT_SH': False, 'OUTPUT_TREEPLANTER': True
}

# Etap 6: Komfort Termiczny
THERMAL_COMFORT_SOLWEIG_REF_FILE = "Kdiff_2023_196_1200D.tif" # Plik z wyników SOLWEIG używany jako wejście
THERMAL_COMFORT_PARAMS = {
    'TC_TYPE': 0, 'AGE': 35, 'ACTIVITY': 80, 'CLO': 0.9, 'WEIGHT': 75,
    'HEIGHT': 180, 'SEX': 0, 'COMFA': False
}

# =============================================================================
# 2. AUTOMATYCZNE TWORZENIE PEŁNYCH ŚCIEŻEK
#    (Tej sekcji nie należy modyfikować)
# =============================================================================

# --- Ścieżki do danych wejściowych ---
INPUT_RASTERS_DIR = os.path.join(BASE_DIR, INPUT_DATA_SUBDIR)
TILING_INPUT_PATHS = [
    os.path.join(INPUT_RASTERS_DIR, RASTER_CANOPY),
    os.path.join(INPUT_RASTERS_DIR, RASTER_BUILDINGS_DSM),
    os.path.join(INPUT_RASTERS_DIR, RASTER_DEM),
    os.path.join(INPUT_RASTERS_DIR, RASTER_LAND_COVER),
    os.path.join(INPUT_RASTERS_DIR, RASTER_UROCK)
]
SOLWEIG_MET_FILE = os.path.join(INPUT_RASTERS_DIR, METEO_FILE)

# --- Ścieżki do folderów wyjściowych (tworzone z BASE_DIR) ---
# Etap 1: Foldery na kafelki
TILING_OUTPUT_DIRS_NAMES = [
    TILES_CANOPY_DIR_NAME, TILES_BUILDINGS_DIR_NAME, TILES_DEM_DIR_NAME,
    TILES_LC_DIR_NAME, TILES_UROCK_DIR_NAME
]
canopy_tiles_dir = os.path.join(BASE_DIR, TILES_CANOPY_DIR_NAME)
building_tiles_dir = os.path.join(BASE_DIR, TILES_BUILDINGS_DIR_NAME)
dem_tiles_dir = os.path.join(BASE_DIR, TILES_DEM_DIR_NAME)
urock_tiles_dir = os.path.join(BASE_DIR, TILES_UROCK_DIR_NAME)

# Etapy 2-6
svf_output_dir = os.path.join(BASE_DIR, SVF_OUTPUT_DIR_NAME)
wall_height_dir = os.path.join(BASE_DIR, WALL_HEIGHT_DIR_NAME)
wall_aspect_dir = os.path.join(BASE_DIR, WALL_ASPECT_DIR_NAME)
solweig_output_dir = os.path.join(BASE_DIR, SOLWEIG_OUTPUT_DIR_NAME)
thermal_comfort_output_dir = os.path.join(BASE_DIR, THERMAL_COMFORT_DIR_NAME)



# =============================================================================
# 4. GŁÓWNY BLOK WYKONAWCZY
#    (Uruchamia cały pipeline)
# =============================================================================


    
print("\n" + "="*60)
print(" ROZPOCZYNAM GŁÓWNY PIPELINE PRZETWARZANIA ".center(60, "="))
print("="*60 + "\n")

try:
    # --- Uruchomienie kolejnych kroków ---
    print("\n===== KROK 1: KAFELKOWANIE Rastrów =====")
    run_step_1_tiling()
        
    print("\n===== KROK 2: OBLICZANIE SKY VIEW FACTOR =====")
    run_step_2_svf()
        
    print("\n===== KROK 3: OBLICZANIE GEOMETRII ŚCIAN =====")
    run_step_3_wall_geometry()
        
    print("\n===== KROK 4: PRZETWARZANIE SOLWEIG =====")
    run_step_4_solweig()
        
    print("\n===== KROK 5: OBLICZANIE KOMFORTU TERMICZNEGO (PET) =====")
    run_step_5_thermal_comfort()

    print("\n" + "="*60)
    print("🎉 WSZYSTKIE ETAPY PIPELINE'U ZAKOŃCZONE POMYŚLNIE 🎉".center(60, " "))
    print("="*60 + "\n")

except Exception as e:
    import traceback
    print(f"\n" + "!"*60)
    print(" WYSTĄPIŁ KRYTYCZNY BŁĄD ".center(60, "!"))
    print(f"BŁĄD: {e}")
    traceback.print_exc()
    print("!"*60 + "\n")
finally:
    # --- Zawsze zamykaj QGIS na końcu ---
    qgs.exitQgis()
    print("✅ Aplikacja QGIS zamknięta. Koniec pracy.")