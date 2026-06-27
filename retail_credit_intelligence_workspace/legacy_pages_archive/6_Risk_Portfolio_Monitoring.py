from __future__ import annotations

import streamlit as st

from components.charts import bar_chart, line_chart
from components.ui import format_currency, format_pct, hero, load_css, metric_card, page_caption
from services.data_loader import load_portfolio
from services.filters import portfolio_filters
from services.metrics import risk_migration_proxy, segment_summary

st.set_page_config(page_title="Risk Monitoring", page_icon="🛡️", layout="wide")
load_css()
hero("Risk & Portfolio Monitoring", "Risk concentration, migration proxy, expected loss, and segments requiring management attention.")
page_caption(["Audience: Portfolio risk / collections / CRO", "Purpose: monitor emerging risk and portfolio quality"])

df = portfolio_filters(load_portfolio(), key_prefix="monitor")
if df.empty:
    st.warning("No records match selected filters.")
    st.stop()

high_risk = df[df["risk_band"].isin(["High Risk", "Very High Risk"])]
negative_return = df[df["expected_return_pct"] < 0]
cols = st.columns(4)
with cols[0]:
    metric_card("High-Risk Borrowers", f"{len(high_risk):,.0f}", format_pct(len(high_risk) / len(df)))
with cols[1]:
    metric_card("Negative Return Accounts", f"{len(negative_return):,.0f}", format_pct(len(negative_return) / len(df)))
with cols[2]:
    metric_card("High-Risk Exposure", format_currency(high_risk["ead"].sum()), "High + very high risk")
with cols[3]:
    metric_card("Negative Return Exposure", format_currency(negative_return["ead"].sum()), "Requires repricing or decline review")

facility = segment_summary(df, "facility_type").head(10)
grade = segment_summary(df, "grade")
risk_band = segment_summary(df, "risk_band")

left, right = st.columns(2)
with left:
    st.plotly_chart(bar_chart(facility, "facility_type", "expected_loss", "Expected Loss by Facility"), use_container_width=True)
with right:
    st.plotly_chart(bar_chart(grade, "grade", "default_rate", "Observed Default Rate by Grade"), use_container_width=True)

st.plotly_chart(bar_chart(risk_band, "risk_band", "exposure", "Exposure by Risk Band"), use_container_width=True)

migration = risk_migration_proxy(df)
if not migration.empty:
    st.subheader("Risk Migration Proxy by Issue Vintage")
    st.plotly_chart(line_chart(migration, "issue_period", "share", "Risk Band Mix by Origination Quarter", color="risk_band"), use_container_width=True)

st.subheader("Management Attention List")
attention = facility[(facility["average_pd"] > df["predicted_pd"].mean()) | (facility["average_return"] < 0)].copy()
st.dataframe(attention, use_container_width=True, hide_index=True)
