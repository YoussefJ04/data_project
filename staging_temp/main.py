"""
Point d'entrée du dashboard.

Pour l'instant ce fichier est un placeholder du Bloc 1 : il vérifie que
les données sont disponibles et les télécharge/nettoie sinon. Au Bloc 2,
il lancera l'application Dash.

Exécution::

    $ python main.py
"""

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
    print("[TODO Bloc 2] Lancer le dashboard Dash ici.")


if __name__ == "__main__":
    main()
