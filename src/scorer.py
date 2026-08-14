"""
Multifamily Residential Investment Scoring Engine
--------------------------------------------------
Scores each DMV submarket on a 0–100 scale using a weighted model calibrated
for Class-A/B multifamily residential acquisition underwriting.

Weight breakdown (sums to 1.0):
  Rent Growth Momentum       0.22  — YoY + 3yr rent appreciation
  Occupancy & Leasing        0.18  — physical occupancy, absorption, days on market
  Job Market Quality         0.18  — job growth, unemployment, federal workforce risk
  Renter Demographics        0.15  — renter %, prime cohort (25-44), migration
  Income Quality             0.10  — median HH income, income growth
  Transit & Walkability      0.10  — walk score, transit score, Metro proximity
  Supply Risk                0.07  — pipeline vs. absorption, concession rate
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def _norm(series: pd.Series, invert: bool = False) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([0.5] * len(series), index=series.index)
    normed = (series - mn) / (mx - mn)
    return (1 - normed) if invert else normed


WEIGHTS: Dict[str, float] = {
    "rent_growth":    0.22,
    "occupancy":      0.18,
    "job_market":     0.18,
    "demographics":   0.15,
    "income_quality": 0.10,
    "transit":        0.10,
    "supply_risk":    0.07,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Rent Growth
    df["_rent_growth"] = (
        _norm(df["rent_growth_yoy"]) * 0.55 +
        _norm(df["rent_growth_3yr"]) * 0.45
    )

    # Occupancy & Leasing (high occ + high absorption + low days on market = good)
    df["_occupancy"] = (
        _norm(df["occupancy_rate"])             * 0.50 +
        _norm(df["absorption_rate"])            * 0.30 +
        _norm(df["avg_days_on_market"], invert=True) * 0.20
    )

    # Job Market (growth + low unemployment + low federal risk)
    df["_job_market"] = (
        _norm(df["job_growth_yoy"])             * 0.45 +
        _norm(df["unemployment_rate"], invert=True) * 0.30 +
        _norm(df["federal_workforce_risk"])     * 0.25
    )

    # Renter Demographics
    df["_demographics"] = (
        _norm(df["renter_pct"])                 * 0.30 +
        _norm(df["age_25_44_pct"])              * 0.25 +
        _norm(df["population_growth_yoy"])      * 0.25 +
        _norm(df["net_migration_score"])        * 0.20
    )

    # Income Quality
    df["_income_quality"] = (
        _norm(df["median_hh_income"])   * 0.50 +
        _norm(df["income_growth_yoy"])  * 0.50
    )

    # Transit & Walkability
    df["_transit"] = (
        _norm(df["transit_score"])                    * 0.40 +
        _norm(df["walk_score"])                       * 0.35 +
        _norm(df["metro_distance_miles"], invert=True) * 0.25
    )

    # Supply Risk (high pipeline relative to absorption = risk; high concession = risk)
    df["_pipeline_excess"] = df["new_supply_units_pipeline"] * (1 - df["absorption_rate"] / 100)
    df["_supply_risk"] = (
        _norm(df["_pipeline_excess"], invert=True)  * 0.60 +
        _norm(df["concession_rate"], invert=True)   * 0.40
    )

    # Composite
    df["score"] = (
        df["_rent_growth"]    * WEIGHTS["rent_growth"]    +
        df["_occupancy"]      * WEIGHTS["occupancy"]      +
        df["_job_market"]     * WEIGHTS["job_market"]     +
        df["_demographics"]   * WEIGHTS["demographics"]   +
        df["_income_quality"] * WEIGHTS["income_quality"] +
        df["_transit"]        * WEIGHTS["transit"]        +
        df["_supply_risk"]    * WEIGHTS["supply_risk"]
    ) * 100

    df["score"] = df["score"].round(1)

    for raw_col, out_col in [
        ("_rent_growth",    "score_rent_growth"),
        ("_occupancy",      "score_occupancy"),
        ("_job_market",     "score_job_market"),
        ("_demographics",   "score_demographics"),
        ("_income_quality", "score_income_quality"),
        ("_transit",        "score_transit"),
        ("_supply_risk",    "score_supply_risk"),
    ]:
        df[out_col] = (df[raw_col] * 100).round(1)

    return df


def assign_signal(score: float) -> Tuple[str, str]:
    if score >= 72:
        return "STRONG BUY", "#2d6a4f"
    elif score >= 60:
        return "BUY", "#52b788"
    elif score >= 48:
        return "WATCH", "#f4a261"
    else:
        return "AVOID", "#c1121f"
