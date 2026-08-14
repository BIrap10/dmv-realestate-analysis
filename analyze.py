#!/usr/bin/env python3
"""
DMV Multifamily Residential Investment Analysis
------------------------------------------------
Scores 8 DMV submarkets for Class-A/B apartment investment viability.
Pulls live market data from Zillow Research, BLS, and Census ACS.

Usage:
    python analyze.py              # Full analysis with live data + charts
    python analyze.py --no-charts  # Scores only
    python analyze.py --refresh    # Force re-fetch from APIs (bypass cache)
    python analyze.py --no-live    # Use curated data only, skip API calls
"""

import argparse
import sys
from datetime import datetime

import pandas as pd

from src.dmv_data import get_dataframe
from src.scorer import compute_scores, assign_signal, WEIGHTS
from src.long_term_scorer import compute_long_term_scores, assign_lt_signal, LONG_TERM_WEIGHTS


AS_OF = "Q1 2026 (live)"


def print_header(live_context=None):
    print("\n" + "═" * 72)
    print("  DMV MULTIFAMILY RESIDENTIAL INVESTMENT ANALYSIS")
    print(f"  Class-A/B Apartments  ·  Washington DC / Virginia / Maryland  ·  {AS_OF}")
    print("═" * 72)

    if live_context and live_context.get("live"):
        print()
        print("  LIVE MARKET DATA — Q1 2026:")
        if live_context.get("zori_q1_2026"):
            yoy  = f"{live_context['zori_q1_yoy']:+.1f}% YoY" if live_context.get("zori_q1_yoy") else ""
            qoq  = f"  |  {live_context['zori_q_over_q']:+.1f}% QoQ" if live_context.get("zori_q_over_q") else ""
            print(f"    Zillow ZORI  DC MSA Q1 2026  →  ${live_context['zori_q1_2026']:,.0f} avg rent  |  {yoy}{qoq}")
        if live_context.get("zori_latest"):
            print(f"    Zillow ZORI  latest ({live_context.get('zori_as_of','')})  →  ${live_context['zori_latest']:,.0f}")
        if live_context.get("bls_unemp_q1_2026") is not None:
            yoy_u = ""
            if live_context.get("bls_unemp_q1_2025"):
                diff = live_context["bls_unemp_q1_2026"] - live_context["bls_unemp_q1_2025"]
                yoy_u = f"  |  {diff:+.1f}pp vs Q1 2025"
            print(f"    BLS  DC MSA Q1 2026 avg       →  {live_context['bls_unemp_q1_2026']:.1f}% unemployment{yoy_u}")
        elif live_context.get("bls_unemployment") is not None:
            print(f"    BLS  DC MSA latest            →  {live_context['bls_unemployment']:.1f}% unemployment  "
                  f"({live_context.get('bls_unemployment_period','')})")
        if live_context.get("census_median_income"):
            print(f"    Census ACS                    →  ${live_context['census_median_income']:,} median HH income")
        print(f"    Sources: {', '.join(live_context.get('sources', []))}")


def print_summary_table(df: pd.DataFrame, live_context: dict = None):
    sz = live_context.get("submarket_zori", {}) if live_context else {}
    has_live = any(v.get("available") for v in sz.values())

    header2 = "ZORI Q1'26" if has_live else "1BR Rent"
    print(f"\n{'Rank':<5} {'Submarket':<38} {'Score':>6}  {'Signal':<12} "
          f"{header2:>11} {'Occ.':>6} {'Cap Rate':>9}")
    print("─" * 88)

    for i, (_, row) in enumerate(df.sort_values("score", ascending=False).iterrows(), 1):
        signal, _ = assign_signal(row["score"])
        name = row["submarket_name"]
        live = sz.get(name, {})

        if has_live and live.get("available") and live.get("zori_q1_2026"):
            rent_str  = f"${live['zori_q1_2026']:>6,.0f}"
            yoy       = live.get("zori_yoy_growth")
            rent_str += f" ({yoy:+.1f}%)" if yoy else ""
        else:
            rent_str = f"${row['avg_rent_1br']:>6,} (curated)"

        print(
            f"  {i:<3} "
            f"{name:<38} "
            f"{row['score']:>5.1f}  "
            f"{signal:<12} "
            f"{rent_str:<16} "
            f"{row['occupancy_rate']:>5.1f}%  "
            f"    {row['cap_rate_market']:.1f}%"
        )


