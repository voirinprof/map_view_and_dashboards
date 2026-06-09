# =============================================================================
# sandbox/exercice_folium.py
# Exercice — Carte Folium multi-couches avec contrôle de visibilité
#
# Objectif : construire une carte qui superpose les 3 sources de données
#   • Arrondissements  (polygones)  — GeoPackage
#   • Réseau routier   (lignes)     — GeoPackage
#   • Occupants        (points)     — CSV
#
# Chaque couche est placée dans un FeatureGroup indépendant, ce qui permet
# à l'utilisateur de les activer ou désactiver via un LayerControl.
#
# Résultat attendu : fichier output/exercice_folium.html autonome
# =============================================================================

from pathlib import Path
import sys

import folium
import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


# =============================================================================
# Chargement des données  (section fournie — rien à modifier ici)
# =============================================================================

config     = load_config()
vector_dir = get_vector_dir(config)
output_dir = get_output_dir(config)

center_lat = config["extent"]["center_lat"]   # 45.404
center_lon = config["extent"]["center_lon"]   # -71.888
zoom       = config["extent"]["zoom_folium"]  # 12

# Polygones — colonnes disponibles : NOM, NUMERO  (+area_km2 calculée ci-dessous)
gdf_arr = gpd.read_file(
    vector_dir / "Arrondissement_-5179909302249146713.gpkg"
).to_crs(4326)
gdf_arr["area_km2"] = gdf_arr.to_crs(32198).geometry.area / 1e6

# Lignes — colonnes disponibles : TOPONYMIE, TYPERUE, VITESSE
gdf_streets = gpd.read_file(
    vector_dir / "SegmentRue_1502216369322323101.gpkg"
).to_crs(4326)

# Points — colonnes disponibles : lat, lng, entreprise, type_etablissement
df_occ = pd.read_csv(vector_dir / "liste_occupants.csv")


# =============================================================================
# TODO 1 — Créer la carte de base
# -----------------------------------------------------------------------------
# Créer un objet folium.Map centré sur Sherbrooke avec le zoom fourni.
# Choisir le fond de carte "CartoDB positron".
#
# Signature : folium.Map(location=[lat, lon], zoom_start=..., tiles=...)
# =============================================================================

m = None  # ← remplacer cette ligne


# =============================================================================
# TODO 2 — Couche Arrondissements (polygones)
# -----------------------------------------------------------------------------
# Ajouter une couche GeoJson dans le FeatureGroup fg_arr déjà créé.
# La couche doit avoir :
#   - une style_function qui retourne fillColor, color, weight, fillOpacity
#   - un GeoJsonTooltip affichant NOM, NUMERO et area_km2
#   - un GeoJsonPopup avec les mêmes champs
#
# Fonctions : folium.GeoJson, folium.GeoJsonTooltip, folium.GeoJsonPopup
#
# BONUS 2 : ajouter aussi une highlight_function qui change le style au survol
#           (même signature que style_function, mais couleurs et épaisseur différentes)
# =============================================================================

fg_arr = folium.FeatureGroup(name="Arrondissements")

# --- votre code ici ---


fg_arr.add_to(m)


# =============================================================================
# TODO 3 — Couche Réseau routier (lignes)
# -----------------------------------------------------------------------------
# Ajouter une couche GeoJson dans fg_streets.
# La couche doit avoir :
#   - un style de ligne (color, weight, opacity)
#   - un GeoJsonTooltip affichant TOPONYMIE et VITESSE
#   - show=False sur le FeatureGroup pour masquer la couche par défaut
#
# Fonctions : folium.GeoJson, folium.GeoJsonTooltip
# =============================================================================

fg_streets = folium.FeatureGroup(name="Réseau routier", show=False)

# --- votre code ici ---


fg_streets.add_to(m)


# =============================================================================
# TODO 4 — Couche Occupants (points)
# -----------------------------------------------------------------------------
# Itérer sur df_occ et ajouter un CircleMarker par ligne dans fg_occ.
# Chaque marqueur doit avoir :
#   - location=[row["lat"], row["lng"]]
#   - radius, color, fill, fill_color, fill_opacity au choix
#   - un Tooltip affichant entreprise et type_etablissement
#
# Fonctions : folium.CircleMarker, folium.Tooltip
#
# BONUS 1 : colorier les marqueurs selon type_etablissement
#   Catégories présentes : "Commerce", "Bureau", "Industriel", "Agricole/pêcherie"
#   Indice : color_map = {"Commerce": "#2196F3", "Bureau": "#FF9800", ...}
# =============================================================================

fg_occ = folium.FeatureGroup(name="Occupants")

# --- votre code ici ---


fg_occ.add_to(m)


# =============================================================================
# TODO 5 — Contrôle de couches et sauvegarde
# -----------------------------------------------------------------------------
# 1. Ajouter un LayerControl à la carte (collapsed=False pour l'afficher ouvert)
# 2. Sauvegarder la carte dans output/exercice_folium.html
#
# Fonctions : folium.LayerControl, m.save(str(output_path))
# =============================================================================

# --- votre code ici ---

output_path = output_dir / "exercice_folium.html"
print(f"Carte sauvegardée : {output_path}")
