from __future__ import annotations

import streamlit as st

from components.charts import bar_chart, scatter_chart
from components.ui import hero, load_css, page_caption
from services.data_loader import load_portfolio
from services.filters import portfolio_filters
from services.metrics import segment_summary

st.set_page_config(page_title="Portfolio Analytics", page_icon="📊", layout="wide")
load_css()
hero("Portfolio Analytics", "Interactive segmentation by facility, tenor, grade, income, DTI, employment, geography, and risk band.")
page_caption(["Audience: Portfolio manager / credit policy", "Purpose: identify segments that need action"])

df = portfolio_filters(load_portfolio(), key_prefix="portfolio")
if df.empty:
    st.warning("No records match selected filters.")
    st.stop()

segment_options = {
    "Facility": "facility_type",
    "Tenor": "term_months",
    "Grade": "grade",
    "Sub-grade": "sub_grade",
    "Purpose": "purpose",
    "Employment": "emp_length",
    "Home Ownership": "home_ownership",
    "Verification Status": "verification_status",
    "Geography": "addr_state",
    "Risk Band": "risk_band",
    "Decision": "recommended_decision",
}
label = st.selectbox("Select analysis dimension", list(segment_options.keys()))
by = segment_options[label]
summary = segment_summary(df, by)

st.subheader(f"Segment Risk Summary by {label}")
st.dataframe(summary, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.plotly_chart(bar_chart(summary.head(15), by, "average_pd", f"Average PD by {label}"), use_container_width=True)
with right:
    st.plotly_chart(bar_chart(summary.head(15), by, "expected_loss", f"Expected Loss by {label}"), use_container_width=True)

st.plotly_chart(
    scatter_chart(summary, "average_pd", "average_return", f"Risk-Return Matrix by {label}", size="exposure"),
    use_container_width=True,
)

st.subheader("Business Interpretation")
st.write(
    "Segments in the upper-left or lower-left of the risk-return matrix require different actions. "
    "High PD with weak return may require tighter approval cutoffs, lower limits, shorter tenor, higher pricing, or manual review. "
    "Low PD with positive return may support controlled growth within risk appetite."
)
