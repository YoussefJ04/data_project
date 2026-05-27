"""
Page 1 — Vue nationale.

Affiche :
- 4 indicateurs clés (KPIs) en haut de page
- Un histogramme de la distribution des prix au m² sur toute la France
- Une carte scatter géolocalisée de toutes les communes
"""

from __future__ import annotations

from dash import Input, Output, callback, dcc, html

from src.components.charts import create_histogram, create_map
from src.utils.common_functions import compute_national_kpis, load_data
from src.utils.constants import COLORS, REGIONS


def layout() -> html.Div:
    """Retourne le layout de la page nationale.

    Returns:
        Arbre de composants Dash pour la page.
    """
    df = load_data()
    kpis = compute_national_kpis(df)

    # Options du dropdown de filtre par région
    region_options = [{"label": "Toute la France", "value": ""}] + [
        {"label": nom, "value": code}
        for code, nom in sorted(REGIONS.items(), key=lambda x: x[1])
    ]

    return html.Div(
        style={"padding": "1.5rem 2rem", "backgroundColor": COLORS["background"]},
        children=[
            # Titre de page
            html.H1(
                "Marché immobilier français — 2024",
                style={
                    "fontFamily": "'DM Serif Display', serif",
                    "color": COLORS["text"],
                    "fontWeight": "400",
                    "fontSize": "1.8rem",
                    "marginBottom": "0.3rem",
                },
            ),
            html.P(
                "Analyse des prix et volumes de transactions par commune sur toute la France métropolitaine.",
                style={
                    "color": COLORS["text_muted"],
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "0.9rem",
                    "marginBottom": "1.8rem",
                },
            ),

            # KPIs
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(4, 1fr)",
                    "gap": "1rem",
                    "marginBottom": "1.8rem",
                },
                children=[
                    _kpi_card("Prix moyen au m²", f"{kpis['prix_m2_moyen']:,.0f} €", "pondéré par nb transactions"),
                    _kpi_card("Transactions", f"{kpis['nb_transactions']:,}", "mutations enregistrées en 2024"),
                    _kpi_card("Surface moyenne", f"{kpis['surface_moyenne']} m²", "tous types de biens confondus"),
                    _kpi_card("Commune la + chère", kpis["commune_plus_chere"], "prix au m² le plus élevé"),
                ],
            ),

            # Filtre région
            html.Div(
                style={"marginBottom": "1.2rem", "display": "flex", "alignItems": "center", "gap": "1rem"},
                children=[
                    html.Label(
                        "Filtrer par région :",
                        style={"color": COLORS["text_muted"], "fontFamily": "'DM Sans', sans-serif", "fontSize": "0.875rem"},
                    ),
                    dcc.Dropdown(
                        id="dropdown-region-nationale",
                        options=region_options,
                        value="",
                        clearable=False,
                        style={"width": "280px", "backgroundColor": COLORS["surface2"], "color": COLORS["text"]},
                    ),
                ],
            ),

            # Histogramme
            html.Div(
                style={"backgroundColor": COLORS["surface"], "borderRadius": "10px", "padding": "1rem", "marginBottom": "1.2rem", "border": f"1px solid {COLORS['border']}"},
                children=[dcc.Graph(id="graph-histogramme-national", config={"displayModeBar": False})],
            ),

            # Carte
            html.Div(
                style={"backgroundColor": COLORS["surface"], "borderRadius": "10px", "padding": "1rem", "border": f"1px solid {COLORS['border']}"},
                children=[dcc.Graph(id="graph-carte-nationale", config={"displayModeBar": True, "scrollZoom": True})],
            ),
        ],
    )


def _kpi_card(titre: str, valeur: str, sous_titre: str) -> html.Div:
    """Crée une carte KPI.

    Args:
        titre: Libellé de l'indicateur.
        valeur: Valeur principale affichée en grand.
        sous_titre: Description courte sous la valeur.

    Returns:
        Composant Dash de type carte KPI.
    """
    return html.Div(
        style={
            "backgroundColor": COLORS["surface"],
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "10px",
            "padding": "1.2rem 1.4rem",
        },
        children=[
            html.P(titre, style={"color": COLORS["text_muted"], "fontSize": "0.75rem", "fontFamily": "'DM Sans', sans-serif", "marginBottom": "0.3rem", "textTransform": "uppercase", "letterSpacing": "0.06em"}),
            html.P(valeur, style={"color": COLORS["accent"], "fontSize": "1.5rem", "fontFamily": "'DM Serif Display', serif", "fontWeight": "400", "marginBottom": "0.2rem"}),
            html.P(sous_titre, style={"color": COLORS["text_muted"], "fontSize": "0.75rem", "fontFamily": "'DM Sans', sans-serif"}),
        ],
    )



@callback(
    Output("graph-histogramme-national", "figure"),
    Output("graph-carte-nationale", "figure"),
    Input("dropdown-region-nationale", "value"),
)
def update_graphs_national(code_region: str):
    """Met à jour l'histogramme et la carte selon la région sélectionnée.

    Args:
        code_region: Code INSEE de la région sélectionnée, ou chaîne vide
            pour afficher toute la France.

    Returns:
        Tuple (figure histogramme, figure carte).
    """
    df = load_data()

    # Filtrage si une région est sélectionnée
    if code_region:
        df_filtre = df[df["code_region"] == code_region].copy()
        nom_region = REGIONS.get(code_region, code_region)
        titre_hist = f"Distribution des prix au m² — {nom_region}"
        titre_carte = f"Prix au m² par commune — {nom_region}"
    else:
        df_filtre = df
        titre_hist = "Distribution des prix au m² — France entière"
        titre_carte = "Prix au m² par commune — France entière"

    fig_hist = create_histogram(df_filtre, title=titre_hist)
    fig_carte = create_map(df_filtre, title=titre_carte)

    return fig_hist, fig_carte
