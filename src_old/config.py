import os

# --- Earth Engine Configuration ---
GEE_PROJECT_ID = 'ee-my-biswajit'
DISTRICT_NAME = 'Goalpara'
GEE_ASSET_PATH = 'projects/ee-my-biswajit/assets/Assam_vill_boundaries' # Use None if using local shapefile
USE_LOCAL_SHP = False 

# --- Time Periods ---
START_YEAR = 2020
END_YEAR = 2025

# --- Local File Paths ---
BASE_DIR = r'D:\Personal Projects\Assignment\Village_Economic_Growth_Intelligence'

# Inputs
INPUT_SHP_PATH = os.path.join(BASE_DIR, 'data', 'output_data', 'vectore', 'filtered_village.shp')
INPUT_CSV_2020 = os.path.join(BASE_DIR, 'data', 'input_data', 'csvs', f'{DISTRICT_NAME}_Village_Data_{START_YEAR}.csv')
INPUT_CSV_END = os.path.join(BASE_DIR, 'data', 'input_data', 'csvs', f'{DISTRICT_NAME}_Village_Data_{END_YEAR}.csv')

# Outputs
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'output_data', 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_TOP100_CSV = os.path.join(OUTPUT_DIR, f'{DISTRICT_NAME}_Top_100_Growing_Villages.csv')
OUTPUT_STATIC_MAP = os.path.join(OUTPUT_DIR, f'{DISTRICT_NAME}_Economic_Growth_Map.png')
OUTPUT_INTERACTIVE_MAP = os.path.join(OUTPUT_DIR, f'{DISTRICT_NAME}_Interactive_Map.html')

# --- Scoring Weights ---
WEIGHT_BUILT = 0.45
WEIGHT_LIGHT = 0.45
WEIGHT_POP = 0.10

# --- Cleaning Thresholds ---
MIN_AREA_HECTARES = 50  # Filter out geometries smaller than ~2 VIIRS pixels