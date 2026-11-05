import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import shape
from config import *

def parse_geometry(df):
    df['geometry'] = df['.geo'].apply(lambda x: shape(json.loads(x)) if pd.notnull(x) else None)
    df = df.drop(columns=['Unnamed: 0', 'system:index', '.geo'], errors='ignore')
    return df

def load_and_merge():
    print("Loading datasets...")
    df_2020 = pd.read_csv(CSV_2020_PATH)
    df_2025 = pd.read_csv(CSV_2025_PATH)
    
    df_2020 = parse_geometry(df_2020)
    df_2025 = parse_geometry(df_2025)
    
    cols_to_drop = ['state_name', 'total_urba', 'village', 'vlcode', 'geometry', 'shape_area', 'district']
    df_2025 = df_2025.drop(columns=cols_to_drop, errors='ignore')
    df_2025 = df_2025.rename(columns={col: f"{col}_2025" for col in df_2025.columns if col != "objectid_1"})
    
    rename_exclude = ["objectid_1", 'district', 'shape_area', 'state_name', 'total_urba', 'village', 'vlcode', 'geometry']
    df_2020 = df_2020.rename(columns={col: f"{col}_2020" for col in df_2020.columns if col not in rename_exclude})
    
    df_merged = df_2020.merge(df_2025, how='inner', on='objectid_1')
    return df_merged

def clean_and_calculate_changes(df_merged):
    print("Calculating changes and applying spatial thresholds...")
    features = ['built', 'crops', 'trees', 'nightlight_density', 'total_population']
    
    for f in features:
        df_merged[f'{f}_change'] = df_merged[f'{f}_2025'] - df_merged[f'{f}_2020']
        
    gdf_merged = gpd.GeoDataFrame(df_merged, geometry='geometry', crs="EPSG:4326")
    
    # Spatial Filtering (Resolution Constraints)
    gdf_merged_projected = gdf_merged.to_crs("EPSG:6933")
    gdf_merged['area_hectares'] = gdf_merged_projected.geometry.area / 10000
    gdf_valid_size = gdf_merged[gdf_merged['area_hectares'] >= SPATIAL_THRESHOLD_HA].copy()
    
    # Strict Economic Signal Filtering
    valid_growth_villages = gdf_valid_size[
        (gdf_valid_size['built_change'] > 0) & 
        (gdf_valid_size['nightlight_density_change'] > 0) & 
        (gdf_valid_size['total_population_change'] >= 0)
    ].copy()
    
    return gdf_valid_size, valid_growth_villages
