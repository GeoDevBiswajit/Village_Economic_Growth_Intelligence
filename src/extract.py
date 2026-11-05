import ee
import geemap
from config import *

def initialize_ee():
    try:
        ee.Initialize(project=EE_PROJECT_ID)
        print("Earth Engine Initialized Successfully.")
    except Exception as e:
        print(f"Error initializing EE: {e}")
        raise e

def get_viirs_nightlights(year_start, year_end, fc):
    viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG") \
              .filterDate(year_start, year_end) \
              .select('avg_rad') \
              .median()
    return viirs.reduceRegions(
        collection=fc,
        reducer=ee.Reducer.mean().setOutputs(['nightlight_density']),
        scale=463
    )

def get_dynamic_world_probabilities(year_start, year_end, fc):
    probability_bands = ['built', 'crops', 'trees']
    dw_probs = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
                 .filterDate(year_start, year_end) \
                 .filterBounds(fc.geometry()) \
                 .select(probability_bands) \
                 .mean() 
    return dw_probs.reduceRegions(
        collection=fc,
        reducer=ee.Reducer.mean(),
        scale=10 
    )

def get_worldpop(year, fc):
    pop_img = ee.ImageCollection("WorldPop/GP/100m/R2025A/v1/pop") \
                .filterDate(f'{year}-01-01', f'{year}-12-31') \
                .select('population') \
                .mosaic()
    return pop_img.reduceRegions(
        collection=fc,
        reducer=ee.Reducer.sum().setOutputs(['total_population']),
        scale=100
    )

def run_extraction():
    initialize_ee()
    
    # Load GEE Asset
    fc_villages = ee.FeatureCollection("projects/ee-my-biswajit/assets/Assam_vill_boundaries")
    fc_villages = fc_villages.filter(ee.Filter.eq('district', DISTRICT_NAME))
    
    print(f"Extracting 2020 data for {DISTRICT_NAME}...")
    viirs_2020 = get_viirs_nightlights(START_2020, END_2020, fc_villages)
    dw_2020 = get_dynamic_world_probabilities(START_2020, END_2020, viirs_2020)
    data_2020 = get_worldpop(2020, dw_2020)

    print(f"Extracting 2025 data for {DISTRICT_NAME}...")
    viirs_2025 = get_viirs_nightlights(START_2025, END_2025, fc_villages)
    dw_2025 = get_dynamic_world_probabilities(START_2025, END_2025, viirs_2025)
    data_2025 = get_worldpop(2025, dw_2025)

    print("Submitting tasks to Earth Engine backend...")
    task_2020 = ee.batch.Export.table.toDrive(
        collection=data_2020,
        description=f'{DISTRICT_NAME}_Village_Data_2020',
        folder='Village_Economic_Growth_Data', 
        fileFormat='CSV'
    )
    task_2025 = ee.batch.Export.table.toDrive(
        collection=data_2025,
        description=f'{DISTRICT_NAME}_Village_Data_2025',
        folder='Village_Economic_Growth_Data',
        fileFormat='CSV'
    )

    task_2020.start()
    task_2025.start()
    print("Tasks submitted! Monitor at https://code.earthengine.google.com/tasks")

if __name__ == "__main__":
    run_extraction()
