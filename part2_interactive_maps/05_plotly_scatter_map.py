# =============================================================================
# part2_interactive_maps/05_plotly_scatter_map.py
# Carte de dispersion interactive avec Plotly Express
# Utilise le fond open-street-map (gratuit, sans token Mapbox)
# =============================================================================

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def make_scatter_map(df: pd.DataFrame, lat_col: str, lon_col: str,
                      color_col: str, size_col: str, hover_name: str,
                      hover_data: list, title: str,
                      center_lat: float, center_lon: float,
                      zoom: int, mapbox_style: str) -> px.scatter_mapbox:
    """
    Génère une carte de dispersion interactive Plotly Express.

    Paramètres
    ----------
    df           : DataFrame des occupants
    lat_col      : colonne latitude
    lon_col      : colonne longitude
    color_col    : colonne pour la couleur des points
    size_col     : colonne pour la taille des points (None = taille fixe)
    hover_name   : colonne affichée en titre du tooltip
    hover_data   : liste de colonnes supplémentaires dans le tooltip
    title        : titre de la figure
    center_lat   : latitude du centre initial
    center_lon   : longitude du centre initial
    zoom         : niveau de zoom initial
    mapbox_style : fond de carte ('open-street-map', 'carto-positron', etc.)

    Retourne
    --------
    plotly.graph_objs.Figure
    """
    fig = px.scatter_mapbox(
        df,
        lat=lat_col,
        lon=lon_col,
        color=color_col,
        size=size_col,
        hover_name=hover_name,
        hover_data=hover_data,
        color_discrete_sequence=px.colors.qualitative.Set1,
        size_max=15,
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style=mapbox_style,
        title=title,
        height=600,
    )

    # Mise en page de la figure
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        legend_title_text="Catégorie",
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

    df = pd.read_csv(vector_dir / "liste_occupants.csv")

    # --- Carte 1 : points colorés par catégorie, taille fixe ---
    fig1 = make_scatter_map(
        df=df,
        lat_col="lat",
        lon_col="lng",
        color_col="type_etablissement",
        size_col=None,
        hover_name="entreprise",
        hover_data=["type_etablissement", "secteur_nom"],
        title="Localisation des occupants par catégorie — Sherbrooke",
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        mapbox_style="open-street-map",
    )

    output_path1 = output_dir / "plotly_scatter_map_categories.html"
    fig1.write_html(str(output_path1))
    print(f"Carte sauvegardée : {output_path1}")

    # générer une taille aléatoire pour chaque point
    # de 1 à 10 pour une meilleure visualisation
    import numpy as np
    np.random.seed(42)
    df["taille"] = np.random.randint(1, 11, size=len(df))

    # --- Carte 2 : points avec taille proportionnelle à la superficie ---
    fig2 = make_scatter_map(
        df=df,
        lat_col="lat",
        lon_col="lng",
        color_col="type_etablissement",
        size_col="taille",
        hover_name="entreprise",
        hover_data=["type_etablissement", "secteur_nom"],
        title="Superficie des occupants (symboles proportionnels) — Sherbrooke",
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        mapbox_style="carto-positron",
    )

    output_path2 = output_dir / "plotly_scatter_map_proportional.html"
    fig2.write_html(str(output_path2))
    print(f"Carte sauvegardée : {output_path2}")

    # --- Carte 3 : fond sombre pour une présentation contrastée ---
    fig3 = make_scatter_map(
        df=df,
        lat_col="lat",
        lon_col="lng",
        color_col="type_etablissement",
        size_col=None,
        hover_name="entreprise",
        hover_data=["type_etablissement", "secteur_nom"],
        title="Occupants — Fond sombre",
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=zoom,
        mapbox_style="carto-darkmatter",
    )

    output_path3 = output_dir / "plotly_scatter_map_dark.html"
    fig3.write_html(str(output_path3))
    print(f"Carte sauvegardée : {output_path3}")


if __name__ == "__main__":
    main()
