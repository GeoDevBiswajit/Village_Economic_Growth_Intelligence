import matplotlib.pyplot as plt
import folium
import os
from config import *
import branca.colormap as cm




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

# def create_interactive_map(top_n_gdf):
#     print("Generating interactive Folium map...")
#     center_lat = top_n_gdf.geometry.centroid.y.mean()
#     center_lon = top_n_gdf.geometry.centroid.x.mean()
    
#     m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles='CartoDB positron')
    
#     folium.Choropleth(
#         geo_data=top_n_gdf.__geo_interface__,
#         data=top_n_gdf,
#         columns=['objectid_1', 'economic_growth_score'],
#         key_on='feature.properties.objectid_1',
#         fill_color='YlOrRd',
#         fill_opacity=0.8,
#         line_opacity=0.5,
#         legend_name='Economic Growth Score (2020-2025)',
#         highlight=True
#     ).add_to(m)
    
#     folium.GeoJson(
#         top_n_gdf,
#         style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
#         tooltip=folium.GeoJsonTooltip(
#             fields=['village', 'economic_growth_score', 'built_change', 'nightlight_density_change'],
#             aliases=['Village Name:', 'Growth Score:', 'Built-up Change:', 'Nightlight Change:'],
#             localize=True
#         )
#     ).add_to(m)
    
#     out_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Top_{TOP_N}_Interactive.html')
#     m.save(out_path)

def create_interactive_map(top_n_gdf):
    print("Generating interactive Folium map...")

    # --- prepare data -------------------------------------------------------
    gdf = top_n_gdf.copy()
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Rank 1 = highest score (computed here if the column isn't already present)
    if 'rank' not in gdf.columns:
        gdf['rank'] = gdf['economic_growth_score'].rank(ascending=False, method='first').astype(int)

    # Keep only what the map needs (avoids non-JSON-serialisable columns) and round for display
    cols = ['rank', 'village', 'objectid_1', 'economic_growth_score',
            'built_change', 'nightlight_density_change', 'total_population_change', 'geometry']
    cols = [c for c in cols if c in gdf.columns]
    gdf = gdf[cols].copy()
    gdf['economic_growth_score'] = gdf['economic_growth_score'].round(3)
    for c in ['built_change', 'nightlight_density_change', 'total_population_change']:
        if c in gdf.columns:
            gdf[c] = gdf[c].round(4)

    # Draw lowest rank first so the best villages end up on top
    gdf = gdf.sort_values('rank', ascending=False)

    pts = gdf.geometry.representative_point()          # always inside the polygon
    center_lat, center_lon = pts.y.mean(), pts.x.mean()

    # --- base map + satellite layers ---------------------------------------
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10,
                   tiles='CartoDB positron', name='Light map')

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri, Maxar, Earthstar Geographics, and the GIS User Community',
        name='Esri Satellite', overlay=False, control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google', name='Google Hybrid (satellite + labels)',
        overlay=False, control=True
    ).add_to(m)

    # folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)

    # --- colour scale -------------------------------------------------------
    vmin, vmax = gdf['economic_growth_score'].min(), gdf['economic_growth_score'].max()
    colormap = cm.LinearColormap(
        ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],   # YlOrRd
        vmin=vmin, vmax=vmax,
        caption='Economic Growth Score (2020-2025)'
    )

    def style_fn(feature):
        return {
            'fillColor': colormap(feature['properties']['economic_growth_score']),
            'color': 'black',
            'weight': 0.8,
            'fillOpacity': 0.75,
        }

    def highlight_fn(feature):
        return {'weight': 3, 'color': '#00e5ff', 'fillOpacity': 0.9}

    # --- village layer: hover = rank, click = full details -----------------
    fields = ['rank', 'village', 'economic_growth_score',
              'built_change', 'nightlight_density_change', 'total_population_change']
    fields = [f for f in fields if f in gdf.columns]
    alias_map = {
        'rank': 'Rank:', 'village': 'Village:', 'economic_growth_score': 'Growth Score:',
        'built_change': 'Built-up Change:', 'nightlight_density_change': 'Nightlight Change:',
        'total_population_change': 'Population Change:',
    }
    aliases = [alias_map[f] for f in fields]

    villages = folium.GeoJson(
        gdf,
        name=f'Top {TOP_N} villages',
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=['rank', 'village', 'economic_growth_score'],
            aliases=['Rank:', 'Village:', 'Growth Score:'],
            sticky=True, localize=True,
            style='font-size:13px; font-weight:bold;'
        ),
        popup=folium.GeoJsonPopup(fields=fields, aliases=aliases, localize=True, max_width=300),
    )
    villages.add_to(m)
    colormap.add_to(m)

    # --- rank badges for the top 10 (toggle-able layer) --------------------
    badges = folium.FeatureGroup(name='Top 10 rank labels', show=True)
    top10 = gdf.nsmallest(10, 'rank')
    for (_, row), pt in zip(top10.iterrows(), top10.geometry.representative_point()):
        folium.Marker(
            location=[pt.y, pt.x],
            icon=folium.DivIcon(html=(
                f'<div style="background:#1B2A41;color:#fff;border:2px solid #fff;'
                f'border-radius:50%;width:24px;height:24px;line-height:20px;'
                f'text-align:center;font-size:12px;font-weight:bold;">{int(row["rank"])}</div>'
            ), icon_size=(24, 24), icon_anchor=(12, 12))
        ).add_to(badges)
    badges.add_to(m)

    # --- usability plugins --------------------------------------------------
    from folium.plugins import Fullscreen, MiniMap, MeasureControl
    Fullscreen().add_to(m)
    MiniMap(toggle_display=True, position='bottomleft').add_to(m)
    MeasureControl(position='topleft').add_to(m)

    m.fit_bounds(villages.get_bounds())
    folium.LayerControl(collapsed=False).add_to(m)

    out_path = os.path.join(RESULTS_DIR, f'{DISTRICT_NAME}_Top_{TOP_N}_Interactive.html')
    m.save(out_path)
    print(f"Saved: {out_path}")