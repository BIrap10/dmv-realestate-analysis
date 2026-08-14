# DMV Multifamily Residential Investment Analysis
### Class-A/B Apartment Communities  ·  Washington DC / Virginia / Maryland  ·  Q1 2026

> A data-driven dual-score framework for evaluating multifamily residential investment opportunities across 9 DMV submarkets. Runs two independent scoring models: one for today's market performance, one for 5–10 year investment thesis. Pulls live rent and employment data directly from public APIs every time it runs. Built to support acquisition targeting and market-entry decisions for apartment operators.

---

## Live Data — Q1 2026

The script fetches real data at run time — no paid subscriptions required:

| Source | Metric | Q1 2026 Reading |
|---|---|---|
| **Zillow ZORI** (DC MSA) | Average rent — Q1 2026 | **$2,405** (+0.2% YoY) |
| **Zillow ZORI** (DC MSA) | Latest reading (Jun 2026) | **$2,448** |
| **BLS Public API** | DC MSA unemployment — Q1 2026 avg | **4.3%** (+0.8pp vs Q1 2025) |
| **Zillow ZORI zip-level** | Per-submarket rent estimates | All 9 submarkets matched |
| **Census ACS 2023** | Median household income | Optional — free key |

> **What's live vs. curated:** Rent (Zillow ZORI) and employment (BLS) are fetched live and reflect Q1/H1 2026 actuals. Submarket-level occupancy, pipeline, and concession data requires paid sources (CoStar/RealPage) — those figures are curated from the latest available public research (H1 2025) and updated manually.

---

## Dual Scoring Models

The analysis runs **two independent scoring models** that answer different questions:

### Model 1 — Current Market Score (what's performing best today)

Each submarket is scored **0–100** across 7 weighted factors calibrated for Class-A/B multifamily underwriting:

| Factor | Weight | Key Inputs |
|---|---|---|
| Rent Growth Momentum | 22% | YoY effective rent growth, 3-year cumulative |
| Occupancy & Leasing | 18% | Physical occupancy, absorption rate, days on market |
| Job Market Quality | 18% | Job growth, unemployment, federal workforce risk score |
| Renter Demographics | 15% | Renter %, prime cohort (25–44), population & net migration |
| Income Quality | 10% | Median HH income, income growth rate |
| Transit & Walkability | 10% | Walk score, transit score, Metro proximity |
| Supply Risk | 7% | Pipeline vs. absorption ratio, concession rate |

| Signal | Score |
|---|---|
| **STRONG BUY** | ≥ 72 |
| **BUY** | 60–71 |
| **WATCH** | 48–59 |
| **AVOID** | < 48 |

### Model 2 — Long-Term Investment Score (where to BUY for 5–10 year appreciation)

Weights fundamentally different factors — the things that drive *future* value, not current income:

| Factor | Weight | Rationale |
|---|---|---|
| Entry Value | 22% | Cheap price/unit = biggest lever for IRR — buy before the market prices in future value |
| Growth Trajectory | 20% | Employer pipeline + 5yr population forecast |
| Infrastructure Pipeline | 18% | Transit investments are the single biggest value driver in the DMV |
| Zoning / Density | 15% | Upzoning = density = appreciation |
| Gentrification Stage | 13% | Earlier = more remaining upside (Stage 1 scores highest, Stage 4 lowest) |
| Rent Headroom | 8% | Income still has room to support meaningfully higher rents |
| Long-Term Stability | 4% | Schools and safety as a 10-year livability anchor |

| Signal | Score |
|---|---|
| **STRONG LONG-TERM BUY** | ≥ 72 |
| **LONG-TERM BUY** | 60–71 |
| **HOLD / MONITOR** | 48–59 |
| **PASS** | < 48 |

---

## Results — Q1 2026

*Live: Zillow ZORI DC MSA Q1 2026 avg $2,405 · BLS unemployment Q1 2026 avg 4.3% (+0.8pp YoY)*

### Current Market Rankings (best income today)

| Rank | Submarket | Score | Signal | ZORI Q1 2026 | Occupancy | Cap Rate |
|---|---|---|---|---|---|---|
| 1 | Tysons / McLean (VA) | 85.6 | **STRONG BUY** | $3,095 (+1.8%) | 95.3% | 4.5% |
| 2 | Navy Yard / Capitol Riverfront (DC) | 80.4 | **STRONG BUY** | $2,126 (-1.6%) | 95.1% | 4.8% |
| 3 | Silver Spring (MD) | 57.9 | **WATCH** | $1,850 (+0.9%) | 94.2% | 5.1% |
| 4 | NoMa / H Street (DC) | 57.4 | **WATCH** | $2,452 (+0.3%) | 94.6% | 4.9% |
| 5 | Arlington / Rosslyn-Ballston (VA) | 54.7 | **WATCH** | $2,662 (-0.6%) | 93.8% | 4.6% |
| 6 | Alexandria / Old Town (VA) | 37.5 | **AVOID** | $2,511 (+0.8%) | 93.3% | 4.8% |
| 7 | Bethesda / Chevy Chase (MD) | 34.1 | **AVOID** | $3,185 (+8.1%) | 92.9% | 4.4% |
| 8 | Rockville (MD) | 24.4 | **AVOID** | $2,654 (+11.6%) | 92.9% | 5.2% |
| 9 | Gaithersburg (MD) | 4.7 | **AVOID** | $2,116 (-0.2%) | 91.9% | 5.5% |

