"""
Point d'entrée du dashboard.

Lance l'application Dash multi-pages sur http://127.0.0.1:8050.
Si les données sont absentes, elles sont téléchargées et nettoyées
automatiquement avant le démarrage du serveur.

Exécution::

    $ python main.py
"""

from __future__ import annotations

import importlib.util
import sys


def _check_required_packages() -> None:
    """Vérifie que tous les packages requis sont installés.

    Termine le programme avec un message d'erreur si un package manque.
    Cette vérification est faite avant les imports lourds pour éviter
    une traceback Python peu lisible en cas d'environnement incomplet.
    """
    required = ["dash", "plotly", "pandas", "requests"]
    missing = [pkg for pkg in required if importlib.util.find_spec(pkg) is None]
    if missing:
        print(f"[ERREUR] Packages manquants : {', '.join(missing)}")
        print("Installez-les avec : python -m pip install -r requirements.txt")
        sys.exit(1)


_check_required_packages()

# Les imports ci-dessous suivent volontairement la vérification des packages,
# pour donner un message d'erreur clair à l'utilisateur si un package manque.
import dash  # noqa: E402
from dash import Input, Output, dcc, html  # noqa: E402

import config  # noqa: E402
from src.components.footer import create_footer  # noqa: E402
from src.components.header import create_header  # noqa: E402
from src.pages import apropos, home, region  # noqa: E402  (enregistre les callbacks)
from src.utils.clean_data import clean_data  # noqa: E402
from src.utils.common_functions import load_data  # noqa: E402
from src.utils.constants import COLORS  # noqa: E402


def _ensure_data_ready() -> None:
    """Garantit la présence des fichiers de données nécessaires au dashboard.

    Déclenche le téléchargement depuis les sources publiques si les fichiers
    bruts sont absents, puis le nettoyage si le fichier final l'est aussi.
    """
    if not config.RAW_DVF_FILE.exists() or not config.RAW_COMMUNES_GEO_FILE.exists():
        from src.utils.get_data import get_data
        get_data()
    if not config.CLEANED_FILE.exists():
        clean_data()


_ensure_data_ready()

# Pré-chargement du DataFrame en mémoire (cache LRU)
load_data()

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
def display_page(pathname: str) -> html.Div:
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
    return home.layout()


if __name__ == "__main__":
    print("Dashboard démarré sur http://127.0.0.1:8050")
    app.run(debug=False, host="127.0.0.1", port=8050)
