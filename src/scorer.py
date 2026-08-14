"""
Multifamily Investment Scoring Engine
--------------------------------------
Scores each DMV submarket on a 0–100 scale using a weighted model aligned
with Class-A multifamily underwriting criteria.

Weight breakdown (sums to 1.0):
  Rent Growth (momentum)       0.22
  Occupancy & Absorption       0.18
  Job Market Strength          0.18
  Population / Demographics    0.15
  Income Quality               0.12
  Transit & Walkability        0.10
  Market Risk (crime, supply)  0.05
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _norm(series: pd.Series, invert: bool = False) -> pd.Series:
    """Min-max normalise to [0, 1]. Set invert=True for 'lower is better' metrics."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([0.5] * len(series), index=series.index)
    normed = (series - mn) / (mx - mn)
    return (1 - normed) if invert else normed


# ---------------------------------------------------------------------------
# Score components
# ---------------------------------------------------------------------------

WEIGHTS: Dict[str, float] = {
    "rent_growth":      0.22,
    "occupancy":        0.18,
    "job_market":       0.18,
    "demographics":     0.15,
    "income_quality":   0.12,
    "transit":          0.10,
    "market_risk":      0.05,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Rent Growth (higher YoY + 3yr = better) ---
    df["_rent_growth"] = (
        _norm(df["rent_growth_yoy"]) * 0.6 +
        _norm(df["rent_growth_3yr"]) * 0.4
    )

    # --- Occupancy & Absorption ---
    df["_occupancy"] = (
        _norm(df["occupancy_rate"]) * 0.6 +
        _norm(df["absorption_rate"]) * 0.4
    )

    # --- Job Market (growth + low unemployment) ---
    df["_job_market"] = (
        _norm(df["job_growth_yoy"]) * 0.6 +
        _norm(df["unemployment_rate"], invert=True) * 0.4
    )

    # --- Demographics (population growth + renter %, prime renter age) ---
    df["_demographics"] = (
        _norm(df["population_growth_yoy"]) * 0.40 +
        _norm(df["net_migration_score"]) * 0.35 +
        _norm(df["age_25_44_pct"]) * 0.25
    )

    # --- Income Quality (income level + growth) ---
    df["_income_quality"] = (
        _norm(df["median_hh_income"]) * 0.5 +
        _norm(df["income_growth_yoy"]) * 0.5
    )

    # --- Transit & Walkability ---
    df["_transit"] = (
        _norm(df["transit_score"]) * 0.40 +
        _norm(df["walk_score"]) * 0.35 +
        _norm(df["metro_distance_miles"], invert=True) * 0.25
    )

    # --- Market Risk (lower crime + manageable supply pipeline) ---
    # Pipeline risk: high pipeline relative to absorption is risky
    df["_pipeline_risk"] = df["new_supply_units_pipeline"] * (1 - df["absorption_rate"] / 100)
    df["_market_risk"] = (
        _norm(df["crime_index"], invert=True) * 0.5 +
        _norm(df["_pipeline_risk"], invert=True) * 0.5
    )

    # --- Composite Score ---
    df["score"] = (
        df["_rent_growth"]    * WEIGHTS["rent_growth"]    +
        df["_occupancy"]      * WEIGHTS["occupancy"]      +
        df["_job_market"]     * WEIGHTS["job_market"]     +
        df["_demographics"]   * WEIGHTS["demographics"]   +
        df["_income_quality"] * WEIGHTS["income_quality"] +
        df["_transit"]        * WEIGHTS["transit"]        +
        df["_market_risk"]    * WEIGHTS["market_risk"]
    ) * 100

    df["score"] = df["score"].round(1)

    # Component scores (0–100 for display)
    for col, key in [
        ("_rent_growth", "score_rent_growth"),
        ("_occupancy", "score_occupancy"),
        ("_job_market", "score_job_market"),
        ("_demographics", "score_demographics"),
        ("_income_quality", "score_income_quality"),
        ("_transit", "score_transit"),
        ("_market_risk", "score_market_risk"),
    ]:
        df[key] = (df[col] * 100).round(1)

    return df


def assign_signal(score: float) -> Tuple[str, str]:
    """Return (signal_label, color) based on composite score."""
    if score >= 72:
        return "STRONG BUY", "#2d6a4f"
    elif score >= 60:
        return "BUY", "#52b788"
    elif score >= 48:
        return "WATCH", "#f4a261"
    else:
        return "AVOID", "#c1121f"
