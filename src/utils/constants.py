"""
Constantes et mappings utilisés dans l'ensemble du dashboard.

Ce module centralise les libellés des régions françaises (codes INSEE → noms),
les couleurs de la charte graphique, et d'autres constantes partagées entre
les pages et composants.
"""

# Mapping code INSEE région → nom officiel (COG 2024, France métropolitaine)
REGIONS: dict[str, str] = {
    "11": "Île-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d'Azur",
    "94": "Corse",
}

# Charte graphique du dashboard
COLORS = {
    "background": "#0f1117",
    "surface": "#1a1d27",
    "surface2": "#22263a",
    "accent": "#4f8ef7",
    "accent2": "#f7934f",
    "text": "#e8eaf0",
    "text_muted": "#8b91a8",
    "success": "#4fd1a0",
    "border": "#2e3250",
}

# Titre affiché dans le navigateur et la navbar
APP_TITLE = "Immobilier France 2024"
