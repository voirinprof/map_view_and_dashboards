# =============================================================================
# part2_interactive_maps/01_folium_base.py
# Carte Folium de base avec marqueurs et fonds de carte
# Folium génère du HTML/Leaflet.js autonome — aucun serveur requis
# CRS : Folium opère toujours en EPSG:4326 (latitude, longitude)
# =============================================================================

from pathlib import Path
import sys

import folium
from folium.plugins import MiniMap, Fullscreen
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def make_base_map(center_lat: float, center_lon: float,
                  zoom: int, tiles: str) -> folium.Map:
    """
    Crée une carte Folium de base avec le fond de carte spécifié.

    Paramètres
    ----------
    center_lat : latitude du centre de la carte
    center_lon : longitude du centre de la carte
    zoom       : niveau de zoom initial
    tiles      : nom du fond de carte Folium (ex. 'CartoDB positron')

    Retourne
    --------
    folium.Map : objet carte prêt à recevoir des couches
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles=tiles,
    )

    # Ajout de couches de fond alternatives sélectionnables
    folium.TileLayer("OpenStreetMap",    name="OpenStreetMap").add_to(m)
    folium.TileLayer("CartoDB dark_matter", name="CartoDB Sombre").add_to(m)
    folium.TileLayer("Esri.WorldImagery",   name="Esri Satellite").add_to(m)

    # Minimap de localisation en bas à droite
    MiniMap(toggle_display=True).add_to(m)

    # Bouton plein écran
    Fullscreen().add_to(m)

    return m


def add_point_markers(m: folium.Map, df: pd.DataFrame,
                      lat_col: str, lon_col: str,
                      name_col: str, category_col: str) -> folium.Map:
    """
    Ajoute des CircleMarkers sur la carte. Les couleurs sont assignées
    dynamiquement selon les valeurs uniques de la colonne de catégorie.

    Paramètres
    ----------
    m            : carte Folium cible
    df           : DataFrame des occupants
    lat_col      : nom de la colonne latitude
    lon_col      : nom de la colonne longitude
    name_col     : colonne utilisée pour le tooltip
    category_col : colonne utilisée pour la couleur des marqueurs

    Retourne
    --------
    folium.Map : carte avec les marqueurs ajoutés
    """
    # Palette cyclique assignée dynamiquement aux valeurs uniques
    palette = ["#2196F3", "#FF9800", "#4CAF50", "#9C27B0",
               "#F44336", "#00BCD4", "#795548", "#607D8B"]
    categories = df[category_col].dropna().unique()
    color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(sorted(categories))}

    # Groupe de couche pour activer/désactiver via LayerControl
    fg = folium.FeatureGroup(name="Occupants — Marqueurs")

    for _, row in df.iterrows():
        color = color_map.get(row[category_col], "#888888")

        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=6,
            color="white",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            tooltip=folium.Tooltip(
                f"<b>{row[name_col]}</b><br>{row[category_col]}",
                sticky=True,
            ),
            popup=folium.Popup(
                f"<b>{row[name_col]}</b><br>"
                f"Type : {row[category_col]}<br>"
                f"Lat : {row[lat_col]:.5f} | Lon : {row[lon_col]:.5f}",
                max_width=250,
            ),
        ).add_to(fg)

    fg.add_to(m)
    return m


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)

    center_lat = config["extent"]["center_lat"]
    center_lon = config["extent"]["center_lon"]
    zoom       = config["extent"]["zoom_folium"]

    # Chargement des occupants (coordonnées en EPSG:4326)
    df = pd.read_csv(vector_dir / "liste_occupants.csv")

    # --- Carte 1 : fond CartoDB clair avec marqueurs ---
    m = make_base_map(center_lat, center_lon, zoom, tiles="CartoDB positron")
    m = add_point_markers(
        m, df,
        lat_col="lat",
        lon_col="lng",
        name_col="entreprise",
        category_col="type_etablissement",
    )

    # Contrôle de couches — affiche les couches de fond et les groupes
    folium.LayerControl(collapsed=False).add_to(m)

    output_path = output_dir / "folium_base_markers.html"
    m.save(str(output_path))
    print(f"Carte sauvegardée : {output_path}")

    # --- Carte 2 : marqueur institutionnel unique (exemple simple) ---
    m2 = make_base_map(center_lat, center_lon, zoom, tiles="CartoDB positron")

    folium.Marker(
        location=[45.3788, -71.9282],
        tooltip="Université de Sherbrooke",
        popup=folium.Popup("<b>Université de Sherbrooke</b><br>Département de géomatique appliquée", max_width=250),
        icon=folium.Icon(color="green", icon="graduation-cap", prefix="fa"),
    ).add_to(m2)

    output_path2 = output_dir / "folium_single_marker.html"
    m2.save(str(output_path2))
    print(f"Carte sauvegardée : {output_path2}")


if __name__ == "__main__":
    main()
