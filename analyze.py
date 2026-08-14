#!/usr/bin/env python3
"""
DMV Multifamily Investment Analysis
-------------------------------------
Run this script to generate scores, signals, and charts for all DMV submarkets.

Usage:
    python analyze.py              # Full analysis + charts
    python analyze.py --no-charts  # Scores only (faster)
"""

import argparse
import sys
import textwrap

import pandas as pd

from src.dmv_data import get_dataframe
from src.scorer import compute_scores, assign_signal, WEIGHTS


def print_header():
    print("\n" + "═" * 70)
    print("  DMV MULTIFAMILY INVESTMENT ANALYSIS  ·  Q4 2024")
    print("  Class-A Rental Housing  ·  Washington DC / Virginia / Maryland")
    print("═" * 70)


def print_summary_table(df: pd.DataFrame):
    ranked = df.sort_values("score", ascending=False)

    print(f"\n{'Rank':<5} {'Submarket':<38} {'Score':>6}  {'Signal':<12} {'Rent Gr.':>9} {'Occ.':>6}")
    print("─" * 80)

    for i, (_, row) in enumerate(ranked.iterrows(), 1):
        signal, _ = assign_signal(row["score"])
        print(
            f"  {i:<3} "
            f"{row['submarket_name']:<38} "
            f"{row['score']:>5.1f}  "
            f"{signal:<12} "
            f"{row['rent_growth_yoy']:>7.1f}%  "
            f"{row['occupancy_rate']:>5.1f}%"
        )


def print_top_picks(df: pd.DataFrame, n: int = 3):
    top = df.nlargest(n, "score")
    print(f"\n{'━' * 70}")
    print(f"  TOP {n} INVESTMENT OPPORTUNITIES")
    print(f"{'━' * 70}")

    for rank, (_, row) in enumerate(top.iterrows(), 1):
        signal, _ = assign_signal(row["score"])
        print(f"\n  #{rank} — {row['submarket_name']}")
        print(f"       Score: {row['score']:.1f} / 100  │  Signal: {signal}")
        print(f"       Rent (1BR): ${row['median_rent_1br']:,}  │  "
              f"YoY Growth: {row['rent_growth_yoy']:.1f}%  │  "
              f"Occupancy: {row['occupancy_rate']:.1f}%")
        print(f"       Job Growth: {row['job_growth_yoy']:.1f}%  │  "
              f"Unemployment: {row['unemployment_rate']:.1f}%  │  "
              f"Cap Rate: {row['cap_rate_market']:.1f}%")
        print(f"       Major Employers: {', '.join(row['major_employers'][:2])}")

        bullets = []
        if row["score_rent_growth"] >= 75:
            bullets.append("Strong rent momentum signals continued NOI growth")
        if row["score_job_market"] >= 70:
            bullets.append("Diversified, high-quality employment base reduces demand risk")
        if row["score_demographics"] >= 70:
            bullets.append("Prime renter cohort (25–44) growing faster than market average")
        if row["score_transit"] >= 70:
            bullets.append("Metro proximity supports premium rents and low vacancy")
        for b in bullets[:2]:
            print(f"       › {b}")


def print_weight_model():
    print(f"\n{'━' * 70}")
    print("  SCORING MODEL WEIGHTS")
    print(f"{'━' * 70}")
    label_map = {
        "rent_growth":    "Rent Growth Momentum   ",
        "occupancy":      "Occupancy & Absorption ",
        "job_market":     "Job Market Strength    ",
        "demographics":   "Population & Renters   ",
        "income_quality": "Income Quality         ",
        "transit":        "Transit & Walkability  ",
        "market_risk":    "Market Risk Mgmt       ",
    }
    for key, w in WEIGHTS.items():
        bar = "█" * int(w * 100 // 3)
        print(f"  {label_map[key]}  {bar:<12}  {int(w*100)}%")


def main():
    parser = argparse.ArgumentParser(description="DMV Real Estate Investment Analysis")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation")
    args = parser.parse_args()

    print_header()
    print("\n  Loading submarket data...")
    df = get_dataframe()

    print("  Running investment scoring model...")
    df = compute_scores(df)

    print_summary_table(df)
    print_top_picks(df)
    print_weight_model()

    if not args.no_charts:
        print(f"\n{'━' * 70}")
        print("  GENERATING CHARTS")
        print(f"{'━' * 70}")
        try:
            from src.charts import (
                chart_leaderboard,
                chart_radar,
                chart_rent_vs_occupancy,
                chart_score_breakdown,
            )
            for fn, label in [
                (chart_leaderboard,        "Leaderboard"),
                (chart_radar,              "Radar / Factor Breakdown"),
                (chart_rent_vs_occupancy,  "Rent vs Occupancy Bubble"),
                (chart_score_breakdown,    "Stacked Score Breakdown"),
            ]:
                path = fn(df)
                print(f"  ✓ {label:<32} → {path}")
            print("\n  All charts saved to /visualizations/")
        except ImportError:
            print("  matplotlib not installed — skipping charts.")
            print("  Run: pip install -r requirements.txt")

    # Export scored data
    out_path = "data/processed/submarket_scores.csv"
    df[[
        "submarket_name", "state", "score",
        "rent_growth_yoy", "rent_growth_3yr", "occupancy_rate",
        "job_growth_yoy", "unemployment_rate", "cap_rate_market",
        "price_per_unit", "score_rent_growth", "score_occupancy",
        "score_job_market", "score_demographics",
        "score_income_quality", "score_transit", "score_market_risk"
    ]].sort_values("score", ascending=False).to_csv(out_path, index=False)
    print(f"\n  Data exported → {out_path}")

    print(f"\n{'═' * 70}\n")


if __name__ == "__main__":
    main()
