

from __future__ import annotations

import config
from src.utils.clean_data import clean_data
from src.utils.get_data import get_data


def main() -> None:
    """Pipeline complet : récupération → nettoyage → (dashboard à venir)."""
    # Étape 1 : récupération des données brutes si absentes
    if not config.RAW_DVF_FILE.exists() or not config.RAW_COMMUNES_GEO_FILE.exists():
        get_data()

    # Étape 2 : nettoyage si nécessaire
    if not config.CLEANED_FILE.exists():
        clean_data()

    print()
    print("✓ Données prêtes.")
    print(f"  Fichier final : {config.CLEANED_FILE}")
    print()


if __name__ == "__main__":
    main()
