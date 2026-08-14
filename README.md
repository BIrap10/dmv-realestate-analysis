# DMV Multifamily Residential Investment Analysis
### Class-A/B Apartment Communities  ·  Washington DC / Virginia / Maryland

> A data-driven scoring framework for evaluating multifamily residential investment opportunities across 8 DMV submarkets. Pulls live rent and employment data from public APIs. Built to support acquisition targeting and market-entry decisions for apartment operators.

---

## Live Data Sources

The script fetches real data at run time — no paid subscriptions required:

| Source | Data | Update Frequency |
|---|---|---|
| **Zillow Research ZORI** | DC MSA effective rent index | Monthly |
| **BLS Public API** | Metro unemployment & employment | Monthly |
| **Census ACS** | Median household income (optional key) | Annual |
| Curated submarket data | Occupancy, pipeline, NOI, transit | Manually refreshed |

Submarket-level data (occupancy, pipeline, cap rates) is curated from Zillow, Apartment List, and CoStar and stored in `src/dmv_data.py`.

---

## Scoring Model

Each submarket is scored **0–100** using 7 weighted factors calibrated for Class-A/B multifamily residential underwriting:

| Factor | Weight | Key Inputs |
|---|---|---|
| Rent Growth Momentum | 22% | YoY effective rent growth, 3-year cumulative |
| Occupancy & Leasing | 18% | Physical occupancy, absorption rate, days on market |
| Job Market Quality | 18% | Job growth, unemployment, federal workforce risk |
| Renter Demographics | 15% | Renter %, prime cohort (25–44), population & migration |
| Income Quality | 10% | Median HH income, income growth rate |
| Transit & Walkability | 10% | Walk score, transit score, Metro proximity |
| Supply Risk | 7% | Pipeline vs. absorption, concession rate |

**Investment signals:**

| Signal | Score Range |
|---|---|
| STRONG BUY | ≥ 72 |
| BUY | 60–71 |
| WATCH | 48–59 |
| AVOID | < 48 |

---

## Latest Results — H1 2025

*Live at run time: Zillow ZORI DC MSA $2,448 avg rent (+0.1% YoY) · BLS 4.1% unemployment (Jun 2026)*

| Rank | Submarket | Score | Signal | 1BR Rent | Occupancy | Cap Rate |
|---|---|---|---|---|---|---|
| 1 | Tysons / McLean (VA) | 84.3 | **STRONG BUY** | $2,720 | 95.3% | 4.5% |
| 2 | Navy Yard / Capitol Riverfront (DC) | 80.0 | **STRONG BUY** | $2,890 | 95.1% | 4.8% |
| 3 | Silver Spring (MD) | 55.9 | **WATCH** | $2,220 | 94.2% | 5.1% |
| 4 | NoMa / H Street (DC) | 55.5 | **WATCH** | $2,680 | 94.6% | 4.9% |
| 5 | Arlington / Rosslyn-Ballston (VA) | 51.7 | **WATCH** | $2,800 | 93.8% | 4.6% |
| 6 | Alexandria / Old Town (VA) | 33.6 | **AVOID** | $2,510 | 93.3% | 4.8% |
| 7 | Bethesda / Chevy Chase (MD) | 29.3 | **AVOID** | $2,750 | 92.9% | 4.4% |
| 8 | Rockville / Gaithersburg (MD) | 3.4 | **AVOID** | $2,080 | 92.4% | 5.3% |

---

## Key Findings

### 1. Tysons / McLean — #1 Pick

Strongest composite score in the DMV. Capital One, Booz Allen Hamilton, and Freddie Mac anchor a deep private-sector employment base that insulates demand from federal workforce cuts (risk score 88/100 — lowest federal exposure in the analysis). Rent growth leads the market at **+5.4% YoY** effective, occupancy holds at **95.3%**, and absorption of new supply runs at 88%. Pipeline is elevated (3,400 units) but track record of absorption supports it.

**Rent:** Studio $2,050 · 1BR $2,720 · 2BR $3,640  
**Returns:** $352K/unit acquisition · $15,840 NOI/unit · 4.5% cap rate

### 2. Navy Yard / Capitol Riverfront — Best Urban Bet

Lowest concession rate in the analysis (2.8%) signals genuine demand pressure. 90% absorption of delivered supply over the past 12 months is the highest in the corridor. The submarket's renter profile is ideal for Class-A: 73% renter-occupied, 46% ages 25–44, median income $128K. Federal workforce risk is moderate (score 72) given DHS/DOT anchoring, but offset by strong Capitol Hill and tech-sector demand.

**Rent:** Studio $2,380 · 1BR $2,890 · 2BR $3,850  
**Returns:** $298K/unit · $14,300 NOI/unit · 4.8% cap rate — best price-entry in the STRONG BUY tier

### 3. Watch List: Silver Spring & NoMa

Both markets show strong rent growth (4.5% and 4.4% respectively) and high Metro connectivity, but job market scores are held back by higher federal workforce exposure and slower private-sector job growth than the VA suburbs. Worth monitoring for a buy entry if federal employment stabilises.

### Risk: Rockville / Gaithersburg — Avoid

Six factors flagged simultaneously: 6.2% concession rate, 74% absorption (weakest in analysis), 1,560-unit pipeline, elevated federal risk, minimal transit access, and slowest job growth. Bethesda faces similar federal risk without the rental yield to compensate.

---

## Usage

```bash
# Install dependencies (all free — no paid APIs)
pip install -r requirements.txt

# Full analysis: live data + 5 charts
python analyze.py

# Force re-fetch from APIs (bypass 24h cache)
python analyze.py --refresh

# Scores only, no chart output
python analyze.py --no-charts

# Curated data only, skip API calls
python analyze.py --no-live
```

**Optional:** Set `CENSUS_API_KEY` for income data from Census ACS:
```bash
export CENSUS_API_KEY=your_free_key  # register at api.census.gov/key_signup.html
```

---

## Charts Generated

| File | Description |
|---|---|
| `01_leaderboard.png` | All submarkets ranked by composite score |
| `02_radar.png` | Factor profile comparison — top 3 submarkets |
| `03_rent_vs_occupancy.png` | Rent growth vs. physical occupancy bubble chart |
| `04_rent_by_unit_type.png` | Effective rent by unit mix — top 4 submarkets |
| `05_noi_vs_price.png` | NOI per unit vs. acquisition price, implied yield |

---

## Project Structure

```
dmv-realestate-analysis/
├── analyze.py              # Main entry point
├── requirements.txt
├── src/
│   ├── data_fetcher.py     # Live API integrations (Zillow, BLS, Census)
│   ├── dmv_data.py         # Curated submarket data (H1 2025)
│   ├── scorer.py           # Weighted scoring engine
│   └── charts.py           # 5 publication-quality chart generators
├── data/
│   ├── raw/                # API response cache (auto-populated)
│   └── processed/          # submarket_scores.csv
└── visualizations/         # Generated chart PNGs
```

---

## Adapting the Model

- **Adjust weights** in `src/scorer.py → WEIGHTS` (must sum to 1.0)
- **Add submarkets** in `src/dmv_data.py` — each is a keyed dict with ~25 metrics
- **Extend to other markets** — swap out the BLS/ZORI region codes in `src/data_fetcher.py`
- **Tighten buy signals** — adjust thresholds in `assign_signal()` in `src/scorer.py`

---

*Data sourced from Zillow Research, BLS, and US Census Bureau. Submarket-level figures from Zillow, Apartment List, CoStar. Not investment advice.*
