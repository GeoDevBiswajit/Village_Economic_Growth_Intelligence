import geemap
import ee
import geopandas as gpd
import time
import config

def initialize_ee():
    try:
        ee.Initialize(project=config.GEE_PROJECT_ID)
        print("Earth Engine Initialized Successfully.")
    except Exception as e:
        print(f"Error initializing EE: {e}")
        exit()

def get_viirs_nightlights(year_start, year_end, fc):
    viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG") \
              .filterDate(f'{year_start}-01-01', f'{year_end}-12-31') \
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
                 .filterDate(f'{year_start}-01-01', f'{year_end}-12-31') \
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

if __name__ == "__main__":
    initialize_ee()

    # Load and Filter Vectors
    if config.USE_LOCAL_SHP:
        village_gdf = gpd.read_file(config.INPUT_SHP_PATH)
        if village_gdf.crs != 'EPSG:4326':
            village_gdf = village_gdf.to_crs('EPSG:4326')
        fc_villages = geemap.geopandas_to_ee(village_gdf)
    else:
        fc_villages = ee.FeatureCollection(config.GEE_ASSET_PATH)

    fc_villages = fc_villages.filter(ee.Filter.eq('district', config.DISTRICT_NAME))

    # Extraction Pipeline
    print(f"Extracting {config.START_YEAR} data...")
    viirs_start = get_viirs_nightlights(config.START_YEAR, config.START_YEAR, fc_villages)
    dw_start = get_dynamic_world_probabilities(config.START_YEAR, config.START_YEAR, viirs_start)
    data_start = get_worldpop(config.START_YEAR, dw_start)

    print(f"Extracting {config.END_YEAR} data...")
    viirs_end = get_viirs_nightlights(config.END_YEAR, config.END_YEAR, fc_villages)
    dw_end = get_dynamic_world_probabilities(config.END_YEAR, config.END_YEAR, viirs_end)
    data_end = get_worldpop(config.END_YEAR, dw_end)

    # Batch Exports
    print("Submitting tasks to Earth Engine backend...")
    task_start = ee.batch.Export.table.toDrive(
        collection=data_start,
        description=f'{config.DISTRICT_NAME}_Village_Data_{config.START_YEAR}',
        folder='Village_Economic_Growth_Data', 
        fileFormat='CSV'
    )
    task_end = ee.batch.Export.table.toDrive(
        collection=data_end,
        description=f'{config.DISTRICT_NAME}_Village_Data_{config.END_YEAR}',
        folder='Village_Economic_Growth_Data',
        fileFormat='CSV'
    )

    task_start.start()
    task_end.start()
    print("Tasks successfully submitted to Google Earth Engine! Check Google Drive.")