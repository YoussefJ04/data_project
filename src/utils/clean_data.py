"""
Nettoyage et préparation des données brutes pour le dashboard.

Étapes :
1. Charger le CSV DVF brut (data/raw/).
2. Charger le CSV des coordonnées de communes (data/raw/).
3. Jointure sur le code INSEE.
4. Filtrage des valeurs aberrantes (cohérent avec la méthodologie du producteur).
5. Renommage des colonnes pour homogénéité (snake_case).
6. Export final dans data/cleaned/ (format exploitable par le dashboard).

Exécution directe::

    $ python -m src.utils.clean_data
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Import du fichier de configuration situé à la racine du projet.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import config  # noqa: E402


def load_raw_dvf() -> pd.DataFrame:
    """Charge le CSV DVF brut en forçant le code INSEE en string.

    Le code INSEE doit rester une chaîne car certains codes commencent par
    un zéro (ex: "01001") qui serait perdu en conversion numérique.
    """
    if not config.RAW_DVF_FILE.exists():
        raise FileNotFoundError(
            f"Fichier DVF brut introuvable: {config.RAW_DVF_FILE}.\n"
            f"Exécutez d'abord `python -m src.utils.get_data`."
        )
    return pd.read_csv(config.RAW_DVF_FILE, dtype={"INSEE_COM": str})


def load_raw_geo() -> pd.DataFrame:
    """Charge le CSV des coordonnées des communes."""
    if not config.RAW_COMMUNES_GEO_FILE.exists():
        raise FileNotFoundError(
            f"Fichier géo brut introuvable: {config.RAW_COMMUNES_GEO_FILE}.\n"
            f"Exécutez d'abord `python -m src.utils.get_data`."
        )
    return pd.read_csv(config.RAW_COMMUNES_GEO_FILE, dtype={"code_insee": str})


def clean_data() -> Path:
    """Pipeline complet de nettoyage et jointure.

    Returns:
        Chemin du CSV nettoyé prêt pour le dashboard.
    """
    print("=" * 60)
    print("Nettoyage des données")
    print("=" * 60)

    df_dvf = load_raw_dvf()
    df_geo = load_raw_geo()
    print(f"  DVF brut       : {len(df_dvf):>6} lignes")
    print(f"  Communes géo   : {len(df_geo):>6} lignes")

    # 1. Suppression des lignes avec INSEE_COM nul (un cas constaté dans le brut)
    n_before = len(df_dvf)
    df_dvf = df_dvf.dropna(subset=["INSEE_COM"]).copy()
    print(f"  → drop INSEE_COM null : {n_before - len(df_dvf)} ligne(s) supprimée(s)")

    # 2. Renommage en snake_case pour homogénéité avec le reste du code
    df_dvf = df_dvf.rename(
        columns={
            "INSEE_COM": "code_insee",
            "annee": "annee",
            "nb_mutations": "nb_mutations",
            "NbMaisons": "nb_maisons",
            "NbApparts": "nb_appartements",
            "PropMaison": "prop_maison",
            "PropAppart": "prop_appartement",
            "PrixMoyen": "prix_moyen",
            "Prixm2Moyen": "prix_m2_moyen",
            "SurfaceMoy": "surface_moyenne",
        }
    )

    # 3. Filtrage des valeurs aberrantes (sécurité — la source applique déjà
    # ces bornes, mais on les ré-applique pour être robuste à un changement
    # de source future).
    mask = (
        df_dvf["prix_m2_moyen"].between(config.PRIX_M2_MIN, config.PRIX_M2_MAX)
        & df_dvf["surface_moyenne"].between(config.SURFACE_MIN, config.SURFACE_MAX)
    )
    n_before = len(df_dvf)
    df_dvf = df_dvf[mask].copy()
    print(
        f"  → filtre bornes prix/m² et surface : "
        f"{n_before - len(df_dvf)} ligne(s) supprimée(s)"
    )

    # 4. Jointure avec les coordonnées (left join : on garde toutes les communes
    # de DVF, certaines peuvent ne pas matcher si codes INSEE désuets).
    df = df_dvf.merge(df_geo, on="code_insee", how="left")
    n_no_geo = df["latitude"].isna().sum()
    print(f"  → jointure géo : {n_no_geo} commune(s) sans coordonnées")

    # 5. On supprime les lignes sans géoloc (impossible de les mettre sur la carte)
    df = df.dropna(subset=["latitude", "longitude"]).copy()

    # 6. Colonnes finales ordonnées (lisibilité)
    cols = [
        "code_insee",
        "nom_commune",
        "code_departement",
        "code_region",
        "annee",
        "nb_mutations",
        "nb_maisons",
        "nb_appartements",
        "prop_maison",
        "prop_appartement",
        "prix_moyen",
        "prix_m2_moyen",
        "surface_moyenne",
        "population",
        "latitude",
        "longitude",
    ]
    df = df[cols]

    # 7. Export
    config.CLEANED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.CLEANED_FILE, index=False, encoding="utf-8")

    size_kb = config.CLEANED_FILE.stat().st_size / 1024
    print(f"  ✓ {config.CLEANED_FILE.name} ({len(df)} lignes, {size_kb:.1f} Ko)")
    print("=" * 60)
    return config.CLEANED_FILE


if __name__ == "__main__":
    clean_data()
