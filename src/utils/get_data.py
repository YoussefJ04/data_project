"""
Récupération des données brutes depuis les sources publiques.

Ce script télécharge :
1. Le CSV "Indicateurs Immobiliers par commune 2024" depuis data.gouv.fr
   (jeu de données de Boris Mericskay, licence ODbL).
2. Les coordonnées géographiques (centroïdes) de toutes les communes
   françaises depuis l'API publique geo.api.gouv.fr (Etalab).

Les fichiers récupérés sont stockés bruts (sans transformation) dans
``data/raw/`` conformément à la consigne du projet.

Si les fichiers existent déjà, ils ne sont
pas re-téléchargés (sauf si ``force=True``).

Exécution directe::

    $ python -m src.utils.get_data
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import requests

# Import du fichier de configuration situé à la racine du projet.
# On ajoute la racine au sys.path pour permettre l'exécution directe du module.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import config  # noqa: E402  (import placé après ajustement de sys.path)


def _download_file(url: str, destination: Path, *, force: bool = False) -> Path:
    """Télécharge un fichier depuis ``url`` et l'écrit dans ``destination``.

    Args:
        url: URL HTTP(S) du fichier à télécharger.
        destination: Chemin local où sauvegarder le contenu téléchargé.
        force: Si ``True``, re-télécharge même si le fichier existe déjà.

    Returns:
        Le chemin du fichier téléchargé (identique à ``destination``).

    Raises:
        requests.HTTPError: En cas de réponse HTTP non-2xx.
    """
    # On évite le téléchargement si déjà présent localement,
    if destination.exists() and not force:
        print(f"  [skip] {destination.name} déjà présent.")
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"  [GET]  {url}")
    headers = {"User-Agent": config.HTTP_USER_AGENT}
    try:
        response = requests.get(
            url, headers=headers, timeout=config.REQUEST_TIMEOUT_SECONDS, stream=True
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Impossible de joindre {url} : vérifiez votre connexion internet."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"Délai dépassé en téléchargeant {url} "
            f"(>{config.REQUEST_TIMEOUT_SECONDS}s)."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Échec HTTP {response.status_code} lors du téléchargement de {url}."
        ) from exc

    # Écriture en streaming pour ne pas saturer la RAM sur des gros fichiers.
    # Si l'écriture échoue à mi-chemin, on supprime le fichier partiel
    # pour ne pas laisser de données corrompues qui bloqueraient le pipeline.
    try:
        with destination.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    fh.write(chunk)
    except OSError:
        if destination.exists():
            destination.unlink()
        raise

    size_kb = destination.stat().st_size / 1024
    print(f"  [ok]   {destination.name} ({size_kb:.1f} Ko)")
    return destination


def fetch_dvf(force: bool = False) -> Path:
    """Télécharge le CSV des indicateurs DVF 2024 depuis data.gouv.fr.

    Args:
        force: Force le re-téléchargement si ``True``.

    Returns:
        Chemin local du fichier CSV brut.
    """
    print("→ Téléchargement des indicateurs DVF par commune (2024)")
    return _download_file(
        config.DVF_2024_URL, config.RAW_DVF_FILE, force=force
    )


def fetch_communes_geo(force: bool = False) -> Path:
    """Télécharge les coordonnées géographiques de toutes les communes françaises.

    Utilise l'API publique geo.api.gouv.fr, qui retourne du JSON. On normalise
    ensuite en CSV pour homogénéiser le format des fichiers ``raw``.

    Args:
        force: Force le re-téléchargement si ``True``.

    Returns:
        Chemin local du CSV des communes géolocalisées.
    """
    print("→ Téléchargement des coordonnées des communes (geo.api.gouv.fr)")

    if config.RAW_COMMUNES_GEO_FILE.exists() and not force:
        print(f"  [skip] {config.RAW_COMMUNES_GEO_FILE.name} déjà présent.")
        return config.RAW_COMMUNES_GEO_FILE

    config.RAW_COMMUNES_GEO_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"  [GET]  {config.COMMUNES_GEO_URL}")
    headers = {"User-Agent": config.HTTP_USER_AGENT}
    response = requests.get(
        config.COMMUNES_GEO_URL,
        headers=headers,
        timeout=config.REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    communes = response.json()

    # Aplatir la structure {code, nom, centre: {coordinates: [lon, lat]}, ...}
    # en DataFrame tabulaire exploitable.
    records = []
    for c in communes:
        centre = c.get("centre") or {}
        coords = centre.get("coordinates") or [None, None]
        records.append(
            {
                "code_insee": c.get("code"),
                "nom_commune": c.get("nom"),
                "code_departement": c.get("codeDepartement"),
                "code_region": c.get("codeRegion"),
                "population": c.get("population"),
                "longitude": coords[0],
                "latitude": coords[1],
            }
        )

    df = pd.DataFrame.from_records(records)
    df.to_csv(config.RAW_COMMUNES_GEO_FILE, index=False, encoding="utf-8")

    size_kb = config.RAW_COMMUNES_GEO_FILE.stat().st_size / 1024
    print(
        f"  [ok]   {config.RAW_COMMUNES_GEO_FILE.name} "
        f"({len(df)} communes, {size_kb:.1f} Ko)"
    )
    return config.RAW_COMMUNES_GEO_FILE


def get_data(force: bool = False) -> tuple[Path, Path]:
    """Point d'entrée principal : récupère toutes les données brutes du projet.

    Args:
        force: Force le re-téléchargement de tous les fichiers si ``True``.

    Returns:
        Tuple (chemin DVF, chemin coordonnées communes).
    """
    print("=" * 60)
    print("Récupération des données brutes")
    print("=" * 60)
    dvf_path = fetch_dvf(force=force)
    geo_path = fetch_communes_geo(force=force)
    print("=" * 60)
    print("✓ Données brutes disponibles dans data/raw/")
    return dvf_path, geo_path


if __name__ == "__main__":
    get_data()
