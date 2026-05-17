# -*- coding: utf-8 -*-
# utils/charts.py
"""
Chart helpers for Streamlit + Plotly.
Provides consistent, styled charts with automatic color palettes.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#f43f5e", "#a78bfa"]

CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def line_chart(df: pd.DataFrame, col: str, title: str = "") -> go.Figure:
    fig = px.line(
        df, y=col,
        title=title or f"Évolution de {col}",
        color_discrete_sequence=PALETTE,
        template="plotly_dark",
    )
    fig.update_layout(**CHART_THEME)
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = px.bar(
        df, x=x, y=y,
        title=title or f"{y} par {x}",
        color_discrete_sequence=PALETTE,
        template="plotly_dark",
    )
    fig.update_layout(**CHART_THEME)
    return fig


def histogram(df: pd.DataFrame, col: str, title: str = "") -> go.Figure:
    fig = px.histogram(
        df, x=col,
        title=title or f"Distribution de {col}",
        color_discrete_sequence=PALETTE,
        template="plotly_dark",
        nbins=30,
    )
    fig.update_layout(**CHART_THEME)
    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure | None:
    num = df.select_dtypes(include="number")
    if num.shape[1] < 2:
        return None
    corr = num.corr()
    fig = px.imshow(
        corr,
        title="Matrice de corrélation",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        template="plotly_dark",
        text_auto=".2f",
    )
    fig.update_layout(**CHART_THEME)
    return fig
