# =============================================================================
# part2_interactive_maps/06_plotly_choropleth.py
# Carte choroplèthe interactive avec Plotly Express et GeoDataFrame
# __geo_interface__ convertit le GeoDataFrame en GeoJSON compatible Plotly
# =============================================================================

from pathlib import Path
import sys

import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def make_choropleth_mapbox(gdf: gpd.GeoDataFrame, value_column: str,
                            legend_title: str, map_title: str,
                            color_scale: str, center_lat: float,
                            center_lon: float, zoom: int,
                            opacity: float) -> go.Figure:
    """
    Génère une carte choroplèthe interactive Plotly Express.

    Paramètres
    ----------
    gdf          : GeoDataFrame en EPSG:4326
    value_column : colonne numérique à représenter
    legend_title : titre de la barre de couleurs
    map_title    : titre de la figure
    color_scale  : palette Plotly (ex. 'YlOrRd', 'Blues', 'Viridis')
    center_lat   : latitude du centre initial
    center_lon   : longitude du centre initial
    zoom         : niveau de zoom initial
    opacity      : transparence des polygones [0, 1]

    Retourne
    --------
    plotly.graph_objs.Figure
    """
    # Réinitialiser l'index pour que locations=gdf.index fonctionne correctement
    gdf = gdf.reset_index(drop=True)

    fig = px.choropleth_mapbox(
        gdf,
        geojson=gdf.__geo_interface__,   # conversion GeoDataFrame → GeoJSON dict
        locations=gdf.index,             # index comme clé de jointure interne
        color=value_column,
        color_continuous_scale=color_scale,
        mapbox_style="carto-positron",
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        opacity=opacity,
        hover_name="NOM",
        hover_data={
            value_column: ":.2f",
            "NUMERO": True,
        },
        labels={value_column: legend_title},
        title=map_title,
        height=600,
    )

    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar={
            "title": legend_title,
            "thickness": 15,
            "len": 0.6,
        },
        font={"family": "Arial", "size": 12},
    )

    return fig


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)

    center_lat = config["extent"]["center_lat"]
    center_lon = config["extent"]["center_lon"]
    zoom       = config["extent"]["zoom_plotly"]

    # Chargement et calcul de la superficie
    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(4326)
    gdf["area_km2"] = gdf.to_crs(32198).geometry.area / 1_000_000

    # --- Carte 1 : superficie — palette YlOrRd ---
    fig1 = make_choropleth_mapbox(
        gdf=gdf,
        value_column="area_km2",
        legend_title="Superficie (km²)",
        map_title="Superficie par arrondissement — Sherbrooke",
        color_scale="YlOrRd",
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        opacity=0.65,
    )
    output_path1 = output_dir / "plotly_choropleth_density.html"
    fig1.write_html(str(output_path1))
    print(f"Carte sauvegardée : {output_path1}")

    # --- Carte 2 : superficie — palette Blues ---
    fig2 = make_choropleth_mapbox(
        gdf=gdf,
        value_column="area_km2",
        legend_title="Superficie (km²)",
        map_title="Superficie par arrondissement — Sherbrooke (Blues)",
        color_scale="Blues",
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        opacity=0.65,
    )
    output_path2 = output_dir / "plotly_choropleth_income.html"
    fig2.write_html(str(output_path2))
    print(f"Carte sauvegardée : {output_path2}")

    # --- Carte 3 : superficie — palette Viridis ---
    fig3 = make_choropleth_mapbox(
        gdf=gdf,
        value_column="area_km2",
        legend_title="Superficie (km²)",
        map_title="Superficie par arrondissement — Sherbrooke (Viridis)",
        color_scale="Viridis",
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        opacity=0.65,
    )
    output_path3 = output_dir / "plotly_choropleth_employment.html"
    fig3.write_html(str(output_path3))
    print(f"Carte sauvegardée : {output_path3}")


if __name__ == "__main__":
    main()
