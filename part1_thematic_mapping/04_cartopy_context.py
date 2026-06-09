# =============================================================================
# part1_thematic_mapping/04_cartopy_context.py
# Carte de contexte régional du Québec avec Cartopy
# Superposition des arrondissements de Sherbrooke sur un fond géographique
# =============================================================================

from pathlib import Path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.feature as cfeature

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def make_regional_context_map(output_path: Path, dpi: int, source_text: str) -> None:
    """
    Génère une carte de contexte régional du Québec centrée sur Sherbrooke.
    Utilise la projection LambertConformal adaptée au Québec.

    Paramètres
    ----------
    output_path : chemin de sortie (PNG)
    dpi         : résolution de sortie
    source_text : texte de source
    """
    # Projection Lambert conforme conique — adaptée aux latitudes moyennes du Québec
    proj = ccrs.LambertConformal(
        central_longitude=-72.0,
        central_latitude=46.0,
        standard_parallels=(46.0, 60.0),
    )

    fig, ax = plt.subplots(
        subplot_kw={"projection": proj},
        figsize=[12, 9]
    )

    # Étendue géographique : Québec méridional
    ax.set_extent([-80.0, -60.0, 43.0, 52.0], crs=ccrs.PlateCarree())

    # Ajout des éléments géographiques de fond
    ax.add_feature(cfeature.LAND,    facecolor="#f5f5f0", zorder=0)
    ax.add_feature(cfeature.OCEAN,   facecolor="#d0e8f0", zorder=0)
    ax.add_feature(cfeature.LAKES,   facecolor="#c8dff0", edgecolor="#aaaaaa", linewidth=0.3)
    ax.add_feature(cfeature.RIVERS,  edgecolor="#88b8d8", linewidth=0.4)
    ax.add_feature(cfeature.BORDERS, edgecolor="#888888", linewidth=0.8, linestyle="--")
    ax.add_feature(cfeature.STATES,  edgecolor="#aaaaaa", linewidth=0.5, linestyle=":")
    ax.add_feature(cfeature.COASTLINE, edgecolor="#666666", linewidth=0.6)

    # Quadrillage avec étiquettes de coordonnées
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        color="grey",
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False

    # Marqueur pour localiser Sherbrooke
    ax.plot(
        -71.888, 45.404,
        marker="*",
        markersize=14,
        color="#e63946",
        transform=ccrs.PlateCarree(),
        zorder=5,
        label="Sherbrooke",
    )

    ax.set_title(
        "Localisation de Sherbrooke — Contexte régional (Québec)",
        fontsize=13, pad=12, fontweight="bold"
    )

    # Légende manuelle
    legend_patch = mpatches.Patch(color="#e63946", label="Sherbrooke")
    ax.legend(handles=[legend_patch], loc="lower right", fontsize=10)

    fig.text(0.5, 0.02, source_text, ha="center", fontsize=7, color="grey", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def make_local_map_with_cartopy(gdf: gpd.GeoDataFrame, output_path: Path,
                                 dpi: int, source_text: str) -> None:
    """
    Superpose les arrondissements de Sherbrooke sur un fond Cartopy.
    Illustre l'intégration GeoDataFrame → GeoAxes Cartopy.

    Paramètres
    ----------
    gdf         : GeoDataFrame des arrondissements en EPSG:4326
    output_path : chemin de sortie (PNG)
    dpi         : résolution de sortie
    source_text : texte de source
    """
    proj = ccrs.LambertConformal(central_longitude=-71.9, central_latitude=45.4)

    fig, ax = plt.subplots(subplot_kw={"projection": proj}, figsize=[10, 8])
    ax.set_extent([-72.3, -71.4, 45.1, 45.7], crs=ccrs.PlateCarree())

    # Fond géographique local
    ax.add_feature(cfeature.LAND,  facecolor="#f0ede8")
    ax.add_feature(cfeature.LAKES, facecolor="#c8dff0", edgecolor="#aaaaaa", linewidth=0.3)
    ax.add_feature(cfeature.RIVERS, edgecolor="#88b8d8", linewidth=0.5)
    ax.add_feature(cfeature.COASTLINE, edgecolor="#888888", linewidth=0.5)

    # Superposition des polygones GeoDataFrame sur les GeoAxes Cartopy
    # Les géométries doivent être en EPSG:4326 → transformer avec PlateCarree()
    for _, row in gdf.iterrows():
        ax.add_geometries(
            [row.geometry],
            crs=ccrs.PlateCarree(),
            facecolor="#3186cc",
            edgecolor="white",
            alpha=0.5,
            linewidth=0.8,
        )

    ax.gridlines(draw_labels=True, linewidth=0.3, color="grey", alpha=0.5)
    ax.set_title(
        "Arrondissements de Sherbrooke — Contexte local",
        fontsize=13, pad=10, fontweight="bold"
    )
    fig.text(0.5, 0.01, source_text, ha="center", fontsize=7, color="grey", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)
    dpi         = config["mapping"]["dpi"]
    source_text = config["styles"]["source_text"]

    # --- Carte 1 : contexte régional Québec ---
    make_regional_context_map(
        output_path=output_dir / "cartopy_regional_context.png",
        dpi=dpi,
        source_text=source_text,
    )

    # --- Carte 2 : superposition des arrondissements ---
    # Chargement en EPSG:4326 pour compatibilité avec Cartopy PlateCarree
    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg").to_crs(4326)

    make_local_map_with_cartopy(
        gdf=gdf,
        output_path=output_dir / "cartopy_local_arrondissements.png",
        dpi=dpi,
        source_text=source_text,
    )


if __name__ == "__main__":
    main()
