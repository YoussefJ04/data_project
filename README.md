# Projet Data — Marché immobilier français 2024

Dashboard d'analyse du marché immobilier résidentiel français à l'échelle communale, basé sur les données DVF (Demandes de Valeurs Foncières) agrégées pour l'année 2024.

## User Guide

### Installation

```bash
git clone <url_du_repo>
cd Python2
python -m venv .venv
source .venv/bin/activate         # Linux / macOS
# ou : .venv\Scripts\activate     # Windows
python -m pip install -r requirements.txt
```

### Lancement

```bash
python main.py
```

Au premier lancement, le programme télécharge automatiquement les données depuis les sources publiques (cf. section *Data*) et les place dans `data/raw/`, puis génère le fichier nettoyé dans `data/cleaned/`. Les lancements suivants utilisent les fichiers locaux : le dashboard est donc utilisable sans connexion internet une fois les données récupérées.

## Data

### Source principale

[**Indicateurs Immobiliers par commune et par année (2014-2024)**](https://www.data.gouv.fr/datasets/indicateurs-immobiliers-par-commune-et-par-annee-prix-et-volumes-sur-la-periode-2014-2024) — data.gouv.fr

- **Producteur** : Boris Mericskay
- **Licence** : Open Database License (ODbL)
- **Méthodologie détaillée** : [journals.openedition.org/cybergeo/39583](https://journals.openedition.org/cybergeo/39583)
- **Format** : CSV agrégé par commune et par année
- **Variables** : nombre de mutations, ventes maisons/appartements, prix moyen, prix au m², surface moyenne

### Source géographique

[**API Découpage administratif**](https://geo.api.gouv.fr/) — Etalab (sans clé d'API requise)

Utilisée pour récupérer le centroïde (latitude/longitude), le département, la région et la population de chaque commune française à partir de son code INSEE.

### Pipeline de données

| Étape | Script | Sortie |
|-------|--------|--------|
| Récupération | `src/utils/get_data.py` | `data/raw/indicateurs_dvf_communes_2024.csv` + `data/raw/communes_geo.csv` |
| Nettoyage | `src/utils/clean_data.py` | `data/cleaned/dvf_communes_geo_2024.csv` |

Les URLs des sources et les chemins sont centralisés dans `config.py`.

## Developer Guide

*Section à compléter ultérieurement avec le diagramme Mermaid de l'architecture et les instructions pour ajouter une page ou un graphique au dashboard.*

## Rapport d'analyse

*Section à compléter ultérieurement avec les principales conclusions extraites des données.*

## Copyright

Nous déclarons sur l'honneur que le code fourni a été produit par nous-mêmes, à l'exception des lignes qui seraient mentionnées explicitement ci-dessous.

Toute ligne non déclarée ci-dessus est réputée être produite par les auteurs du projet. L'absence ou l'omission de déclaration sera considérée comme du plagiat.