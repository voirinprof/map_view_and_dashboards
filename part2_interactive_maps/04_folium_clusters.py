# =============================================================================
# part2_interactive_maps/04_folium_clusters.py
# Regroupement de points avec MarkerCluster — indispensable pour de grands
# nuages de points (performance et lisibilité à petite échelle)
# =============================================================================

from pathlib import Path
import sys

import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def build_cluster_map(df: pd.DataFrame, center_lat: float, center_lon: float,
                       zoom: int, lat_col: str, lon_col: str,
                       name_col: str, category_col: str) -> folium.Map:
    """
    Construit une carte Folium avec clusters de points par catégorie.
    Chaque catégorie a son propre FeatureGroup pour permettre le filtrage.

    Paramètres
    ----------
    df           : DataFrame des occupants
    center_lat   : latitude du centre
    center_lon   : longitude du centre
    zoom         : niveau de zoom initial
    lat_col      : colonne latitude
    lon_col      : colonne longitude
    name_col     : colonne nom (tooltip)
    category_col : colonne catégorie (filtrage par couche)

    Retourne
    --------
    folium.Map
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB positron",
    )

    # Couleurs par catégorie
    color_map = {
        "Commerce":    "#2196F3",
        "Bureau":     "#FF9800",
        "Industriel": "#4CAF50",
        "Agricole/pêcherie":     "#9C27B0",
    }

    # Un cluster par catégorie pour permettre l'activation/désactivation
    for category, color in color_map.items():
        subset = df[df[category_col] == category]
        if subset.empty:
            continue

        fg = folium.FeatureGroup(name=f"Occupants — {category.capitalize()}")
        cluster = MarkerCluster().add_to(fg)

        for _, row in subset.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=5,
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
                    f"<b>{row[name_col]}</b><br>Catégorie : {row[category_col]}",
                    max_width=200,
                ),
            ).add_to(cluster)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def build_heatmap(df: pd.DataFrame, center_lat: float, center_lon: float,
                   zoom: int, lat_col: str, lon_col: str,
                   weight_col: str = None) -> folium.Map:
    """
    Construit une carte de chaleur (heatmap) des occupants.
    La pondération optionnelle permet de moduler l'intensité par une valeur.

    Paramètres
    ----------
    df         : DataFrame des occupants
    center_lat : latitude du centre
    center_lon : longitude du centre
    zoom       : niveau de zoom initial
    lat_col    : colonne latitude
    lon_col    : colonne longitude
    weight_col : colonne de pondération (optionnel)

    Retourne
    --------
    folium.Map
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB dark_matter",   # fond sombre = meilleur contraste heatmap
    )

    # Préparation des données [lat, lon] ou [lat, lon, poids]
    if weight_col and weight_col in df.columns:
        heat_data = df[[lat_col, lon_col, weight_col]].dropna().values.tolist()
    else:
        heat_data = df[[lat_col, lon_col]].dropna().values.tolist()

    HeatMap(
        heat_data,
        name="Carte de chaleur",
        min_opacity=0.3,
        radius=15,
        blur=12,
        gradient={0.4: "blue", 0.65: "lime", 1.0: "red"},
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)

    center_lat = config["extent"]["center_lat"]
    center_lon = config["extent"]["center_lon"]
    zoom       = config["extent"]["zoom_folium"]

    df = pd.read_csv(vector_dir / "liste_occupants.csv")

    # --- Carte 1 : clusters par catégorie ---
    m1 = build_cluster_map(
        df=df,
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        lat_col="lat",
        lon_col="lng",
        name_col="entreprise",
        category_col="type_etablissement",
    )
    output_path1 = output_dir / "folium_clusters.html"
    m1.save(str(output_path1))
    print(f"Carte sauvegardée : {output_path1}")

    # --- Carte 2 : heatmap des occupants ---
    m2 = build_heatmap(
        df=df,
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        lat_col="lat",
        lon_col="lng",
    )
    output_path2 = output_dir / "folium_heatmap.html"
    m2.save(str(output_path2))
    print(f"Carte sauvegardée : {output_path2}")


if __name__ == "__main__":
    main()
