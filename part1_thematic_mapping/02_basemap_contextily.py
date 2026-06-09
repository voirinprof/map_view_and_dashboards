# =============================================================================
# part1_thematic_mapping/02_basemap_contextily.py
# Ajout d'un fond de carte raster (tuiles web) avec contextily
# contextily exige EPSG:3857 (Web Mercator) ou reprojette automatiquement
# =============================================================================

from pathlib import Path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_vector_dir, get_output_dir


def add_basemap(ax, source, crs: int) -> None:
    """
    Ajoute un fond de carte contextily sur un axe Matplotlib.
    Reprojette automatiquement si le CRS n'est pas EPSG:3857.

    Paramètres
    ----------
    ax     : axe Matplotlib sur lequel ajouter le fond de carte
    source : fournisseur de tuiles contextily (ex. ctx.providers.OpenStreetMap.Mapnik)
    crs    : code EPSG du CRS courant des données
    """
    ctx.add_basemap(
        ax,
        source=source,
        crs=f"EPSG:{crs}",   # contextily reprojette les tuiles si nécessaire
        zoom="auto",
    )


def make_map_with_basemap(gdf: gpd.GeoDataFrame, column: str, title: str,
                          output_path: Path, provider, crs: int,
                          cmap: str, alpha: float, figsize: list,
                          dpi: int, source_text: str) -> None:
    """
    Génère une carte avec fond de carte contextily.

    Paramètres
    ----------
    gdf         : GeoDataFrame reprojeté dans le CRS de travail
    column      : colonne à représenter (None = fond de carte seul)
    title       : titre de la carte
    output_path : chemin de sortie (PNG)
    provider    : fournisseur contextily
    crs         : code EPSG du CRS des données
    cmap        : palette de couleurs
    alpha       : transparence des polygones (0=transparent, 1=opaque)
    figsize     : dimensions [largeur, hauteur]
    dpi         : résolution de sortie
    source_text : texte de source
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Dessin des polygones avec transparence pour laisser apparaître le fond
    if column:
        gdf.plot(
            column=column,
            cmap=cmap,
            scheme="NaturalBreaks",
            k=3,
            legend=True,
            alpha=alpha,
            edgecolor="white",
            linewidth=0.5,
            ax=ax,
        )
    else:
        # Contours seulement — .boundary.plot() évite les artefacts de facecolor="none"
        # zorder=2 garantit que les contours s'affichent par-dessus les tuiles
        gdf.boundary.plot(
            edgecolor="white",
            linewidth=1.5,
            ax=ax,
            zorder=2,
        )

    # Ajout du fond de carte
    add_basemap(ax, source=provider, crs=crs)

    ax.set_title(title, fontsize=13, pad=10, fontweight="bold")
    ax.axis("off")
    fig.text(0.5, 0.01, source_text, ha="center", fontsize=7, color="grey", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def main():
    config = load_config()
    vector_dir  = get_vector_dir(config)
    output_dir  = get_output_dir(config)

    figsize     = config["mapping"]["figsize"]
    dpi         = config["mapping"]["dpi"]
    source_text = config["styles"]["source_text"]

    # Chargement — contextily reprojette automatiquement depuis le CRS du fichier
    gdf = gpd.read_file(vector_dir / "Arrondissement_-5179909302249146713.gpkg")
    crs_source = gdf.crs.to_epsg()

    # Calcul de la superficie (reprojection temporaire en EPSG:32198 pour les mètres)
    gdf["area_km2"] = gdf.to_crs(32198).geometry.area / 1_000_000

    # --- Carte 1 : fond OSM avec choroplèthe semi-transparente ---
    make_map_with_basemap(
        gdf=gdf,
        column="area_km2",
        title="Superficie par arrondissement (km²) — Sherbrooke\nFond : OpenStreetMap",
        output_path=output_dir / "basemap_osm_choropleth.png",
        provider=ctx.providers.OpenStreetMap.Mapnik,
        crs=crs_source,
        cmap="Blues",
        alpha=0.6,
        figsize=figsize,
        dpi=dpi,
        source_text=source_text,
    )

    # --- Carte 2 : fond CartoDB clair — meilleur contraste pour données thématiques ---
    make_map_with_basemap(
        gdf=gdf,
        column="area_km2",
        title="Superficie par arrondissement (km²) — Sherbrooke\nFond : CartoDB Positron",
        output_path=output_dir / "basemap_cartodb_choropleth.png",
        provider=ctx.providers.CartoDB.Positron,
        crs=crs_source,
        cmap="YlOrRd",
        alpha=0.65,
        figsize=figsize,
        dpi=dpi,
        source_text=source_text,
    )

    # --- Carte 3 : contours seulement sur fond Esri satellite ---
    make_map_with_basemap(
        gdf=gdf,
        column=None,
        title="Arrondissements de Sherbrooke\nFond : Esri World Imagery",
        output_path=output_dir / "basemap_esri_contours.png",
        provider=ctx.providers.Esri.WorldImagery,
        crs=crs_source,
        cmap=None,
        alpha=1.0,
        figsize=figsize,
        dpi=dpi,
        source_text=source_text,
    )


if __name__ == "__main__":
    main()
