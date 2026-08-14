# DMV Multifamily Investment Analysis
### Class-A Rental Housing · Washington DC / Virginia / Maryland · Q4 2024

> A data-driven scoring framework for evaluating Class-A multifamily investment opportunities across the DC–Maryland–Virginia metro area. Built to support acquisition, underwriting, and market-entry decisions.

---

## Overview

This tool scores 8 key DMV submarkets across 7 quantitative factors — from rent growth momentum to job market depth — and outputs a composite investment signal (**STRONG BUY / BUY / WATCH / AVOID**) for each market.

It is designed for multifamily operators and investors evaluating where to deploy capital in the DMV corridor.

---

## Scoring Model

Scores are calculated on a **0–100 scale** using a weighted model calibrated to Class-A underwriting criteria:

| Factor | Weight | Data Points |
|---|---|---|
| Rent Growth Momentum | 22% | YoY & 3-year rent growth |
| Occupancy & Absorption | 18% | Occupancy rate, absorbed units % |
| Job Market Strength | 18% | Job growth rate, unemployment rate |
| Population & Demographics | 15% | Population growth, net migration, prime renter cohort (25–44) |
| Income Quality | 12% | Median HH income, income growth |
| Transit & Walkability | 10% | Transit score, walk score, Metro proximity |
| Market Risk | 5% | Crime index, supply pipeline risk |

**Signal thresholds:**
- `STRONG BUY` — Score ≥ 72
- `BUY` — Score 60–71
- `WATCH` — Score 48–59
- `AVOID` — Score < 48

---

## Results — Q4 2024

| Rank | Submarket | Score | Signal | Rent Growth | Occupancy |
|---|---|---|---|---|---|
| 1 | Navy Yard / Capitol Riverfront (DC) | 84.6 | **STRONG BUY** | +5.6% | 95.3% |
| 2 | Tysons / McLean (VA) | 81.5 | **STRONG BUY** | +5.1% | 95.1% |
| 3 | NoMa / H Street (DC) | 57.3 | **WATCH** | +4.8% | 94.8% |
| 4 | Arlington / Rosslyn-Ballston (VA) | 52.7 | **WATCH** | +4.2% | 94.1% |
| 5 | Silver Spring (MD) | 51.1 | **WATCH** | +4.6% | 94.4% |
| 6 | Alexandria / Old Town (VA) | 31.8 | **AVOID** | +3.7% | 93.6% |
| 7 | Bethesda / Chevy Chase (MD) | 31.1 | **AVOID** | +3.9% | 93.2% |
| 8 | Rockville / Gaithersburg (MD) | 5.0 | **AVOID** | +3.4% | 92.8% |

---

## Key Findings

### 1. Navy Yard / Capitol Riverfront — Top Pick
The strongest overall submarket in the DMV. Rent growth leads the region at **+5.6% YoY**, absorption holds at **91%** of delivered supply, and the demographic profile is ideal: 72% renters, median age 31. The continued buildout of the Capitol Riverfront BID and proximity to Amazon's HQ2 feeder jobs supports a durable demand thesis.

### 2. Tysons / McLean — Best Job Market Anchor
**+4.1% job growth** — the highest in the DMV — driven by Capital One, Booz Allen Hamilton, and Freddie Mac headquarters clustering within walkable distance of Silver Line stations. Crime index of 22 (national avg: 100) signals a safe, high-income renter base. Supply pipeline risk is elevated (3,200 units) but absorption history supports it.

### 3. NoMa / H Street — Best Value Entry
Strong fundamentals at a lower price-per-unit ($285K) than Navy Yard or Tysons. Rent growth of **+4.8% YoY** and walkability score of 88 make this the most accessible STRONG BUY-adjacent market. Amazon HQ2 job spillover from Arlington continues to lift demand eastward into NoMa.

### Caution: Rockville / Gaithersburg
Weakest absorption (76%) relative to a large pipeline (1,450 units), combined with lower transit scores and slower job growth. Unless underwritten at a significant discount to Bethesda, this submarket carries meaningful lease-up risk.

---

## Data Sources

| Dataset | Source |
|---|---|
| Rent & occupancy rates | Zillow Research (ZORI), CoStar |
| Employment & unemployment | US Bureau of Labor Statistics (BLS) |
| Population & demographic growth | US Census Bureau, ACS 5-Year Estimates |
| Income data | US Census Bureau ACS |
| Walk / Transit scores | Walk Score API |
| Crime index | FBI UCR / local PD data |
| Cap rates, price-per-unit | CoStar, RealPage |

> All figures reflect Q4 2024 / YE 2024 actuals. Pipeline data reflects projects under construction or permitted as of December 2024.

---

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full analysis (scores + charts)
python analyze.py

# Scores only (no chart output)
python analyze.py --no-charts
```

**Output:**
- Terminal: ranked leaderboard, top picks with investment rationale, model weight breakdown
- `/visualizations/`: 4 publication-quality charts
- `/data/processed/submarket_scores.csv`: full scored dataset

---

## Charts Generated

| File | Description |
|---|---|
| `01_leaderboard.png` | Horizontal bar chart — all submarkets ranked by composite score |
| `02_radar.png` | Spider chart — top 3 submarkets compared across all 7 factors |
| `03_rent_vs_occupancy.png` | Bubble chart — rent growth vs occupancy, bubble size = score |
| `04_score_breakdown.png` | Stacked bar — weighted contribution of each factor per submarket |

---

## Extending the Model

The scoring engine (`src/scorer.py`) is fully parameterised. To adjust for a different investment thesis:

- **Change weights** in `WEIGHTS` dict (must sum to 1.0)
- **Add new markets** via `src/dmv_data.py` — each submarket is a keyed dict
- **Adjust signal thresholds** in `assign_signal()` to tighten or relax buy criteria
- **Swap in live data** by replacing `get_dataframe()` with a CoStar or Zillow API call

---

*Built for real estate investment analysis. Data reflects public sources and market estimates; not investment advice.*
