# Visualisation & communication des résultats

## Structure du dépôt

```
gmq580-seance06/
├── config.yaml                      # paramètres centralisés (noms de fichiers, IDs Drive, CRS)
├── config_loader.py                 # chargement du config.yaml + helpers de chemins
├── download_data.py                 # téléchargement individuel depuis Google Drive
├── part1_thematic_mapping/          # cartographie thématique statique (PNG)
├── part2_interactive_maps/          # cartes interactives exportées en HTML
├── part3_dashboards/                # tableaux de bord Dash et Streamlit (serveur local)
├── part4_automated_report/          # rapport Word automatisé
├── data/
│   ├── vector/                      # données vecteur (.gpkg, .csv)
│   └── raster/                      # données raster (.tif)
└── output/                          # cartes et rapports générés
```

---

## Scripts

### Partie 1 — Cartographie thématique statique

Produit des cartes PNG dans `output/`. Exécuter avec `python <script>`.

| Script | Intérêt |
|---|---|
| `01_choropleth_geopandas.py` | Carte choroplèthe avec discrétisation statistique (NaturalBreaks, Quantiles, EqualInterval) via **mapclassify** — illustre l'impact du choix de la méthode sur la lecture de la carte |
| `02_basemap_contextily.py` | Superposition d'un fond de carte raster (tuiles CartoDB, OpenStreetMap) avec **contextily** — montre comment contextualiser une carte vectorielle |
| `03_raster_map.py` | Lecture d'une image Landsat multi-bandes avec **rasterio**, visualisation d'une composition colorée et calcul du NDVI |
| `04_cartopy_context.py` | Carte avec projection géodésique explicite via **cartopy** — utile pour les représentations à petite échelle nécessitant une projection correcte |
| `05_multi_panel.py` | Composition multi-cartes côte à côte avec `matplotlib.gridspec` — pattern pour produire des figures de comparaison prêtes à publier |

---

### Partie 2 — Cartes interactives HTML

Produit des fichiers `.html` autonomes dans `output/`. Exécuter avec `python <script>`.

| Script | Intérêt |
|---|---|
| `01_folium_base.py` | Carte **Folium** de base avec markers issus d'un CSV, minimap et bouton plein écran — point d'entrée minimal pour Leaflet.js en Python |
| `02_folium_geojson.py` | Couche GeoJSON cliquable avec tooltip et popup configurés — illustre comment exposer les attributs d'un polygone à l'utilisateur |
| `03_folium_choropleth.py` | Choroplèthe Folium avec barre de couleur et légende personnalisée — version interactive du script 01 de la partie 1 |
| `04_folium_clusters.py` | Regroupement automatique de points (`MarkerCluster`) et carte de chaleur (`HeatMap`) avec les plugins Folium |
| `05_plotly_scatter_map.py` | Carte à points avec **Plotly Express** (`scatter_mapbox`) — alternative légère à Folium, exportable en HTML ou intégrable dans Dash |
| `06_plotly_choropleth.py` | Choroplèthe interactif avec **Plotly** (`choropleth_mapbox`) et ajout de traces supplémentaires via `graph_objects` |

---

### Partie 3 — Tableaux de bord interactifs

Applications avec serveur local. Voir les commandes de lancement ci-dessous.

| Script | Intérêt |
|---|---|
| `01_dash_app.py` | Application **Dash** avec sélecteur de palette qualitative (chaque arrondissement reçoit une couleur distincte), carte et tableau synchronisés — démontre le pattern `dcc.Store` + deux callbacks pour un lien bidirectionnel carte ↔ tableau |
| `02_streamlit_app.py` | Application **Streamlit** avec carte **Folium** (`streamlit-folium`), sélecteur de couleur et tableau synchronisé — montre la gestion de l'état avec `st.session_state` et le lien bidirectionnel via `on_select` |

---

### Partie 4 — Rapport automatisé

| Script | Intérêt |
|---|---|
| `01_report_docx.py` | Génération d'un rapport Word structuré avec **python-docx** — injecte des cartes PNG, un tableau de données et du texte dans un document `.docx` mis en forme ; illustre la reproductibilité d'un rapport cartographique |

