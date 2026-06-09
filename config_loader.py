# =============================================================================
# config_loader.py
# Chargement et accès centralisé à la configuration YAML
# =============================================================================

from pathlib import Path
import yaml


def load_config(config_path: Path = None) -> dict:
    """
    Charge le fichier config.yaml et retourne un dictionnaire de configuration.

    Paramètres
    ----------
    config_path : Path, optionnel
        Chemin vers le fichier config.yaml. Par défaut, cherche dans le
        répertoire racine du projet.

    Retourne
    --------
    dict
        Dictionnaire contenant tous les paramètres de configuration.
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def get_data_dir(config: dict) -> Path:
    """Retourne le chemin absolu vers le répertoire racine des données."""
    return Path(__file__).parent / "data"


def get_vector_dir(config: dict) -> Path:
    """Retourne le chemin absolu vers le répertoire des données vecteur."""
    d = Path(__file__).parent / "data" / "vector"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_raster_dir(config: dict) -> Path:
    """Retourne le chemin absolu vers le répertoire des données raster."""
    d = Path(__file__).parent / "data" / "raster"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_output_dir(config: dict) -> Path:
    """
    Retourne le chemin absolu vers le répertoire de sortie.
    Crée le répertoire s'il n'existe pas.
    """
    output_dir = Path(__file__).parent / config["output"]["directory"]
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