def print_long_term_table(df: pd.DataFrame):
    ranked = df.sort_values("lt_score", ascending=False)
    print(f"\n{'━' * 72}")
    print("  LONG-TERM INVESTMENT RANKING  (5–10 year hold)")
    print(f"{'━' * 72}")
    print(f"\n{'Rank':<5} {'Submarket':<38} {'LT Score':>8}  {'LT Signal':<22} {'Entry $/unit':>13} {'Stage':>6}")
    print("─" * 88)
    for i, (_, row) in enumerate(ranked.iterrows(), 1):
        sig, _ = assign_lt_signal(row["lt_score"])
        stage_label = ["", "Early", "Mid", "Late", "Mature"][int(row["gentrification_stage"])]
        print(
            f"  {i:<3} "
            f"{row['submarket_name']:<38} "
            f"{row['lt_score']:>7.1f}  "
            f"{sig:<22} "
            f"${row['price_per_unit']:>10,}  "
            f"{stage_label:>6}"
        )


def print_long_term_picks(df: pd.DataFrame, n: int = 3):
    top = df.nlargest(n, "lt_score")
    print(f"\n{'━' * 72}")
    print(f"  TOP {n} LONG-TERM OPPORTUNITIES  (5–10 year investment thesis)")
    print(f"{'━' * 72}")
    for rank, (_, row) in enumerate(top.iterrows(), 1):
        sig, _ = assign_lt_signal(row["lt_score"])
        stage_label = ["", "Early", "Mid", "Late", "Mature"][int(row["gentrification_stage"])]
        print(f"\n  #{rank} — {row['submarket_name']}  [Gentrification: {stage_label}]")
        print(f"       LT Score: {row['lt_score']:.1f} / 100   Signal: {sig}")
        print(f"       Entry:  ${row['price_per_unit']:,}/unit  |  Cap Rate: {row['cap_rate_market']:.1f}%  |  Rent Headroom: {row['rent_headroom']:.2f}x")
        print(f"       Zoning Trajectory: {row['zoning_trajectory']}/100  |  Infra Pipeline: {row['infrastructure_pipeline']}/100  |  Employer Pipeline: {row['employer_pipeline_score']}/100")
        print(f"       5-yr Pop Forecast: +{row['pop_growth_5yr_forecast']:.1f}%")
        print(f"       Major Employers: {', '.join(row['major_employers'][:2])}")
        if row.get("long_term_note"):
            print(f"\n       THESIS: {row['long_term_note']}")


def print_top_picks(df: pd.DataFrame, n: int = 3):
    top = df.nlargest(n, "score")
    print(f"\n{'━' * 72}")
    print(f"  TOP {n} INVESTMENT OPPORTUNITIES — DMV MULTIFAMILY")
    print(f"{'━' * 72}")

    for rank, (_, row) in enumerate(top.iterrows(), 1):
        signal, _ = assign_signal(row["score"])
        print(f"\n  #{rank} — {row['submarket_name']}  [{row['class']}]")
        print(f"       Score: {row['score']:.1f} / 100   Signal: {signal}")
        print(f"       Effective Rent   Studio: ${row['avg_rent_studio']:,}  "
              f"| 1BR: ${row['avg_rent_1br']:,}  "
              f"| 2BR: ${row['avg_rent_2br']:,}")
        print(f"       Rent Growth: {row['rent_growth_yoy']:+.1f}% YoY  "
              f"| Occ.: {row['occupancy_rate']:.1f}%  "
              f"| Absorption: {row['absorption_rate']}%  "
              f"| Concessions: {row['concession_rate']:.1f}%")
        print(f"       Cap Rate: {row['cap_rate_market']:.1f}%  "
              f"| Price/Unit: ${row['price_per_unit']:,}  "
              f"| NOI/Unit: ${row['avg_noi_per_unit']:,}/yr")
        print(f"       Jobs: +{row['job_growth_yoy']:.1f}% YoY  "
              f"| Unemployment: {row['unemployment_rate']:.1f}%  "
              f"| Federal Risk Score: {row['federal_workforce_risk']}/100")
        print(f"       Major Employers: {', '.join(row['major_employers'][:2])}")

        bullets = []
        if row["score_rent_growth"] >= 70:
            bullets.append("Rent momentum among the strongest in the corridor — NOI growth likely")
        if row["score_job_market"] >= 70:
            bullets.append("Private-sector job base limits federal headcount exposure")
        if row["score_demographics"] >= 70:
            bullets.append("Prime renter cohort (25–44) expanding faster than metro average")
        if row["score_transit"] >= 70:
            bullets.append("Metro proximity supports premium rent capture and lower concessions")
        if row["score_supply_risk"] >= 70:
            bullets.append("Lean supply pipeline relative to absorption reduces lease-up risk")
        for b in bullets[:3]:
            print(f"       › {b}")