---

## Installation

```bash
pip install geopandas pyogrio rasterio numpy pandas matplotlib mapclassify \
            contextily cartopy folium plotly dash \
            streamlit streamlit-folium \
            python-docx gdown pyyaml
```

> Les paquets géospatiaux (`geopandas`, `rasterio`, `cartopy`) reposent sur des bibliothèques C (GDAL, GEOS, PROJ).  
> Sur Windows/macOS, préférer l'installation via **conda** (`environment.yml`).

---

## Démarrage rapide

### 1. Télécharger les données

```bash
python download_data.py
```

> Les identifiants Google Drive sont configurés dans `config.yaml`.  
> Le script télécharge chaque fichier dans `data/vector/` ou `data/raster/` et saute les fichiers déjà présents.

---

### 2. Exécuter les scripts

**Partie 1 — Cartes statiques (PNG dans `output/`)**
```bash
python part1_thematic_mapping/01_choropleth_geopandas.py
python part1_thematic_mapping/02_basemap_contextily.py
python part1_thematic_mapping/03_raster_map.py
python part1_thematic_mapping/04_cartopy_context.py
python part1_thematic_mapping/05_multi_panel.py
```

**Partie 2 — Cartes interactives (HTML dans `output/`)**
```bash
python part2_interactive_maps/01_folium_base.py
python part2_interactive_maps/02_folium_geojson.py
python part2_interactive_maps/03_folium_choropleth.py
python part2_interactive_maps/04_folium_clusters.py
python part2_interactive_maps/05_plotly_scatter_map.py
python part2_interactive_maps/06_plotly_choropleth.py
```

**Partie 3 — Tableaux de bord (serveur local)**
```bash
# Application Dash → http://localhost:8050
python part3_dashboards/01_dash_app.py

# Application Streamlit → http://localhost:8501
streamlit run part3_dashboards/02_streamlit_app.py
```

**Partie 4 — Rapport Word (nécessite les PNG de la partie 1)**
```bash
python part4_automated_report/01_report_docx.py
```

---

## Données requises

| Fichier | Répertoire | Description |
|---|---|---|
| `Arrondissement_-5179909302249146713.gpkg` | `data/vector/` | Polygones des 4 arrondissements de Sherbrooke (EPSG:3857) |
| `SegmentRue_1502216369322323101.gpkg` | `data/vector/` | Réseau routier (segments) |
| `liste_occupants.csv` | `data/vector/` | Liste des occupants avec coordonnées |
| `Landsat89_Sherbrooke_RGBNIRSWI_2025.tif` | `data/raster/` | Image Landsat 8/9 — 5 bandes (R, G, B, NIR, SWIR) |

> **Ordre des bandes raster** : B1=Rouge · B2=Vert · B3=Bleu · B4=NIR · B5=SWIR

---

## Bibliothèques couvertes

| Bibliothèque | Usage dans ce dépôt |
|---|---|
| GeoPandas | Lecture et manipulation de données vecteur (.gpkg) |
| Matplotlib | Cartographie statique, mise en page et figures multi-panneaux |
| mapclassify | Discrétisation statistique (NaturalBreaks, Quantiles, EqualInterval) |
| contextily | Fonds de carte raster (tuiles web CartoDB, OSM) |
| Cartopy | Projections géodésiques et couches géographiques |
| Rasterio | Lecture et affichage d'images raster GeoTIFF |
| Folium | Cartes web interactives basées sur Leaflet.js |
| Plotly | Graphiques et cartes interactives (scatter_mapbox, choropleth_mapbox) |
| Dash | Applications web avec callbacks réactifs (carte ↔ tableau) |
| Streamlit | Applications web avec gestion d'état via session_state |
| streamlit-folium | Intégration des cartes Folium dans une application Streamlit |
| python-docx | Génération de rapports Word (.docx) |
| gdown | Téléchargement de fichiers depuis Google Drive |
