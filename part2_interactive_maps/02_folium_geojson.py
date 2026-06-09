# =============================================================================
# part2_interactive_maps/02_folium_geojson.py
# Couche GeoJson Folium avec style dynamique, tooltip et contrôle de couches
# Illustre la différence entre style_function (statique) et highlight_function
# =============================================================================

from pathlib import Path
import sys

import folium
import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def style_polygon(feature: dict) -> dict:
    """
    Fonction de style appliquée à chaque feature GeoJson.
    Retourne un dictionnaire de style Leaflet.

    Paramètres
    ----------
    feature : dictionnaire GeoJson de la feature courante

    Retourne
    --------
    dict : style Leaflet (fillColor, color, weight, fillOpacity)
    """
    return {
        "fillColor": "#3186cc",
        "color": "white",
        "weight": 1.5,
        "fillOpacity": 0.5,
    }


def highlight_polygon(feature: dict) -> dict:
    """
    Style appliqué au survol de la souris (highlight).
    Permet un retour visuel immédiat à l'utilisateur.
    """
    return {
        "fillColor": "#e63946",
        "color": "white",
        "weight": 3,
        "fillOpacity": 0.8,
    }


def add_geojson_layer(m: folium.Map, gdf: gpd.GeoDataFrame,
                      layer_name: str, tooltip_fields: list,
                      tooltip_aliases: list) -> folium.Map:
    """
    Ajoute une couche GeoJson interactive sur la carte Folium.

    Paramètres
    ----------
    m               : carte Folium cible
    gdf             : GeoDataFrame en EPSG:4326
    layer_name      : nom de la couche (affiché dans LayerControl)
    tooltip_fields  : liste des colonnes à afficher dans le tooltip
    tooltip_aliases : étiquettes correspondantes pour le tooltip

    Retourne
    --------
    folium.Map : carte avec la couche GeoJson ajoutée
    """
    folium.GeoJson(
        gdf,
        name=layer_name,
        style_function=style_polygon,
        highlight_function=highlight_polygon,
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,        # formatage des nombres selon la locale
            sticky=False,         # tooltip suit la souris
            labels=True,
            style="font-size: 12px;",
        ),
        popup=folium.GeoJsonPopup(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            max_width=300,
        ),
    ).add_to(m)

    return m


def add_street_layer(m: folium.Map, gdf_streets: gpd.GeoDataFrame) -> folium.Map:
    """
    Ajoute le réseau routier comme couche GeoJson secondaire.
    Désactivée par défaut dans LayerControl (show=False).

    Paramètres
    ----------
    m            : carte Folium cible
    gdf_streets  : GeoDataFrame du réseau routier en EPSG:4326

    Retourne
    --------
    folium.Map : carte avec la couche routière ajoutée
    """
    folium.GeoJson(
        gdf_streets,
        name="Réseau routier",
        show=False,              # couche masquée par défaut
        style_function=lambda f: {
            "color": "#555555",
            "weight": 1,
            "opacity": 0.6,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["TOPONYMIE", "TYPERUE", "VITESSE"],
            aliases=["Rue :", "Type :", "Vitesse (km/h) :"],
        ),
    ).add_to(m)

    return m


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)

    center_lat = config["extent"]["center_lat"]
    center_lon = config["extent"]["center_lon"]
    zoom       = config["extent"]["zoom_folium"]

    # Chargement et reprojection en EPSG:4326 (exigé par Folium)
    gdf_arr = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(4326)
    gdf_arr["area_km2"] = gdf_arr.to_crs(32198).geometry.area / 1_000_000

    gdf_streets = gpd.read_file(vector_dir / "SegmentRue_1502216369322323101.gpkg").to_crs(4326)

    # Création de la carte de base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB positron",
    )

    # Couche arrondissements avec tooltip et highlight
    m = add_geojson_layer(
        m=m,
        gdf=gdf_arr,
        layer_name="Arrondissements",
        tooltip_fields=["NOM", "NUMERO", "area_km2"],
        tooltip_aliases=["Arrondissement :", "Numéro :", "Superficie (km²) :"],
    )

    # Couche réseau routier (désactivée par défaut)
    m = add_street_layer(m, gdf_streets)

    # Contrôle de couches
    folium.LayerControl(collapsed=False).add_to(m)

    output_path = output_dir / "folium_geojson_layers.html"
    m.save(str(output_path))
    print(f"Carte sauvegardée : {output_path}")


if __name__ == "__main__":
    main()
