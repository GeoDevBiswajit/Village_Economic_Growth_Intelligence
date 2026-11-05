import os
from config import *
from extract import run_extraction
from process import load_and_merge, clean_and_calculate_changes
from score import calculate_scores
from visualize import create_static_map, create_interactive_map
from eda import generate_eda_plots

def main():
    print(f"--- Starting Village Economic Growth Pipeline for {DISTRICT_NAME} ---")
    
    if not os.path.exists(CSV_2020_PATH) or not os.path.exists(CSV_2025_PATH):
        print(f"Missing CSV data in {CSV_DIR}. Executing extraction...")
        run_extraction()
        print("Please wait for Google Earth Engine to finish the background export to your Google Drive.")
        return

    # Process
    df_merged = load_and_merge()

    # EDA
    generate_eda_plots(df_merged)
    district_gdf, valid_growth_villages = clean_and_calculate_changes(df_merged)
    
    # Score
    top_100_villages = calculate_scores(valid_growth_villages)
    
    # Save CSV
    csv_out = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Top_{TOP_N}_Villages.csv')
    gpkg_out = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Top_{TOP_N}_Villages.gpkg')
    top_100_villages.to_file(gpkg_out, driver='GPKG', index=False)
    top_100_villages.drop(columns=['geometry']).to_csv(csv_out, index=False)
    
    # Visualize
    create_static_map(district_gdf, top_100_villages)
    create_interactive_map(top_100_villages)
    
    print("--- Pipeline Execution Complete ---")

if __name__ == "__main__":
    main()
