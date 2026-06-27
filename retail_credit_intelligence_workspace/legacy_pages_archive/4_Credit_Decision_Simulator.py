from __future__ import annotations

import streamlit as st

from components.ui import format_currency, format_pct, hero, insight_box, load_css, metric_card, page_caption
from services.data_loader import load_config, load_portfolio
from services.risk_engine import assign_risk_band, calculate_economics, recommend_decision, simulate_pd_from_changes

st.set_page_config(page_title="Credit Decision Simulator", page_icon="🧮", layout="wide")
load_css()
hero("Credit Decision Simulator", "Modify borrower characteristics and observe scenario impact on PD, EL, return, and decision.")
page_caption(["Audience: Underwriter / product manager", "Purpose: transparent what-if analysis"])

config = load_config()
df = load_portfolio()
borrower_id = st.selectbox("Choose base borrower", df["borrower_id"].head(5000).tolist())
row = df[df["borrower_id"] == borrower_id].iloc[0]

st.info("Simulator output is a controlled scenario estimate anchored on the original model PD. It is not a replacement for retraining or live model scoring.")

left, right = st.columns(2)
with left:
    loan_amount = st.number_input("Loan Amount", min_value=500.0, max_value=100000.0, value=float(row["loan_amnt"]), step=500.0)
    term_months = st.selectbox("Tenor", [36, 60], index=0 if int(row["term_months"]) == 36 else 1)
    interest_rate = st.slider("Interest Rate", 0.03, 0.35, float(row["int_rate_decimal"]), step=0.005)
    lgd = st.slider("LGD", 0.20, 0.90, float(row["lgd"]), step=0.05)
with right:
    dti = st.slider("DTI", 0.0, 60.0, float(row.get("dti", 20) or 20), step=0.5)
    revol_util = st.slider("Revolving Utilization", 0.0, 120.0, float(row.get("revol_util", 45) or 45), step=1.0)
    delinq_2yrs = st.slider("Delinquencies in Last 2 Years", 0, 10, int(row.get("delinq_2yrs", 0) or 0))

sim_pd = simulate_pd_from_changes(row, {"dti": dti, "revol_util": revol_util, "term_months": term_months, "delinq_2yrs": delinq_2yrs})
economics = calculate_economics(
    sim_pd,
    loan_amount,
    interest_rate,
    term_months,
    lgd,
    cost_of_funds=float(config["cost_of_funds"]),
    operating_cost_rate=float(config["operating_cost_rate"]),
)
risk_band = assign_risk_band(sim_pd)
decision = recommend_decision(sim_pd, economics["expected_return_pct"])

cols = st.columns(4)
with cols[0]:
    metric_card("Scenario PD", format_pct(sim_pd), f"Original: {row['predicted_pd']:.2%}")
with cols[1]:
    metric_card("Risk Band", risk_band, "Scenario classification")
with cols[2]:
    metric_card("Expected Loss", format_currency(economics["expected_loss"]), "PD × LGD × EAD")
with cols[3]:
    metric_card("Expected Return", format_pct(economics["expected_return_pct"]), decision)

if decision == "Decline":
    insight_box("Scenario recommendation: Decline. Risk or economics exceed policy comfort under the selected assumptions.", "danger")
elif decision == "Manual Review":
    insight_box("Scenario recommendation: Manual Review. A senior underwriter should review compensating factors and policy exceptions.", "warning")
elif decision == "Approve with Conditions":
    insight_box("Scenario recommendation: Approve with Conditions. Consider lower amount, shorter tenor, or stronger verification.", "warning")
else:
    insight_box("Scenario recommendation: Approve. Risk and expected return are within simplified policy appetite.", "info")

st.subheader("Original vs Scenario")
st.dataframe(
    {
        "Metric": ["PD", "Loan Amount", "Tenor", "Interest Rate", "Expected Loss", "Expected Return", "Decision"],
        "Original": [
            f"{row['predicted_pd']:.2%}", f"${float(row['loan_amnt']):,.0f}", f"{int(row['term_months'])} months",
            f"{float(row['int_rate_decimal']):.2%}", f"${float(row['expected_loss']):,.0f}", f"{float(row['expected_return_pct']):.2%}", row.get("recommended_decision", "N/A"),
        ],
        "Scenario": [
            f"{sim_pd:.2%}", f"${loan_amount:,.0f}", f"{term_months} months", f"{interest_rate:.2%}",
            f"${economics['expected_loss']:,.0f}", f"{economics['expected_return_pct']:.2%}", decision,
        ],
    },
    use_container_width=True,
    hide_index=True,
)
