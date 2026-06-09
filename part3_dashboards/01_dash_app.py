# =============================================================================
# part3_dashboards/01_dash_app.py
# Tableau de bord Dash — arrondissements de Sherbrooke
# Carte choroplèthe qualitative + tableau avec lien bidirectionnel
# Lancer : python 01_dash_app.py  →  http://localhost:8050
# =============================================================================

from pathlib import Path
import sys
import json

import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir

# Palettes qualitatives disponibles : chaque arrondissement reçoit une couleur distincte
PALETTE_OPTIONS = ["Plotly", "D3", "Bold", "Pastel", "Safe", "Vivid"]

# Couleur de mise en évidence de l'arrondissement sélectionné
HIGHLIGHT_COLOR = "#ff4444"


def load_data(vector_dir: Path) -> tuple:
    """Charge les arrondissements et prépare le GeoJSON pour Plotly."""
    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(4326)
    # Superficie calculée en MTM Québec pour éviter les distorsions métriques
    gdf["area_km2"] = gdf.to_crs(32198).geometry.area / 1e6
    gdf["area_km2"] = gdf["area_km2"].round(2)
    geojson = json.loads(gdf.to_json())
    df_table = gdf.drop(columns="geometry").copy()
    return gdf, geojson, df_table


def build_layout(df_table) -> html.Div:
    """Définit la structure statique de l'application."""
    return html.Div(
        style={"padding": "20px", "fontFamily": "Arial"},
        children=[
            html.H1("Carte interactive des arrondissements — Sherbrooke"),

            html.Div(
                style={"display": "flex", "gap": "20px"},
                children=[
                    # Panneau gauche : carte
                    html.Div(
                        style={"width": "70%"},
                        children=[
                            html.H3("Carte"),
                            dcc.Graph(id="map", style={"height": "600px"}),
                        ]
                    ),

                    # Panneau droit : sélecteur de palette + info sélection
                    html.Div(
                        style={"width": "30%"},
                        children=[
                            html.H3("Options"),
                            html.Label("Palette de couleurs"),
                            dcc.Dropdown(
                                id="palette-select",
                                options=[{"label": p, "value": p} for p in PALETTE_OPTIONS],
                                value=PALETTE_OPTIONS[0],
                                clearable=False,
                            ),
                            html.Br(),
                            html.Div(
                                id="selection-info",
                                style={
                                    "padding": "10px",
                                    "border": "1px solid #ddd",
                                    "borderRadius": "5px",
                                }
                            ),
                        ]
                    ),
                ]
            ),

            html.H3("Tableau des arrondissements"),
            dash_table.DataTable(
                id="data-table",
                data=df_table.to_dict("records"),
                columns=[{"name": col, "id": col} for col in df_table.columns],
                row_selectable="single",
                selected_rows=[],
                page_size=20,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "8px",
                    "fontFamily": "Arial",
                    "fontSize": "14px",
                },
                style_header={
                    "fontWeight": "bold",
                    "backgroundColor": "#f2f2f2",
                },
            ),

            # Stockage de l'ID actif partagé entre les deux callbacks
            dcc.Store(id="active-id"),
        ]
    )


def register_callbacks(app: Dash, gdf, geojson, df_table) -> None:
    """Enregistre les callbacks qui gèrent la synchronisation carte ↔ tableau."""

    # Callback 1 : détermine l'ID actif selon la source du déclenchement
    @app.callback(
        Output("active-id", "data"),
        Input("map", "clickData"),
        Input("data-table", "selected_rows"),
        State("active-id", "data"),
        prevent_initial_call=True,
    )
    def sync_selection(click_data, selected_rows, current_id):
        """Met à jour l'ID actif à partir d'un clic carte ou d'une sélection tableau."""
        trigger = callback_context.triggered[0]["prop_id"].split(".")[0]

        if trigger == "map" and click_data:
            # Récupération de l'ID depuis les propriétés du polygone cliqué
            return click_data["points"][0]["location"]

        if trigger == "data-table" and selected_rows:
            # Récupération de l'ID depuis la ligne sélectionnée
            return df_table.iloc[selected_rows[0]]["ID"]

        return current_id

    # Callback 2 : redessine la carte et met à jour le tableau selon l'ID actif
    @app.callback(
        Output("map", "figure"),
        Output("data-table", "style_data_conditional"),
        Output("data-table", "selected_rows"),
        Output("selection-info", "children"),
        Input("palette-select", "value"),
        Input("active-id", "data"),
    )
    def render_interface(palette_name, active_id):
        """Met à jour carte, tableau et panneau d'information."""
        # Récupération des couleurs de la palette qualitative Plotly
        palette_colors = getattr(px.colors.qualitative, palette_name)

        # Attribution d'une couleur distincte par arrondissement
        noms = gdf["NOM"].tolist()
        color_map = {nom: palette_colors[i % len(palette_colors)] for i, nom in enumerate(noms)}

        # Remplacement de la couleur par la couleur de mise en évidence pour la sélection
        if active_id is not None:
            match = gdf[gdf["ID"] == active_id]
            if not match.empty:
                color_map[match.iloc[0]["NOM"]] = HIGHLIGHT_COLOR

        fig = px.choropleth_mapbox(
            gdf,
            geojson=geojson,
            locations="ID",
            featureidkey="properties.ID",
            color="NOM",
            color_discrete_map=color_map,
            hover_name="NOM",
            hover_data={"ID": True, "NUMERO": True, "area_km2": True},
            center={
                "lat": gdf.geometry.centroid.y.mean(),
                "lon": gdf.geometry.centroid.x.mean(),
            },
            zoom=10,
            mapbox_style="carto-positron",
            opacity=0.65,
        )
        fig.update_traces(marker_line_width=1, marker_line_color="#333333")
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False,
        )

        # Mise en évidence de la ligne correspondante dans le tableau
        row_styles = []
        selected_rows = []
        info = "Aucun arrondissement sélectionné"

        if active_id is not None:
            mask = df_table["ID"] == active_id
            if mask.any():
                idx = df_table.index[mask][0]
                selected_rows = [idx]
                row_styles.append({
                    "if": {"row_index": idx},
                    "backgroundColor": "#ffe6e6",
                    "fontWeight": "bold",
                })
                info = html.Div([
                    html.Strong("Arrondissement sélectionné"),
                    html.Br(),
                    html.Span(df_table.loc[idx, "NOM"]),
                ])

        return fig, row_styles, selected_rows, info


def main():
    config = load_config()
    gdf, geojson, df_table = load_data(get_vector_dir(config))

    app = Dash(__name__, title="GMQ 580 — Arrondissements Sherbrooke")
    app.layout = build_layout(df_table)
    register_callbacks(app, gdf, geojson, df_table)

    print("Application disponible à : http://localhost:8050")
    app.run(debug=True, port=8050)


if __name__ == "__main__":
    main()
