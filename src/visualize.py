import matplotlib.pyplot as plt
import folium
import os
from config import *

def create_static_map(district_gdf, top_n_gdf):
    print("Generating static choropleth map...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    district_gdf.plot(ax=ax, color='whitesmoke', edgecolor='lightgrey', linewidth=0.5)
    
    top_n_gdf.plot(
        column='economic_growth_score',
        ax=ax,
        cmap='YlOrRd',
        legend=True,
        legend_kwds={
            'label': "Economic Growth Score (Normalized Weighted Index)",
            'orientation': "horizontal",
            'shrink': 0.7
        },
        edgecolor='black',
        linewidth=0.5
    )
    
    ax.set_title(f'Top {TOP_N} Economically Growing Villages in {DISTRICT_NAME} (2020-2025)', fontsize=16, pad=15)
    ax.set_axis_off()
    
    out_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Economic_Growth_Map.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

def create_interactive_map(top_n_gdf):
    print("Generating interactive Folium map...")
    center_lat = top_n_gdf.geometry.centroid.y.mean()
    center_lon = top_n_gdf.geometry.centroid.x.mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles='CartoDB positron')
    
    folium.Choropleth(
        geo_data=top_n_gdf.__geo_interface__,
        data=top_n_gdf,
        columns=['objectid_1', 'economic_growth_score'],
        key_on='feature.properties.objectid_1',
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_opacity=0.5,
        legend_name='Economic Growth Score (2020-2025)',
        highlight=True
    ).add_to(m)
    
    folium.GeoJson(
        top_n_gdf,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
        tooltip=folium.GeoJsonTooltip(
            fields=['village', 'economic_growth_score', 'built_change', 'nightlight_density_change'],
            aliases=['Village Name:', 'Growth Score:', 'Built-up Change:', 'Nightlight Change:'],
            localize=True
        )
    ).add_to(m)
    
    out_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Top_{TOP_N}_Interactive.html')
    m.save(out_path)
