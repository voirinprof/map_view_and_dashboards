# =============================================================================
# part1_thematic_mapping/03_raster_map.py
# Affichage thématique d'un raster Landsat — calcul et visualisation du NDVI
# NDVI = (NIR - Rouge) / (NIR + Rouge)
# Ordre des bandes (Landsat89_Sherbrooke_RGBNIRSWI) :
#   B1 = Rouge  |  B2 = Vert  |  B3 = Bleu  |  B4 = NIR  |  B5 = SWIR
# =============================================================================

from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent.parent))
from config_loader import load_config, get_raster_dir, get_output_dir


def compute_ndvi(red: np.ndarray, nir: np.ndarray,
                 nodata_value: float = None) -> np.ndarray:
    """
    Calcule le NDVI à partir des bandes rouge et proche-infrarouge.
    Les pixels nodata et les divisions par zéro sont masqués (NaN).

    Paramètres
    ----------
    red          : tableau numpy de la bande rouge
    nir          : tableau numpy de la bande NIR
    nodata_value : valeur nodata à masquer (optionnel)

    Retourne
    --------
    np.ndarray : NDVI en float32, valeurs dans [-1, 1]
    """
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)

    # Masquer les pixels nodata
    if nodata_value is not None:
        red[red == nodata_value] = np.nan
        nir[nir == nodata_value] = np.nan

    # Éviter la division par zéro — propager NaN
    denominator = nir + red
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = np.where(denominator != 0, (nir - red) / denominator, np.nan)

    return ndvi.astype(np.float32)


def plot_raster_thematic(data: np.ndarray, transform, crs,
                         title: str, cmap: str,
                         vmin: float, vmax: float, label: str,
                         output_path: Path, dpi: int,
                         source_text: str) -> None:
    """
    Génère une carte thématique d'un raster mono-bande.

    Paramètres
    ----------
    data        : tableau 2D (lignes x colonnes)
    transform   : transformation affine Rasterio
    crs         : système de référence du raster
    title       : titre de la carte
    cmap        : palette de couleurs
    vmin, vmax  : bornes de la palette
    label       : étiquette de la barre de couleurs
    output_path : chemin de sortie (PNG)
    dpi         : résolution de sortie
    source_text : texte de source
    """
    fig, ax = plt.subplots(figsize=[10, 8])

    # Affichage du raster avec imshow — masquer les NaN
    img = ax.imshow(
        data,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest",
    )

    # Barre de couleurs verticale
    cbar = plt.colorbar(img, ax=ax, fraction=0.03, pad=0.03)
    cbar.set_label(label, fontsize=10)

    ax.set_title(title, fontsize=13, pad=10, fontweight="bold")
    ax.axis("off")
    fig.text(0.5, 0.01, source_text, ha="center", fontsize=7, color="grey", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Carte sauvegardée : {output_path}")


def main():
    config = load_config()
    raster_dir  = get_raster_dir(config)
    output_dir  = get_output_dir(config)
    dpi         = config["mapping"]["dpi"]
    source_text = config["styles"]["source_text"]

    raster_path = raster_dir / "Landsat89_Sherbrooke_RGBNIRSWI_2025.tif"

    with rasterio.open(raster_path) as src:
        # Ordre RGBNIRSWI : B1=Rouge, B2=Vert, B3=Bleu, B4=NIR, B5=SWIR
        # Les indices Rasterio commencent à 1
        red = src.read(1).astype(np.float32)
        nir = src.read(4).astype(np.float32)
        nodata = src.nodata
        transform = src.transform
        crs = src.crs

        # Lecture de la bande rouge seule pour une visualisation en niveaux de gris
        band_red_display = src.read(1)

    # --- Calcul du NDVI ---
    ndvi = compute_ndvi(red, nir, nodata_value=nodata)

    # --- Carte 1 : NDVI avec palette RdYlGn ---
    plot_raster_thematic(
        data=ndvi,
        transform=transform,
        crs=crs,
        title="Indice de végétation normalisé (NDVI)\nLandsat 8/9 — Sherbrooke",
        cmap="RdYlGn",
        vmin=-0.2,
        vmax=0.8,
        label="NDVI",
        output_path=output_dir / "raster_ndvi.png",
        dpi=dpi,
        source_text=source_text,
    )

    # --- Carte 2 : bande rouge en niveaux de gris (référence visuelle) ---
    plot_raster_thematic(
        data=band_red_display,
        transform=transform,
        crs=crs,
        title="Bande rouge (B4) — Niveaux de gris\nLandsat 8/9 — Sherbrooke",
        cmap="gray",
        vmin=np.nanpercentile(band_red_display, 2),
        vmax=np.nanpercentile(band_red_display, 98),
        label="Réflectance (B4)",
        output_path=output_dir / "raster_band_red.png",
        dpi=dpi,
        source_text=source_text,
    )

    # --- Statistiques NDVI ---
    valid_ndvi = ndvi[~np.isnan(ndvi)]
    print(f"\nStatistiques NDVI :")
    print(f"  Min    : {valid_ndvi.min():.3f}")
    print(f"  Max    : {valid_ndvi.max():.3f}")
    print(f"  Moyen  : {valid_ndvi.mean():.3f}")
    print(f"  Médian : {np.median(valid_ndvi):.3f}")


if __name__ == "__main__":
    main()
