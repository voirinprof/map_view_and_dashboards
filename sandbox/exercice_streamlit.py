# =============================================================================
# sandbox/exercice_streamlit.py
# Exercice — Tableau de bord Streamlit : exploration des occupants
#
# Objectif : construire un tableau de bord avec filtres dans une st.sidebar,
# une carte Folium des points filtrés, un graphique de distribution
# et des métriques résumant la sélection courante.
#
# Lancer : streamlit run exercice_streamlit.py
# =============================================================================

from pathlib import Path
import sys

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir


# =============================================================================
# Chargement des données  (section fournie — rien à modifier ici)
# =============================================================================

@st.cache_data
def load_data() -> tuple:
    """
    Charge les arrondissements et les occupants.
    Effectue une jointure spatiale pour associer chaque occupant
    à l'arrondissement dans lequel il se trouve.
    """
    config     = load_config()
    vector_dir = get_vector_dir(config)

    gdf_arr = gpd.read_file(
        vector_dir / "Arrondissement_-5179909302249146713.gpkg"
    ).to_crs(4326)

    df_occ = pd.read_csv(vector_dir / "liste_occupants.csv")

    # Conversion du CSV en GeoDataFrame pour la jointure spatiale
    gdf_occ = gpd.GeoDataFrame(
        df_occ,
        geometry=gpd.points_from_xy(df_occ["lng"], df_occ["lat"]),
        crs=4326,
    )

    # Chaque occupant hérite du NOM de l'arrondissement qui le contient
    joined = gpd.sjoin(
        gdf_occ, gdf_arr[["NOM", "geometry"]],
        how="left", predicate="within",
    )
    df_occ["arrondissement"] = joined["NOM"].fillna("Hors limites").values

    return gdf_arr, df_occ


config     = load_config()
center_lat = config["extent"]["center_lat"]
center_lon = config["extent"]["center_lon"]
zoom       = config["extent"]["zoom_folium"]

gdf_arr, df_occ = load_data()


# =============================================================================
# TODO 1 — Configuration de la page et titre
# -----------------------------------------------------------------------------
# 1. Configurer la page : st.set_page_config(page_title=..., layout="wide")
# 2. Afficher le titre principal de l'application : st.title(...)
# 3. Ajouter un en-tête dans la sidebar : st.sidebar.header(...)
# =============================================================================

# --- votre code ici ---


# =============================================================================
# TODO 2 — Filtres dans la sidebar
# -----------------------------------------------------------------------------
# Créer deux widgets de filtre dans st.sidebar :
#   a) Un selectbox "Arrondissement" avec ["Tous"] + liste des arrondissements
#   b) Un multiselect "Types d'établissement" avec tous les types disponibles
#
# Colonnes disponibles : df_occ["arrondissement"], df_occ["type_etablissement"]
# Fonctions : st.sidebar.selectbox, st.sidebar.multiselect
# =============================================================================

# --- votre code ici ---
# selected_arr   = ...
# selected_types = ...


# =============================================================================
# TODO 3 — Filtrage du DataFrame
# -----------------------------------------------------------------------------
# Appliquer les deux filtres sur df_occ pour produire df_filtered.
#   - Si selected_arr == "Tous" : ne pas filtrer par arrondissement
#   - Si selected_types est vide : ne pas filtrer par type
#
# Indice : utiliser des conditions if/else avec .copy() et .isin()
# =============================================================================

df_filtered = df_occ.copy()   # ← remplacer par la logique de filtrage


# =============================================================================
# TODO 4 — Métriques
# -----------------------------------------------------------------------------
# Afficher 3 métriques côte à côte dans des colonnes :
#   - Nombre d'occupants dans df_filtered
#   - Nombre de types d'établissement distincts
#   - Nombre d'arrondissements distincts
#
# Fonctions : st.columns(3), st.metric(label=..., value=...)
# =============================================================================

# --- votre code ici ---


# =============================================================================
# TODO 5 — Carte et graphique côte à côte
# -----------------------------------------------------------------------------
# Créer deux colonnes (ratio 2:1) :
#
# Colonne gauche — Carte Folium :
#   - Carte centrée sur Sherbrooke (center_lat, center_lon, zoom)
#   - Couche GeoJson des arrondissements en fond (style neutre)
#   - Un CircleMarker par ligne de df_filtered (lat, lng, entreprise, type_etablissement)
#   - Afficher avec st_folium(m, width=None, height=500, key="map")
#
# Colonne droite — Graphique à barres :
#   - Compter les occupants par type_etablissement dans df_filtered
#   - Graphique horizontal avec px.bar (orientation="h")
#   - Afficher avec st.plotly_chart(..., use_container_width=True)
#
# Fonctions : st.columns, folium.Map, folium.GeoJson, folium.CircleMarker,
#             folium.Tooltip, st_folium, px.bar, st.plotly_chart
#
# BONUS 1 : colorier les marqueurs selon type_etablissement
#   (même color_map que dans l'exercice Folium)
# =============================================================================

# --- votre code ici ---


# =============================================================================
# BONUS 2 — Tableau des occupants filtrés
# -----------------------------------------------------------------------------
# Afficher df_filtered (sans la colonne géométrie si présente) sous la carte
# avec st.dataframe(..., use_container_width=True, hide_index=True)
# =============================================================================

# --- votre code ici ---
