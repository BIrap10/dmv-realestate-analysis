"""
DMV Multifamily Residential — Curated Submarket Data
-----------------------------------------------------
Sources: Zillow Research, Apartment List, CoStar, BLS, US Census ACS, Walk Score,
         Montgomery County Master Plans, WMATA Capital Plan, Maryland DOT

Each submarket carries two sets of metrics:
  CURRENT  — snapshot of today's market (rent, occupancy, job market)
  FORWARD  — long-term investment drivers (infrastructure pipeline, zoning,
              gentrification stage, employer expansion plans)

Forward-looking field definitions:
  gentrification_stage     1=early (most upside), 2=mid, 3=late, 4=mature
  zoning_trajectory        0–100: how aggressively is the jurisdiction upzoning for density?
  employer_pipeline_score  0–100: announced / expected employer expansions in next 3–5 yr
  infrastructure_pipeline  0–100: planned transit / infrastructure investments
  pop_growth_5yr_forecast  % projected population growth over next 5 years
  rent_headroom            (median_hh_income × 0.30) / (avg_rent_1br × 12)
                           > 1.0 = income can still support meaningfully higher rents
"""

import pandas as pd

SUBMARKETS = {
    "Navy Yard / Capitol Riverfront (DC)": {
        "state": "DC",
        "class": "A",
        # --- Rent (effective, after concessions) ---
        "avg_rent_studio":  2_380,
        "avg_rent_1br":     2_890,
        "avg_rent_2br":     3_850,
        "avg_rent_3br":     5_100,
        "rent_growth_yoy":  4.9,     # % YoY H1 2025
        "rent_growth_3yr":  13.7,    # % cumulative 2022–2025
        "concession_rate":  2.8,     # % of asking rent (e.g., weeks free)
        # --- Occupancy & Leasing ---
        "occupancy_rate":   95.1,    # %
        "absorption_rate":  90,      # % of delivered units absorbed in 12 mo
        "avg_days_on_market": 19,
        # --- Supply Pipeline ---
        "new_supply_units_pipeline": 1_020,
        "typical_building_size":     280,  # avg units per building in submarket
        # --- Employment ---
        "job_growth_yoy":   3.2,
        "unemployment_rate": 3.3,
        "federal_workforce_risk": 72,   # 0=high risk, 100=no risk
        "major_employers": [
            "US Dept of Transportation", "Dept of Homeland Security",
            "DC United / Audi Field anchored retail", "Capitol Hill staff"
        ],
        # --- Demographics (renter profile) ---
        "median_hh_income":    128_000,
        "income_growth_yoy":   4.3,
        "population_growth_yoy": 2.9,
        "net_migration_score":   78,    # 0–100
        "renter_pct":            73,    # % of housing units that are renter-occupied
        "age_25_44_pct":         46,    # % of adult population
        # --- Location & Transit ---
        "walk_score":            91,
        "transit_score":         89,
        "metro_distance_miles":  0.4,
        # --- Investment Metrics ---
        "cap_rate_market":       4.8,   # % market cap rate for Class A
        "price_per_unit":        298_000,
        "avg_noi_per_unit":      14_300, # annual NOI $ / unit
        # --- Risk ---
        "crime_index":           36,
        "school_rating":         6.7,
        # --- Forward-looking (long-term investment thesis) ---
        "gentrification_stage":     4,    # mature — most appreciation already captured
        "zoning_trajectory":        52,   # RFK Stadium area redevelopment, but mostly built-out
        "employer_pipeline_score":  60,   # steady federal + Capitol Hill, no major expansions
        "infrastructure_pipeline":  62,   # RFK/Anacostia waterfront development; no new transit
        "pop_growth_5yr_forecast":  2.8,
        "long_term_note": "Excellent stabilized income asset. Most appreciation already captured; RFK Stadium redevelopment is the one wildcard for upside.",
    },

    "Tysons / McLean (VA)": {
        "state": "VA",
        "class": "A",
        "avg_rent_studio":  2_050,
        "avg_rent_1br":     2_720,
        "avg_rent_2br":     3_640,
        "avg_rent_3br":     4_850,
        "rent_growth_yoy":  5.4,
        "rent_growth_3yr":  14.8,
        "concession_rate":  3.1,
        "occupancy_rate":   95.3,
        "absorption_rate":  88,
        "avg_days_on_market": 17,
        "new_supply_units_pipeline": 3_400,
        "typical_building_size":     320,
        "job_growth_yoy":   4.3,
        "unemployment_rate": 2.6,
        "federal_workforce_risk": 88,
        "major_employers": [
            "Capital One HQ", "Booz Allen Hamilton HQ",
            "Freddie Mac HQ", "DXC Technology", "MITRE Corp"
        ],
        "median_hh_income":    162_000,
        "income_growth_yoy":   5.4,
        "population_growth_yoy": 3.0,
        "net_migration_score":   76,
        "renter_pct":            54,
        "age_25_44_pct":         37,
        "walk_score":            74,
        "transit_score":         76,
        "metro_distance_miles":  0.5,
        "cap_rate_market":       4.5,
        "price_per_unit":        352_000,
        "avg_noi_per_unit":      15_840,
        "crime_index":           21,
        "school_rating":         8.7,
        # --- Forward-looking ---
        "gentrification_stage":     3,    # late — Silver Line drove transformation, some runway left
        "zoning_trajectory":        62,   # Tysons master plan still has undeveloped phases
        "employer_pipeline_score":  74,   # Capital One expanding; Booz Allen, MITRE stable
        "infrastructure_pipeline":  55,   # Silver Line complete; no major new transit planned
        "pop_growth_5yr_forecast":  2.8,
        "long_term_note": "Strong income property but expensive entry limits long-term return. Best suited for an operator already in the market seeking scale.",
    },

    "NoMa / H Street (DC)": {
        "state": "DC",
        "class": "A",
        "avg_rent_studio":  2_100,
        "avg_rent_1br":     2_680,
        "avg_rent_2br":     3_600,
        "avg_rent_3br":     4_750,
        "rent_growth_yoy":  4.4,
        "rent_growth_3yr":  10.9,
        "concession_rate":  3.8,
        "occupancy_rate":   94.6,
        "absorption_rate":  85,
        "avg_days_on_market": 24,
        "new_supply_units_pipeline": 1_500,
        "typical_building_size":     240,
        "job_growth_yoy":   2.6,
        "unemployment_rate": 3.6,
        "federal_workforce_risk": 55,
        "major_employers": [
            "US Federal Govt (multiple agencies)", "Amazon HQ2 feeder",
            "Union Market district employers"
        ],
        "median_hh_income":    113_000,
        "income_growth_yoy":   3.7,
        "population_growth_yoy": 2.2,
        "net_migration_score":   68,
        "renter_pct":            69,
        "age_25_44_pct":         44,
        "walk_score":            88,
        "transit_score":         92,
        "metro_distance_miles":  0.3,
        "cap_rate_market":       4.9,
        "price_per_unit":        278_000,
        "avg_noi_per_unit":      13_620,
        "crime_index":           44,
        "school_rating":         6.1,
        # --- Forward-looking ---
        "gentrification_stage":     3,    # late — H Street corridor mostly built out
        "zoning_trajectory":        48,   # limited upzoning room in dense DC
        "employer_pipeline_score":  58,   # Amazon feeder demand; federal uncertainty a headwind
        "infrastructure_pipeline":  52,   # no major new transit near this corridor
        "pop_growth_5yr_forecast":  2.5,
        "long_term_note": "Good urban asset but federal workforce headwinds and limited density upside constrain long-term appreciation vs. VA suburbs.",
    },

    "Arlington / Rosslyn-Ballston (VA)": {
        "state": "VA",
        "class": "A",
        "avg_rent_studio":  2_200,
        "avg_rent_1br":     2_800,
        "avg_rent_2br":     3_780,
        "avg_rent_3br":     5_050,
        "rent_growth_yoy":  4.0,
        "rent_growth_3yr":  10.2,
        "concession_rate":  4.2,
        "occupancy_rate":   93.8,
        "absorption_rate":  82,
        "avg_days_on_market": 27,
        "new_supply_units_pipeline": 2_200,
        "typical_building_size":     300,
        "job_growth_yoy":   3.3,
        "unemployment_rate": 2.9,
        "federal_workforce_risk": 65,
        "major_employers": [
            "Amazon HQ2 (National Landing)", "Accenture Federal",
            "DARPA / Pentagon-adjacent", "Boeing Defense"
        ],
        "median_hh_income":    141_000,
        "income_growth_yoy":   4.0,
        "population_growth_yoy": 1.7,
        "net_migration_score":   63,
        "renter_pct":            62,
        "age_25_44_pct":         43,
        "walk_score":            86,
        "transit_score":         88,
        "metro_distance_miles":  0.4,
        "cap_rate_market":       4.6,
        "price_per_unit":        335_000,
        "avg_noi_per_unit":      15_410,
        "crime_index":           29,
        "school_rating":         8.2,
        # --- Forward-looking ---
        "gentrification_stage":     4,    # mature — fully transformed; limited additional upside
        "zoning_trajectory":        45,   # already dense; Amazon HQ2 area mostly built
        "employer_pipeline_score":  72,   # Amazon HQ2 Phase 2 still ramping; Accenture, Boeing
        "infrastructure_pipeline":  55,   # HQ2 infrastructure mostly complete
        "pop_growth_5yr_forecast":  2.2,
        "long_term_note": "Amazon HQ2 demand is already priced in. Mature market with strong income but limited appreciation runway.",
    },

    "Silver Spring (MD)": {
        "state": "MD",
        "class": "A/B",
        "avg_rent_studio":  1_750,
        "avg_rent_1br":     2_220,
        "avg_rent_2br":     2_980,
        "avg_rent_3br":     3_900,
        "rent_growth_yoy":  4.5,
        "rent_growth_3yr":  12.1,
        "concession_rate":  3.5,
        "occupancy_rate":   94.2,
        "absorption_rate":  87,
        "avg_days_on_market": 21,
        "new_supply_units_pipeline": 1_150,
        "typical_building_size":     210,
        "job_growth_yoy":   2.7,
        "unemployment_rate": 3.4,
        "federal_workforce_risk": 58,
        "major_employers": [
            "Discovery / Warner Bros. Discovery", "Montgomery County Govt",
            "FDA (White Oak campus nearby)"
        ],
        "median_hh_income":    89_000,
        "income_growth_yoy":   3.8,
        "population_growth_yoy": 2.1,
        "net_migration_score":   67,
        "renter_pct":            65,
        "age_25_44_pct":         41,
        "walk_score":            84,
        "transit_score":         85,
        "metro_distance_miles":  0.4,
        "cap_rate_market":       5.1,
        "price_per_unit":        248_000,
        "avg_noi_per_unit":      12_648,
        "crime_index":           49,
        "school_rating":         6.8,
        # --- Forward-looking ---
        "gentrification_stage":     2,    # mid — meaningful upside remaining
        "zoning_trajectory":        71,   # Montgomery County investing in Purple Line TOD corridors
        "employer_pipeline_score":  62,   # Warner Bros. Discovery stable; county govt steady
        "infrastructure_pipeline":  92,   # PURPLE LINE — opening 2027–28, Silver Spring is the hub
                                          # connecting Red + Purple Lines; transformational for the area
        "pop_growth_5yr_forecast":  3.4,  # Purple Line will accelerate in-migration
        "long_term_note": "The Purple Line is a once-in-a-generation infrastructure event for Silver Spring. When it opens (2027-28), Silver Spring becomes the only DMV submarket connecting two Metro lines. Buy before the market prices it in.",
    },

    "Alexandria / Old Town (VA)": {
        "state": "VA",
        "class": "A/B",
        "avg_rent_studio":  1_920,
        "avg_rent_1br":     2_510,
        "avg_rent_2br":     3_380,
        "avg_rent_3br":     4_450,
        "rent_growth_yoy":  3.5,
        "rent_growth_3yr":  8.9,
        "concession_rate":  5.1,
        "occupancy_rate":   93.3,
        "absorption_rate":  80,
        "avg_days_on_market": 30,
        "new_supply_units_pipeline": 820,
        "typical_building_size":     190,
        "job_growth_yoy":   2.4,
        "unemployment_rate": 3.1,
        "federal_workforce_risk": 60,
        "major_employers": [
            "US Patent & Trademark Office", "Inova Health System", "Leidos"
        ],
        "median_hh_income":    123_000,
        "income_growth_yoy":   3.2,
        "population_growth_yoy": 1.3,
        "net_migration_score":   55,
        "renter_pct":            58,
        "age_25_44_pct":         38,
        "walk_score":            83,
        "transit_score":         80,
        "metro_distance_miles":  0.8,
        "cap_rate_market":       4.8,
        "price_per_unit":        292_000,
        "avg_noi_per_unit":      14_016,
        "crime_index":           35,
        "school_rating":         7.5,
        # --- Forward-looking ---
        "gentrification_stage":     4,    # mature — established for decades
        "zoning_trajectory":        52,   # Potomac Yard growing; Old Town NIMBY pressure limits density
        "employer_pipeline_score":  58,   # USPTO, Inova stable but not growing fast
        "infrastructure_pipeline":  62,   # Potomac Yard Metro (2023) already priced in
        "pop_growth_5yr_forecast":  2.0,
        "long_term_note": "Solid but fully mature. Potomac Yard is the one growth node; Old Town itself has limited density upside due to historic preservation constraints.",
    },

    "Bethesda / Chevy Chase (MD)": {
        "state": "MD",
        "class": "A",
        "avg_rent_studio":  2_100,
        "avg_rent_1br":     2_750,
        "avg_rent_2br":     3_700,
        "avg_rent_3br":     5_200,
        "rent_growth_yoy":  3.6,
        "rent_growth_3yr":  8.6,
        "concession_rate":  4.8,
        "occupancy_rate":   92.9,
        "absorption_rate":  78,
        "avg_days_on_market": 33,
        "new_supply_units_pipeline": 940,
        "typical_building_size":     180,
        "job_growth_yoy":   2.2,
        "unemployment_rate": 3.0,
        "federal_workforce_risk": 52,
        "major_employers": [
            "NIH (National Institutes of Health)", "Marriott International HQ",
            "USDA / FDA campuses"
        ],
        "median_hh_income":    156_000,
        "income_growth_yoy":   3.6,
        "population_growth_yoy": 1.1,
        "net_migration_score":   51,
        "renter_pct":            49,
        "age_25_44_pct":         33,
        "walk_score":            81,
        "transit_score":         78,
        "metro_distance_miles":  0.5,
        "cap_rate_market":       4.4,
        "price_per_unit":        368_000,
        "avg_noi_per_unit":      16_192,
        "crime_index":           24,
        "school_rating":         8.9,
        # --- Forward-looking ---
        "gentrification_stage":     4,    # mature — one of the most established suburbs in the US
        "zoning_trajectory":        42,   # NIMBY pressure; limited density appetite
        "employer_pipeline_score":  62,   # NIH steady; Marriott HQ expanding downtown Bethesda
        "infrastructure_pipeline":  72,   # Purple Line end station at Bethesda; already well-served
        "pop_growth_5yr_forecast":  1.8,  # stable but slow-growing affluent suburb
        "long_term_note": "Wealth preservation asset. High income tenants, excellent schools. But entry price ($368K/unit) and mature stage limit long-term appreciation upside.",
    },

    "Gaithersburg (MD)": {
        "state": "MD",
        "class": "A/B",
        # Gaithersburg is the Shady Grove end-of-Red-Line biotech corridor.
        # NIST HQ, AstraZeneca, and the Life Sciences cluster at Shady Grove drive demand,
        # but the submarket is suburban and car-dependent outside the Shady Grove station area.
        "avg_rent_studio":  1_550,
        "avg_rent_1br":     2_010,
        "avg_rent_2br":     2_700,
        "avg_rent_3br":     3_560,
        "rent_growth_yoy":  3.0,
        "rent_growth_3yr":  7.6,
        "concession_rate":  6.8,        # highest concession pressure in the dataset
        "occupancy_rate":   91.9,
        "absorption_rate":  71,
        "avg_days_on_market": 42,
        "new_supply_units_pipeline": 980,
        "typical_building_size":     200,
        "job_growth_yoy":   2.3,
        "unemployment_rate": 3.3,
        "federal_workforce_risk": 46,   # NIST is federal; limited private-sector diversification
        "major_employers": [
            "NIST (National Institute of Standards & Technology)",
            "AstraZeneca (Gaithersburg campus)",
            "Sodexo HQ", "Montgomery County Public Schools"
        ],
        "median_hh_income":    98_000,
        "income_growth_yoy":   2.7,
        "population_growth_yoy": 1.1,
        "net_migration_score":   44,
        "renter_pct":            41,
        "age_25_44_pct":         30,
        "walk_score":            61,    # suburban — low walkability except near Shady Grove Metro
        "transit_score":         60,
        "metro_distance_miles":  1.4,   # Shady Grove station is end-of-line
        "cap_rate_market":       5.5,
        "price_per_unit":        218_000,
        "avg_noi_per_unit":      11_990,
        "crime_index":           47,
        "school_rating":         7.3,
        # --- Forward-looking ---
        "gentrification_stage":     1,    # early — most upside remaining in the dataset
        "zoning_trajectory":        84,   # Shady Grove Sector Plan: Montgomery County actively
                                          # upzoning for TOD, higher density, mixed-use near Metro
        "employer_pipeline_score":  79,   # I-270 Life Sciences Corridor accelerating:
                                          # AstraZeneca expanding campus; biotech pipeline strong;
                                          # NIST quantum computing initiative attracting spinoffs
        "infrastructure_pipeline":  74,   # Corridor Cities Transitway BRT planned;
                                          # I-270 managed lanes Phase 1 underway
        "pop_growth_5yr_forecast":  3.2,  # biotech worker influx + housing affordability pushout
        "long_term_note": "Most undervalued long-term play in the DMV. Cheapest entry ($218K/unit), Stage 1 gentrification, aggressive county upzoning, and one of the strongest biotech employment corridors on the East Coast. Requires patient capital — 5-7 year hold.",
    },

    "Rockville (MD)": {
        "state": "MD",
        "class": "A/B",
        # Rockville Town Center is denser and more walkable than Gaithersburg.
        # Rockville Metro station (Red Line) gives direct access to DC.
        # Biotech/pharma employers nearby but slower absorption than inner suburbs.
        "avg_rent_studio":  1_700,
        "avg_rent_1br":     2_160,
        "avg_rent_2br":     2_880,
        "avg_rent_3br":     3_760,
        "rent_growth_yoy":  3.3,
        "rent_growth_3yr":  8.5,
        "concession_rate":  5.5,
        "occupancy_rate":   92.9,
        "absorption_rate":  77,
        "avg_days_on_market": 34,
        "new_supply_units_pipeline": 640,
        "typical_building_size":     190,
        "job_growth_yoy":   2.1,
        "unemployment_rate": 3.1,
        "federal_workforce_risk": 51,
        "major_employers": [
            "NIH / FDA (White Oak / Rockville cluster)",
            "Novavax", "Human Genome Sciences / GSK",
            "Montgomery County Govt"
        ],
        "median_hh_income":    110_000,
        "income_growth_yoy":   3.1,
        "population_growth_yoy": 1.3,
        "net_migration_score":   50,
        "renter_pct":            46,
        "age_25_44_pct":         33,
        "walk_score":            72,
        "transit_score":         70,
        "metro_distance_miles":  0.8,
        "cap_rate_market":       5.2,
        "price_per_unit":        240_000,
        "avg_noi_per_unit":      12_480,
        "crime_index":           39,
        "school_rating":         7.7,
        # --- Forward-looking ---
        "gentrification_stage":     2,    # mid — Town Center actively transforming
        "zoning_trajectory":        76,   # Rockville Pike BRT corridor upzoning; Town Center Phase II
        "employer_pipeline_score":  68,   # NIH / FDA cluster steady; Novavax biotech pipeline
        "infrastructure_pipeline":  71,   # Rockville Pike BRT planned; I-270 managed lanes
        "pop_growth_5yr_forecast":  2.8,
        "long_term_note": "Underrated value play. Cheaper than Bethesda, better trajectory than Gaithersburg today, with Town Center densification creating a walkable urban core out of a suburban grid.",
    },
}


def get_dataframe() -> pd.DataFrame:
    rows = []
    for name, d in SUBMARKETS.items():
        row = {"submarket_name": name}
        row.update(d)
        rows.append(row)
    return pd.DataFrame(rows)
