from __future__ import annotations

from pathlib import Path
from typing import Iterable

import streamlit as st


def load_css(path: str = "assets/styles.css") -> None:
    """Load local CSS so the dashboard has a controlled enterprise visual system."""
    css_path = Path(path)
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    """Render a light-theme executive header with a visible project evidence trail."""
    st.markdown(
        f"""
        <div class="bank-hero">
            <div class="eyebrow">Retail Credit Risk Intelligence</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <div class="progress-strip">
                <div class="progress-pill">1. Business research</div>
                <div class="progress-pill">2. Dataset audit</div>
                <div class="progress-pill">3. Leakage control</div>
                <div class="progress-pill">4. Portfolio analysis</div>
                <div class="progress-pill">5. Model validation</div>
                <div class="progress-pill">6. Explainability</div>
                <div class="progress-pill">7. Decision dashboard</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "", style: str = "") -> None:
    """Render a KPI card with full business wording rather than unexplained abbreviations."""
    safe_style = f" {style}" if style else ""
    st.markdown(
        f"""
        <div class="metric-card{safe_style}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(text: str, kind: str = "info") -> None:
    """Render a concise insight card; long explanations should stay in reports, not the workspace."""
    css_class = {
        "info": "insight-box",
        "warning": "warning-box",
        "danger": "danger-box",
        "success": "success-box",
    }.get(kind, "insight-box")
    st.markdown(f"<div class='{css_class}'>{text}</div>", unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    """Use consistent headers so the analyst can scan the single dashboard quickly."""
    st.markdown(
        f"""
        <div class="section-title">
            <h3>{title}</h3>
            <span>{subtitle}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str = "neutral") -> str:
    """Return an HTML status badge for a lending recommendation or risk category."""
    css_class = {
        "approve": "badge-approve",
        "review": "badge-review",
        "decline": "badge-decline",
        "neutral": "badge-neutral",
    }.get(kind, "badge-neutral")
    return f"<span class='status-badge {css_class}'>{text}</span>"


def field_grid(items: dict[str, str]) -> None:
    """Render borrower profile fields in compact two-column cards."""
    html = "<div class='field-grid'>"
    for label, value in items.items():
        html += f"<div class='field-box'><div class='field-label'>{label}</div><div class='field-value'>{value}</div></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def page_caption(items: Iterable[str]) -> None:
    """Show short context for the page without turning the dashboard into a report."""
    st.caption(" • ".join(items))


def format_currency(value: float, symbol: str = "$") -> str:
    """Format monetary values compactly so KPI cards remain readable."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "Not available"
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    if abs_value >= 1_000_000_000:
        return f"{sign}{symbol}{abs_value / 1_000_000_000:,.2f}B"
    if abs_value >= 1_000_000:
        return f"{sign}{symbol}{abs_value / 1_000_000:,.2f}M"
    if abs_value >= 1_000:
        return f"{sign}{symbol}{abs_value / 1_000:,.1f}K"
    return f"{sign}{symbol}{abs_value:,.0f}"


def format_pct(value: float) -> str:
    """Format a ratio as a percentage with two decimals."""
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return "Not available"


def format_number(value: float) -> str:
    """Format counts for executive readability."""
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return "Not available"
