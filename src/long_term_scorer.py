"""
Long-Term Investment Scoring Engine (5–10 Year Hold)
------------------------------------------------------
Answers a different question than the current-market scorer:
  NOT "what is performing best right now?"
  BUT "where is cheap to buy today that will appreciate the most over 5–10 years?"

The key insight: the factors that make a great investment today (high occupancy,
low concessions) are NOT the same as the factors that drive long-term appreciation.
Long-term returns are driven by buying before the market prices in future value.

Weight breakdown (sums to 1.0):
  Entry Value             0.22  — cheapest entry = biggest lever for IRR
  Growth Trajectory       0.20  — employer pipeline + population forecast
  Infrastructure Pipeline 0.18  — transit investments = biggest value driver in DMV
  Zoning / Density        0.15  — upzoning = density = appreciation
  Gentrification Stage    0.13  — earlier stage = more remaining upside (inverted)
  Rent Headroom           0.08  — income can still support meaningfully higher rents
  Long-Term Stability     0.04  — schools, safety as 10-year livability anchor
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

LONG_TERM_WEIGHTS: Dict[str, float] = {
    "entry_value":          0.22,
    "growth_trajectory":    0.20,
    "infrastructure":       0.18,
    "zoning_density":       0.15,
    "gentrification_stage": 0.13,
    "rent_headroom":        0.08,
    "lt_stability":         0.04,
}

assert abs(sum(LONG_TERM_WEIGHTS.values()) - 1.0) < 1e-9


def _norm(series: pd.Series, invert: bool = False) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([0.5] * len(series), index=series.index)
    normed = (series - mn) / (mx - mn)
    return (1 - normed) if invert else normed


def compute_long_term_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Rent headroom: (income × 30%) / (1BR annual rent). >1 = room to raise rents.
    df["rent_headroom"] = (df["median_hh_income"] * 0.30) / (df["avg_rent_1br"] * 12)

    # Entry Value — cheaper price per unit + higher cap rate = better entry
    df["_entry_value"] = (
        _norm(df["price_per_unit"],  invert=True) * 0.65 +
        _norm(df["cap_rate_market"])              * 0.35
    )

    # Growth Trajectory — employer pipeline + 5yr population forecast
    df["_growth"] = (
        _norm(df["employer_pipeline_score"]) * 0.55 +
        _norm(df["pop_growth_5yr_forecast"]) * 0.45
    )

    # Infrastructure Pipeline — transit / capital investment score
    df["_infrastructure"] = _norm(df["infrastructure_pipeline"])

    # Zoning / Density — county upzoning aggressiveness
    df["_zoning"] = _norm(df["zoning_trajectory"])

    # Gentrification Stage — INVERTED: Stage 1 (early) = highest score
    df["_gentrification"] = _norm(df["gentrification_stage"], invert=True)

    # Rent Headroom — higher ratio = more room to grow rents
    df["_rent_headroom"] = _norm(df["rent_headroom"])

    # Long-Term Stability — schools + safety
    df["_lt_stability"] = (
        _norm(df["school_rating"])             * 0.55 +
        _norm(df["crime_index"], invert=True)  * 0.45
    )

    # Composite Long-Term Score
    df["lt_score"] = (
        df["_entry_value"]    * LONG_TERM_WEIGHTS["entry_value"]    +
        df["_growth"]         * LONG_TERM_WEIGHTS["growth_trajectory"] +
        df["_infrastructure"] * LONG_TERM_WEIGHTS["infrastructure"]  +
        df["_zoning"]         * LONG_TERM_WEIGHTS["zoning_density"]  +
        df["_gentrification"] * LONG_TERM_WEIGHTS["gentrification_stage"] +
        df["_rent_headroom"]  * LONG_TERM_WEIGHTS["rent_headroom"]   +
        df["_lt_stability"]   * LONG_TERM_WEIGHTS["lt_stability"]
    ) * 100

    df["lt_score"] = df["lt_score"].round(1)

    # Component scores (0–100 for display)
    for raw, out in [
        ("_entry_value",   "lt_score_entry"),
        ("_growth",        "lt_score_growth"),
        ("_infrastructure","lt_score_infra"),
        ("_zoning",        "lt_score_zoning"),
        ("_gentrification","lt_score_gentrif"),
        ("_rent_headroom", "lt_score_headroom"),
        ("_lt_stability",  "lt_score_stability"),
    ]:
        df[out] = (df[raw] * 100).round(1)

    return df


def assign_lt_signal(score: float) -> Tuple[str, str]:
    if score >= 72:  return "STRONG LONG-TERM BUY", "#2d6a4f"
    if score >= 60:  return "LONG-TERM BUY",        "#52b788"
    if score >= 48:  return "HOLD / MONITOR",       "#f4a261"
    return "PASS",                                   "#c1121f"
