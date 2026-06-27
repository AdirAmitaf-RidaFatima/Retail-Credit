from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import bar_chart, donut_chart, gauge, horizontal_bar, risk_band_bar, scatter_chart
from components.ui import (
    badge,
    field_grid,
    format_currency,
    format_number,
    format_pct,
    hero,
    insight_box,
    load_css,
    metric_card,
    section_header,
)
from services.data_loader import get_plot_path, load_markdown_report, load_portfolio, load_report
from services.insights import generate_executive_insights, suggested_analyst_note
from services.metrics import portfolio_health_score, portfolio_kpis, segment_summary
from services.report_service import borrower_credit_memo, dataframe_to_excel_bytes
from services.risk_engine import calculate_economics, recommend_decision, simulate_pd_from_changes, top_reason_codes

st.set_page_config(
    page_title="Retail Credit Intelligence Workspace",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css()

USER_FRIENDLY_COLUMNS = {
    "borrower_id": "Borrower Reference",
    "facility_type": "Facility Type",
    "term_months": "Loan Tenor in Months",
    "loan_amnt": "Loan Amount",
    "ead": "Exposure Amount",
    "predicted_pd": "Predicted Default Probability",
    "risk_band": "Risk Category",
    "expected_loss": "Expected Credit Loss",
    "expected_profit": "Expected Profit After Credit Loss",
    "expected_return_pct": "Expected Profit Rate After Credit Loss",
    "recommended_decision": "Lending Recommendation",
    "grade": "Credit Grade",
    "sub_grade": "Detailed Credit Grade",
    "purpose": "Loan Purpose",
    "addr_state": "Borrower Location",
    "annual_inc": "Annual Income",
    "dti": "Debt-to-Income Burden",
    "revol_util": "Revolving Credit Utilization",
    "delinq_2yrs": "Delinquencies in Last Two Years",
    "inq_last_6mths": "Credit Inquiries in Last Six Months",
    "home_ownership": "Home Ownership",
    "verification_status": "Income Verification Status",
    "emp_length": "Employment Length",
    "int_rate_decimal": "Portfolio Yield",
}

DIMENSIONS = {
    "Facility type": "facility_type",
    "Loan tenor": "term_months",
    "Credit grade": "grade",
    "Detailed credit grade": "sub_grade",
    "Loan purpose": "purpose",
    "Borrower location": "addr_state",
    "Employment length": "emp_length",
    "Home ownership": "home_ownership",
    "Income verification status": "verification_status",
    "Risk category": "risk_band",
    "Lending recommendation": "recommended_decision",
}


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert values safely because borrower fields may contain missing values."""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def humanize_model_name(name: str) -> str:
    """Translate technical model names into readable stakeholder labels."""
    replacements = {
        "scorecard_woe_logistic_calibrated": "Calibrated credit scorecard",
        "scorecard_woe_logistic_uncalibrated": "Uncalibrated credit scorecard",
        "scorecard_woe_logistic": "Credit scorecard",
        "logistic_regression": "Logistic regression score model",
        "random_forest": "Random forest challenger",
        "decision_tree": "Decision tree challenger",
        "policy_rule_baseline": "Policy-rule baseline",
    }
    return replacements.get(str(name), str(name).replace("_", " ").title())


def add_derived_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Create business-friendly bands used by slicers and charts."""
    data = df.copy()
    if "annual_inc" in data.columns:
        data["income_band"] = pd.cut(
            data["annual_inc"],
            bins=[-np.inf, 40_000, 70_000, 100_000, 150_000, np.inf],
            labels=["Below $40K", "$40K-$70K", "$70K-$100K", "$100K-$150K", "Above $150K"],
        ).astype("object").fillna("Income not available")
    if "dti" in data.columns:
        data["debt_burden_band"] = pd.cut(
            data["dti"],
            bins=[-np.inf, 10, 20, 30, 40, np.inf],
            labels=["Very low burden", "Manageable burden", "Elevated burden", "High burden", "Severe burden"],
        ).astype("object").fillna("Debt burden not available")
    if "revol_util" in data.columns:
        data["utilization_band"] = pd.cut(
            data["revol_util"],
            bins=[-np.inf, 30, 60, 80, 100, np.inf],
            labels=["Low utilization", "Moderate utilization", "High utilization", "Very high utilization", "Above limit or unusual"],
        ).astype("object").fillna("Utilization not available")
    if "term_months" in data.columns:
        data["tenor_label"] = data["term_months"].apply(lambda x: f"{safe_float(x):.0f} months")
    return data


def multi_filter(data: pd.DataFrame, column: str, label: str, key: str) -> pd.DataFrame:
    """Apply a top-row slicer only when the analyst selects values."""
    if column not in data.columns:
        return data
    options = sorted([value for value in data[column].dropna().unique().tolist()], key=lambda x: str(x))
    if not options:
        return data
    selected = st.multiselect(label, options, default=[], key=key, help=f"Filter the dashboard by {label.lower()}.")
    if selected:
        return data[data[column].isin(selected)]
    return data


def apply_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Render slicers at the top of the single dashboard and return the filtered portfolio."""
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    section_header("Portfolio Slicers", "Use these filters to change every chart, card, table, and borrower queue below.")
    row1 = st.columns([1.2, 1.0, 1.0, 1.1, 1.0, 1.0])
    filtered = df
    with row1[0]:
        search_text = st.text_input(
            "Search borrower or segment",
            value="",
            placeholder="Example: LC-0000123, personal loan, CA",
            help="Search borrower reference, facility type, purpose, state, credit grade, or lending recommendation.",
        )
    with row1[1]:
        filtered = multi_filter(filtered, "facility_type", "Facility type", "facility_filter")
    with row1[2]:
        filtered = multi_filter(filtered, "term_months", "Loan tenor", "tenor_filter")
    with row1[3]:
        filtered = multi_filter(filtered, "risk_band", "Risk category", "risk_filter")
    with row1[4]:
        filtered = multi_filter(filtered, "recommended_decision", "Lending recommendation", "decision_filter")
    with row1[5]:
        filtered = multi_filter(filtered, "grade", "Credit grade", "grade_filter")

    row2 = st.columns([1.0, 1.0, 1.0, 1.0])
    with row2[0]:
        filtered = multi_filter(filtered, "addr_state", "Borrower location", "location_filter")
    with row2[1]:
        filtered = multi_filter(filtered, "income_band", "Income band", "income_filter")
    with row2[2]:
        probability_range = st.slider(
            "Predicted default probability range",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.01,
            help="Limits the dashboard to borrowers within the selected model-estimated default probability range.",
        )
    with row2[3]:
        return_range = st.slider(
            "Expected profit rate after credit loss",
            min_value=-1.0,
            max_value=1.0,
            value=(-1.0, 1.0),
            step=0.02,
            help="Limits the dashboard to borrowers within the selected risk-adjusted profitability range.",
        )

    if "predicted_pd" in filtered.columns:
        filtered = filtered[filtered["predicted_pd"].between(probability_range[0], probability_range[1])]
    if "expected_return_pct" in filtered.columns:
        filtered = filtered[filtered["expected_return_pct"].between(return_range[0], return_range[1])]
    if search_text:
        search_space = filtered[[col for col in ["borrower_id", "facility_type", "purpose", "addr_state", "grade", "recommended_decision"] if col in filtered.columns]].astype(str).agg(" ".join, axis=1)
        filtered = filtered[search_space.str.contains(search_text, case=False, na=False)]
    st.markdown("</div>", unsafe_allow_html=True)
    return filtered, search_text


def kpi_cards(filtered: pd.DataFrame) -> None:
    """Show the eight executive cards that answer portfolio health in under 30 seconds."""
    kpi = portfolio_kpis(filtered)
    health = portfolio_health_score(filtered)
    health_style = "health-good" if health >= 70 else "health-watch" if health >= 45 else "health-risk"
    cards = [
        ("Borrower Accounts", format_number(kpi["borrowers"]), "Number of scored borrower records in the selected view", ""),
        ("Total Exposure Amount", format_currency(kpi["exposure"]), "Loan amount at risk before repayments and recoveries", ""),
        ("Average Predicted Default Probability", format_pct(kpi["average_pd"]), "Average model-estimated chance of borrower default", ""),
        ("Expected Credit Loss", format_currency(kpi["expected_loss"]), "Estimated loss using default probability, loss severity, and exposure", "health-risk" if kpi["expected_loss"] > 0 else ""),
        ("Expected Profit After Credit Loss", format_currency(kpi["expected_profit"]), "Profit after funding cost, operating cost, and expected credit loss", "health-good" if kpi["expected_profit"] >= 0 else "health-risk"),
        ("Average Portfolio Yield", format_pct(kpi["portfolio_yield"]), "Average contractual interest rate on the selected portfolio", ""),
        ("Average Risk-Adjusted Return", format_pct(kpi["expected_return"]), "Expected profit divided by total exposure", "health-good" if kpi["expected_return"] >= 0 else "health-risk"),
        ("Portfolio Health Score", f"{health:.0f}/100", "Composite signal from risk, return, concentration, and approval mix", health_style),
    ]
    first_row = st.columns(4)
    second_row = st.columns(4)
    for idx, (label, value, note, style) in enumerate(cards):
        with (first_row if idx < 4 else second_row)[idx % 4]:
            metric_card(label, value, note, style=style)


def build_segment_table(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Create a readable segment table for portfolio and policy review."""
    summary = segment_summary(df, by)
    if summary.empty:
        return summary
    renamed = summary.rename(
        columns={
            by: USER_FRIENDLY_COLUMNS.get(by, by.replace("_", " ").title()),
            "borrowers": "Borrower Accounts",
            "exposure": "Exposure Amount",
            "average_pd": "Average Predicted Default Probability",
            "default_rate": "Observed Default Rate",
            "expected_loss": "Expected Credit Loss",
            "expected_profit": "Expected Profit After Credit Loss",
            "average_return": "Average Expected Profit Rate",
            "average_yield": "Average Portfolio Yield",
            "exposure_share": "Exposure Share",
        }
    )
    return renamed


def show_management_attention(filtered: pd.DataFrame) -> None:
    """Show computed alerts so effort is visible without long report paragraphs."""
    section_header("Management Attention", "Computed alerts from the selected portfolio, not static text.")
    for item in generate_executive_insights(filtered):
        severity = item.get("severity", "info")
        title = item.get("title", "Insight")
        message = item.get("message", "")
        insight_box(f"<b>{title}</b><br>{message}", kind=severity)


def borrower_queue(filtered: pd.DataFrame) -> pd.DataFrame:
    """Prepare the borrower queue with the few columns an analyst actually needs first."""
    columns = [
        "borrower_id",
        "facility_type",
        "term_months",
        "loan_amnt",
        "predicted_pd",
        "risk_band",
        "expected_loss",
        "expected_profit",
        "expected_return_pct",
        "recommended_decision",
        "grade",
        "addr_state",
    ]
    available = [column for column in columns if column in filtered.columns]
    table = filtered[available].copy()
    if "predicted_pd" in table.columns:
        table = table.sort_values(["predicted_pd", "expected_loss"], ascending=[False, False])
    return table.rename(columns=USER_FRIENDLY_COLUMNS)


def show_borrower_detail(row: pd.Series) -> None:
    """Render the selected borrower in credit-officer language."""
    decision = str(row.get("recommended_decision", "Manual Review"))
    badge_kind = "decline" if any(term in decision.lower() for term in ["reject", "decline"]) else "review" if any(term in decision.lower() for term in ["review", "condition", "reprice"]) else "approve"
    st.markdown(badge(decision, badge_kind), unsafe_allow_html=True)
    metric_row = st.columns(4)
    with metric_row[0]:
        metric_card("Predicted Default Probability", format_pct(row.get("predicted_pd", 0)), str(row.get("risk_band", "Risk category")))
    with metric_row[1]:
        metric_card("Expected Credit Loss", format_currency(row.get("expected_loss", 0)), "Modelled credit cost for this borrower")
    with metric_row[2]:
        metric_card("Expected Profit After Credit Loss", format_currency(row.get("expected_profit", 0)), format_pct(row.get("expected_return_pct", 0)))
    with metric_row[3]:
        metric_card("Loan Amount", format_currency(row.get("loan_amnt", 0)), f"{safe_float(row.get('term_months')):.0f} month tenor")

    st.markdown("<br>", unsafe_allow_html=True)
    field_grid(
        {
            "Facility type": str(row.get("facility_type", "Not available")),
            "Credit grade": f"{row.get('grade', 'Not available')} / {row.get('sub_grade', 'Not available')}",
            "Annual income": format_currency(row.get("annual_inc", 0)),
            "Debt-to-income burden": f"{safe_float(row.get('dti')):.2f}",
            "Home ownership": str(row.get("home_ownership", "Not available")),
            "Employment length": str(row.get("emp_length", "Not available")),
            "Revolving credit utilization": f"{safe_float(row.get('revol_util')):.1f}%",
            "Credit inquiries in last six months": f"{safe_float(row.get('inq_last_6mths')):.0f}",
        }
    )

    risk_drivers, mitigants = top_reason_codes(row)
    left, right = st.columns(2)
    with left:
        section_header("Main Risk Drivers", "Reasons the borrower may need conditions, review, or decline.")
        for item in risk_drivers or ["No major adverse driver was detected from the available fields."]:
            insight_box(item, kind="warning")
    with right:
        section_header("Risk Mitigants", "Factors that support repayment capacity or lower risk.")
        for item in mitigants or ["No major risk mitigant was detected from the available fields."]:
            insight_box(item, kind="success")

    section_header("Suggested Analyst Note", "Plain-language note suitable for a credit memo.")
    insight_box(suggested_analyst_note(row), kind="info")


def show_simulator(row: pd.Series) -> None:
    """Provide scenario testing without pretending that original borrower data was changed."""
    section_header("Credit Decision Simulator", "Scenario testing only. It does not change the original borrower record.")
    c1, c2, c3 = st.columns(3)
    with c1:
        new_amount = st.number_input("Scenario loan amount", min_value=500.0, max_value=100_000.0, value=float(row.get("loan_amnt", 10_000) or 10_000), step=500.0)
        new_tenor = st.select_slider("Scenario loan tenor", options=[12, 24, 36, 48, 60, 72], value=int(safe_float(row.get("term_months"), 36)) if int(safe_float(row.get("term_months"), 36)) in [12, 24, 36, 48, 60, 72] else 36)
    with c2:
        new_rate = st.slider("Scenario portfolio yield", min_value=0.03, max_value=0.35, value=float(row.get("int_rate_decimal", 0.12) or 0.12), step=0.005, format="%.3f")
        new_loss_severity = st.slider("Loss severity if borrower defaults", min_value=0.20, max_value=0.90, value=float(row.get("lgd", 0.65) or 0.65), step=0.05)
    with c3:
        new_debt_burden = st.slider("Debt-to-income burden", min_value=0.0, max_value=60.0, value=float(row.get("dti", 20) or 20), step=1.0)
        new_utilization = st.slider("Revolving credit utilization", min_value=0.0, max_value=120.0, value=float(row.get("revol_util", 45) or 45), step=1.0)

    new_delinquencies = st.slider("Delinquencies in last two years", min_value=0, max_value=10, value=int(safe_float(row.get("delinq_2yrs"), 0)), step=1)
    simulated_probability = simulate_pd_from_changes(
        row,
        {
            "dti": new_debt_burden,
            "revol_util": new_utilization,
            "term_months": new_tenor,
            "delinq_2yrs": new_delinquencies,
        },
    )
    economics = calculate_economics(simulated_probability, new_amount, new_rate, new_tenor, new_loss_severity)
    scenario_decision = recommend_decision(simulated_probability, economics["expected_return_pct"])
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Scenario Predicted Default Probability", format_pct(simulated_probability), "Adjusted using transparent sensitivity rules")
    with m2:
        metric_card("Scenario Expected Credit Loss", format_currency(economics["expected_loss"]), "Loss if this scenario is approved")
    with m3:
        metric_card("Scenario Expected Profit", format_currency(economics["expected_profit"]), format_pct(economics["expected_return_pct"]))
    with m4:
        metric_card("Scenario Lending Recommendation", scenario_decision, "Based on probability and risk-adjusted return")


def model_assurance_panel() -> None:
    """Summarize model evidence without overloading the main dashboard."""
    section_header("Model Assurance Snapshot", "Compact validation evidence for supervisors and model reviewers.")
    comparison = load_report("model_comparison_metrics.csv")
    calibration = load_report("calibration_comparison.csv")
    if comparison.empty:
        insight_box("Model comparison report was not found. Upload the modelling outputs to show model evidence.", kind="warning")
        return
    comparison = comparison.copy()
    comparison["Readable Model Name"] = comparison["model"].apply(humanize_model_name)
    best = comparison.sort_values("roc_auc", ascending=False).iloc[0]
    calibrated = calibration.sort_values("brier_score", ascending=True).iloc[0] if not calibration.empty else None
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Best Model Ranking Quality", humanize_model_name(best["model"]), f"Model ranking quality: {safe_float(best.get('roc_auc')):.3f}")
    with c2:
        if calibrated is not None:
            metric_card("Best Probability Calibration", humanize_model_name(calibrated["model"]), f"Calibration error: {safe_float(calibrated.get('brier_score')):.3f}")
        else:
            metric_card("Best Probability Calibration", "Not available", "Upload calibration report")
    with c3:
        metric_card("Explainability Evidence", "Available", "Feature importance and reason-code style explanations")

    with st.expander("Show detailed model validation evidence"):
        display = comparison.rename(
            columns={
                "roc_auc": "Model Ranking Quality",
                "pr_auc": "Risky Borrower Detection Quality",
                "accuracy": "Overall Classification Accuracy",
                "precision": "Precision on Predicted Defaulters",
                "recall": "Defaulter Capture Rate",
                "f1_score": "Balanced Classification Score",
                "brier_score": "Probability Calibration Error",
                "ks_statistic": "Risk Separation Strength",
                "gini_coefficient": "Model Separation Coefficient",
                "approval_rate": "Approval Rate Under Policy",
                "expected_return_pct": "Expected Profit Rate After Credit Loss",
            }
        )
        show_cols = [col for col in ["Readable Model Name", "Model Ranking Quality", "Risky Borrower Detection Quality", "Defaulter Capture Rate", "Probability Calibration Error", "Risk Separation Strength", "Expected Profit Rate After Credit Loss"] if col in display.columns]
        st.dataframe(display[show_cols], use_container_width=True, hide_index=True)
        left, right = st.columns(2)
        with left:
            calibration_plot = get_plot_path("calibration_curve_champion.png")
            if calibration_plot.exists():
                st.image(str(calibration_plot), caption="Calibration curve for the champion model")
        with right:
            shap_plot = get_plot_path("shap_summary_random_forest.png")
            if shap_plot.exists():
                st.image(str(shap_plot), caption="Main reasons behind model predictions")


def export_panel(filtered: pd.DataFrame, selected_row: pd.Series | None) -> None:
    """Offer outputs that make the dashboard committee-ready."""
    section_header("Reports and Exports", "Evidence pack for committee review, portfolio discussion, or interview demonstration.")
    export_cols = [
        "borrower_id", "facility_type", "term_months", "loan_amnt", "predicted_pd", "risk_band",
        "expected_loss", "expected_profit", "expected_return_pct", "recommended_decision", "grade", "addr_state",
    ]
    available = [col for col in export_cols if col in filtered.columns]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "Download filtered portfolio summary",
            data=filtered[available].rename(columns=USER_FRIENDLY_COLUMNS).to_csv(index=False),
            file_name="filtered_retail_credit_portfolio.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "Download Excel evidence pack",
            data=dataframe_to_excel_bytes(filtered[available].rename(columns=USER_FRIENDLY_COLUMNS), sheet_name="Credit Portfolio"),
            file_name="retail_credit_evidence_pack.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c3:
        if selected_row is not None:
            st.download_button(
                "Download borrower credit memo",
                data=borrower_credit_memo(selected_row),
                file_name=f"credit_memo_{selected_row.get('borrower_id', 'borrower')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with st.expander("Show executive model report"):
        report = load_markdown_report("executive_model_report.md")
        if report:
            st.markdown(report)
        else:
            st.info("Executive model report is not available in the reports folder.")


def show_story_strip(filtered: pd.DataFrame) -> None:
    """Make the weeks of work visible through a compact product story, not long text blocks."""
    kpi = portfolio_kpis(filtered)
    story = [
        ("1", "Borrower data captured", "Facility, income, employment, credit behavior, location, tenor"),
        ("2", "Credit risk estimated", f"Average predicted default probability is {format_pct(kpi['average_pd'])}"),
        ("3", "Loss calculated", f"Expected credit loss is {format_currency(kpi['expected_loss'])}"),
        ("4", "Return tested", f"Expected profit after credit loss is {format_currency(kpi['expected_profit'])}"),
        ("5", "Decision recommended", "Approve, approve with conditions, manual review, or decline"),
    ]
    cols = st.columns(5)
    for col, (num, title, body) in zip(cols, story):
        with col:
            insight_box(f"<b>{num}. {title}</b><br>{body}", kind="info")


# -----------------------------
# Main single-dashboard workflow
# -----------------------------
hero(
    "Retail Credit Intelligence Workspace",
    "A single light-theme analyst dashboard that turns retail lending data into borrower decisions, facility strategy, expected credit loss, expected profit after credit loss, and model assurance evidence.",
)

try:
    raw_df = load_portfolio()
except Exception as exc:
    st.error(f"The scored credit portfolio could not be loaded: {exc}")
    st.stop()

portfolio = add_derived_bands(raw_df)
filtered, search_text = apply_filters(portfolio)

if filtered.empty:
    st.warning("No borrower records match the selected slicers. Relax one or more filters to continue.")
    st.stop()

show_story_strip(filtered)
kpi_cards(filtered)

st.markdown("<hr>", unsafe_allow_html=True)

# Main analytics grid: portfolio intelligence on the left, management and model evidence on the right.
left_area, right_area = st.columns([1.55, 1.0])
with left_area:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    section_header("Portfolio Risk and Return", "Identify which business segments create loss, profit, or policy concern.")
    dimension_label = st.selectbox(
        "Analyze the portfolio by",
        list(DIMENSIONS.keys()),
        index=0,
        help="This slicer replaces many separate dashboard pages. It lets the same charts analyze facility, tenor, grade, geography, employment, and recommendations.",
    )
    dimension = DIMENSIONS[dimension_label]
    summary = segment_summary(filtered, dimension)
    if summary.empty:
        st.info("The selected dimension is not available for this dataset.")
    else:
        chart_summary = summary.head(12).copy()
        chart_summary[dimension] = chart_summary[dimension].astype(str)
        chart_title = f"Expected Credit Loss by {dimension_label}"
        st.plotly_chart(horizontal_bar(chart_summary, "expected_loss", dimension, chart_title, height=360), use_container_width=True)
        st.plotly_chart(
            scatter_chart(
                summary.head(20),
                "average_pd",
                "average_return",
                f"Risk and Profitability Map by {dimension_label}",
                color=dimension,
                size="exposure",
                height=390,
            ),
            use_container_width=True,
        )
        with st.expander("Show segment table"):
            table = build_segment_table(filtered, dimension)
            st.dataframe(table, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    section_header("Facility and Tenor View", "Direct answer to which loan products and loan tenors are safer or riskier.")
    facility_summary = segment_summary(filtered, "facility_type").head(10)
    tenor_summary = segment_summary(filtered, "term_months").copy()
    c1, c2 = st.columns(2)
    with c1:
        if not facility_summary.empty:
            st.plotly_chart(bar_chart(facility_summary, "facility_type", "average_pd", "Average Predicted Default Probability by Facility", height=330), use_container_width=True)
    with c2:
        if not tenor_summary.empty:
            tenor_summary["term_months"] = tenor_summary["term_months"].astype(str) + " months"
            st.plotly_chart(bar_chart(tenor_summary, "term_months", "expected_profit", "Expected Profit After Credit Loss by Loan Tenor", height=330), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_area:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    health = portfolio_health_score(filtered)
    st.plotly_chart(gauge(health, "Portfolio Health Score"), use_container_width=True)
    risk_distribution = filtered["risk_band"].value_counts().reset_index()
    risk_distribution.columns = ["Risk Category", "Borrower Accounts"]
    st.plotly_chart(risk_band_bar(risk_distribution, "Borrower Accounts by Risk Category"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    show_management_attention(filtered)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Borrower decision desk: queue plus selected borrower profile.
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
section_header("Borrower Decision Desk", "Find the accounts that require action, then review the selected borrower in plain credit-officer language.")
queue = borrower_queue(filtered)
queue_display = queue.head(50).copy()
st.dataframe(queue_display, use_container_width=True, hide_index=True)

borrower_options = filtered.sort_values("predicted_pd", ascending=False)["borrower_id"].astype(str).head(500).tolist()
selected_borrower = st.selectbox("Select borrower for detailed credit review", borrower_options)
selected_row = filtered[filtered["borrower_id"].astype(str) == str(selected_borrower)].iloc[0]
show_borrower_detail(selected_row)
with st.expander("Run scenario simulator for selected borrower"):
    show_simulator(selected_row)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

bottom_left, bottom_right = st.columns([1.25, 1.0])
with bottom_left:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    model_assurance_panel()
    st.markdown("</div>", unsafe_allow_html=True)

with bottom_right:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    export_panel(filtered, selected_row)
    st.markdown("</div>", unsafe_allow_html=True)

st.caption(
    "Governance note: This is a production-style educational prototype. A real bank would require live bureau data, rejected application data, KYC/AML controls, override logging, access controls, audit trails, and formal model validation approval before production use."
)
