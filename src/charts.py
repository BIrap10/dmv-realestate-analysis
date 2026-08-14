"""Chart generation utilities — saves PNGs to /visualizations/."""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
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
        "figure.facecolor":  DARK_BG,
        "axes.facecolor":    CARD_BG,
        "axes.edgecolor":    "#2e3147",
        "axes.labelcolor":   TEXT_SUB,
        "xtick.color":       TEXT_SUB,
        "ytick.color":       TEXT_SUB,
        "text.color":        TEXT_MAIN,
        "grid.color":        "#2e3147",
        "grid.linestyle":    "--",
        "grid.alpha":        0.6,
        "font.family":       "sans-serif",
    })


# ---------------------------------------------------------------------------
# 1. Composite Score Leaderboard
# ---------------------------------------------------------------------------

def chart_leaderboard(df: pd.DataFrame) -> str:
    _style()
    ranked = df.sort_values("score", ascending=True)
    signals = [assign_signal(s)[0] for s in ranked["score"]]
    colors  = [PALETTE[s] for s in signals]

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(ranked["submarket_name"], ranked["score"], color=colors,
                   height=0.6, edgecolor="none")

    for bar, score, sig in zip(bars, ranked["score"], signals):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{score:.0f}  {sig}", va="center", fontsize=10, color=TEXT_MAIN)

    ax.set_xlim(0, 105)
    ax.set_xlabel("Composite Investment Score (0–100)", fontsize=11)
    ax.set_title("DMV Submarket Investment Rankings\nClass-A Multifamily | Q4 2024",
                 fontsize=15, color=GOLD, pad=16)
    ax.axvline(72, color=PALETTE["STRONG BUY"], lw=1.2, ls="--", alpha=0.7, label="Strong Buy threshold")
    ax.axvline(60, color=PALETTE["BUY"],        lw=1.2, ls=":",  alpha=0.7, label="Buy threshold")

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
# 2. Radar / Spider for top 3 submarkets
# ---------------------------------------------------------------------------

RADAR_LABELS = [
    "Rent\nGrowth", "Occupancy", "Jobs",
    "Demographics", "Income", "Transit", "Risk\nMgmt"
]
RADAR_COLS = [
    "score_rent_growth", "score_occupancy", "score_job_market",
    "score_demographics", "score_income_quality", "score_transit", "score_market_risk"
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
        ax.plot(angles, vals, color=color, linewidth=2, label=row["submarket_name"])
        ax.fill(angles, vals, color=color, alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(RADAR_LABELS, fontsize=11, color=TEXT_MAIN)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8, color=TEXT_SUB)
    ax.set_ylim(0, 100)
    ax.tick_params(colors=TEXT_SUB)
    ax.grid(color="#2e3147", linestyle="--", alpha=0.5)
    ax.spines["polar"].set_color("#2e3147")

    ax.set_title("Top 3 Submarkets — Factor Breakdown",
                 fontsize=14, color=GOLD, pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
              framealpha=0.15, labelcolor=TEXT_MAIN, edgecolor="#2e3147")

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "02_radar.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out


# ---------------------------------------------------------------------------
# 3. Rent Growth vs Occupancy Bubble Chart
# ---------------------------------------------------------------------------

def chart_rent_vs_occupancy(df: pd.DataFrame) -> str:
    _style()
    signals = [assign_signal(s)[0] for s in df["score"]]
    colors  = [PALETTE[s] for s in signals]
    sizes   = (df["score"] * 3).values

    fig, ax = plt.subplots(figsize=(11, 7))
    sc = ax.scatter(df["occupancy_rate"], df["rent_growth_yoy"],
                    s=sizes, c=colors, alpha=0.85, edgecolors="#ffffff22", linewidth=0.5)

    for _, row in df.iterrows():
        ax.annotate(
            row["submarket_name"].split(" (")[0].split(" /")[0],
            (row["occupancy_rate"], row["rent_growth_yoy"]),
            xytext=(6, 4), textcoords="offset points",
            fontsize=8.5, color=TEXT_MAIN, alpha=0.9
        )

    ax.set_xlabel("Occupancy Rate (%)", fontsize=12)
    ax.set_ylabel("YoY Rent Growth (%)", fontsize=12)
    ax.set_title("Rent Growth vs. Occupancy Rate\nBubble size = Composite Score",
                 fontsize=14, color=GOLD, pad=14)
    ax.axhline(df["rent_growth_yoy"].mean(), color=TEXT_SUB, lw=1, ls="--", alpha=0.5)
    ax.axvline(df["occupancy_rate"].mean(),  color=TEXT_SUB, lw=1, ls="--", alpha=0.5)
    ax.text(ax.get_xlim()[0] + 0.05, df["rent_growth_yoy"].mean() + 0.05,
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
# 4. Score breakdown stacked bar (component contributions)
# ---------------------------------------------------------------------------

def chart_score_breakdown(df: pd.DataFrame) -> str:
    _style()
    from src.scorer import WEIGHTS

    ranked = df.sort_values("score", ascending=False)

    component_keys = [
        ("score_rent_growth",    "Rent Growth",    "#c9a84c"),
        ("score_occupancy",      "Occupancy",      "#52b788"),
        ("score_job_market",     "Job Market",     "#64b5f6"),
        ("score_demographics",   "Demographics",   "#9b72cf"),
        ("score_income_quality", "Income Quality", "#f4a261"),
        ("score_transit",        "Transit",        "#48cae4"),
        ("score_market_risk",    "Market Risk",    "#a8dadc"),
    ]
    weight_list = [WEIGHTS["rent_growth"], WEIGHTS["occupancy"], WEIGHTS["job_market"],
                   WEIGHTS["demographics"], WEIGHTS["income_quality"],
                   WEIGHTS["transit"], WEIGHTS["market_risk"]]

    fig, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(ranked))
    bottom = np.zeros(len(ranked))

    for (col, label, color), weight in zip(component_keys, weight_list):
        contrib = (ranked[col] * weight).values
        ax.bar(x, contrib, bottom=bottom, label=f"{label} ({int(weight*100)}%)",
               color=color, alpha=0.88, width=0.7, edgecolor="none")
        bottom += contrib

    ax.set_xticks(x)
    ax.set_xticklabels(
        [s.split(" (")[0] for s in ranked["submarket_name"]],
        rotation=30, ha="right", fontsize=9, color=TEXT_MAIN
    )
    ax.set_ylabel("Score Contribution (weighted)", fontsize=11)
    ax.set_title("Composite Score Breakdown by Factor\nAll DMV Submarkets | Q4 2024",
                 fontsize=14, color=GOLD, pad=14)
    ax.legend(loc="upper right", framealpha=0.15, labelcolor=TEXT_MAIN,
              edgecolor="#2e3147", fontsize=9)
    ax.grid(axis="y")
    ax.set_axisbelow(True)

    plt.tight_layout()
    out = os.path.join(VIZ_DIR, "04_score_breakdown.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close()
    return out
