"""
Page 3 — À propos.

Présente le contexte du projet, les sources de données utilisées
et la méthodologie de traitement.
"""

from dash import html
from src.utils.constants import COLORS


def layout() -> html.Div:
    """Retourne le layout de la page À propos.

    Returns:
        Arbre de composants Dash pour la page.
    """
    return html.Div(
        style={"padding": "1.5rem 2rem", "maxWidth": "860px", "backgroundColor": COLORS["background"]},
        children=[
            html.H1(
                "À propos du projet",
                style={
                    "fontFamily": "'DM Serif Display', serif",
                    "color": COLORS["text"],
                    "fontWeight": "400",
                    "fontSize": "1.8rem",
                    "marginBottom": "1.5rem",
                },
            ),

            _section(
                "Contexte",
                "Ce dashboard a été réalisé dans le cadre du cours Python 2 — Manipulation de données "
                "(E4-DSIA, ESIEE Paris, année 2024–2025). L'objectif est d'éclairer un sujet d'intérêt "
                "public à partir de données open data : ici, le marché immobilier résidentiel français "
                "en 2024, à l'échelle de la commune.",
            ),

            _section(
                "Sources de données",
                None,
                children=[
                    _source_item(
                        "Indicateurs Immobiliers par commune (2014–2024)",
                        "https://www.data.gouv.fr/datasets/indicateurs-immobiliers-par-commune-et-par-annee-prix-et-volumes-sur-la-periode-2014-2024",
                        "Producteur : Boris Mericskay · data.gouv.fr · Licence ODbL. "
                        "Données dérivées de la base DVF géolocalisée (DGFiP) : mutations monoventes, "
                        "prix entre 15 000 € et 10 000 000 €, surfaces filtrées.",
                    ),
                    _source_item(
                        "API Découpage administratif",
                        "https://geo.api.gouv.fr/",
                        "Etalab · sans clé d'API. Utilisée pour récupérer les coordonnées géographiques "
                        "(centroïde latitude/longitude) de chaque commune à partir de son code INSEE.",
                    ),
                ],
            ),

            _section(
                "Méthodologie",
                "Le pipeline de données suit deux étapes : "
                "(1) get_data.py télécharge les fichiers bruts depuis les sources publiques et les stocke dans data/raw/ ; "
                "(2) clean_data.py joint les deux sources sur le code INSEE, supprime les valeurs aberrantes "
                "(prix au m² hors bornes 330–15 000 €/m², surfaces hors 10–400 m²) et produit le fichier "
                "final dans data/cleaned/. Ce fichier est chargé une seule fois en mémoire au démarrage "
                "du dashboard (cache LRU), garantissant des callbacks fluides.",
            ),

            _section(
                "Technologies",
                "Python 3.13 · pandas 2.2 · Dash · Plotly · requests. "
                "Développé sous Windows, testé avec Python 3.12+.",
            ),
        ],
    )


def _section(titre: str, texte: str | None, children: list | None = None) -> html.Div:
    """Crée une section de contenu avec titre et paragraphe.

    Args:
        titre: Titre de la section.
        texte: Paragraphe de texte (optionnel si ``children`` fourni).
        children: Composants enfants optionnels (pour les listes de sources).

    Returns:
        Composant Dash de type section.
    """
    content = []
    if texte:
        content.append(
            html.P(
                texte,
                style={
                    "color": COLORS["text"],
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "0.95rem",
                    "lineHeight": "1.7",
                },
            )
        )
    if children:
        content.extend(children)

    return html.Div(
        style={"marginBottom": "2rem"},
        children=[
            html.H2(
                titre,
                style={
                    "fontFamily": "'DM Serif Display', serif",
                    "color": COLORS["accent"],
                    "fontWeight": "400",
                    "fontSize": "1.2rem",
                    "marginBottom": "0.7rem",
                    "borderBottom": f"1px solid {COLORS['border']}",
                    "paddingBottom": "0.4rem",
                },
            ),
            *content,
        ],
    )


def _source_item(titre: str, url: str, description: str) -> html.Div:
    """Crée un élément de source de données avec lien.

    Args:
        titre: Nom de la source.
        url: URL de la source.
        description: Description courte.

    Returns:
        Composant Dash de type item source.
    """
    return html.Div(
        style={
            "backgroundColor": COLORS["surface"],
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "8px",
            "padding": "1rem 1.2rem",
            "marginBottom": "0.8rem",
        },
        children=[
            html.A(
                titre,
                href=url,
                target="_blank",
                style={
                    "color": COLORS["accent"],
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "0.95rem",
                    "fontWeight": "600",
                    "textDecoration": "none",
                },
            ),
            html.P(
                description,
                style={
                    "color": COLORS["text_muted"],
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "0.85rem",
                    "marginTop": "0.4rem",
                    "lineHeight": "1.6",
                },
            ),
        ],
    )
