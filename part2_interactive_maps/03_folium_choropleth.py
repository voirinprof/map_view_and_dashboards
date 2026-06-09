# =============================================================================
# part2_interactive_maps/03_folium_choropleth.py
# Choroplèthe interactive Folium avec tooltip superposé
# Pattern classique : Choropleth (couleur) + GeoJson invisible (tooltip)
# =============================================================================

from pathlib import Path
import sys

import folium
import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def add_choropleth_layer(m: folium.Map, gdf: gpd.GeoDataFrame,
                          key_column: str, value_column: str,
                          legend_name: str, color_scheme: str,
                          n_bins: int) -> folium.Map:
    """
    Ajoute une couche choroplèthe sur la carte Folium.
    Folium.Choropleth n'inclut pas de tooltip natif — voir add_tooltip_layer().

    Paramètres
    ----------
    m             : carte Folium cible
    gdf           : GeoDataFrame en EPSG:4326
    key_column    : colonne servant de clé de jointure (ex. 'nom')
    value_column  : colonne numérique à représenter
    legend_name   : intitulé de la légende
    color_scheme  : palette YlOrRd, Blues, etc. (ColorBrewer)
    n_bins        : nombre de classes de couleur

    Retourne
    --------
    folium.Map
    """
    folium.Choropleth(
        geo_data=gdf,
        data=gdf,
        columns=[key_column, value_column],
        # key_on pointe vers la propriété GeoJson correspondant à key_column
        key_on=f"feature.properties.{key_column}",
        fill_color=color_scheme,
        fill_opacity=0.7,
        line_opacity=0.4,
        line_color="white",
        line_weight=1,
        legend_name=legend_name,
        bins=n_bins,
        reset=True,
        name=f"Choroplèthe — {value_column}",
    ).add_to(m)

    return m


def add_tooltip_layer(m: folium.Map, gdf: gpd.GeoDataFrame,
                       tooltip_fields: list, tooltip_aliases: list) -> folium.Map:
    """
    Ajoute une couche GeoJson transparente uniquement pour le tooltip.
    C'est le pattern standard pour combiner Choropleth et tooltip dans Folium.

    Paramètres
    ----------
    m               : carte Folium cible
    gdf             : même GeoDataFrame que celui de la choroplèthe
    tooltip_fields  : colonnes à afficher dans le tooltip
    tooltip_aliases : étiquettes du tooltip

    Retourne
    --------
    folium.Map
    """
    folium.GeoJson(
        gdf,
        name="Tooltip arrondissements",
        style_function=lambda f: {
            "fillColor": "transparent",   # polygone invisible
            "color": "transparent",
            "weight": 0,
        },
        highlight_function=lambda f: {
            "fillColor": "white",
            "fillOpacity": 0.2,
            "color": "white",
            "weight": 2,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=True,
            style="font-size: 12px; background-color: white; border: 1px solid #ccc;",
        ),
        show=True,
    ).add_to(m)

    return m


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)

    center_lat = config["extent"]["center_lat"]
    center_lon = config["extent"]["center_lon"]
    zoom       = config["extent"]["zoom_folium"]

    # Chargement et calcul de la superficie
    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(4326)
    gdf["area_km2"] = gdf.to_crs(32198).geometry.area / 1_000_000

    # --- Carte 1 : superficie par arrondissement ---
    m1 = folium.Map(location=[center_lat, center_lon], zoom_start=zoom,
                    tiles="CartoDB positron")

    m1 = add_choropleth_layer(
        m=m1, gdf=gdf,
        key_column="NOM",
        value_column="area_km2",
        legend_name="Superficie (km²)",
        color_scheme="YlOrRd",
        n_bins=5,
    )

    # Couche tooltip superposée — rend la choroplèthe interactive
    m1 = add_tooltip_layer(
        m=m1, gdf=gdf,
        tooltip_fields=["NOM", "NUMERO", "area_km2"],
        tooltip_aliases=["Arrondissement :", "Numéro :", "Superficie (km²) :"],
    )

    folium.LayerControl().add_to(m1)
    output_path1 = output_dir / "folium_choropleth_density.html"
    m1.save(str(output_path1))
    print(f"Carte sauvegardée : {output_path1}")

    # --- Carte 2 : même variable, palette différente (Blues) ---
    m2 = folium.Map(location=[center_lat, center_lon], zoom_start=zoom,
                    tiles="CartoDB positron")

    m2 = add_choropleth_layer(
        m=m2, gdf=gdf,
        key_column="NOM",
        value_column="area_km2",
        legend_name="Superficie (km²)",
        color_scheme="Blues",
        n_bins=5,
    )
    m2 = add_tooltip_layer(
        m=m2, gdf=gdf,
        tooltip_fields=["NOM", "NUMERO", "area_km2"],
        tooltip_aliases=["Arrondissement :", "Numéro :", "Superficie (km²) :"],
    )

    folium.LayerControl().add_to(m2)
    output_path2 = output_dir / "folium_choropleth_income.html"
    m2.save(str(output_path2))
    print(f"Carte sauvegardée : {output_path2}")


if __name__ == "__main__":
    main()
