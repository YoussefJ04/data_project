"""
Composants graphiques réutilisables du dashboard.

Ce module fournit deux fonctions de construction de figures Plotly :
- ``create_histogram`` : distribution des prix au m².
- ``create_map`` : carte scatter des communes colorées par prix au m².

Les figures retournées sont prêtes à être affectées à la propriété
``figure`` d'un ``dcc.Graph``.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.constants import COLORS


def create_map(df: pd.DataFrame, title: str = "Prix au m² par commune") -> go.Figure:
    """Crée une carte scatter géolocalisée des communes.

    Args:
        df: DataFrame filtré contenant les colonnes ``latitude``,
            ``longitude``, ``prix_m2_moyen``, ``nom_commune``,
            ``nb_mutations``, ``surface_moyenne``.
        title: Titre affiché au-dessus du graphique.

    Returns:
        Figure Plotly prête à être passée à un ``dcc.Graph``.
    """
    # Cas limite : DataFrame vide → on retourne une figure avec message
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font={"color": COLORS["text_muted"], "size": 14},
        )
        fig.update_layout(
            paper_bgcolor=COLORS["surface"], plot_bgcolor=COLORS["surface"],
            height=480, margin={"r": 0, "t": 45, "l": 0, "b": 0},
        )
        return fig

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="prix_m2_moyen",
        size="nb_mutations",
        size_max=18,
        hover_name="nom_commune",
        hover_data={
            "prix_m2_moyen": ":,.0f",
            "nb_mutations": True,
            "surface_moyenne": ":.0f",
            "latitude": False,
            "longitude": False,
        },
        color_continuous_scale=[
            [0.0, "#2d6a9f"],
            [0.3, "#4f8ef7"],
            [0.6, "#f7c34f"],
            [1.0, "#e84545"],
        ],
        zoom=4.8,
        center={"lat": 46.5, "lon": 2.5},
        mapbox_style="carto-darkmatter",
        title=title,
        labels={
            "prix_m2_moyen": "Prix/m² (€)",
            "nb_mutations": "Nb transactions",
            "surface_moyenne": "Surface moy. (m²)",
        },
    )

    fig.update_layout(
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font={"color": COLORS["text"], "family": "'DM Sans', sans-serif"},
        title={"font": {"size": 15, "color": COLORS["text"]}, "x": 0.01},
        coloraxis_colorbar={
            "title": "€/m²",
            "title_font": {"color": COLORS["text_muted"]},
            "tickfont": {"color": COLORS["text_muted"]},
            "bgcolor": COLORS["surface2"],
            "bordercolor": COLORS["border"],
        },
        margin={"r": 0, "t": 45, "l": 0, "b": 0},
        height=480,
    )
    return fig


def create_histogram(
    df: pd.DataFrame,
    title: str = "Distribution des prix au m²",
    nbins: int = 60,
) -> go.Figure:
    """Crée un histogramme de distribution des prix au m².

    Args:
        df: DataFrame filtré contenant la colonne ``prix_m2_moyen``.
        title: Titre du graphique.
        nbins: Nombre de barres de l'histogramme.

    Returns:
        Figure Plotly.
    """
    fig = go.Figure()

    # Cas limite : DataFrame vide → message d'absence
    if df.empty or df["prix_m2_moyen"].dropna().empty:
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font={"color": COLORS["text_muted"], "size": 14},
        )
    else:
        values = df["prix_m2_moyen"].dropna().tolist()
        fig.add_trace(go.Histogram(
            x=values,
            nbinsx=nbins,
            marker={"color": COLORS["accent"], "line": {"color": COLORS["border"], "width": 0.5}},
            hovertemplate="Prix au m² : %{x:,.0f} €<br>Nb communes : %{y}<extra></extra>",
            name="Communes",
        ))

        # Ligne verticale : médiane
        mediane = float(df["prix_m2_moyen"].median())
        fig.add_vline(
            x=mediane,
            line_dash="dash",
            line_color=COLORS["accent2"],
            annotation_text=f"Médiane : {mediane:,.0f} €/m²",
            annotation_position="top right",
            annotation_font_color=COLORS["accent2"],
        )

    fig.update_layout(
        title={"text": title, "font": {"size": 15, "color": COLORS["text"]}, "x": 0.01},
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface2"],
        font={"color": COLORS["text"], "family": "'DM Sans', sans-serif"},
        xaxis={
            "title": "Prix moyen au m² (€)",
            "gridcolor": COLORS["border"],
            "color": COLORS["text_muted"],
        },
        yaxis={
            "title": "Nombre de communes",
            "gridcolor": COLORS["border"],
            "color": COLORS["text_muted"],
        },
        bargap=0.05,
        margin={"r": 20, "t": 45, "l": 60, "b": 50},
        height=380,
        showlegend=False,
    )
    return fig
