from __future__ import annotations

import streamlit as st

from components.ui import hero, insight_box, load_css, page_caption
from services.data_loader import load_portfolio, load_report
from services.filters import portfolio_filters
from services.insights import generate_executive_insights
from services.metrics import segment_summary

st.set_page_config(page_title="Executive Insights", page_icon="💡", layout="wide")
load_css()
hero("Executive Insights", "Plain-language, computed observations for management and policy committees.")
page_caption(["Audience: Executive management / credit policy", "Purpose: convert analysis into business actions"])

df = portfolio_filters(load_portfolio(), key_prefix="insights")
if df.empty:
    st.warning("No records match selected filters.")
    st.stop()

st.subheader("Generated Insights")
for item in generate_executive_insights(df):
    insight_box(f"<b>{item['title']}:</b> {item['message']}", kind=item["severity"])

st.subheader("EDA Phase Insights")
eda_insights = load_report("eda_executive_risk_insights.csv")
if not eda_insights.empty:
    st.dataframe(eda_insights, use_container_width=True, hide_index=True)

st.subheader("Policy Action Candidates")
facility = segment_summary(df, "facility_type")
tenor = segment_summary(df, "term_months")
col1, col2 = st.columns(2)
with col1:
    st.write("Facilities requiring review")
    st.dataframe(facility.head(6), use_container_width=True, hide_index=True)
with col2:
    st.write("Tenor performance")
    st.dataframe(tenor, use_container_width=True, hide_index=True)
