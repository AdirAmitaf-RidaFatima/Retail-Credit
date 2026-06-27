from __future__ import annotations

import streamlit as st

from components.ui import hero, load_css, page_caption
from services.data_loader import load_markdown_report, load_portfolio, load_report
from services.filters import portfolio_filters
from services.metrics import portfolio_kpis, segment_summary
from services.report_service import dataframe_to_excel_bytes

st.set_page_config(page_title="Reports & Export", page_icon="📁", layout="wide")
load_css()
hero("Reports & Export", "Export portfolio summaries, model reports, borrower data, and PDF-ready report content.")
page_caption(["Audience: audit / committees / project reviewers", "Purpose: portable reporting and evidence pack"])

df = portfolio_filters(load_portfolio(), key_prefix="exports")
if df.empty:
    st.warning("No records match selected filters.")
    st.stop()

st.subheader("Export Portfolio Data")
st.download_button(
    "Download Filtered Portfolio CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_scored_portfolio.csv",
    mime="text/csv",
)
st.download_button(
    "Download Filtered Portfolio Excel",
    data=dataframe_to_excel_bytes(df.head(100000), "ScoredPortfolio"),
    file_name="filtered_scored_portfolio.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.subheader("Committee Summary")
kpi = portfolio_kpis(df)
facility = segment_summary(df, "facility_type")
summary_text = f"""
# Retail Credit Intelligence Committee Summary

- Total borrowers: {kpi['borrowers']:,.0f}
- Total exposure: ${kpi['exposure']:,.0f}
- Average PD: {kpi['average_pd']:.2%}
- Expected loss: ${kpi['expected_loss']:,.0f}
- Expected profit: ${kpi['expected_profit']:,.0f}
- Expected return: {kpi['expected_return']:.2%}
- Approval / conditional share: {kpi['approval_rate']:.2%}

## Largest Expected Loss Segments
{facility.head(8).to_markdown(index=False)}

## Governance Note
This output is generated from the approved scored portfolio and supports decision review. It does not replace KYC, AML, fraud checks, delegated approval authority, or internal policy documentation.
""".strip()
st.download_button("Download Committee Summary (.md)", summary_text, file_name="committee_summary.md", mime="text/markdown")
st.markdown(summary_text)

st.subheader("Model Reports")
for file_name in ["model_comparison_metrics.csv", "calibration_comparison.csv", "feature_importance_report.csv", "confusion_matrices.csv"]:
    report = load_report(file_name)
    if not report.empty:
        with st.expander(file_name):
            st.dataframe(report, use_container_width=True, hide_index=True)
            st.download_button(
                f"Download {file_name}",
                data=report.to_csv(index=False).encode("utf-8"),
                file_name=file_name,
                mime="text/csv",
                key=file_name,
            )

executive_report = load_markdown_report("executive_model_report.md")
if executive_report:
    st.download_button("Download Executive Model Report", executive_report, file_name="executive_model_report.md", mime="text/markdown")