> **Note on ZORI zip figures:** Zillow ZORI includes all rental types (apartments, condos, and single-family). Bethesda and Rockville read higher because their zip codes contain expensive single-family rentals. The composite scores use multifamily-specific curated rent data.

### Long-Term Investment Rankings (5–10 year hold thesis)

The ranking **completely reverses**. The markets that look worst today are the best long-term buys — because the market hasn't yet priced in their future catalysts.

| Rank | Submarket | LT Score | LT Signal | Entry $/unit | Gentrification Stage |
|---|---|---|---|---|---|
| 1 | **Gaithersburg (MD)** | **83.4** | **STRONG LONG-TERM BUY** | $218,000 | Early (Stage 1) |
| 2 | **Silver Spring (MD)** | **65.0** | **LONG-TERM BUY** | $248,000 | Mid (Stage 2) |
| 3 | **Rockville (MD)** | **64.4** | **LONG-TERM BUY** | $265,000 | Mid (Stage 2) |
| 4 | NoMa / H Street (DC) | 57.2 | Hold / Monitor | $310,000 | Late (Stage 3) |
| 5 | Arlington / Rosslyn-Ballston (VA) | 52.1 | Hold / Monitor | $328,000 | Late (Stage 3) |
| 6 | Navy Yard / Capitol Riverfront (DC) | 48.3 | Hold / Monitor | $298,000 | Mature (Stage 4) |
| 7 | Alexandria / Old Town (VA) | 43.7 | Pass | $302,000 | Mature (Stage 4) |
| 8 | Bethesda / Chevy Chase (MD) | 38.2 | Pass | $425,000 | Mature (Stage 4) |
| 9 | Tysons / McLean (VA) | 40.9 | Pass | $352,000 | Late (Stage 3) |

> The markets that score best in today's model (Tysons, Navy Yard) are expensive, late-stage, and already fully priced. A buyer entering today pays for value the market has already captured. The long-term model rewards buying *before* that pricing happens.

---

## Key Findings — Q1 2026

### Today's Best Operators: Tysons and Navy Yard

**Tysons / McLean** is the top current-market performer. Capital One, Booz Allen Hamilton, and Freddie Mac anchor a deep private-sector employment base that limits federal workforce exposure (risk score 88/100 — lowest in the analysis). Rent growth of **+5.4% YoY** leads the market, occupancy holds at **95.3%**, and absorption runs at 88% of delivered supply. DC MSA unemployment rose to 4.3% in Q1 2026 — Tysons's private-sector anchors insulate it from that trend more than any other DMV submarket.

**Rent:** Studio $2,050 · 1BR $2,720 · 2BR $3,640  
**Returns:** $352K/unit · $15,840 NOI/unit · 4.5% cap rate

**Navy Yard / Capitol Riverfront** has the lowest concession rate in the analysis (2.8%) and highest absorption (90%) — genuine demand pressure with no landlord giveaways. The renter profile is ideal for Class-A: 73% renter-occupied, 46% ages 25–44, median income $128K. At $298K/unit it is the most accessible price-entry of the two STRONG BUY markets.

**Rent:** Studio $2,380 · 1BR $2,890 · 2BR $3,850  
**Returns:** $298K/unit · $14,300 NOI/unit · 4.8% cap rate

### Watch List: Silver Spring & NoMa

Both show solid rent momentum (4.5% and 4.4% YoY) and top-tier Metro access, but federal workforce risk scores of 58 and 55 respectively create meaningful demand uncertainty given DC government employment contraction visible in Q1 2026 BLS data. **Notably, Silver Spring ranks #2 long-term** — the Purple Line opening 2027–28 is a major infrastructure catalyst that the current-market score does not reflect.

---

### The Long-Term Case: Gaithersburg, Silver Spring, Rockville

This is where the analysis diverges sharply from the current market story.

**Gaithersburg (MD) — #1 Long-Term Buy (LT Score 83.4)**

Today's model rates Gaithersburg last — elevated concessions (6.8%), weak absorption (71%), heavy NIST federal exposure. That's the correct read on today's income. But the long-term model tells the opposite story:

