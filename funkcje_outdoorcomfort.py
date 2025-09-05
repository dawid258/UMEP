# =============================================================================
# 3. DEFINICJE FUNKCJI PIPELINE
#    (Logika przetwarzania dla każdego etapu)
# =============================================================================

def initialize_qgis():
    """Inicjalizuje aplikację QGIS."""
    qgs = QgsApplication([], False)
    QgsApplication.setPrefixPath(QGIS_PREFIX_PATH, True)
    qgs.initQgis()
    print("✅ Aplikacja QGIS zainicjalizowana.")
    return qgs

def run_step_1_tiling():
    """Krok 1: Tnie duże rastry na mniejsze kafelki z marginesem."""
    print("Rozpoczynam kafelkowanie rastrów wejściowych...")
    output_dirs = [os.path.join(BASE_DIR, name) for name in TILING_OUTPUT_DIRS_NAMES]
    for odir in output_dirs:
        os.makedirs(odir, exist_ok=True)
    
    print(f"Margines (px): {TILING_MARGIN_PX}")

    def compute_max_tile_size(margin, max_pixels):
        size = int(math.floor(math.sqrt(max_pixels)))
        while (size + 2 * margin) ** 2 > max_pixels:
            size -= 1
        return size

    tile_size = compute_max_tile_size(TILING_MARGIN_PX, TILING_MAX_PIXELS)
    print(f"Finalny tile_size bez marginesu: {tile_size} px")

    with ExitStack() as stack:
        srcs = [stack.enter_context(rasterio.open(p)) for p in TILING_INPUT_PATHS]
        widths = [src.width for src in srcs]
        heights = [src.height for src in srcs]
        W, H = min(widths), min(heights)
        print(f"Wspólny obszar rastrów: {W} x {H} px")

        for row_idx, top in enumerate(range(0, H, tile_size)):
            h = min(tile_size, H - top)
            for col_idx, left in enumerate(range(0, W, tile_size)):
                w = min(tile_size, W - left)

                top_m = TILING_MARGIN_PX if top > 0 else 0
                left_m = TILING_MARGIN_PX if left > 0 else 0
                bot_m = TILING_MARGIN_PX if (top + h) < H else 0
                right_m = TILING_MARGIN_PX if (left + w) < W else 0

                win_top = max(top - top_m, 0)
                win_left = max(left - left_m, 0)
                win_height = h + top_m + bot_m
                win_width = w + left_m + right_m

                if win_height * win_width > TILING_MAX_PIXELS:
                    print(f"⚠️ Pomijam kafelek ({row_idx},{col_idx}) – za dużo pikseli")
                    continue

                window = Window(win_left, win_top, win_width, win_height)
                transform = srcs[0].window_transform(window)
                profile = srcs[0].profile.copy()
                profile.update({'height': int(win_height), 'width': int(win_width), 'transform': transform})
                base_name = f"tile_r{row_idx:03d}_c{col_idx:03d}.tif"
                for idx, src in enumerate(srcs):
                    out_path = os.path.join(output_dirs[idx], base_name)
                    with rasterio.open(out_path, 'w', **profile) as dst:
                        dst.write(src.read(1, window=window), 1)
    print("✅ Krok 1 zakończony: Kafelki z marginesem zapisane.")

def run_step_2_svf():
    """Krok 2: Oblicza Sky View Factor dla każdego kafelka."""
    print("Rozpoczynam obliczenia Sky View Factor (SVF)...")
    os.makedirs(svf_output_dir, exist_ok=True)
    dsm_list = glob.glob(os.path.join(building_tiles_dir, "tile_*.tif"))
    for dsm_path in dsm_list:
        fname = os.path.basename(dsm_path)
        name_wo_ext = os.path.splitext(fname)[0]
        cdsm_path = os.path.join(canopy_tiles_dir, fname)
        dem_path = os.path.join(dem_tiles_dir, fname)
        if not (os.path.exists(cdsm_path) and os.path.exists(dem_path)):
            print(f"!! Brak pliku CDSM lub DEM dla {fname}, pomijam SVF.")
            continue
        out_dir = os.path.join(svf_output_dir, name_wo_ext)
        os.makedirs(out_dir, exist_ok=True)
        params = {'INPUT_DSM': dsm_path, 'INPUT_CDSM': cdsm_path, 'INPUT_DEM': dem_path, 'OUTPUT_DIR': out_dir, **SVF_PARAMS}
        print(f"  -> SVF dla {fname}")
        processing.run("umep:Urban Geometry: Sky View Factor", params)
    print("✅ Krok 2 zakończony: Obliczono SVF dla wszystkich kafelków.")

