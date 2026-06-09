# =============================================================================
# download_data.py
# Téléchargement des données depuis Google Drive (liens publics individuels)
# Utilise gdown — aucune authentification requise pour les liens publics
# =============================================================================

from pathlib import Path

import gdown

from config_loader import load_config, get_vector_dir, get_raster_dir


def download_file(drive_id: str, destination: Path) -> None:
    """
    Télécharge un fichier depuis Google Drive par son identifiant.

    Paramètres
    ----------
    drive_id    : identifiant Google Drive (extrait de l'URL de partage)
    destination : chemin complet de destination (répertoire + nom de fichier)
    """
    url = f"https://drive.google.com/uc?id={drive_id}"
    print(f"  Téléchargement : {destination.name}")
    gdown.download(url, str(destination), quiet=False)

    if not destination.exists():
        raise RuntimeError(
            f"Échec du téléchargement de {destination.name} — vérifier l'ID Google Drive."
        )


def main():
    config = load_config()

    vector_dir = get_vector_dir(config)
    raster_dir = get_raster_dir(config)

    subdir_map = {
        "vector": vector_dir,
        "raster": raster_dir,
    }

    files = config["data"]["files"]

    print("=== Vérification et téléchargement des données ===\n")

    all_present = True
    for key, info in files.items():
        dest_dir  = subdir_map[info["subdir"]]
        dest_path = dest_dir / info["filename"]

        if dest_path.exists():
            print(f"  ✓ {info['filename']} (déjà présent)")
        else:
            all_present = False
            print(f"  ✗ {info['filename']} — téléchargement en cours...")
            download_file(info["drive_id"], dest_path)
            print(f"    → Sauvegardé : {dest_path}")

    print()
    if all_present:
        print("Toutes les données sont déjà présentes. Aucun téléchargement nécessaire.")
    else:
        print("Téléchargement terminé. Vérification finale :")
        for key, info in files.items():
            dest_path = subdir_map[info["subdir"]] / info["filename"]
            status = "✓" if dest_path.exists() else "✗ MANQUANT"
            print(f"  {status}  {info['filename']}")

    print("\nDonnées prêtes. Vous pouvez exécuter les scripts des parties 1 à 4.")


if __name__ == "__main__":
    main()
