from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DecisionResult:
    """Structured output for borrower decision support."""
    pd_value: float
    risk_band: str
    decision: str
    expected_loss: float
    expected_profit: float
    expected_return_pct: float
    explanation: str


def assign_risk_band(pd_value: float) -> str:
    """Translate PD into banking-readable risk bands."""
    if pd_value < 0.05:
        return "Low Risk"
    if pd_value < 0.12:
        return "Moderate Risk"
    if pd_value < 0.20:
        return "High Risk"
    return "Very High Risk"


def recommend_decision(pd_value: float, expected_return_pct: float) -> str:
    """Apply transparent credit policy rules to convert model risk into lending action."""
    if pd_value <= 0.08 and expected_return_pct > 0.00:
        return "Approve"
    if pd_value <= 0.15 and expected_return_pct > 0.00:
        return "Approve with Conditions"
    if pd_value <= 0.25:
        return "Manual Review"
    return "Decline"


def calculate_economics(
    pd_value: float,
    loan_amount: float,
    interest_rate: float,
    term_months: float,
    lgd: float,
    cost_of_funds: float = 0.08,
    operating_cost_rate: float = 0.01,
) -> dict[str, float]:
    """Calculate EL and profit using the approved project economics logic."""
    term_years = max(float(term_months or 0) / 12.0, 0.01)
    ead = float(loan_amount or 0)
    expected_loss = float(pd_value) * float(lgd) * ead
    interest_income = ead * float(interest_rate) * term_years
    funding_cost = ead * cost_of_funds * term_years
    operating_cost = ead * operating_cost_rate
    expected_profit = interest_income - funding_cost - operating_cost - expected_loss
    expected_return_pct = expected_profit / ead if ead else np.nan
    return {
        "ead": ead,
        "expected_loss": expected_loss,
        "expected_interest_income": interest_income,
        "funding_cost": funding_cost,
        "operating_cost": operating_cost,
        "expected_profit": expected_profit,
        "expected_return_pct": expected_return_pct,
    }


def simulate_pd_from_changes(original: pd.Series, changes: dict[str, float | str]) -> float:
    """Estimate a scenario PD by adjusting the original PD with explainable policy-style effects.

    The production model output is used as the anchor. The simulator then applies controlled
    sensitivity adjustments for affordability, utilization, tenor, and delinquency changes. This
    keeps the simulator transparent and avoids pretending that a full online model server exists.
    """
    pd_value = float(original.get("predicted_pd", 0.20))
    original_dti = float(original.get("dti", 18) or 18)
    original_util = float(original.get("revol_util", 45) or 45)
    original_term = float(original.get("term_months", 36) or 36)
    original_delinq = float(original.get("delinq_2yrs", 0) or 0)
    new_dti = float(changes.get("dti", original_dti))
    new_util = float(changes.get("revol_util", original_util))
    new_term = float(changes.get("term_months", original_term))
    new_delinq = float(changes.get("delinq_2yrs", original_delinq))
    dti_effect = (new_dti - original_dti) * 0.006
    util_effect = (new_util - original_util) * 0.0025
    term_effect = (new_term - original_term) * 0.003
    delinq_effect = (new_delinq - original_delinq) * 0.035
    simulated_pd = pd_value + dti_effect + util_effect + term_effect + delinq_effect
    return float(np.clip(simulated_pd, 0.005, 0.95))


def top_reason_codes(row: pd.Series) -> tuple[list[str], list[str]]:
    """Generate plain-language borrower risk drivers from available fields."""
    risk_drivers: list[str] = []
    mitigants: list[str] = []
    pd_value = float(row.get("predicted_pd", 0))
    dti = float(row.get("dti", np.nan))
    util = float(row.get("revol_util", np.nan))
    delinq = float(row.get("delinq_2yrs", 0) or 0)
    inquiries = float(row.get("inq_last_6mths", 0) or 0)
    term_months = float(row.get("term_months", 0) or 0)
    annual_inc = float(row.get("annual_inc", np.nan))
    expected_return = float(row.get("expected_return_pct", np.nan))

    if pd_value >= 0.20:
        risk_drivers.append("Model-estimated PD is above the high-risk decision threshold.")
    elif pd_value < 0.08:
        mitigants.append("Model-estimated PD is within the bank's lower-risk approval range.")

    if not np.isnan(dti) and dti >= 30:
        risk_drivers.append("Debt-to-income is elevated, reducing repayment capacity under stress.")
    elif not np.isnan(dti) and dti <= 15:
        mitigants.append("Debt burden is moderate, supporting repayment affordability.")

    if not np.isnan(util) and util >= 75:
        risk_drivers.append("Credit utilization is high, indicating possible liquidity pressure.")
    elif not np.isnan(util) and util <= 35:
        mitigants.append("Credit utilization is controlled, indicating available credit cushion.")

    if delinq > 0:
        risk_drivers.append("Recent delinquencies weaken borrower character and repayment history.")
    else:
        mitigants.append("No recent delinquencies are visible in the available bureau-style fields.")

    if inquiries >= 3:
        risk_drivers.append("Multiple recent inquiries may indicate credit hunger or refinancing stress.")

    if term_months >= 60:
        risk_drivers.append("Longer tenor increases the period over which income or macro shocks can occur.")
    else:
        mitigants.append("Shorter tenor limits the bank's time-at-risk compared with long-tenor lending.")

    if not np.isnan(annual_inc) and annual_inc >= 100_000:
        mitigants.append("Income level is above the sample median and provides repayment capacity.")

    if not np.isnan(expected_return) and expected_return < 0:
        risk_drivers.append("Expected return is negative after funding cost, operating cost, and expected loss.")
    elif not np.isnan(expected_return) and expected_return > 0.08:
        mitigants.append("Expected return remains positive after modelled credit losses.")

    return risk_drivers[:5], mitigants[:5]
