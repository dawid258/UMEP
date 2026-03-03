import pandas as pd
import numpy as np

# --- KONFIGURACJA ---
INPUT_CSV   = "C:/Users/dawids/Desktop/PRACA/PROJEKTY/7_PILA/2025/ERA_5/fileb62143b1178_lat=53.25_lng=16.75_period=2023.csv"
OUTPUT_TXT  = "C:/Users/dawids/Desktop/PRACA/PROJEKTY/7_PILA/2025/ERA_5/era5_PILA_2023.txt"
UTC_OFFSET  = 1  # offset lokalnego czasu (godziny)
# ----------------------

# 1) Wczytanie CSV z danymi ERA5, pomijając komentarze
df = pd.read_csv(
    INPUT_CSV,
    comment='#',
    parse_dates=['datetime_lst']
)

# 2) Rozbicie daty i czasu
df['iy']   = df['datetime_lst'].dt.year
df['id']   = df['datetime_lst'].dt.dayofyear
df['it']   = df['datetime_lst'].dt.hour
df['imin'] = df['datetime_lst'].dt.minute

# 3) Obliczenie punktu rosy (do własnych analiz)
#    T w °C (ERA5 t2m już w °C)
T = df['t2m']
RH = df['r2m']
gamma = np.log(RH/100) + 17.27 * T / (237.7 + T)
df['Td'] = 237.7 * gamma / (17.27 - gamma)

# 4) Przygotowanie Tair dla SOLWEIG (w °C)
#    Używamy bezpośrednio t2m, bo jest w °C
df['Tair_C'] = df['t2m']

# 5) Mapowanie kolumn do formatu SEBE
out = pd.DataFrame({
    'iy':    df['iy'].astype(int),
    'id':    df['id'].astype(int),
    'it':    df['it'].astype(int),
    'imin':  df['imin'].astype(int),
    'qn':    -999.00,
    'qh':    -999.00,
    'qe':    -999.00,
    'qs':    -999.00,
    'qf':    -999.00,
    'U':     df['ws10'],         # prędkość wiatru 10m
    'RH':    df['r2m'],          # wilgotność względna
    'Tair':  df['Tair_C'],       # temperatura powietrza w °C
    'pres':  df['sp'],           # ciśnienie [Pa]
    'rain':  df['tp'],           # opad [mm]
    'kdown': df['ssrd'],         # promieniowanie krótkofalowe [W/m2]
    'snow':  df['sd'],           # pokrywa śnieżna [mm]
    'ldown': df['strd'],         # promieniowanie długofalowe [W/m2]
    'fcld':  -999.00,
    'wuh':   -999.00,
    'xsmd':  -999.00,
    'lai':   -999.00,
    'kdiff': df['dhi'],          # rozproszone promieniowanie [W/m2]
    'kdir':  df['dni'],          # bezpośrednie promieniowanie [W/m2]
    'wdir':  df['wdir10'],       # kierunek wiatru 10m
})

# 6) Zapis pliku SEBE z nagłówkiem
header = (
    '%iy id it imin   Q*      QH      QE      Qs      Qf    Wind    RH     Tair   '
    'press   rain    Kdn    snow    ldown   fcld    wuh     xsmd    lai_hr  Kdiff   '
    'Kdir    Wd\n'
)
with open(OUTPUT_TXT, 'w') as f:
    f.write(header)
    out.to_csv(f, sep=' ', index=False, float_format='%.2f')

print("Zapisano plik SEBE →", OUTPUT_TXT)
