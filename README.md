# DMV Multifamily Residential Investment Analysis
### Class-A/B Apartment Communities  ·  Washington DC / Virginia / Maryland  ·  Q1 2026

> A data-driven scoring framework for evaluating multifamily residential investment opportunities across 9 DMV submarkets. Pulls live rent and employment data directly from public APIs every time it runs. Built to support acquisition targeting and market-entry decisions for apartment operators.

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

## Scoring Model

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

**Investment signals:**

| Signal | Score |
|---|---|
| **STRONG BUY** | ≥ 72 |
| **BUY** | 60–71 |
| **WATCH** | 48–59 |
| **AVOID** | < 48 |

---

## Results — Q1 2026

*Live: Zillow ZORI DC MSA Q1 2026 avg $2,405 · BLS unemployment Q1 2026 avg 4.3% (+0.8pp YoY)*

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

---

## Key Findings — Q1 2026

### 1. Tysons / McLean — #1 STRONG BUY

The strongest composite score in the corridor. Capital One, Booz Allen Hamilton, and Freddie Mac anchor a deep private-sector employment base that limits federal workforce exposure (risk score 88/100 — lowest in the analysis). Rent growth of **+5.4% YoY** leads the market, occupancy holds at **95.3%**, and absorption runs at 88% of delivered supply. Pipeline is elevated (3,400 units) but absorption track record supports it. DC MSA unemployment rose to 4.3% in Q1 2026 — Tysons's private-sector anchors insulate it from that trend more than any other DMV submarket.

**Rent:** Studio $2,050 · 1BR $2,720 · 2BR $3,640  
**Returns:** $352K/unit · $15,840 NOI/unit · 4.5% cap rate

### 2. Navy Yard / Capitol Riverfront — Best Urban Entry

Lowest concession rate in the analysis (2.8%) and highest absorption (90%) signal genuine demand pressure with no landlord giveaways needed. The renter profile is ideal for Class-A: 73% renter-occupied, 46% ages 25–44, median income $128K. At $298K/unit it is also the most accessible price-entry of the two STRONG BUY markets, with a 4.8% cap rate providing better going-in yield than Tysons. Federal workforce risk is moderate (72/100) — some DHS/DOT exposure, but Capitol Hill and tech-adjacent demand provides a buffer.

**Rent:** Studio $2,380 · 1BR $2,890 · 2BR $3,850  
**Returns:** $298K/unit · $14,300 NOI/unit · 4.8% cap rate

### 3. Watch List: Silver Spring & NoMa

Both show solid rent momentum (4.5% and 4.4% YoY) and top-tier Metro access, but federal workforce risk scores of 58 and 55 respectively create meaningful demand uncertainty given the DC government employment contraction visible in Q1 2026 BLS data. Revisit if the federal headcount picture stabilises in H2 2026.

### Risk: Gaithersburg & Rockville — Avoid

Gaithersburg carries the worst profile in the dataset: 6.8% concession rate (landlords giving 3+ weeks free), 71% absorption, a 980-unit pipeline, and 46/100 federal risk (NIST is a federal employer). Rockville is marginally better but still flagged on concessions, absorption, and federal risk simultaneously. Neither market justifies Class-A acquisition pricing without a significant discount.

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
├── analyze.py              # Main entry point
├── requirements.txt
├── src/
│   ├── data_fetcher.py     # Live APIs: Zillow ZORI, BLS, Census ACS
│   ├── dmv_data.py         # Curated submarket data (9 submarkets)
│   ├── scorer.py           # Weighted investment scoring engine
│   ├── charts.py           # 5 publication-quality chart generators
│   └── map_builder.py      # Interactive Folium heatmap
├── data/
│   ├── raw/                # API response cache (auto-populated)
│   └── processed/          # submarket_scores.csv
└── visualizations/         # Charts + interactive map HTML
```

---

## Adapting the Model

- **Adjust weights** in `src/scorer.py → WEIGHTS` (must sum to 1.0)
- **Add submarkets** in `src/dmv_data.py` — each is a keyed dict with ~25 metrics
- **Add zip codes** to a new submarket in `src/data_fetcher.py → SUBMARKET_ZIPS` for live ZORI
- **Extend to other metros** — swap BLS series IDs and ZORI region name in `src/data_fetcher.py`
- **Tighten buy thresholds** — adjust `assign_signal()` in `src/scorer.py`

---

*Rent data: Zillow Research ZORI (Q1 2026 live). Employment: BLS LAUS (Q1 2026 live). Income: Census ACS 2023. Submarket occupancy, pipeline, and cap rates: curated from Zillow, Apartment List, CoStar (H1 2025). Not investment advice.*
