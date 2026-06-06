"""
Composant header partagé entre toutes les pages du dashboard.

Affiche le titre de l'application et une barre de navigation avec
les liens vers les différentes pages.
"""

from dash import html

from src.utils.constants import APP_TITLE, COLORS


def create_header() -> html.Div:
    """Crée le header avec navbar.

    Returns:
        Composant Dash représentant le header complet.
    """
    return html.Div(
        style={
            "backgroundColor": COLORS["surface"],
            "borderBottom": f"1px solid {COLORS['border']}",
            "padding": "0 2rem",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "height": "60px",
            "position": "sticky",
            "top": "0",
            "zIndex": "100",
        },
        children=[
            # Titre / logo
            html.Div(
                children=[
                    html.Span("🏠 ", style={"fontSize": "1.2rem"}),
                    html.Span(
                        APP_TITLE,
                        style={
                            "fontFamily": "'DM Serif Display', serif",
                            "fontSize": "1.2rem",
                            "color": COLORS["text"],
                            "fontWeight": "400",
                            "letterSpacing": "0.02em",
                        },
                    ),
                ]
            ),
            # Navigation
            html.Nav(
                style={"display": "flex", "gap": "0.5rem"},
                children=[
                    _nav_link("/", "Vue nationale"),
                    _nav_link("/region", "Par région"),
                    _nav_link("/apropos", "À propos"),
                ],
            ),
        ],
    )


def _nav_link(href: str, label: str) -> html.A:
    """Crée un lien de navigation stylisé.

    Args:
        href: URL de destination.
        label: Texte affiché.

    Returns:
        Élément ``<a>`` stylisé.
    """
    return html.A(
        label,
        href=href,
        style={
            "color": COLORS["text_muted"],
            "textDecoration": "none",
            "padding": "0.4rem 0.9rem",
            "borderRadius": "6px",
            "fontSize": "0.875rem",
            "fontFamily": "'DM Sans', sans-serif",
            "transition": "all 0.15s ease",
        },
    )
