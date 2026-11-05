import pandas as pd
import geopandas as gpd
import numpy as np
import json
from shapely.geometry import shape
import matplotlib.pyplot as plt
import folium
from sklearn.preprocessing import RobustScaler
import config

def load_and_prep_data():
    """Loads CSVs, parses geometry, and merges datasets."""
    df_start = pd.read_csv(config.INPUT_CSV_2020)
    df_end = pd.read_csv(config.INPUT_CSV_END)

    # Parse Geometries
    for df in [df_start, df_end]:
        df['geometry'] = df['.geo'].apply(lambda x: shape(json.loads(x)) if pd.notnull(x) else None)
        df.drop(columns=['Unnamed: 0', 'system:index', '.geo'], inplace=True, errors='ignore')

    # Rename columns for clarity before merge
    df_end.drop(columns=['state_name', 'total_urba', 'village', 'vlcode', 'geometry', 'shape_area', 'district'], errors='ignore', inplace=True)
    df_end = df_end.rename(columns={col: f"{col}_{config.END_YEAR}" for col in df_end.columns if col != "objectid_1"})
    
    df_start = df_start.rename(columns={
        col: f"{col}_{config.START_YEAR}" for col in df_start.columns 
        if col not in ["objectid_1", 'district', 'shape_area', 'state_name', 'total_urba','village', 'vlcode', 'geometry']
    })

    return df_start.merge(df_end, how='inner', on='objectid_1')

def remove_outliers_iqr(df, column):
    """Removes extreme outliers using the Interquartile Range method."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

if __name__ == "__main__":
    print("Loading and preparing data...")
    df_merged = load_and_prep_data()

    # 1. Feature Engineering (Calculating Deltas)
    features = ['built', 'crops', 'trees', 'nightlight_density', 'total_population']
    for f in features:
        df_merged[f'{f}_change'] = df_merged[f'{f}_{config.END_YEAR}'] - df_merged[f'{f}_{config.START_YEAR}']

    # Convert to GeoDataFrame for Spatial Operations
    gdf_merged = gpd.GeoDataFrame(df_merged, geometry='geometry', crs="EPSG:4326")

    # 2. Cleaning: Spatial Area Filter
    # Project to Equal Area to calculate hectares, remove villages too small for VIIRS resolution
    gdf_projected = gdf_merged.to_crs("EPSG:6933")
    gdf_merged['area_hectares'] = gdf_projected.geometry.area / 10000
    gdf_clean = gdf_merged[gdf_merged['area_hectares'] >= config.MIN_AREA_HECTARES].copy()
    print(f"Removed {len(gdf_merged) - len(gdf_clean)} villages below {config.MIN_AREA_HECTARES}ha threshold.")

    # 3. Cleaning: IQR Outlier Removal on extreme anomalies
    gdf_clean = remove_outliers_iqr(gdf_clean, 'nightlight_density_change')
    gdf_clean = remove_outliers_iqr(gdf_clean, 'built_change')

    # 4. Processing: Filter for strictly growing villages
    growing_villages = gdf_clean[
        (gdf_clean['built_change'] > 0) & 
        (gdf_clean['nightlight_density_change'] > 0) & 
        (gdf_clean['total_population_change'] >= 0)
    ].copy()

    # 5. Processing: Robust Scaling
    scaler = RobustScaler()
    features_to_scale = ['built_change', 'nightlight_density_change', 'total_population_change']
    scaled_features = [f"{f}_scaled" for f in features_to_scale]
    growing_villages[scaled_features] = scaler.fit_transform(growing_villages[features_to_scale])

    # 6. Scoring: Normalized Weighted Sum
    growing_villages['economic_growth_score'] = (
        (growing_villages['built_change_scaled'] * config.WEIGHT_BUILT) +
        (growing_villages['nightlight_density_change_scaled'] * config.WEIGHT_LIGHT) +
        (growing_villages['total_population_change_scaled'] * config.WEIGHT_POP)
    )

    # 7. Final Ranking
    top_100_villages = growing_villages.sort_values(by='economic_growth_score', ascending=False).head(100)
    
    # Export Top 100 Dataset
    export_cols = ['objectid_1', 'village', 'district', 'economic_growth_score', 'built_change', 'nightlight_density_change', 'total_population_change']
    top_100_villages[export_cols].to_csv(config.OUTPUT_TOP100_CSV, index=False)
    print(f"Top 100 data saved to: {config.OUTPUT_TOP100_CSV}")

    # 8. Visualization: Static Map
    print("Generating visualisations...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    gdf_merged.plot(ax=ax, color='whitesmoke', edgecolor='lightgrey', linewidth=0.5) # Background
    top_100_villages.plot(
        column='economic_growth_score', ax=ax, cmap='YlOrRd', legend=True,
        legend_kwds={'label': "Economic Growth Score", 'orientation': "horizontal", 'shrink': 0.7},
        edgecolor='black', linewidth=0.5
    )
    ax.set_title(f'Top 100 Economically Growing Villages in {config.DISTRICT_NAME} ({config.START_YEAR}-{config.END_YEAR})', fontsize=16)
    ax.set_axis_off()
    plt.savefig(config.OUTPUT_STATIC_MAP, dpi=300)
    plt.close()

    # 9. Visualization: Interactive Folium Map
    center_lat = top_100_villages.geometry.centroid.y.mean()
    center_lon = top_100_villages.geometry.centroid.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles='CartoDB positron')
    
    folium.Choropleth(
        geo_data=top_100_villages.__geo_interface__,
        data=top_100_villages,
        columns=['objectid_1', 'economic_growth_score'],
        key_on='feature.properties.objectid_1',
        fill_color='YlOrRd', fill_opacity=0.8, line_opacity=0.5,
        legend_name='Economic Growth Score'
    ).add_to(m)

    folium.GeoJson(
        top_100_villages,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
        tooltip=folium.GeoJsonTooltip(
            fields=['village', 'economic_growth_score', 'built_change', 'nightlight_density_change'],
            aliases=['Village:', 'Growth Score:', 'Built Change:', 'Light Change:']
        )
    ).add_to(m)

    m.save(config.OUTPUT_INTERACTIVE_MAP)
    print("Pipeline complete. All files generated.")