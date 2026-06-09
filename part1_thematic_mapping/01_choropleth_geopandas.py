# =============================================================================
# part1_thematic_mapping/01_choropleth_geopandas.py
# Carte choroplèthe avec GeoPandas et discrétisation via mapclassify
# =============================================================================

from pathlib import Path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import mapclassify
import numpy as np

# Accès au config depuis un sous-répertoire
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def compute_area_km2(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calcule la superficie en km² à partir de la géométrie des polygones.
    Les superficies sont calculées dans le CRS projeté (EPSG:32198).
    """
    gdf = gdf.copy()
    gdf["area_km2"] = gdf.geometry.area / 1_000_000
    return gdf


def classify_variable(series, scheme: str, k: int):
    """
    Applique une méthode de discrétisation sur une série de valeurs.
    Retourne un objet mapclassify contenant les classes et les bornes.
    """
    # Mapping des noms de méthodes vers les classes mapclassify
    classifiers = {
        "NaturalBreaks": mapclassify.NaturalBreaks,
        "Quantiles":     mapclassify.Quantiles,
        "EqualInterval": mapclassify.EqualInterval,
        "FisherJenks":   mapclassify.FisherJenks,
    }

    if scheme not in classifiers:
        raise ValueError(f"Méthode de discrétisation inconnue : {scheme}")

    return classifiers[scheme](series.dropna(), k=k)


def make_choropleth(gdf: gpd.GeoDataFrame, column: str, title: str,
                    output_path: Path, cmap: str, scheme: str, k: int,
                    figsize: list, dpi: int, source_text: str,
                    legend_title: str = "") -> None:
    """
    Génère et sauvegarde une carte choroplèthe standardisée.

    Paramètres
    ----------
    gdf          : GeoDataFrame avec les données et géométries
    column       : nom de la colonne à représenter
    title        : titre de la carte
    output_path  : chemin de sortie (PNG)
    cmap         : palette de couleurs Matplotlib
    scheme       : méthode de discrétisation mapclassify
    k            : nombre de classes
    figsize      : dimensions de la figure [largeur, hauteur]
    dpi          : résolution de sortie
    source_text  : texte de source affiché en bas de la carte
    legend_title : titre de la légende
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Dessin de la carte choroplèthe avec légende
    gdf.plot(
        column=column,
        cmap=cmap,
        scheme=scheme,
        k=k,
        legend=True,
        legend_kwds={
            "title": legend_title,
            "loc": "lower left",
            "fontsize": 8,
            "title_fontsize": 9,
        },
        edgecolor="white",
        linewidth=0.5,
        ax=ax,
        missing_kwds={"color": "lightgrey", "label": "Données manquantes"},
    )

    # Mise en page
    ax.set_title(title, fontsize=14, pad=12, fontweight="bold")
    ax.axis("off")

    # Texte de source en bas de la figure
    fig.text(
        0.5, 0.02,
        source_text,
        ha="center", fontsize=8, color="grey", style="italic"
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def main():
    # Charger la configuration
    config = load_config()
    vector_dir = get_vector_dir(config)
    output_dir = get_output_dir(config)

    crs_projected = config["crs"]["projected"]
    cmap          = config["mapping"]["default_cmap"]
    scheme        = config["mapping"]["default_scheme"]
    k             = config["mapping"]["default_k"]
    figsize       = config["mapping"]["figsize"]
    dpi           = config["mapping"]["dpi"]
    source_text   = config["styles"]["source_text"]

    # Chargement des arrondissements et reprojection en EPSG:32198
    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(crs_projected)

    # Calcul de la superficie en km²
    gdf = compute_area_km2(gdf)

    # --- Carte 1 : superficie par arrondissement avec NaturalBreaks ---
    make_choropleth(
        gdf=gdf,
        column="area_km2",
        title="Superficie par arrondissement (km²)\nSherbrooke — NaturalBreaks (k=3)",
        output_path=output_dir / "choropleth_natural_breaks.png",
        cmap=cmap,
        scheme=scheme,
        k=k,
        figsize=figsize,
        dpi=dpi,
        source_text=source_text,
        legend_title="Superficie (km²)",
    )

    # --- Carte 2 : comparaison de méthodes de discrétisation ---
    # Illustre l'impact du choix de méthode sur la lecture du phénomène
    methods = ["NaturalBreaks", "Quantiles", "EqualInterval"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, method in zip(axes, methods):
        gdf.plot(
            column="area_km2",
            cmap=cmap,
            scheme=method,
            k=k,
            legend=False,
            edgecolor="white",
            linewidth=0.4,
            ax=ax,
        )
        ax.set_title(method, fontsize=11)
        ax.axis("off")

    fig.suptitle(
        "Impact de la méthode de discrétisation — Superficie des arrondissements",
        fontsize=14, fontweight="bold"
    )
    fig.text(0.5, 0.02, source_text, ha="center", fontsize=8, color="grey", style="italic")
    plt.tight_layout()

    output_path = output_dir / "choropleth_methods_comparison.png"
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


if __name__ == "__main__":
    main()
