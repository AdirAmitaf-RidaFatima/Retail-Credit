from __future__ import annotations

import pandas as pd

from services.metrics import portfolio_kpis, segment_summary


def generate_executive_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    """Generate computed business insights rather than hard-coded dashboard text."""
    insights: list[dict[str, str]] = []
    if df.empty:
        return [{"severity": "warning", "title": "No portfolio records", "message": "Relax filters to view portfolio insights."}]
    kpi = portfolio_kpis(df)
    if kpi["average_pd"] > 0.25:
        insights.append({
            "severity": "danger",
            "title": "Portfolio PD is elevated",
            "message": f"Average PD is {kpi['average_pd']:.1%}. Management should review approval cut-offs and high-risk segment growth.",
        })
    elif kpi["average_pd"] > 0.15:
        insights.append({
            "severity": "warning",
            "title": "Moderate portfolio risk",
            "message": f"Average PD is {kpi['average_pd']:.1%}. Continue monitoring tenor, facility, and grade concentration.",
        })
    else:
        insights.append({
            "severity": "info",
            "title": "Controlled average PD",
            "message": f"Average PD is {kpi['average_pd']:.1%}, indicating a relatively controlled risk profile under current filters.",
        })
    facility = segment_summary(df, "facility_type")
    if not facility.empty:
        top_loss = facility.iloc[0]
        insights.append({
            "severity": "warning" if top_loss["expected_loss"] > 0 else "info",
            "title": "Expected loss concentration",
            "message": f"{top_loss['facility_type']} contributes the largest expected loss at ${top_loss['expected_loss']:,.0f}; review pricing, limits, and tenor for this facility.",
        })
        top_conc = facility.sort_values("exposure_share", ascending=False).iloc[0]
        if top_conc["exposure_share"] > 0.50:
            insights.append({
                "severity": "warning",
                "title": "Facility concentration risk",
                "message": f"{top_conc['facility_type']} represents {top_conc['exposure_share']:.1%} of exposure. Portfolio limits should be monitored.",
            })
    if kpi["expected_return"] < 0:
        insights.append({
            "severity": "danger",
            "title": "Negative expected return",
            "message": "Expected profit after credit losses is negative. Risk-based pricing or approval cutoffs should be revisited.",
        })
    else:
        insights.append({
            "severity": "info",
            "title": "Positive loss-adjusted return",
            "message": f"Expected return after credit losses is {kpi['expected_return']:.1%}. Validate this by segment before growth decisions.",
        })
    return insights[:6]


def suggested_analyst_note(row: pd.Series) -> str:
    """Create a concise credit memo note from borrower-level fields."""
    decision = row.get("recommended_decision", "Manual Review")
    pd_value = float(row.get("predicted_pd", 0))
    facility = row.get("facility_type", "facility")
    tenor = row.get("term_months", "N/A")
    expected_return = float(row.get("expected_return_pct", 0))
    return (
        f"Borrower is assessed under {facility} with {tenor}-month tenor. "
        f"Model PD is {pd_value:.1%}; recommended action is {decision}. "
        f"Expected return after modelled credit loss is {expected_return:.1%}. "
        "Review affordability, bureau-style indicators, and policy exceptions before final sanction."
    )
