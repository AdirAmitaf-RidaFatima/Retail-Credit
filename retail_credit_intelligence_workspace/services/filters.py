from __future__ import annotations

import pandas as pd
import streamlit as st


def portfolio_filters(df: pd.DataFrame, key_prefix: str = "global") -> pd.DataFrame:
    """Create standard sidebar filters shared across pages."""
    st.sidebar.subheader("Portfolio Filters")
    filtered = df
    filter_specs = [
        ("facility_type", "Facility"),
        ("risk_band", "Risk Band"),
        ("recommended_decision", "Decision"),
        ("grade", "Grade"),
        ("term_months", "Tenor"),
        ("addr_state", "State"),
    ]
    for column, label in filter_specs:
        if column not in filtered.columns:
            continue
        options = sorted([x for x in filtered[column].dropna().unique().tolist()])
        if len(options) > 0 and len(options) <= 80:
            selected = st.sidebar.multiselect(label, options, default=[], key=f"{key_prefix}_{column}")
            if selected:
                filtered = filtered[filtered[column].isin(selected)]
    if "predicted_pd" in filtered.columns:
        min_pd, max_pd = st.sidebar.slider(
            "PD Range",
            0.0,
            1.0,
            (0.0, 1.0),
            step=0.01,
            key=f"{key_prefix}_pd_range",
        )
        filtered = filtered[(filtered["predicted_pd"] >= min_pd) & (filtered["predicted_pd"] <= max_pd)]
    return filtered
