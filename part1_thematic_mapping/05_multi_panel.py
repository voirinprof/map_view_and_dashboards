# =============================================================================
# part1_thematic_mapping/05_multi_panel.py
# Cartes multi-panneaux (facettes) — comparer plusieurs variables ou périodes
# Pattern utile pour les rapports d'évolution temporelle ou de comparaison
# =============================================================================

from pathlib import Path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def make_facet_map(gdf: gpd.GeoDataFrame, variables: list, titles: list,
                   suptitle: str, output_path: Path,
                   cmap: str, scheme: str, k: int,
                   dpi: int, source_text: str) -> None:
    """
    Génère une grille de cartes choroplèthes (une par variable).
    Toutes les cartes partagent la même palette et le même nombre de classes.

    Paramètres
    ----------
    gdf         : GeoDataFrame contenant toutes les variables
    variables   : liste des colonnes à représenter
    titles      : liste des titres de panneaux (même longueur que variables)
    suptitle    : titre général de la figure
    output_path : chemin de sortie (PNG)
    cmap        : palette de couleurs commune
    scheme      : méthode de discrétisation commune
    k           : nombre de classes commun
    dpi         : résolution de sortie
    source_text : texte de source
    """
    n = len(variables)
    # Mise en page automatique : 1 ligne si ≤ 3 variables, sinon 2 lignes
    ncols = min(n, 3)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(7 * ncols, 6 * nrows))

    # Aplatir les axes pour un accès uniforme (1D ou 2D selon la grille)
    axes_flat = np.array(axes).flatten()

    for ax, var, title in zip(axes_flat, variables, titles):
        gdf.plot(
            column=var,
            cmap=cmap,
            scheme=scheme,
            k=k,
            legend=True,
            legend_kwds={"fontsize": 7, "title_fontsize": 8},
            edgecolor="white",
            linewidth=0.4,
            ax=ax,
            missing_kwds={"color": "lightgrey"},
        )
        ax.set_title(title, fontsize=11, pad=6)
        ax.axis("off")

    # Masquer les panneaux vides si le nombre de variables ne remplit pas la grille
    for ax in axes_flat[n:]:
        ax.set_visible(False)

    fig.suptitle(suptitle, fontsize=15, fontweight="bold", y=1.01)
    fig.text(0.5, -0.01, source_text, ha="center", fontsize=8, color="grey", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def make_palette_comparison_map(gdf: gpd.GeoDataFrame, column: str,
                                 output_path: Path, dpi: int,
                                 source_text: str) -> None:
    """
    Compare deux palettes de couleurs sur la même variable, côte à côte.
    Illustre l'impact du choix de palette sur la lecture du phénomène.

    Paramètres
    ----------
    gdf         : GeoDataFrame avec la colonne à représenter
    column      : colonne numérique à cartographier
    output_path : chemin de sortie (PNG)
    dpi         : résolution de sortie
    source_text : texte de source
    """
    fig = plt.figure(figsize=(14, 6))

    gs = gridspec.GridSpec(1, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    for ax, cmap, label in [
        (ax1, "YlOrRd", "Palette divergente (YlOrRd)"),
        (ax2, "Blues",  "Palette séquentielle (Blues)"),
    ]:
        gdf.plot(
            column=column,
            cmap=cmap,
            scheme="NaturalBreaks",
            k=3,
            legend=True,
            legend_kwds={"fontsize": 8, "title": "Superficie (km²)", "title_fontsize": 9},
            edgecolor="white",
            linewidth=0.5,
            ax=ax,
        )
        ax.set_title(label, fontsize=11)
        ax.axis("off")

    fig.suptitle(
        "Impact du choix de palette — Superficie des arrondissements (km²)",
        fontsize=14, fontweight="bold"
    )
    fig.text(0.5, -0.02, source_text, ha="center", fontsize=7, color="grey", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def main():
    config = load_config()
    vector_dir = get_vector_dir(config)
    output_dir = get_output_dir(config)

    crs_projected = config["crs"]["projected"]
    cmap          = config["mapping"]["default_cmap"]
    scheme        = config["mapping"]["default_scheme"]
    k             = config["mapping"]["default_k"]
    dpi           = config["mapping"]["dpi"]
    source_text   = config["styles"]["source_text"]

    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(crs_projected)

    # Calcul de la superficie des polygones dans le CRS projeté
    gdf["area_km2"] = gdf.geometry.area / 1_000_000

    # --- Carte 1 : facette par arrondissement ---
    variables = ["area_km2"]
    titles    = ["Superficie (km²)"]

    make_facet_map(
        gdf=gdf,
        variables=variables,
        titles=titles,
        suptitle="Superficie des arrondissements — Sherbrooke",
        output_path=output_dir / "multi_panel_variables.png",
        cmap=cmap,
        scheme=scheme,
        k=k,
        dpi=dpi,
        source_text=source_text,
    )

    # --- Carte 2 : comparaison de palettes sur la même variable ---
    make_palette_comparison_map(
        gdf=gdf,
        column="area_km2",
        output_path=output_dir / "multi_panel_comparison.png",
        dpi=dpi,
        source_text=source_text,
    )


if __name__ == "__main__":
    main()
