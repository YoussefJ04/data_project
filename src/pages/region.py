"""
Page 2 — Analyse par région.

Affiche pour une région sélectionnée :
- Un histogramme des prix au m²
- Une carte zoomée sur la région
- Un bar chart comparant prix maisons vs appartements par département
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from src.components.charts import create_histogram, create_map
from src.utils.common_functions import load_data
from src.utils.constants import COLORS, REGIONS

# Région affichée par défaut au chargement de la page
DEFAULT_REGION = "11"


def layout() -> html.Div:
    """Retourne le layout de la page d'analyse par région.

    Returns:
        Arbre de composants Dash pour la page.
    """
    region_options = [
        {"label": nom, "value": code}
        for code, nom in sorted(REGIONS.items(), key=lambda x: x[1])
    ]

    return html.Div(
        style={"padding": "1.5rem 2rem", "backgroundColor": COLORS["background"]},
        children=[
            html.H1(
                "Analyse par région",
                style={
                    "fontFamily": "'DM Serif Display', serif",
                    "color": COLORS["text"],
                    "fontWeight": "400",
                    "fontSize": "1.8rem",
                    "marginBottom": "0.3rem",
                },
            ),
            html.P(
                "Sélectionnez une région pour explorer la distribution des prix et la répartition maisons / appartements.",
                style={
                    "color": COLORS["text_muted"],
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "0.9rem",
                    "marginBottom": "1.8rem",
                },
            ),

            # Sélecteur de région
            html.Div(
                style={"marginBottom": "1.5rem", "display": "flex", "alignItems": "center", "gap": "1rem"},
                children=[
                    html.Label(
                        "Région :",
                        style={"color": COLORS["text_muted"], "fontFamily": "'DM Sans', sans-serif", "fontSize": "0.875rem"},
                    ),
                    dcc.Dropdown(
                        id="dropdown-region-page2",
                        options=region_options,
                        value=DEFAULT_REGION,
                        clearable=False,
                        style={"width": "320px", "backgroundColor": COLORS["surface2"], "color": COLORS["text"]},
                    ),
                ],
            ),

            # KPIs région
            html.Div(id="kpis-region", style={"marginBottom": "1.5rem"}),

            # Ligne : histogramme + bar chart maisons/apparts
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem", "marginBottom": "1.2rem"},
                children=[
                    html.Div(
                        style={"backgroundColor": COLORS["surface"], "borderRadius": "10px", "padding": "1rem", "border": f"1px solid {COLORS['border']}"},
                        children=[dcc.Graph(id="graph-histogramme-region", config={"displayModeBar": False})],
                    ),
                    html.Div(
                        style={"backgroundColor": COLORS["surface"], "borderRadius": "10px", "padding": "1rem", "border": f"1px solid {COLORS['border']}"},
                        children=[dcc.Graph(id="graph-barchart-region", config={"displayModeBar": False})],
                    ),
                ],
            ),

            # Carte de la région
            html.Div(
                style={"backgroundColor": COLORS["surface"], "borderRadius": "10px", "padding": "1rem", "border": f"1px solid {COLORS['border']}"},
                children=[dcc.Graph(id="graph-carte-region", config={"displayModeBar": True, "scrollZoom": True})],
            ),
        ],
    )


def _create_barchart_maisons_apparts(df: pd.DataFrame, nom_region: str) -> go.Figure:
    """Crée un bar chart comparant le prix moyen maisons vs appartements par département.

    Args:
        df: DataFrame filtré sur la région.
        nom_region: Nom affiché dans le titre.

    Returns:
        Figure Plotly.
    """
    # Agrégation par département : prix moyen pondéré pour maisons et appartements.
    # On calcule numérateur (prix * nb) et dénominateur (nb) puis on divise pour
    # obtenir une moyenne pondérée par département, sans dépendre du groupby.apply
    # qui a un comportement instable selon la version de pandas.
    df_calc = df.copy()
    df_calc["prix_x_maisons"] = df_calc["prix_moyen"] * df_calc["nb_maisons"]
    df_calc["prix_x_apparts"] = df_calc["prix_moyen"] * df_calc["nb_appartements"]

    agg = df_calc.groupby("code_departement", as_index=False).agg(
        prix_x_maisons_sum=("prix_x_maisons", "sum"),
        nb_maisons_sum=("nb_maisons", "sum"),
        prix_x_apparts_sum=("prix_x_apparts", "sum"),
        nb_apparts_sum=("nb_appartements", "sum"),
    )

    # Calcul des moyennes pondérées (NaN si le département n'a aucun bien du type)
    agg["prix_moyen_maison"] = agg["prix_x_maisons_sum"].where(
        agg["nb_maisons_sum"] > 0
    ) / agg["nb_maisons_sum"].where(agg["nb_maisons_sum"] > 0)
    agg["prix_moyen_appart"] = agg["prix_x_apparts_sum"].where(
        agg["nb_apparts_sum"] > 0
    ) / agg["nb_apparts_sum"].where(agg["nb_apparts_sum"] > 0)

    dept = agg[["code_departement", "prix_moyen_maison", "prix_moyen_appart"]].sort_values(
        "code_departement"
    )

    fig = go.Figure()

    if not dept.empty:
        fig.add_trace(go.Bar(
            name="Maisons",
            x=dept["code_departement"],
            y=dept["prix_moyen_maison"],
            marker_color=COLORS["accent"],
            hovertemplate="Dépt %{x}<br>Maisons : %{y:,.0f} €<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name="Appartements",
            x=dept["code_departement"],
            y=dept["prix_moyen_appart"],
            marker_color=COLORS["accent2"],
            hovertemplate="Dépt %{x}<br>Apparts : %{y:,.0f} €<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        title={"text": f"Prix moyen par type — {nom_region}", "font": {"size": 14, "color": COLORS["text"]}, "x": 0.01},
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface2"],
        font={"color": COLORS["text"], "family": "'DM Sans', sans-serif"},
        xaxis={"title": "Département", "gridcolor": COLORS["border"], "color": COLORS["text_muted"]},
        yaxis={"title": "Prix moyen (€)", "gridcolor": COLORS["border"], "color": COLORS["text_muted"]},
        legend={"font": {"color": COLORS["text_muted"]}},
        margin={"r": 20, "t": 45, "l": 70, "b": 50},
        height=380,
    )
    return fig


# --- Callbacks ---------------------------------------------------------------

@callback(
    Output("kpis-region", "children"),
    Output("graph-histogramme-region", "figure"),
    Output("graph-barchart-region", "figure"),
    Output("graph-carte-region", "figure"),
    Input("dropdown-region-page2", "value"),
)
def update_page_region(code_region: str):
    """Met à jour tous les graphiques et KPIs pour la région sélectionnée.

    Args:
        code_region: Code INSEE de la région choisie dans le dropdown.

    Returns:
        Tuple (composant KPIs, fig histogramme, fig barchart, fig carte).
    """
    df = load_data()
    df_region = df[df["code_region"] == code_region].copy()
    nom_region = REGIONS.get(code_region, code_region)

    # KPIs de la région
    if df_region.empty:
        kpis_div = html.P("Aucune donnée pour cette région.", style={"color": COLORS["text_muted"]})
    else:
        prix_med = df_region["prix_m2_moyen"].median()
        nb_communes = len(df_region)
        nb_mutations = int(df_region["nb_mutations"].sum())
        prix_max = df_region["prix_m2_moyen"].max()

        kpis_div = html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "1rem"},
            children=[
                _kpi_card("Prix médian / m²", f"{prix_med:,.0f} €", nom_region),
                _kpi_card("Communes analysées", f"{nb_communes:,}", "avec au moins 1 transaction"),
                _kpi_card("Transactions", f"{nb_mutations:,}", "en 2024 dans la région"),
                _kpi_card("Prix max / m²", f"{prix_max:,.0f} €", "commune la plus chère"),
            ],
        )

    # Zoom de la carte sur la région
    lat_centre = df_region["latitude"].mean() if not df_region.empty else 46.5
    lon_centre = df_region["longitude"].mean() if not df_region.empty else 2.5

    fig_hist = create_histogram(df_region, title=f"Distribution des prix au m² — {nom_region}")
    fig_bar = _create_barchart_maisons_apparts(df_region, nom_region)
    fig_carte = create_map(df_region, title=f"Prix au m² par commune — {nom_region}")

    # Recentrage de la carte sur la région sélectionnée
    fig_carte.update_layout(
        map={
            "center": {"lat": lat_centre, "lon": lon_centre},
            "zoom": 6.5,
        }
    )

    return kpis_div, fig_hist, fig_bar, fig_carte


def _kpi_card(titre: str, valeur: str, sous_titre: str) -> html.Div:
    """Crée une carte KPI pour la page région.

    Args:
        titre: Libellé de l'indicateur.
        valeur: Valeur principale.
        sous_titre: Description courte.

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
            html.P(valeur, style={"color": COLORS["success"], "fontSize": "1.5rem", "fontFamily": "'DM Serif Display', serif", "fontWeight": "400", "marginBottom": "0.2rem"}),
            html.P(sous_titre, style={"color": COLORS["text_muted"], "fontSize": "0.75rem", "fontFamily": "'DM Sans', sans-serif"}),
        ],
    )
