
# UMEP
Install packed and script for using UMEP in QGIS
# QGIS + UMEP Setup & Running Custom Scripts


---

## Spis treści

1. [Pobranie i instalacja QGIS](#1-pobranie-i-instalacja-qgis-windows)
2. [Instalacja i konfiguracja JDK 24.0.1](#2-instalacja-i-konfiguracja-jdk-2401)
3. [Przygotowanie środowiska Python](#3-przygotowanie-środowiska-python)
4. [Instalacja wtyczki UMEP](#4-instalacja-wtyczki-umep)
5. [Dodanie folderu `scripts` do ścieżki Pythona](#5-dodanie-folderu-scripts-do-ścieżki-pythona)
6. [Uruchamianie własnych skryptów](#6-uruchamianie-własnych-skryptów)

---

## 1. Pobranie i instalacja QGIS (Windows)

1. Wejdź na: [https://qgis.org/pl/site/forusers/download.html](https://qgis.org/pl/site/forusers/download.html)
2. Pobierz **QGIS Standalone Installer** (zalecane LTR).
3. Uruchom pobrany plik `.exe`, klikasz **Next ▶** bez zmian, potem **Install**.
4. Po zakończeniu otwórz QGIS raz, żeby wygenerować domyślną strukturę profilu.

---

## 2. Instalacja i konfiguracja JDK 24.0.1

1. Oracle JDK: [https://www.oracle.com/java/technologies/javase/jdk24-archive-downloads.html](https://www.oracle.com/java/technologies/javase/jdk24-archive-downloads.html)
   OpenJDK: [https://jdk.java.net/24/](https://jdk.java.net/24/)
2. Pobierz **Windows x64 Installer (.exe)** → uruchom → **Next ▶** → **Install**.

   > Domyślna ścieżka: `C:\Program Files\Java\jdk-24.0.1`
3. Ustaw zmienne środowiskowe:

   * `JAVA_HOME` = `C:\Program Files\Java\jdk-24.0.1`
   * `PATH` → dodaj `%JAVA_HOME%\bin`
4. Sprawdź w cmd:

   ```bat
   java -version
   ```

   Powinno wypisać: `java version "24.0.1" ...`
=======
# UMEP w QGIS: Instalacja i Użycie z Własnymi Skryptami

Kompletny przewodnik po instalacji wtyczki UMEP w QGIS, konfiguracji środowiska oraz uruchamianiu zautomatyzowanych skryptów do analiz solarnych.

---

## Spis Treści

1.  [Instalacja QGIS](#1-instalacja-qgis)
2.  [Konfiguracja JDK](#2-konfiguracja-jdk)
3.  [Przygotowanie środowiska Python](#3-przygotowanie-środowiska-python)
4.  [Instalacja wtyczki UMEP](#4-instalacja-wtyczki-umep)
5.  [Uruchamianie własnych skryptów](#5-uruchamianie-własnych-skryptów)

---

## 1. Instalacja QGIS

Aby rozpocząć, potrzebujesz działającej instalacji QGIS. Zalecana jest wersja **LTR (Long Term Release)** ze względu na jej stabilność.

1.  Przejdź na oficjalną stronę: [qgis.org/pl/site/forusers/download.html](https://qgis.org/pl/site/forusers/download.html).
2.  Pobierz **QGIS Standalone Installer** dla Twojego systemu (np. Windows).
3.  Uruchom instalator i postępuj zgodnie z instrukcjami, akceptując domyślne ustawienia.
4.  Po instalacji uruchom QGIS przynajmniej raz. Spowoduje to utworzenie niezbędnych folderów profilu użytkownika (np. w `C:\Users\TwojaNazwa\AppData\Roaming\QGIS\QGIS3`).

---

## 2. Konfiguracja JDK

UMEP, a w szczególności niektóre jego narzędzia, wymagają środowiska Java Development Kit (JDK) do poprawnego działania.

1.  **Pobierz JDK**, np. w wersji 24.0.1. Możesz wybrać pomiędzy:
    * **Oracle JDK**: [Oficjalna strona Oracle](https://www.oracle.com/java/technologies/javase/jdk24-archive-downloads.html)
    * **OpenJDK**: [Strona OpenJDK](https://jdk.java.net/24/)
2.  Uruchom pobrany instalator `.exe`. Domyślna ścieżka instalacji to `C:\Program Files\Java\jdk-24.0.1`.
3.  **Ustaw zmienne środowiskowe**, aby system "wiedział", gdzie szukać Javy:
    * Naciśnij `Win + S` i wyszukaj "Edytuj zmienne środowiskowe systemu".
    * W oknie "Właściwości systemu" kliknij **Zmienne środowiskowe**.
    * W sekcji **Zmienne systemowe** dodaj nową zmienną:
        * **Nazwa zmiennej**: `JAVA_HOME`
        * **Wartość zmiennej**: `C:\Program Files\Java\jdk-24.0.1` (upewnij się, że ścieżka jest poprawna!)
    * Zaktualizuj zmienną `Path`:
        * Znajdź `Path` na liście zmiennych systemowych i kliknij **Edytuj**.
        * Dodaj nowy wpis: `%JAVA_HOME%\bin`. Pozwoli to na uruchamianie poleceń `java` z dowolnego miejsca w systemie.
4.  **Zweryfikuj instalację**:
    * Otwórz nowy wiersz poleceń (CMD/PowerShell) i wpisz:
      ```sh
      java -version
      ```
    * Oczekiwany wynik powinien potwierdzić zainstalowaną wersję, np. `java version "24.0.1"`.


---

## 3. Przygotowanie środowiska Python


1. Otwórz **OSGeo4W Shell** (domyślny terminal QGIS) lub terminal systemowy.
2. Skopiuj i wklej poniższą komendę instalacji bibliotek

   ```
   python -m pip install --no-cache-dir affine==2.4.0 annotated-types==0.7.0 anyio==4.9.0 argon2-cffi==25.1.0 argon2-cffi-bindings==21.2.0 arrow==1.3.0 asteval==1.0.6 asttokens==3.0.0 async-lru==2.0.5 atmosp==0.2.9 attrs==25.3.0 babel==2.17.0 beautifulsoup4==4.13.4 bleach==6.2.0 cdsapi==0.7.6 certifi==2025.7.14 cffi==1.17.1 cftime==1.6.4.post1 chardet==5.2.0 charset-normalizer==3.4.2 click==8.2.1 click-plugins==1.1.1.2 cligj==0.7.2 cloudpickle==3.1.1 colorama==0.4.6 comm==0.2.2 contourpy==1.2.1 cycler==0.12.1 dask==2025.7.0 debugpy==1.8.15 decorator==5.2.1 defusedxml==0.7.1 dill==0.4.0 duckdb==1.3.1 ecmwf-datastores-client==0.2.0 et_xmlfile==1.1.0 executing==2.2.0 ExifRead==3.0.0 f90nml==1.4.4 f90wrap==0.2.16 fastjsonschema==2.21.1 flexcache==0.3 flexparser==0.4 fonttools==4.51.0 fqdn==1.5.1 fsspec==2025.7.0 future==1.0.0 GDAL==3.11.3 geographiclib==2.0 geopandas==1.0.1 h11==0.16.0 h3==4.3.0 h5py==3.14.0 httpcore==1.0.9 httplib2==0.22.0 httpx==0.28.1 idna==3.10 ipykernel==6.30.0 ipython==9.4.0 ipython_pygments_lexers==1.1.1 isoduration==20.11.0 JayDeBeApi==1.2.3 jedi==0.19.2 Jinja2==3.1.6 jpype1==1.6.0 json5==0.12.0 jsonpointer==3.0.0 jsonschema==4.25.0 jsonschema-specifications==2025.4.1 jupyter-events==0.12.0 jupyter-lsp==2.2.6 jupyter_client==8.6.3 jupyter_core==5.8.1 jupyter_server==2.16.0 jupyter_server_terminals==0.5.3 jupyterlab==4.4.5 jupyterlab_pygments==0.3.0 jupyterlab_server==2.27.3 kiwisolver==1.4.5 lark==1.2.2 linecache2==1.0.0 llvmlite==0.42.0 lmfit==1.3.4 locket==1.0.0 lxml==5.3.0 MarkupSafe==3.0.2 matplotlib==3.10.0 matplotlib-inline==0.1.7 mistune==3.1.3 mock==5.1.0 multiprocess==0.70.18 multiurl==0.3.6 nbclient==0.10.2 nbconvert==7.16.6 nbformat==5.10.4 nest-asyncio==1.6.0 netCDF4==1.7.2 networkx==3.3 nose==1.3.7 nose2==0.14.1 notebook_shim==0.2.4 numba==0.59.0 numdifftools==0.9.41 numexpr==2.11.0 numpy==1.26.4 openpyxl==3.1.2 overrides==7.7.0 OWSLib==0.32.0 packaging==25.0 pandas==2.2.2 pandocfilters==1.5.1 parso==0.8.4 partd==1.4.2 pillow==11.1.0 Pint==0.24.4 platformdirs==4.3.8 Platypus-Opt==1.0.4 plotly==5.20.0 ply==3.11 prometheus_client==0.22.1 prompt_toolkit==3.0.51 psutil==7.0.0 psycopg==3.1.18 psycopg2==2.9.10 pure_eval==0.2.3 pvlib==0.13.0 pycparser==2.22 pydantic==2.11.7 pydantic_core==2.33.2 Pygments==2.19.2 pyodbc==5.1.0 PyOpenGL==3.1.7 pyparsing==3.1.2 PyPDF2==3.0.1 pypiwin32==223 pyproj==3.7.0 PyQt5==5.15.11 PyQt5_sip==12.16.1 pyserial==3.5 python-dateutil==2.9.0.post0 python-json-logger==3.3.0 pytz==2024.1 PyYAML==6.0.2 pyzmq==27.0.0 rasterio==1.4.3 referencing==0.36.2 remotior_sensus==0.4.4 reportlab==4.2.5 requests==2.32.4 rfc3339-validator==0.1.4 rfc3986-validator==0.1.1 rfc3987-syntax==1.1.0 rioxarray==0.19.0 rpds-py==0.26.0 scipy==1.13.0 seaborn==0.13.2 Send2Trash==1.8.3 setuptools==80.9.0 shapely==2.0.6 simplejson==3.19.2 sip==6.9.1 six==1.17.0 sniffio==1.3.1 soupsieve==2.7 stack-data==0.6.3 supy==2025.7.9.dev0 target-py==0.1.1 tenacity==8.2.3 terminado==0.18.1 timezonefinder==6.0.1 tinycss2==1.4.0 toolz==1.0.0 tornado==6.5.1 tqdm==4.67.1 traceback2==1.4.0 traitlets==5.14.3 types-python-dateutil==2.9.0.20250708 typing-inspection==0.4.1 typing_extensions==4.14.1 tzdata==2024.1 umep-reqs==2.6 uncertainties==3.2.3 unittest2==1.1.0 uri-template==1.3.0 urllib3==2.5.0 wcwidth==0.2.13 webcolors==24.11.1 webencodings==0.5.1 websocket-client==1.8.0 xarray==2025.7.1 xlrd==2.0.1 xlwt==1.3.0

=======
QGIS posiada własne środowisko Python. Aby uruchomić zaawansowane skrypty, należy doinstalować wymagane biblioteki.

1.  Otwórz **OSGeo4W Shell**, który jest dołączony do instalacji QGIS (znajdziesz go w menu Start).
2.  Wklej i uruchom poniższą komendę, aby zainstalować wszystkie niezbędne pakiety. Użycie opcji `--no-cache-dir` pomaga uniknąć problemów z przestarzałymi wersjami pakietów.

    ```bash
    python -m pip install --no-cache-dir affine==2.4.0 annotated-types==0.7.0 anyio==4.9.0 argon2-cffi==25.1.0 argon2-cffi-bindings==21.2.0 arrow==1.3.0 asteval==1.0.6 asttokens==3.0.0 async-lru==2.0.5 atmosp==0.2.9 attrs==25.3.0 babel==2.17.0 beautifulsoup4==4.13.4 bleach==6.2.0 cdsapi==0.7.6 certifi==2025.7.14 cffi==1.17.1 cftime==1.6.4.post1 chardet==5.2.0 charset-normalizer==3.4.2 click==8.2.1 click-plugins==1.1.1.2 cligj==0.7.2 cloudpickle==3.1.1 colorama==0.4.6 comm==0.2.2 contourpy==1.2.1 cycler==0.12.1 dask==2025.7.0 debugpy==1.8.15 decorator==5.2.1 defusedxml==0.7.1 dill==0.4.0 duckdb==1.3.1 ecmwf-datastores-client==0.2.0 et_xmlfile==1.1.0 executing==2.2.0 ExifRead==3.0.0 f90nml==1.4.4 f90wrap==0.2.16 fastjsonschema==2.21.1 flexcache==0.3 flexparser==0.4 fonttools==4.51.0 fqdn==1.5.1 fsspec==2025.7.0 future==1.0.0 GDAL==3.11.3 geographiclib==2.0 geopandas==1.0.1 h11==0.16.0 h3==4.3.0 h5py==3.14.0 httpcore==1.0.9 httplib2==0.22.0 httpx==0.28.1 idna==3.10 ipykernel==6.30.0 ipython==9.4.0 ipython_pygments_lexers==1.1.1 isoduration==20.11.0 JayDeBeApi==1.2.3 jedi==0.19.2 Jinja2==3.1.6 jpype1==1.6.0 json5==0.12.0 jsonpointer==3.0.0 jsonschema==4.25.0 jsonschema-specifications==2025.4.1 jupyter-events==0.12.0 jupyter-lsp==2.2.6 jupyter_client==8.6.3 jupyter_core==5.8.1 jupyter_server==2.16.0 jupyter_server_terminals==0.5.3 jupyterlab==4.4.5 jupyterlab_pygments==0.3.0 jupyterlab_server==2.27.3 kiwisolver==1.4.5 lark==1.2.2 linecache2==1.0.0 llvmlite==0.42.0 lmfit==1.3.4 locket==1.0.0 lxml==5.3.0 MarkupSafe==3.0.2 matplotlib==3.10.0 matplotlib-inline==0.1.7 mistune==3.1.3 mock==5.1.0 multiprocess==0.70.18 multiurl==0.3.6 nbclient==0.10.2 nbconvert==7.16.6 nbformat==5.10.4 nest-asyncio==1.6.0 netCDF4==1.7.2 networkx==3.3 nose==1.3.7 nose2==0.14.1 notebook_shim==0.2.4 numba==0.59.0 numdifftools==0.9.41 numexpr==2.11.0 numpy==1.26.4 openpyxl==3.1.2 overrides==7.7.0 OWSLib==0.32.0 packaging==25.0 pandas==2.2.2 pandocfilters==1.5.1 parso==0.8.4 partd==1.4.2 pillow==11.1.0 Pint==0.24.4 platformdirs==4.3.8 Platypus-Opt==1.0.4 plotly==5.20.0 ply==3.11 prometheus_client==0.22.1 prompt_toolkit==3.0.51 psutil==7.0.0 psycopg==3.1.18 psycopg2==2.9.10 pure_eval==0.2.3 pvlib==0.13.0 pycparser==2.22 pydantic==2.11.7 pydantic_core==2.33.2 Pygments==2.19.2 pyodbc==5.1.0 PyOpenGL==3.1.7 pyparsing==3.1.2 PyPDF2==3.0.1 pypiwin32==223 pyproj==3.7.0 PyQt5==5.15.11 PyQt5_sip==12.16.1 pyserial==3.5 python-dateutil==2.9.0.post0 python-json-logger==3.3.0 pytz==2024.1 PyYAML==6.0.2 pyzmq==27.0.0 rasterio==1.4.3 referencing==0.36.2 remotior_sensus==0.4.4 reportlab==4.2.5 requests==2.32.4 rfc3339-validator==0.1.4 rfc3986-validator==0.1.1 rfc3987-syntax==1.1.0 rioxarray==0.19.0 rpds-py==0.26.0 scipy==1.13.0 seaborn==0.13.2 Send2Trash==1.8.3 setuptools==80.9.0 shapely==2.0.6 simplejson==3.19.2 sip==6.9.1 six==1.17.0 sniffio==1.3.1 soupsieve==2.7 stack-data==0.6.3 supy==2025.7.9.dev0 target-py==0.1.1 tenacity==8.2.3 terminado==0.18.1 timezonefinder==6.0.1 tinycss2==1.4.0 toolz==1.0.0 tornado==6.5.1 tqdm==4.67.1 traceback2==1.4.0 traitlets==5.14.3 types-python-dateutil==2.9.0.20250708 typing-inspection==0.4.1 typing_extensions==4.14.1 tzdata==2024.1 umep-reqs==2.6 uncertainties==3.2.3 unittest2==1.1.0 uri-template==1.3.0 urllib3==2.5.0 wcwidth==0.2.13 webcolors==24.11.1 webencodings==0.5.1 websocket-client==1.8.0 xarray==2025.7.1 xlrd==2.0.1 xlwt==1.3.0
    ```


---

## 4. Instalacja wtyczki UMEP


### Opcja A: Plugin Manager

1. W QGIS: **Wtyczki ▶ Zarządzaj i instaluj...**
2. Wyszukaj `UMEP`, kliknij **Zainstaluj wtyczkę**.

### Opcja B: Ręczna instalacja

1. Pobierz ZIP z GitHub:
   [https://github.com/janangilani/qgis-umep-plugin/archive/refs/heads/master.zip](https://github.com/janangilani/qgis-umep-plugin/archive/refs/heads/master.zip)
2. Rozpakuj folder `qgis-umep-plugin-master` do:

   ```
   %USERPROFILE%\.qgis3\python\plugins\umep
   ```
3. Zrestartuj QGIS.

---

## 5. Pobranie skryptów

1. Pobranie skryptów dla odpowiedniej metody i uruchomienie. Tutaj przykład uruchomienia skryptu obliczania nasłonecznienia:
```
---
import os
from funkcje_SEBE import *
import glob, psutil
from qgis.core import QgsProcessingFeedback
import processing

```
```
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
```


```
# -------------------------------------------------------------------------
# 2) KATALOGI UMEP / SEBE
# -------------------------------------------------------------------------
UMEP_HEIGHT_DIR  = os.path.join(WORK_DIR, 'umep_height')
UMEP_ASPECT_DIR  = os.path.join(WORK_DIR, 'umep_aspect')
SEBE_SKY_DIR     = os.path.join(WORK_DIR, 'sky_irr')
SEBE_OUTPUT_DIR  = os.path.join(WORK_DIR, 'roof_irr')
```

```
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
```

```
# -------------------------------------------------------------------------
# 4) Uruchomienie pipeline
# -------------------------------------------------------------------------
os.makedirs(TILES_DIR,           exist_ok=True)
os.makedirs(UMEP_HEIGHT_DIR,     exist_ok=True)
os.makedirs(UMEP_ASPECT_DIR,     exist_ok=True)
os.makedirs(SEBE_SKY_DIR,        exist_ok=True)
os.makedirs(SEBE_OUTPUT_DIR,     exist_ok=True)
os.makedirs(os.path.dirname(MOSAIC_TIF), exist_ok=True)
```

=======
Najprostszym sposobem instalacji UMEP jest użycie wbudowanego menedżera wtyczek QGIS.

1.  W QGIS przejdź do menu **Wtyczki > Zarządzaj i instaluj wtyczki**.
2.  W wyszukiwarce wpisz `UMEP`.
3.  Zaznacz wtyczkę na liście i kliknij **Zainstaluj wtyczkę**.
4.  Po zakończeniu instalacji **zrestartuj QGIS**, aby upewnić się, że wszystkie komponenty zostały poprawnie załadowane.

---

## 5. Uruchamianie własnych skryptów

Poniższy przykład demonstruje, jak zautomatyzować proces obliczania nasłonecznienia (insolacji) dachów z wykorzystaniem narzędzi UMEP i `processing` w QGIS.

### Krok 1: Import bibliotek i zdefiniowanie ścieżek

Na początku skryptu importujemy niezbędne moduły i definiujemy wszystkie ścieżki do danych wejściowych, pośrednich i wynikowych.

```python
import os
import glob
import psutil
from qgis.core import QgsProcessingFeedback
import processing
# Załóżmy, że funkcje pomocnicze są w pliku funkcje_SEBE.py
from funkcje_SEBE import *
```
```
# --- 1) GŁÓWNE KATALOGI ---
BASE_DIR = r"C:/Users/dawids/Desktop/PRACA/PROJEKTY/7_PILA/SEBE_V3_pipeline_test"
RAW_DIR = os.path.join(BASE_DIR, '1_dane')
WORK_DIR = os.path.join(BASE_DIR, 'pipeline_work')
TILES_DIR = os.path.join(WORK_DIR, 'tiles')
```
```

# --- 2) PLIKI WEJŚCIOWE I WYJŚCIOWE ---
DSM_TIF = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/rzeszow_NMPT_przyciete.tif"
MASK_VECTOR_GPKG = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/maska_przyciecia.gpkg"
BUILDINGS_GPKG = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/bdot_przyciety.gpkg"
SEBE_METEO_FILE = "C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/SEBE/solar_Rzeszow_2023.txt"
MOSAIC_TIF = os.path.join(WORK_DIR, 'pila_mozaika.tif')
CLIPPED_MOSAIC_TIF = os.path.join(WORK_DIR, 'pila_solar_cut.tif')
```
```
# --- 3) KATALOGI DLA WYNIKÓW UMEP / SEBE ---
UMEP_HEIGHT_DIR = os.path.join(WORK_DIR, 'umep_height')
UMEP_ASPECT_DIR = os.path.join(WORK_DIR, 'umep_aspect')
SEBE_SKY_DIR = os.path.join(WORK_DIR, 'sky_irr')
SEBE_OUTPUT_DIR = os.path.join(WORK_DIR, 'roof_irr')
```
```
# --- 4) Pozostałe pliki wynikowe ---
SLOPE_TIF = os.path.join(WORK_DIR, 'slope_deg.tif')
AREA_TIF = os.path.join(WORK_DIR, 'actual_area.tif')
ENERGY_CORRECTED_TIF = os.path.join(WORK_DIR, 'energy_corrected.tif')
BUILDINGS_CLASS_GPKG = os.path.join(WORK_DIR, 'buildings_classified.gpkg')
BUILDINGS_BUF_GPKG = os.path.join(WORK_DIR, 'buildings_buffer.gpkg')
ENERGY_BUILD_TIF = os.path.join(WORK_DIR, 'energy_corrected_building.tif')
```
```
# --- Przygotowanie struktury folderów ---
os.makedirs(TILES_DIR, exist_ok=True)
os.makedirs(UMEP_HEIGHT_DIR, exist_ok=True)
os.makedirs(UMEP_ASPECT_DIR, exist_ok=True)
os.makedirs(SEBE_SKY_DIR, exist_ok=True)
os.makedirs(SEBE_OUTPUT_DIR, exist_ok=True)

```

```
# 0) Preprocessing
NMPT_PATH = os.path.join("C:/Users/dawids/Desktop/Dawid/TESTY/RZESZOW/rzeszow_NMPT_przyciete.tif")
preprocess_nmpt_tiles(
    nmpt_path=NMPT_PATH,
    out_dir=TILES_DIR,
    margin=20,
    max_pixels=500_000
)


```
```
=======
```
```


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
```
```
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
```
```
# 3) Mozaika
feather = 40
mem, w, h = estimate_memory_requirements(SEBE_OUTPUT_DIR, feather)
tile_sz = 1024 if mem > psutil.virtual_memory().available/(1024**3)*0.8 else 2048
mosaic_with_gauss_grid(SEBE_OUTPUT_DIR, MOSAIC_TIF, feather_px=feather, tile_size=tile_sz)
```


=======

```
# # 4) Przycinanie
clip_raster_to_mask(MOSAIC_TIF, MASK_VECTOR_GPKG, output_path=CLIPPED_MOSAIC_TIF)
```


=======

```
# 5) Nachylenie i korekta
create_slope_raster(DSM_TIF, SLOPE_TIF)
compute_actual_area(SLOPE_TIF, AREA_TIF)
compute_corrected_energy(ENERGY_RAW_TIF, SLOPE_TIF, ENERGY_CORRECTED_TIF)
reclassify_radiation(ENERGY_CORRECTED_TIF, RAD_CLASS_TIF)
```



=======

```
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

```
