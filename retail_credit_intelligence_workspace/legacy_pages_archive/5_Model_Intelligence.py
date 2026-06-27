from __future__ import annotations

import streamlit as st

from components.charts import bar_chart
from components.ui import hero, insight_box, load_css, page_caption
from services.data_loader import get_plot_path, load_markdown_report, load_report

st.set_page_config(page_title="Model Intelligence", page_icon="🧠", layout="wide")
load_css()
hero("Model Intelligence", "Champion/challenger performance, calibration, explainability, and model governance evidence.")
page_caption(["Audience: Model validation / CRO / analytics", "Purpose: prove model is useful, explainable, and controlled"])

metrics = load_report("model_comparison_metrics.csv")
calibration = load_report("calibration_comparison.csv")
importance = load_report("feature_importance_report.csv")
confusion = load_report("confusion_matrices.csv")

st.subheader("Model Comparison")
if not metrics.empty:
    st.dataframe(metrics, use_container_width=True, hide_index=True)
    metric_view = metrics[["model", "roc_auc", "pr_auc", "brier_score", "ks_statistic", "expected_return_pct"]].copy()
    st.plotly_chart(bar_chart(metric_view, "model", "roc_auc", "ROC-AUC by Model"), use_container_width=True)
else:
    st.warning("Model comparison report is missing.")

st.subheader("Calibration")
if not calibration.empty:
    st.dataframe(calibration, use_container_width=True, hide_index=True)
calibration_plot = get_plot_path("calibration_curve_champion.png")
if calibration_plot.exists():
    st.image(str(calibration_plot), caption="Champion calibration curve")

st.subheader("Confusion Matrices")
if not confusion.empty:
    st.dataframe(confusion, use_container_width=True, hide_index=True)

st.subheader("Feature Importance")
if not importance.empty:
    selected_model = st.selectbox("Model", sorted(importance["model"].unique()))
    top_features = importance[importance["model"] == selected_model].head(20)
    st.plotly_chart(bar_chart(top_features, "feature", "absolute_importance", f"Top Features - {selected_model}"), use_container_width=True)

shap_plot = get_plot_path("shap_summary_random_forest.png")
if shap_plot.exists():
    st.subheader("SHAP Summary")
    st.image(str(shap_plot), caption="SHAP summary plot from challenger model")

st.subheader("Executive Model Report")
report = load_markdown_report("executive_model_report.md")
if report:
    st.markdown(report)
else:
    insight_box("Executive model report file is not available. Add executive_model_report.md to the reports folder.", "warning")

st.subheader("Banking Interpretation")
insight_box("A model should not be selected only because it has the highest AUC. For credit decisions, calibration, stability, explainability, maintainability, and policy usability matter.", "info")
