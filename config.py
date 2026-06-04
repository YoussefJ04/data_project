"""
Fichier de configuration central du projet.

Centralise les URLs des sources de données, les chemins du système de fichiers,
et les constantes métier. Importé par les autres modules pour éviter la
duplication de chaînes "magiques" dans le code.
"""

from pathlib import Path

# Chemins du projet
# On utilise pathlib + résolution relative à ce fichier pour que les chemins
# fonctionnent quel que soit le répertoire d'exécution.

PROJECT_ROOT: Path = Path(__file__).resolve().parent

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
CLEANED_DATA_DIR: Path = DATA_DIR / "cleaned"
IMAGES_DIR: Path = PROJECT_ROOT / "images"

# Fichiers spécifiques
RAW_DVF_FILE: Path = RAW_DATA_DIR / "indicateurs_dvf_communes_2024.csv"
RAW_COMMUNES_GEO_FILE: Path = RAW_DATA_DIR / "communes_geo.csv"
CLEANED_FILE: Path = CLEANED_DATA_DIR / "dvf_communes_geo_2024.csv"

# URLs des sources de données
# Source principale : data.gouv.fr (licence ODbL)
# Dataset "Indicateurs Immobiliers par commune et par année (2014-2024)"
# Producteur : Boris Mericskay
# Page : https://www.data.gouv.fr/datasets/indicateurs-immobiliers-par-commune-et-par-annee-prix-et-volumes-sur-la-periode-2014-2024
DVF_2024_URL: str = (
    "https://www.data.gouv.fr/api/1/datasets/r/1b85be7c-17ce-42dc-b191-3b8f3c469087"
)

# Source géolocalisation : API publique geo.api.gouv.fr (sans clé, Etalab)
# On récupère le centre (lat/lon) de chaque commune par code INSEE
COMMUNES_GEO_URL: str = (
    "https://geo.api.gouv.fr/communes"
    "?fields=code,nom,centre,codeDepartement,codeRegion,population"
    "&format=json"
    "&geometry=centre"
)

# sParamètres réseau
REQUEST_TIMEOUT_SECONDS: int = 60
HTTP_USER_AGENT: str = "ESIEE-E4FD-DataProject/1.0 (academic use)"

# Paramètres de nettoyage
# Bornes de filtrage (cohérentes avec la méthodologie du producteur de la base)
PRIX_M2_MIN: int = 330       # €/m²
PRIX_M2_MAX: int = 15_000    # €/m²
SURFACE_MIN: int = 10        # m²
SURFACE_MAX: int = 400       # m²
