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
# définition du titre de la page, du titre principal et de l'en-tête de la sidebar.
st.set_page_config(page_title="Exploration des occupants", layout="wide")
# le titre principal de l'application doit être "Exploration des occupants — Sherbrooke"
st.title("Exploration des occupants — Sherbrooke")
# l'en-tête de la sidebar doit être "Filtres"
st.sidebar.header("Filtres")


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

# pour définir un filtre pour les arrondissements, on utilise un selectbox avec comme options "Tous" + la liste 
# des arrondissements uniques présents dans le DataFrame.

# on veut les valeurs uniques de la colonne "arrondissement", triées par ordre alphabétique, 
# et on ajoute "Tous" au début de la liste pour permettre de désactiver le filtre.
arr_options = ["Tous"] + sorted(df_occ["arrondissement"].unique().tolist())
selected_arr = st.sidebar.selectbox("Arrondissement", arr_options)

# pour le filtre des types d'établissement, on utilise un multiselect avec comme options la liste 
# des types d'établissement uniques présents dans le DataFrame.

# on veut les valeurs uniques de la colonne "type_etablissement", triées par ordre alphabétique,
# et on ignore les valeurs manquantes (dropna) pour éviter d'avoir une option "NaN" dans le multiselect.
type_options = sorted(df_occ["type_etablissement"].dropna().unique().tolist())

selected_types = st.sidebar.multiselect(
    "Types d'établissement",
    options=type_options,
    default=[],   # vide = tous les types affichés
)


# =============================================================================
# TODO 3 — Filtrage du DataFrame
# -----------------------------------------------------------------------------
# Appliquer les deux filtres sur df_occ pour produire df_filtered.
#   - Si selected_arr == "Tous" : ne pas filtrer par arrondissement
#   - Si selected_types est vide : ne pas filtrer par type
#
# Indice : utiliser des conditions if/else avec .copy() et .isin()
# =============================================================================

#df_filtered = df_occ.copy()   # ← remplacer par la logique de filtrage

# faison une copie du DataFrame original pour ne pas modifier les données brutes.
df_filtered = df_occ.copy()

# ensuite on applique les filtres un par un.

# Filtre par arrondissement — "Tous" désactive le filtre
if selected_arr != "Tous":
    df_filtered = df_filtered[df_filtered["arrondissement"] == selected_arr]

# Filtre par type — liste vide désactive le filtre
if selected_types:
    df_filtered = df_filtered[df_filtered["type_etablissement"].isin(selected_types)]


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

# on aura 3 colonnes pour afficher les métriques, que l'on peut créer avec st.columns(3).
col1, col2, col3 = st.columns(3)
# ensuite on utilise la méthode metric de chaque colonne pour afficher les différentes métriques demandées.
col1.metric("Occupants",       len(df_filtered))
col2.metric("Types distincts", df_filtered["type_etablissement"].nunique())
col3.metric("Arrondissements", df_filtered["arrondissement"].nunique())

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
# si on veut appliquer une couleur différente à chaque type d'établissement, on peut définir une color_map qui associe chaque type à une couleur spécifique.
color_map = {
    "Commerce":          "#2196F3",
    "Bureau":            "#FF9800",
    "Industriel":        "#4CAF50",
    "Agricole/pêcherie": "#9C27B0",
}

# pour créer la mise en page avec une carte à gauche et un graphique à droite, on utilise st.columns avec un ratio de 2:1.
col_map, col_chart = st.columns([2, 1])

with col_map:
    st.subheader("Carte")

    # création de la carte centrée sur Sherbrooke avec le fond "CartoDB positron"
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB positron",
    )

    # ajout de la couche des arrondissements en fond neutre
    folium.GeoJson(
        gdf_arr,
        style_function=lambda f: {
            "fillColor": "#eeeeee",
            "color": "#333333",
            "weight": 1.5,
            "fillOpacity": 0.3,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["NOM"],
            aliases=["Arrondissement :"],
        ),
    ).add_to(m)

    # ajout d'un marqueur pour chaque occupant filtré
    for _, row in df_filtered.iterrows():
        fill_color = color_map.get(row["type_etablissement"], "#888888")  # BONUS 1

        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=6,
            color="white",
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.7,
            tooltip=folium.Tooltip(
                text=f"Entreprise : {row['entreprise']}\nType : {row['type_etablissement']}"
            )
         ).add_to(m)

    # affichage de la carte avec st_folium
    st_folium(m, width=None, height=500, key="map")



# =============================================================================
# BONUS 2 — Tableau des occupants filtrés
# -----------------------------------------------------------------------------
# Afficher df_filtered (sans la colonne géométrie si présente) sous la carte
# avec st.dataframe(..., use_container_width=True, hide_index=True)
# =============================================================================

# --- votre code ici ---
with col_chart:
    st.subheader("Distribution par type")

    # si le DataFrame filtré est vide, on affiche un message d'information. Sinon, on crée un graphique à barres horizontal qui montre la distribution des types d'établissement dans la sélection courante.
    if df_filtered.empty:
        st.info("Aucun occupant pour cette sélection.")
    else:
        # pour créer le graphique à barres, on doit d'abord compter le nombre d'occupants par type d'établissement dans df_filtered. On peut faire cela avec value_counts() et reset_index() pour obtenir un DataFrame avec les colonnes "type_etablissement" et "count". Ensuite, on utilise px.bar pour créer le graphique à barres horizontal, en spécifiant orientation="h" et les labels des axes.
        counts = (
            df_filtered["type_etablissement"]
            .value_counts()
            .reset_index()
        )
        counts.columns = ["Type", "Nombre"]

        # enfin, on affiche le graphique avec st.plotly_chart en utilisant use_container_width=True pour qu'il s'adapte à la largeur de la colonne.
        fig = px.bar(
            counts,
            x="Nombre",
            y="Type",
            orientation="h",
            color="Type",
            color_discrete_map=color_map,
        )
        fig.update_layout(
            showlegend=False,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TODO 6 — Affichage du tableau des occupants filtrés
# -----------------------------------------------------------------------------

st.subheader(f"Données filtrées ({len(df_filtered)} occupants)")
# Afficher df_filtered (sans la colonne géométrie si présente) sous la carte
st.dataframe(
    df_filtered[["entreprise", "type_etablissement", "arrondissement", "lat", "lng"]],
    use_container_width=True,
    hide_index=True,
)