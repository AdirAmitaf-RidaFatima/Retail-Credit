from __future__ import annotations

import streamlit as st

from components.charts import bar_chart, donut_chart, gauge, histogram
from components.ui import format_currency, format_pct, hero, insight_box, load_css, metric_card, page_caption
from services.data_loader import load_config, load_portfolio
from services.filters import portfolio_filters
from services.insights import generate_executive_insights
from services.metrics import portfolio_health_score, portfolio_kpis, segment_summary

st.set_page_config(page_title="Executive Dashboard", page_icon="🏦", layout="wide")
load_css()
hero("Executive Dashboard", "Portfolio health, exposure, risk-return performance, and management actions in one view.")
page_caption(["Audience: CEO, CRO, Head of Retail", "Purpose: 30-second portfolio risk answer"])

config = load_config()
df = load_portfolio()
filtered = portfolio_filters(df, key_prefix="exec")
if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

kpi = portfolio_kpis(filtered)
health = portfolio_health_score(filtered)
cols = st.columns(4)
with cols[0]:
    metric_card("Total Borrowers", f"{kpi['borrowers']:,.0f}", "Filtered portfolio records")
with cols[1]:
    metric_card("Total Exposure", format_currency(kpi["exposure"]), "EAD / loan amount proxy")
with cols[2]:
    metric_card("Average PD", format_pct(kpi["average_pd"]), "Model-estimated default risk")
with cols[3]:
    metric_card("Expected Loss", format_currency(kpi["expected_loss"]), "PD × LGD × EAD")

cols = st.columns(4)
with cols[0]:
    metric_card("Expected Return", format_pct(kpi["expected_return"]), "After funding, ops cost and EL")
with cols[1]:
    metric_card("Portfolio Yield", format_pct(kpi["portfolio_yield"]), "Average contractual rate")
with cols[2]:
    metric_card("Approval Distribution", format_pct(kpi["approval_rate"]), "Approve / conditional share")
with cols[3]:
    metric_card("Portfolio Health", f"{health:.0f}/100", "Composite risk-return signal")

left, right = st.columns([1, 1])
with left:
    st.plotly_chart(gauge(health, "Portfolio Health Score"), use_container_width=True)
with right:
    risk = filtered["risk_band"].value_counts().reset_index()
    risk.columns = ["risk_band", "borrowers"]
    st.plotly_chart(donut_chart(risk, "risk_band", "borrowers", "Risk Distribution"), use_container_width=True)

left, right = st.columns([1, 1])
with left:
    decision = filtered["recommended_decision"].value_counts().reset_index()
    decision.columns = ["recommended_decision", "borrowers"]
    st.plotly_chart(bar_chart(decision, "recommended_decision", "borrowers", "Approval / Decision Distribution"), use_container_width=True)
with right:
    st.plotly_chart(histogram(filtered, "predicted_pd", "PD Distribution", nbins=45), use_container_width=True)

facility = segment_summary(filtered, "facility_type").head(10)
tenor = segment_summary(filtered, "term_months")
state = segment_summary(filtered, "addr_state").head(12)
left, right = st.columns([1, 1])
with left:
    st.plotly_chart(bar_chart(facility, "facility_type", "exposure", "Facility Mix by Exposure"), use_container_width=True)
with right:
    st.plotly_chart(bar_chart(tenor, "term_months", "average_pd", "Average PD by Tenor"), use_container_width=True)

st.plotly_chart(bar_chart(state, "addr_state", "expected_loss", "Top Geographic Expected Loss Concentrations"), use_container_width=True)

st.subheader("Executive Insights")
for item in generate_executive_insights(filtered):
    insight_box(f"<b>{item['title']}:</b> {item['message']}", kind=item["severity"])
