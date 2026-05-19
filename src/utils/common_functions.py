"""
Fonctions utilitaires partagées entre les pages du dashboard.

Ce module fournit le chargement en mémoire du CSV nettoyé (avec mise en cache
via ``@lru_cache``) et les fonctions de filtrage/agrégation réutilisables.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import config 
from src.utils.constants import REGIONS


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Charge le CSV nettoyé en mémoire et le met en cache.

    Le cache ``lru_cache`` garantit que le fichier n'est lu qu'une seule fois
    pendant toute la durée de vie du processus Dash, évitant des I/O répétées
    à chaque callback.

    Returns:
        DataFrame avec toutes les colonnes du fichier nettoyé.

    Raises:
        FileNotFoundError: Si le CSV nettoyé est absent (pipeline non exécuté).
    """
    if not config.CLEANED_FILE.exists():
        raise FileNotFoundError(
            f"Fichier nettoyé introuvable : {config.CLEANED_FILE}\n"
            "Lancez d'abord : python main.py"
        )
    df = pd.read_csv(
        config.CLEANED_FILE,
        dtype={
            "code_insee": str,
            "code_departement": str,
            "code_region": str,
        },
    )
    # Ajout du nom de région pour les affichages lisibles
    df["nom_region"] = df["code_region"].map(REGIONS).fillna("Autre")
    return df


def filter_by_region(df: pd.DataFrame, code_region: str | None) -> pd.DataFrame:
    """Filtre le DataFrame par code région.

    Args:
        df: DataFrame complet chargé par ``load_data()``.
        code_region: Code INSEE de la région (ex: "11"). Si ``None`` ou vide,
            retourne le DataFrame complet.

    Returns:
        Sous-ensemble du DataFrame correspondant à la région.
    """
    if not code_region:
        return df
    return df[df["code_region"] == code_region].copy()


def compute_national_kpis(df: pd.DataFrame) -> dict[str, float | str]:
    """Calcule les indicateurs clés nationaux affichés en haut de la page principale.

    Args:
        df: DataFrame complet.

    Returns:
        Dictionnaire avec les KPIs : prix_m2_moyen, nb_transactions,
        surface_moyenne, commune_plus_chere.
    """
    # Prix moyen pondéré par le nombre de mutations pour éviter le biais
    # des petites communes avec peu de transactions.
    prix_pondere = (
        (df["prix_m2_moyen"] * df["nb_mutations"]).sum() / df["nb_mutations"].sum()
    )
    commune_chere = df.loc[df["prix_m2_moyen"].idxmax(), "nom_commune"]
    return {
        "prix_m2_moyen": round(prix_pondere, 0),
        "nb_transactions": int(df["nb_mutations"].sum()),
        "surface_moyenne": round(df["surface_moyenne"].mean(), 1),
        "commune_plus_chere": commune_chere,
    }
