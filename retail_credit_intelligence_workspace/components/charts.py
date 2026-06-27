from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_white"
COLOR_SEQUENCE = ["#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed", "#0891b2", "#ea580c"]
RISK_COLORS = {
    "Low Risk": "#059669",
    "Moderate Risk": "#2563eb",
    "High Risk": "#d97706",
    "Very High Risk": "#dc2626",
}


def _polish(fig: go.Figure, height: int = 360) -> go.Figure:
    """Apply a shared report-quality layout to every figure."""
    fig.update_layout(
        template=TEMPLATE,
        height=height,
        margin=dict(l=20, r=20, t=58, b=40),
        title_x=0.02,
        title_font=dict(size=16, color="#111827"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        legend_title_text="",
        font=dict(color="#1f2937", size=12),
    )
    fig.update_xaxes(showgrid=False, title_font=dict(size=12), tickfont=dict(size=11))
    fig.update_yaxes(gridcolor="#e5e7eb", title_font=dict(size=12), tickfont=dict(size=11))
    return fig


def bar_chart(data: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 360) -> go.Figure:
    """Create a comparison chart for portfolio segments."""
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    return _polish(fig, height=height)


def horizontal_bar(data: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 360) -> go.Figure:
    """Create a horizontal ranking chart for management attention items."""
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        orientation="h",
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return _polish(fig, height=height)


def line_chart(data: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 360) -> go.Figure:
    """Create a trend chart for portfolio monitoring."""
    fig = px.line(
        data,
        x=x,
        y=y,
        color=color,
        markers=True,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    return _polish(fig, height=height)


def donut_chart(data: pd.DataFrame, names: str, values: str, title: str, height: int = 330) -> go.Figure:
    """Create a share-of-portfolio chart where composition matters."""
    fig = px.pie(
        data,
        names=names,
        values=values,
        hole=0.58,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _polish(fig, height=height)


def histogram(data: pd.DataFrame, x: str, title: str, nbins: int = 40, height: int = 330) -> go.Figure:
    """Create a distribution chart for risk or profitability diagnostics."""
    fig = px.histogram(data, x=x, nbins=nbins, title=title, color_discrete_sequence=["#2563eb"])
    return _polish(fig, height=height)


def scatter_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    size: str | None = None,
    height: int = 390,
) -> go.Figure:
    """Create a risk-return map for strategy and pricing decisions."""
    fig = px.scatter(
        data,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE,
        hover_data=data.columns,
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
    return _polish(fig, height=height)


def gauge(value: float, title: str, min_value: float = 0, max_value: float = 100, height: int = 270) -> go.Figure:
    """Create an executive health indicator."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 32, "color": "#111827"}},
            title={"text": title, "font": {"size": 15, "color": "#111827"}},
            gauge={
                "axis": {"range": [min_value, max_value], "tickcolor": "#64748b"},
                "bar": {"color": "#2563eb"},
                "bgcolor": "#ffffff",
                "borderwidth": 1,
                "bordercolor": "#d9e2ef",
                "steps": [
                    {"range": [0, 40], "color": "rgba(220, 38, 38, .18)"},
                    {"range": [40, 70], "color": "rgba(217, 119, 6, .18)"},
                    {"range": [70, 100], "color": "rgba(5, 150, 105, .18)"},
                ],
            },
        )
    )
    return _polish(fig, height=height)


def risk_band_bar(data: pd.DataFrame, title: str, height: int = 330) -> go.Figure:
    """Create a risk-band chart with fixed risk colors."""
    fig = px.bar(data, x="Risk Category", y="Borrower Accounts", color="Risk Category", title=title, color_discrete_map=RISK_COLORS)
    return _polish(fig, height=height)