def run_step_3_wall_geometry():
    """Krok 3: Oblicza wysokość i ekspozycję ścian."""
    print("Rozpoczynam obliczenia geometrii ścian (wysokość i ekspozycja)...")
    os.makedirs(wall_height_dir, exist_ok=True)
    os.makedirs(wall_aspect_dir, exist_ok=True)
    feedback = QgsProcessingFeedback()
    pattern = os.path.join(building_tiles_dir, "*.tif")
    for in_fp in glob.glob(pattern):
        base = os.path.splitext(os.path.basename(in_fp))[0]
        out_h = os.path.join(wall_height_dir, f"{base}_wall_height.tif")
        out_a = os.path.join(wall_aspect_dir, f"{base}_wall_aspect.tif")
        print(f"  -> Geometria ścian dla {base}")
        params = {'INPUT': in_fp, 'INPUT_LIMIT': WALL_GEOMETRY_LIMIT, 'OUTPUT_HEIGHT': out_h, 'OUTPUT_ASPECT': out_a}
        processing.run("umep:Urban Geometry: Wall Height and Aspect", params, feedback=feedback)
    print("✅ Krok 3 zakończony: Obliczono geometrię ścian dla wszystkich kafelków.")

def run_step_4_solweig():
    """Krok 4: Uruchamia model SOLWEIG i zmienia nazwy plików wynikowych."""
    print("Rozpoczynam przetwarzanie modelem SOLWEIG...")
    os.makedirs(solweig_output_dir, exist_ok=True)
    for dsm_path in glob.glob(os.path.join(building_tiles_dir, "tile_*.tif")):
        fname = os.path.basename(dsm_path)
        name = os.path.splitext(fname)[0]
        out_dir = os.path.join(solweig_output_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        svf_zip = os.path.join(svf_output_dir, name, "svfs.zip")
        height = os.path.join(wall_height_dir, f"{name}_wall_height.tif")
        aspect = os.path.join(wall_aspect_dir, f"{name}_wall_aspect.tif")
        cdsm = os.path.join(canopy_tiles_dir, fname)
        dem = os.path.join(dem_tiles_dir, fname)
        missing = [p for p in (svf_zip, height, aspect, cdsm, dem) if not os.path.exists(p)]
        if missing:
            for p in missing:
                print(f"!! Brak pliku wejściowego {p} – pomijam SOLWEIG dla {name}")
            continue
        params = {'INPUT_DSM': dsm_path, 'INPUT_SVF': svf_zip, 'INPUT_HEIGHT': height, 'INPUT_ASPECT': aspect, 'INPUT_CDSM': cdsm, 'INPUT_DEM': dem, 'INPUTMET': SOLWEIG_MET_FILE, 'OUTPUT_DIR': out_dir, **SOLWEIG_PARAMS}
        print(f"  -> [SOLWEIG] {name}")
        processing.run("umep:Outdoor Thermal Comfort: SOLWEIG", params)
    print("\n--- Zakończono przetwarzanie SOLWEIG, rozpoczynam zmianę nazw plików Tmrt_average.tif ---")
    for dsm_path in glob.glob(os.path.join(building_tiles_dir, "tile_*.tif")):
        name = os.path.splitext(os.path.basename(dsm_path))[0]
        out_dir_tile = os.path.join(solweig_output_dir, name)
        old_file_path = os.path.join(out_dir_tile, "Tmrt_average.tif")
        new_file_path = os.path.join(out_dir_tile, f"{name}_Tmrt_average.tif")
        if os.path.exists(old_file_path):
            try:
                os.rename(old_file_path, new_file_path)
                print(f"  -> Zmieniono nazwę: {os.path.basename(old_file_path)} -> {os.path.basename(new_file_path)}")
            except OSError as e:
                print(f"!! Błąd przy zmianie nazwy pliku {old_file_path}: {e}")
        else:
            print(f"!! Plik {old_file_path} nie istnieje, pomijam zmianę nazwy.")
    print("✅ Krok 4 zakończony: Przetwarzanie SOLWEIG i zmiana nazw ukończone.")

def run_step_5_thermal_comfort():
    """Krok 5: Oblicza przestrzenny komfort termiczny (PET)."""
    print("Rozpoczynam obliczenia finalnego komfortu termicznego (PET)...")
    os.makedirs(thermal_comfort_output_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Używam folderu tymczasowego: {temp_dir}")
        for tile_path in glob.glob(os.path.join(building_tiles_dir, "tile_*.tif")):
            fname = os.path.basename(tile_path)
            name = os.path.splitext(fname)[0]
            tmrt_path = os.path.join(solweig_output_dir, name, THERMAL_COMFORT_SOLWEIG_REF_FILE)
            urock_path = os.path.join(urock_tiles_dir, fname)
            output_path = os.path.join(thermal_comfort_output_dir, f"{name}_thermal_comfort_PET.tif")
            if not os.path.exists(tmrt_path) or not os.path.exists(urock_path):
                if not os.path.exists(tmrt_path): print(f"!! Brak pliku TMRT: {tmrt_path}")
                if not os.path.exists(urock_path): print(f"!! Brak pliku Urock: {urock_path}")
                print(f"-- Pomijam kafelek {name}")
                continue
            print(f"--- Przetwarzam kafelek: {name} ---")
            tmrt_layer = QgsRasterLayer(tmrt_path, "tmrt_layer")
            urock_layer = QgsRasterLayer(urock_path, "urock_layer")
            if not tmrt_layer.isValid() or not urock_layer.isValid():
                print(f"!! Nie można wczytać jednego z rastrów dla {name}. Pomijam.")
                continue
            tmrt_to_process, urock_to_process = tmrt_path, urock_path
            if tmrt_layer.extent() != urock_layer.extent():
                print(f"  -> Wykryto różne zasięgi. Docinam do wspólnego obszaru.")
                intersect_extent = tmrt_layer.extent().intersect(urock_layer.extent())
                if intersect_extent.isNull() or intersect_extent.width() < tmrt_layer.rasterUnitsPerPixelX():
                    print(f"!! Wspólny obszar dla {name} jest zbyt mały. Pomijam.")
                    continue
                mask_path = os.path.join(temp_dir, f"{name}_mask.gpkg")
                mask_layer = QgsVectorLayer(f"Polygon?crs={tmrt_layer.crs().authid()}", "mask", "memory")
                prov = mask_layer.dataProvider()
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromRect(intersect_extent))
                prov.addFeature(feat)
                QgsVectorFileWriter.writeAsVectorFormat(mask_layer, mask_path, "utf-8", mask_layer.crs(), "GPKG")
                clipped_tmrt_path = os.path.join(temp_dir, f"{name}_tmrt_clipped.tif")
                clipped_urock_path = os.path.join(temp_dir, f"{name}_urock_clipped.tif")
                processing.run("gdal:cliprasterbymasklayer", {'INPUT': tmrt_path, 'MASK': mask_path, 'OUTPUT': clipped_tmrt_path})
                processing.run("gdal:cliprasterbymasklayer", {'INPUT': urock_path, 'MASK': mask_path, 'OUTPUT': clipped_urock_path})
                tmrt_to_process, urock_to_process = clipped_tmrt_path, clipped_urock_path
            params = {'TMRT_MAP': tmrt_to_process, 'UROCK_MAP': urock_to_process, 'TC_OUT': output_path, **THERMAL_COMFORT_PARAMS}
            print(f"  -> Uruchamiam analizę komfortu dla {name}...")
            try:
                processing.run("umep:Outdoor Thermal Comfort: Spatial Thermal Comfort", params)
                print(f"  -> Wynik zapisano w: {output_path}")
            except Exception as e:
                print(f"!!!! Wystąpił błąd podczas analizy {name}: {e}")
    print("✅ Krok 5 zakończony: Obliczanie komfortu termicznego ukończone.")