- **Cheapest entry in the DMV** at $218K/unit and 5.5% cap rate — you are buying early, not late
- **Stage 1 gentrification** — the earliest stage in the dataset, meaning the most remaining upside
- **Shady Grove Sector Plan** — Montgomery County upzoned the area aggressively for TOD (transit-oriented development) around the Shady Grove Metro station
- **I-270 Life Sciences Corridor** — NIST, AstraZeneca, and a growing biotech cluster are drawing high-income workers who will need housing
- **Employer pipeline score 79/100** — announced expansions over the next 3–5 years are the highest in MD suburbs
- Rent headroom: at current income levels, rents can grow materially before hitting affordability limits

The current weak metrics (concessions, absorption) reflect a market that is still being "discovered." That is exactly the entry point the long-term model targets.

**Silver Spring (MD) — #2 Long-Term Buy (LT Score 65.0)**

The **Purple Line light rail**, opening 2027–28, runs directly through Silver Spring and connects it to Bethesda and College Park without requiring a trip through downtown DC. Transit investments of this scale have historically driven 15–25% rent appreciation in the corridors they serve, compressing cap rates as institutional capital reprices the market. Silver Spring's infrastructure pipeline score is 92/100 — highest in the dataset.

**Rockville (MD) — #3 Long-Term Buy (LT Score 64.4)**

Rockville Town Center densification is underway. Mid-rise mixed-use is replacing surface parking, and the city's zoning trajectory is among the most aggressive in Montgomery County. At $265K/unit with a 5.2% cap rate, entry is still well below the DC/VA markets that have already re-rated.

---

## Interactive Heatmap

The project generates a self-contained interactive HTML map of the DMV showing investment intensity by submarket:

```bash
python analyze.py --map
```

**Output:** `visualizations/dmv_investment_map.html` — open in any browser.

Three toggleable layers:
- **Choropleth** — 33 zip-code areas filled by investment score (green → red)
- **Heatmap overlay** — Gaussian intensity gradient across the metro
- **Markers** — click any submarket for a full investment scorecard popup

---

## Usage

```bash
# Install dependencies (all free — no paid APIs)
pip install -r requirements.txt

# Full analysis: live Q1 2026 data + 5 charts
python analyze.py

# Also generate the interactive DMV heatmap
python analyze.py --map

# Force re-fetch from APIs (bypass 24h cache)
python analyze.py --refresh

# Scores only, no charts
python analyze.py --no-charts

# Skip live API calls, use curated data only
python analyze.py --no-live
```

**Optional:** Set `CENSUS_API_KEY` for Census ACS income data:
```bash
export CENSUS_API_KEY=your_free_key  # register at api.census.gov/key_signup.html
```

---

## Charts Generated

| File | Description |
|---|---|
| `01_leaderboard.png` | All 9 submarkets ranked by composite score |
| `02_radar.png` | Factor profile comparison — top 3 submarkets |
| `03_rent_vs_occupancy.png` | Rent growth vs. physical occupancy bubble chart |
| `04_rent_by_unit_type.png` | Effective rent by unit mix — top 4 submarkets |
| `05_noi_vs_price.png` | NOI per unit vs. acquisition price, implied yield |
| `dmv_investment_map.html` | Interactive DMV heatmap (open in browser) |

---

## Project Structure

```
dmv-realestate-analysis/
├── analyze.py                  # Main entry point — runs both scoring models
├── requirements.txt
├── src/
│   ├── data_fetcher.py         # Live APIs: Zillow ZORI, BLS, Census ACS
│   ├── dmv_data.py             # Curated submarket data (9 submarkets, 35+ fields each)
│   ├── scorer.py               # Current-market scoring engine
│   ├── long_term_scorer.py     # Long-term (5–10yr) scoring engine
│   ├── charts.py               # 5 publication-quality chart generators
│   └── map_builder.py          # Interactive Folium heatmap
├── data/
│   ├── raw/                    # API response cache (auto-populated)
│   └── processed/              # submarket_scores.csv
└── visualizations/             # Charts + interactive map HTML
```

---

## Adapting the Model

**Current-market model:**
- Adjust weights in `src/scorer.py → WEIGHTS` (must sum to 1.0)
- Tighten buy thresholds in `assign_signal()` in `src/scorer.py`

**Long-term model:**
- Adjust weights in `src/long_term_scorer.py → LONG_TERM_WEIGHTS` (must sum to 1.0)
- Update forward-looking fields in `src/dmv_data.py` as new pipeline/zoning data becomes available
- Adjust buy thresholds in `assign_lt_signal()` in `src/long_term_scorer.py`

**Adding markets:**
- Add a submarket dict to `src/dmv_data.py` with all required fields (including the forward-looking fields for the LT model)
- Add zip codes to `src/data_fetcher.py → SUBMARKET_ZIPS` for live ZORI
- Extend to other metros by swapping BLS series IDs and ZORI region name in `src/data_fetcher.py`

---

*Rent data: Zillow Research ZORI (Q1 2026 live). Employment: BLS LAUS (Q1 2026 live). Income: Census ACS 2023. Submarket occupancy, pipeline, and cap rates: curated from Zillow, Apartment List, CoStar (H1 2025). Not investment advice.*