def print_risk_flags(df: pd.DataFrame):
    print(f"\n{'━' * 72}")
    print("  RISK FLAGS")
    print(f"{'━' * 72}")
    risky = df[df["score"] < 48].sort_values("score")
    if risky.empty:
        print("  No AVOID-rated submarkets in current dataset.")
        return
    for _, row in risky.iterrows():
        issues = []
        if row["concession_rate"] > 5.0:
            issues.append(f"high concessions ({row['concession_rate']:.1f}%)")
        if row["absorption_rate"] < 78:
            issues.append(f"weak absorption ({row['absorption_rate']}%)")
        if row["federal_workforce_risk"] < 55:
            issues.append(f"elevated federal workforce risk ({row['federal_workforce_risk']}/100)")
        if row["new_supply_units_pipeline"] > 1200:
            issues.append(f"heavy pipeline ({row['new_supply_units_pipeline']:,} units)")
        print(f"  {row['submarket_name']}")
        print(f"    Score: {row['score']:.1f}  |  Issues: {', '.join(issues) if issues else 'multiple weak factors'}")


def print_weight_model():
    print(f"\n{'━' * 72}")
    print("  SCORING MODEL — WEIGHT BREAKDOWN")
    print(f"{'━' * 72}")
    label_map = {
        "rent_growth":    "Rent Growth Momentum       ",
        "occupancy":      "Occupancy & Leasing        ",
        "job_market":     "Job Market Quality         ",
        "demographics":   "Renter Demographics        ",
        "income_quality": "Income Quality             ",
        "transit":        "Transit & Walkability      ",
        "supply_risk":    "Supply Risk                ",
    }
    for key, w in WEIGHTS.items():
        bar = "█" * int(w * 100 // 3)
        print(f"  {label_map[key]}  {bar:<12}  {int(w*100)}%")


def main():
    parser = argparse.ArgumentParser(description="DMV Multifamily Investment Analysis")
    parser.add_argument("--no-charts", action="store_true")
    parser.add_argument("--map",       action="store_true", help="Generate interactive investment heatmap")
    parser.add_argument("--refresh",   action="store_true", help="Force re-fetch from APIs")
    parser.add_argument("--no-live",   action="store_true", help="Skip live API calls")
    args = parser.parse_args()

    live_context = {}
    if not args.no_live:
        try:
            from src.data_fetcher import fetch_live_context
            live_context = fetch_live_context(force=args.refresh)
        except Exception as e:
            print(f"  [WARN] Live data fetch error: {e}")

    print_header(live_context)

    print("\n  Loading submarket data...")
    df = get_dataframe()
    print("  Running current-market scoring model...")
    df = compute_scores(df)
    print("  Running long-term scoring model...")
    df = compute_long_term_scores(df)

    print_summary_table(df, live_context)
    print_long_term_table(df)
    print_top_picks(df)
    print_long_term_picks(df)
    print_risk_flags(df)
    print_weight_model()

    if not args.no_charts:
        print(f"\n{'━' * 72}")
        print("  GENERATING CHARTS")
        print(f"{'━' * 72}")
        try:
            from src.charts import (
                chart_leaderboard,
                chart_radar,
                chart_rent_vs_occupancy,
                chart_rent_by_unit_type,
                chart_noi_vs_price,
            )
            for fn, label, kwargs in [
                (chart_leaderboard,       "Investment Leaderboard",         {"as_of": AS_OF}),
                (chart_radar,             "Factor Radar (Top 3)",           {}),
                (chart_rent_vs_occupancy, "Rent Growth vs Occupancy",       {}),
                (chart_rent_by_unit_type, "Rent by Unit Type (Top 4)",      {}),
                (chart_noi_vs_price,      "NOI vs Price Per Unit",          {}),
            ]:
                path = fn(df, **kwargs)
                print(f"  ✓ {label:<36} → {os.path.basename(path)}")
        except ImportError:
            print("  matplotlib not installed — run: pip install -r requirements.txt")

    if args.map:
        print(f"\n{'━' * 72}")
        print("  GENERATING INTERACTIVE HEATMAP")
        print(f"{'━' * 72}")
        try:
            from src.map_builder import build_map
            map_path = build_map(df, force_geojson=args.refresh)
            print(f"  Open in browser: file://{map_path}")
        except Exception as e:
            print(f"  Map generation failed: {e}")

    out_path = "data/processed/submarket_scores.csv"
    export_cols = [
        "submarket_name", "state", "class", "score",
        "avg_rent_1br", "rent_growth_yoy", "rent_growth_3yr",
        "occupancy_rate", "absorption_rate", "concession_rate",
        "job_growth_yoy", "federal_workforce_risk",
        "cap_rate_market", "price_per_unit", "avg_noi_per_unit",
        "score_rent_growth", "score_occupancy", "score_job_market",
        "score_demographics", "score_income_quality", "score_transit", "score_supply_risk",
    ]
    df.sort_values("score", ascending=False)[export_cols].to_csv(out_path, index=False)
    print(f"\n  Data exported → {out_path}")
    print(f"\n{'═' * 72}\n")


import os
if __name__ == "__main__":
    main()
