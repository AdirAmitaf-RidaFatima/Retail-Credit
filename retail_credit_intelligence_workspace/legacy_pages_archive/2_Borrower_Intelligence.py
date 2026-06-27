from __future__ import annotations

import streamlit as st

from components.ui import format_currency, format_pct, hero, insight_box, load_css, metric_card, page_caption
from services.data_loader import load_portfolio
from services.insights import suggested_analyst_note
from services.report_service import borrower_credit_memo
from services.risk_engine import top_reason_codes

st.set_page_config(page_title="Borrower Intelligence", page_icon="👤", layout="wide")
load_css()
hero("Borrower Intelligence", "Search borrower records, review PD, expected loss, decision recommendation, and risk drivers.")
page_caption(["Audience: Credit officer / underwriter", "Purpose: borrower-level credit memo and decision support"])

df = load_portfolio()
search = st.text_input("Search Borrower ID", value=df["borrower_id"].iloc[0])
matched = df[df["borrower_id"].str.contains(search, case=False, na=False)] if search else df.head(50)
if matched.empty:
    st.warning("No borrower found. Try another ID or clear the search box.")
    st.stop()

borrower_id = st.selectbox("Select Borrower", matched["borrower_id"].head(250).tolist())
row = df[df["borrower_id"] == borrower_id].iloc[0]

cols = st.columns(4)
with cols[0]:
    metric_card("Predicted PD", format_pct(row["predicted_pd"]), row.get("risk_band", "Risk band"))
with cols[1]:
    metric_card("Loan Amount", format_currency(row["loan_amnt"]), f"{row.get('term_months', 'N/A')} months")
with cols[2]:
    metric_card("Expected Loss", format_currency(row["expected_loss"]), "Modelled credit cost")
with cols[3]:
    metric_card("Expected Return", format_pct(row["expected_return_pct"]), row.get("recommended_decision", "Decision"))

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Applicant Information")
    st.dataframe(
        {
            "Field": [
                "Borrower ID", "Facility", "Purpose", "Grade", "Sub-grade", "State",
                "Employment Length", "Home Ownership", "Verification Status", "Annual Income",
                "DTI", "Revolving Utilization", "Delinquencies 2Y", "Inquiries 6M",
            ],
            "Value": [
                row.get("borrower_id", "N/A"), row.get("facility_type", "N/A"), row.get("purpose", "N/A"),
                row.get("grade", "N/A"), row.get("sub_grade", "N/A"), row.get("addr_state", "N/A"),
                row.get("emp_length", "N/A"), row.get("home_ownership", "N/A"), row.get("verification_status", "N/A"),
                f"${float(row.get('annual_inc', 0)):,.0f}" if row.get("annual_inc") == row.get("annual_inc") else "N/A",
                f"{float(row.get('dti', 0)):.2f}" if row.get("dti") == row.get("dti") else "N/A",
                f"{float(row.get('revol_util', 0)):.1f}%" if row.get("revol_util") == row.get("revol_util") else "N/A",
                row.get("delinq_2yrs", "N/A"), row.get("inq_last_6mths", "N/A"),
            ],
        },
        use_container_width=True,
        hide_index=True,
    )
with right:
    st.subheader("Lending Recommendation")
    decision = str(row.get("recommended_decision", "Manual Review"))
    if "Reject" in decision or "Decline" in decision:
        kind = "danger"
    elif "Review" in decision or "Condition" in decision:
        kind = "warning"
    else:
        kind = "info"
    insight_box(f"<b>{decision}</b><br>{suggested_analyst_note(row)}", kind=kind)

risk_drivers, mitigants = top_reason_codes(row)
left, right = st.columns(2)
with left:
    st.subheader("Top Risk Factors")
    for item in risk_drivers or ["No material adverse reason code from available fields."]:
        insight_box(item, kind="warning")
with right:
    st.subheader("Risk Mitigants")
    for item in mitigants or ["No material mitigant detected from available fields."]:
        insight_box(item, kind="info")

st.subheader("Suggested Analyst Notes")
st.write(suggested_analyst_note(row))
memo = borrower_credit_memo(row)
st.download_button("Download Borrower Credit Memo (.md)", data=memo, file_name=f"credit_memo_{borrower_id}.md", mime="text/markdown")
with st.expander("Preview credit memo"):
    st.markdown(memo)
