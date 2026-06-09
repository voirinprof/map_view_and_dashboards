# =============================================================================
# part3_dashboards/02_streamlit_app.py
# Tableau de bord Streamlit — arrondissements de Sherbrooke
# Carte Folium qualitative + tableau avec lien bidirectionnel
# Lancer : streamlit run 02_streamlit_app.py
# =============================================================================

from pathlib import Path
import sys

import geopandas as gpd
import folium
import plotly.express as px
from streamlit_folium import st_folium
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir

# Palettes qualitatives disponibles : chaque arrondissement reçoit une couleur distincte
PALETTE_OPTIONS = ["Plotly", "D3", "Bold", "Pastel", "Safe", "Vivid"]

# Couleur de mise en évidence de l'arrondissement sélectionné
HIGHLIGHT_COLOR = "#ff4444"

GPKG_FILE = "Arrondissement_-5179909302249146713.gpkg"


@st.cache_data
def load_data() -> gpd.GeoDataFrame:
    """Charge les arrondissements en EPSG:4326 et calcule la superficie."""
    config = load_config()
    vector_dir = get_vector_dir(config)
    gdf = gpd.read_file(vector_dir / GPKG_FILE).to_crs(4326)
    # Superficie calculée en MTM Québec pour éviter les distorsions métriques
    gdf["area_km2"] = gdf.to_crs(32198).geometry.area / 1e6
    gdf["area_km2"] = gdf["area_km2"].round(2)
    return gdf[["ID", "NUMERO", "NOM", "area_km2", "geometry"]]


def get_palette_colors(palette_name: str, n: int) -> list:
    """Retourne n couleurs issues d'une palette qualitative Plotly."""
    colors = getattr(px.colors.qualitative, palette_name)
    # Répétition cyclique si la palette contient moins de couleurs que d'arrondissements
    return [colors[i % len(colors)] for i in range(n)]


def build_map(gdf: gpd.GeoDataFrame, palette_name: str, active_id) -> folium.Map:
    """Construit la carte Folium avec coloration qualitative et mise en évidence."""
    center = [
        gdf.geometry.centroid.y.mean(),
        gdf.geometry.centroid.x.mean(),
    ]

    # Dictionnaire ID → couleur de palette pour un accès O(1) dans style_function
    ids = gdf["ID"].tolist()
    palette_colors = get_palette_colors(palette_name, len(ids))
    color_by_id = dict(zip(ids, palette_colors))

    m = folium.Map(location=center, zoom_start=11, tiles="CartoDB positron")

    def style_function(feature):
        """Retourne le style d'un polygone selon son état de sélection."""
        oid = feature["properties"]["ID"]
        if oid == active_id:
            return {
                "fillColor": HIGHLIGHT_COLOR,
                "color": HIGHLIGHT_COLOR,
                "weight": 4,
                "fillOpacity": 0.65,
            }
        return {
            "fillColor": color_by_id.get(oid, "#999999"),
            "color": "#333333",
            "weight": 1,
            "fillOpacity": 0.55,
        }

    folium.GeoJson(
        gdf,
        name="Arrondissements",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["NOM", "NUMERO", "area_km2"],
            aliases=["Nom", "Numéro", "Superficie (km²)"],
        ),
        popup=folium.GeoJsonPopup(
            fields=["NOM", "NUMERO", "area_km2"],
            aliases=["Nom", "Numéro", "Superficie (km²)"],
        ),
    ).add_to(m)

    return m


def main():
    st.set_page_config(page_title="Arrondissements de Sherbrooke", layout="wide")

    gdf = load_data()

    # Initialisation de l'état de sélection dans la session
    if "active_id" not in st.session_state:
        st.session_state.active_id = None

    st.title("Carte interactive des arrondissements — Sherbrooke")

    col_map, col_options = st.columns([2, 1])

    # --- Panneau d'options ---
    with col_options:
        st.subheader("Options")

        palette_name = st.selectbox("Palette de couleurs", PALETTE_OPTIONS)

        st.write("Arrondissement sélectionné :")
        if st.session_state.active_id is None:
            st.info("Aucun")
        else:
            match = gdf.loc[gdf["ID"] == st.session_state.active_id]
            if not match.empty:
                st.success(match.iloc[0]["NOM"])

    # --- Carte ---
    with col_map:
        st.subheader("Carte")

        m = build_map(gdf, palette_name, st.session_state.active_id)

        map_output = st_folium(
            m,
            width=None,
            height=600,
            returned_objects=["last_active_drawing"],
        )

        # Clic sur un polygone → mise à jour de l'ID actif
        if map_output and map_output.get("last_active_drawing"):
            props = map_output["last_active_drawing"]["properties"]
            clicked_id = props.get("ID")
            if clicked_id is not None and clicked_id != st.session_state.active_id:
                st.session_state.active_id = clicked_id
                st.rerun()

    # --- Tableau ---
    st.subheader("Tableau des arrondissements")

    df_display = gdf.drop(columns="geometry").copy()

    # Indicateur textuel de la ligne active (contournement : st.dataframe ne supporte pas
    # la présélection programmatique d'une ligne)
    df_display["sélectionné"] = df_display["ID"].apply(
        lambda x: "← sélectionné" if x == st.session_state.active_id else ""
    )

    table_event = st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Clic sur une ligne → mise à jour de l'ID actif
    if table_event.selection.rows:
        row_idx = table_event.selection.rows[0]
        clicked_id = df_display.iloc[row_idx]["ID"]
        if clicked_id != st.session_state.active_id:
            st.session_state.active_id = clicked_id
            st.rerun()

    # --- Fiche détail ---
    if st.session_state.active_id is not None:
        st.subheader("Détail")
        detail = gdf.loc[gdf["ID"] == st.session_state.active_id].drop(columns="geometry")
        st.table(detail)


if __name__ == "__main__":
    main()
