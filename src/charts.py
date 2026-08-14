"""Chart generation — saves PNGs to /visualizations/."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from src.scorer import assign_signal

VIZ_DIR = os.path.join(os.path.dirname(__file__), "..", "visualizations")
os.makedirs(VIZ_DIR, exist_ok=True)

PALETTE = {
    "STRONG BUY": "#2d6a4f",
    "BUY":        "#52b788",
    "WATCH":      "#f4a261",
    "AVOID":      "#c1121f",
}

DARK_BG   = "#0f1117"
CARD_BG   = "#1a1d27"
GOLD      = "#c9a84c"
TEXT_MAIN = "#e8e0d0"
TEXT_SUB  = "#9a9182"


def _style():
    plt.rcParams.update({
        "figure.facecolor": DARK_BG,
        "axes.facecolor":   CARD_BG,
        "axes.edgecolor":   "#2e3147",
        "axes.labelcolor":  TEXT_SUB,
        "xtick.color":      TEXT_SUB,
        "ytick.color":      TEXT_SUB,
        "text.color":       TEXT_MAIN,
        "grid.color":       "#2e3147",
        "grid.linestyle":   "--",
        "grid.alpha":       0.6,
        "font.family":      "sans-serif",
    })


def _short(name: str) -> str:
    """Shorten submarket name for chart labels."""
    return name.split(" (")[0].split(" /")[0]


# ---------------------------------------------------------------------------
# 1. Composite Score Leaderboard
# ---------------------------------------------------------------------------

def chart_leaderboard(df: pd.DataFrame, as_of: str = "H1 2025") -> str:
    _style()
    ranked = df.sort_values("score", ascending=True)
    signals = [assign_signal(s)[0] for s in ranked["score"]]
    colors  = [PALETTE[s] for s in signals]

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(ranked["submarket_name"], ranked["score"],
                   color=colors, height=0.6, edgecolor="none")

    for bar, score, sig in zip(bars, ranked["score"], signals):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{score:.0f}  {sig}", va="center", fontsize=10, color=TEXT_MAIN)

    ax.set_xlim(0, 108)
    ax.set_xlabel("Composite Investment Score (0–100)", fontsize=11)
    ax.set_title(
        f"DMV Multifamily Residential — Submarket Investment Rankings\nClass-A/B Apartments  ·  {as_of}",
        fontsize=14, color=GOLD, pad=16
    )
    ax.axvline(72, color=PALETTE["STRONG BUY"], lw=1.2, ls="--", alpha=0.7, label="Strong Buy ≥72")
    ax.axvline(60, color=PALETTE["BUY"],        lw=1.2, ls=":",  alpha=0.7, label="Buy ≥60")

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in PALETTE.items()]
    ax.legend(handles=legend_patches, loc="lower right", framealpha=0.15,
              labelcolor=TEXT_MAIN, edgecolor="#2e3147")
    ax.grid(axis="x")
    ax.set_axisbelow(True)

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "01_leaderboard.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 2. Radar — top 3 submarkets across all 7 factors
# ---------------------------------------------------------------------------

RADAR_LABELS = [
    "Rent\nGrowth", "Occupancy\n& Leasing", "Job\nMarket",
    "Renter\nDemographics", "Income", "Transit", "Supply\nRisk"
]
RADAR_COLS = [
    "score_rent_growth", "score_occupancy", "score_job_market",
    "score_demographics", "score_income_quality", "score_transit", "score_supply_risk"
]


def chart_radar(df: pd.DataFrame, top_n: int = 3) -> str:
    _style()
    top = df.nlargest(top_n, "score")

    N = len(RADAR_LABELS)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"polar": True})
    ax.set_facecolor(CARD_BG)
    fig.patch.set_facecolor(DARK_BG)

    colors = ["#c9a84c", "#52b788", "#64b5f6"]
    for (_, row), color in zip(top.iterrows(), colors):
        vals = [row[c] for c in RADAR_COLS] + [row[RADAR_COLS[0]]]
        ax.plot(angles, vals, color=color, linewidth=2, label=_short(row["submarket_name"]))
        ax.fill(angles, vals, color=color, alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(RADAR_LABELS, fontsize=10, color=TEXT_MAIN)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color=TEXT_SUB)
    ax.set_ylim(0, 100)
    ax.grid(color="#2e3147", linestyle="--", alpha=0.5)
    ax.spines["polar"].set_color("#2e3147")

    ax.set_title("Top 3 Submarkets — Factor Score Comparison",
                 fontsize=14, color=GOLD, pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.38, 1.15),
              framealpha=0.15, labelcolor=TEXT_MAIN, edgecolor="#2e3147")

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "02_radar.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 3. Rent Growth vs Occupancy Bubble
# ---------------------------------------------------------------------------

def chart_rent_vs_occupancy(df: pd.DataFrame) -> str:
    _style()
    signals = [assign_signal(s)[0] for s in df["score"]]
    colors  = [PALETTE[s] for s in signals]
    sizes   = (df["score"] * 4).values

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.scatter(df["occupancy_rate"], df["rent_growth_yoy"],
               s=sizes, c=colors, alpha=0.85, edgecolors="#ffffff22", linewidth=0.5)

    for _, row in df.iterrows():
        ax.annotate(
            _short(row["submarket_name"]),
            (row["occupancy_rate"], row["rent_growth_yoy"]),
            xytext=(6, 4), textcoords="offset points",
            fontsize=8.5, color=TEXT_MAIN, alpha=0.9
        )

    ax.set_xlabel("Physical Occupancy Rate (%)", fontsize=12)
    ax.set_ylabel("Effective Rent Growth YoY (%)", fontsize=12)
    ax.set_title("Rent Growth vs. Occupancy — DMV Multifamily Residential\nBubble size = Composite Score  ·  H1 2025",
                 fontsize=13, color=GOLD, pad=14)
    ax.axhline(df["rent_growth_yoy"].mean(), color=TEXT_SUB, lw=1, ls="--", alpha=0.5)
    ax.axvline(df["occupancy_rate"].mean(),  color=TEXT_SUB, lw=1, ls="--", alpha=0.5)
    ax.text(df["occupancy_rate"].min() + 0.05, df["rent_growth_yoy"].mean() + 0.04,
            " Market Avg", color=TEXT_SUB, fontsize=9, alpha=0.7)
    ax.grid(True)
    ax.set_axisbelow(True)

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in PALETTE.items()]
    ax.legend(handles=legend_patches, loc="lower right", framealpha=0.15,
              labelcolor=TEXT_MAIN, edgecolor="#2e3147")

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "03_rent_vs_occupancy.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 4. Rent by unit type — grouped bar for top 4 submarkets
# ---------------------------------------------------------------------------

def chart_rent_by_unit_type(df: pd.DataFrame, top_n: int = 4) -> str:
    _style()
    top = df.nlargest(top_n, "score")

    unit_types = ["Studio", "1BR", "2BR", "3BR"]
    rent_cols  = ["avg_rent_studio", "avg_rent_1br", "avg_rent_2br", "avg_rent_3br"]
    unit_colors = ["#c9a84c", "#52b788", "#64b5f6", "#9b72cf"]

    x = np.arange(top_n)
    width = 0.2
    offsets = np.linspace(-1.5, 1.5, 4) * width

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, (col, label, color) in enumerate(zip(rent_cols, unit_types, unit_colors)):
        rents = top[col].values
        bars = ax.bar(x + offsets[i], rents, width=width,
                      label=label, color=color, alpha=0.88, edgecolor="none")
        for bar, val in zip(bars, rents):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                    f"${val:,.0f}", ha="center", va="bottom", fontsize=7.5, color=TEXT_SUB)

    ax.set_xticks(x)
    ax.set_xticklabels([_short(n) for n in top["submarket_name"]], fontsize=10, color=TEXT_MAIN)
    ax.set_ylabel("Effective Monthly Rent ($)", fontsize=11)
    ax.set_title("Effective Rent by Unit Type — Top 4 Submarkets\nClass-A Multifamily Residential  ·  H1 2025",
                 fontsize=13, color=GOLD, pad=14)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend(framealpha=0.15, labelcolor=TEXT_MAIN, edgecolor="#2e3147")
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "04_rent_by_unit_type.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 5. NOI vs Price-per-Unit scatter (implied yield)
# ---------------------------------------------------------------------------

def chart_noi_vs_price(df: pd.DataFrame) -> str:
    _style()
    signals = [assign_signal(s)[0] for s in df["score"]]
    colors  = [PALETTE[s] for s in signals]

    df = df.copy()
    df["implied_yield"] = (df["avg_noi_per_unit"] / df["price_per_unit"] * 100).round(2)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.scatter(df["price_per_unit"] / 1000, df["avg_noi_per_unit"] / 1000,
               s=df["score"] * 4, c=colors, alpha=0.85,
               edgecolors="#ffffff22", linewidth=0.5)

    for _, row in df.iterrows():
        ax.annotate(
            f"{_short(row['submarket_name'])}\n{row['implied_yield']:.1f}% yield",
            (row["price_per_unit"] / 1000, row["avg_noi_per_unit"] / 1000),
            xytext=(6, 3), textcoords="offset points",
            fontsize=8, color=TEXT_MAIN, alpha=0.9
        )

    ax.set_xlabel("Price Per Unit ($K)", fontsize=12)
    ax.set_ylabel("Annual NOI Per Unit ($K)", fontsize=12)
    ax.set_title("NOI vs. Acquisition Price Per Unit\nImplied yield labeled  ·  H1 2025",
                 fontsize=13, color=GOLD, pad=14)
    ax.grid(True)
    ax.set_axisbelow(True)

    legend_patches = [mpatches.Patch(color=c, label=l) for l, c in PALETTE.items()]
    ax.legend(handles=legend_patches, loc="upper left", framealpha=0.15,
              labelcolor=TEXT_MAIN, edgecolor="#2e3147")

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "05_noi_vs_price.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out
