from __future__ import annotations

import importlib.util
import sys

# Vérification des packages requis avant tout import
_REQUIRED = ["dash", "plotly", "pandas", "requests"]
_MISSING = [pkg for pkg in _REQUIRED if importlib.util.find_spec(pkg) is None]
if _MISSING:
    print(f"[ERREUR] Packages manquants : {', '.join(_MISSING)}")
    print("Installez-les avec : python -m pip install -r requirements.txt")
    sys.exit(1)

import dash
from dash import Input, Output, dcc, html

import config
from src.components.footer import create_footer
from src.components.header import create_header
from src.utils.clean_data import clean_data
from src.utils.common_functions import load_data
from src.utils.constants import COLORS

# Pipeline de données : téléchargement et nettoyage si fichiers absents
if not config.RAW_DVF_FILE.exists() or not config.RAW_COMMUNES_GEO_FILE.exists():
    from src.utils.get_data import get_data
    get_data()

if not config.CLEANED_FILE.exists():
    clean_data()

# Pré-chargement du DataFrame en mémoire
load_data()

# Import des pages AVANT la création de l'app pour enregistrer tous les callbacks
from src.pages import apropos, home, region  # noqa: E402

# Application Dash

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Immobilier France 2024",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap"
    ],
)

app.layout = html.Div(
    style={
        "backgroundColor": COLORS["background"],
        "minHeight": "100vh",
        "fontFamily": "'DM Sans', sans-serif",
    },
    children=[
        dcc.Location(id="url", refresh=False),
        create_header(),
        html.Main(id="page-content", style={"minHeight": "calc(100vh - 120px)"}),
        create_footer(),
    ],
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname: str):
    """Charge le layout de la page correspondant à l'URL.

    Args:
        pathname: Chemin de l'URL courante (ex: "/", "/region", "/apropos").

    Returns:
        Layout Dash de la page correspondante.
    """
    if pathname == "/region":
        return region.layout()
    elif pathname == "/apropos":
        return apropos.layout()
    else:
        return home.layout()


if __name__ == "__main__":
    print("Dashboard démarré sur http://127.0.0.1:8050")
    app.run(debug=False, host="127.0.0.1", port=8050)