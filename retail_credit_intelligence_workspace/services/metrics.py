from __future__ import annotations

import numpy as np
import pandas as pd


def portfolio_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Compute executive KPIs from the scored portfolio."""
    exposure = df["ead"].sum() if "ead" in df else df["loan_amnt"].sum()
    expected_loss = df["expected_loss"].sum()
    expected_profit = df["expected_profit"].sum()
    return {
        "borrowers": len(df),
        "exposure": exposure,
        "average_pd": df["predicted_pd"].mean(),
        "expected_loss": expected_loss,
        "expected_return": expected_profit / exposure if exposure else np.nan,
        "expected_profit": expected_profit,
        "portfolio_yield": df.get("int_rate_decimal", pd.Series(dtype=float)).mean(),
        "approval_rate": df["recommended_decision"].str.contains("Approve", case=False, na=False).mean(),
        "default_rate": df.get("default_flag", pd.Series(dtype=float)).mean(),
    }


def segment_summary(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Aggregate portfolio risk and return by a selected business dimension."""
    if by not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.groupby(by, dropna=False)
        .agg(
            borrowers=("borrower_id", "count"),
            exposure=("ead", "sum"),
            average_pd=("predicted_pd", "mean"),
            default_rate=("default_flag", "mean"),
            expected_loss=("expected_loss", "sum"),
            expected_profit=("expected_profit", "sum"),
            average_return=("expected_return_pct", "mean"),
            average_yield=("int_rate_decimal", "mean"),
        )
        .reset_index()
    )
    total_exposure = grouped["exposure"].sum()
    grouped["exposure_share"] = grouped["exposure"] / total_exposure if total_exposure else 0
    return grouped.sort_values("expected_loss", ascending=False)


def portfolio_health_score(df: pd.DataFrame) -> float:
    """Calculate a simple 0-100 health score from risk, return, concentration, and approval quality."""
    kpi = portfolio_kpis(df)
    avg_pd = kpi["average_pd"] or 0
    expected_return = kpi["expected_return"] or 0
    approval_rate = kpi["approval_rate"] or 0
    facility = segment_summary(df, "facility_type")
    concentration = facility["exposure_share"].max() if not facility.empty else 1
    pd_score = max(0, 100 - avg_pd * 350)
    return_score = min(100, max(0, 50 + expected_return * 400))
    concentration_score = max(0, 100 - concentration * 100)
    approval_score = 100 - abs(approval_rate - 0.55) * 120
    score = 0.35 * pd_score + 0.25 * return_score + 0.20 * concentration_score + 0.20 * approval_score
    return float(np.clip(score, 0, 100))


def risk_migration_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """Create a proxy risk migration table using issue vintage and risk band mix."""
    if "issue_d" not in df.columns or "risk_band" not in df.columns:
        return pd.DataFrame()
    temp = df.copy()
    temp["issue_period"] = pd.to_datetime(temp["issue_d"], format="%b-%Y", errors="coerce").dt.to_period("Q").astype(str)
    temp = temp.dropna(subset=["issue_period"])
    if temp.empty:
        return pd.DataFrame()
    mix = temp.groupby(["issue_period", "risk_band"]).size().reset_index(name="count")
    mix["share"] = mix["count"] / mix.groupby("issue_period")["count"].transform("sum")
    return mix
