"""
Composant footer partagé entre toutes les pages du dashboard.

Affiche les informations sur les sources de données et les auteurs.
"""

from dash import html

from src.utils.constants import COLORS


def create_footer() -> html.Div:
    """Crée le footer.

    Returns:
        Composant Dash représentant le footer.
    """
    return html.Footer(
        style={
            "backgroundColor": COLORS["surface"],
            "borderTop": f"1px solid {COLORS['border']}",
            "padding": "1.5rem 2rem",
            "marginTop": "3rem",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
            "flexWrap": "wrap",
            "gap": "0.5rem",
        },
        children=[
            html.Span(
                "Données : DVF — data.gouv.fr (Boris Mericskay) · Licence ODbL",
                style={
                    "color": COLORS["text_muted"],
                    "fontSize": "0.8rem",
                    "fontFamily": "'DM Sans', sans-serif",
                },
            ),
            html.Span(
                "Projet Data ESIEE Paris — E4-FD · 2025-2026",
                style={
                    "color": COLORS["text_muted"],
                    "fontSize": "0.8rem",
                    "fontFamily": "'DM Sans', sans-serif",
                },
            ),
        ],
    )
