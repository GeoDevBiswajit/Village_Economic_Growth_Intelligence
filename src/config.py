import os

# --- Earth Engine Parameters ---
EE_PROJECT_ID = 'ee-my-biswajit'
DISTRICT_NAME = 'Goalpara'
START_2020 = '2020-01-01'
END_2020 = '2020-12-31'
START_2025 = '2025-01-01'
END_2025 = '2025-12-31'

# --- File Paths ---
# Use absolute paths or dynamic relative paths based on environment
BASE_DIR = r'D:\Personal Projects\Assignment\Village_Economic_Growth_Intelligence'
VECTOR_DIR = os.path.join(BASE_DIR, 'data', 'output_data', 'vectore')
CSV_DIR = os.path.join(BASE_DIR, 'data', 'input_data', 'csvs')
RESULTS_DIR = os.path.join(BASE_DIR, 'data', 'output_data', 'results')

# Ensure directories exist
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

CSV_2020_PATH = os.path.join(CSV_DIR, f'{DISTRICT_NAME}_Village_Data_2020.csv')
CSV_2025_PATH = os.path.join(CSV_DIR, f'{DISTRICT_NAME}_Village_Data_2025.csv')

# --- Processing & Scoring Parameters ---
SPATIAL_THRESHOLD_HA = 50  # Minimum village size in hectares (~2 VIIRS pixels)
WEIGHT_BUILT = 0.45
WEIGHT_LIGHTS = 0.45
WEIGHT_POP = 0.10
TOP_N = 100
