"""
Live data fetcher — pulls from public APIs and merges with curated submarket data.

Sources:
  Zillow Research ZORI  — metro-level rent index (updates monthly, no key needed)
  BLS Public API        — metro employment & unemployment (no key needed for <500/day)
  Census ACS API        — household income & demographics (free key: api.census.gov/key_signup.html)

Submarket-level data (occupancy, pipeline, crime, transit) is curated from
CoStar / Apartment List / local PD sources and stored in dmv_data.py.
Run `python analyze.py --refresh` to re-fetch from APIs.
"""

import json
import os
import time
import urllib.request
import urllib.error
import io
import csv
from datetime import datetime
from typing import Optional, Dict, Any

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Zillow ZORI — Zillow Observed Rent Index (multifamily + SFR, smoothed)
# Metro_zori_uc_sfrcondomfr_sm_month.csv  (monthly, updated ~25th of each month)
# ---------------------------------------------------------------------------

ZORI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zori/"
    "Metro_zori_uc_sfrcondomfr_sm_month.csv"
)

# Zillow RegionName for DC MSA
DC_REGION = "Washington, DC"


def fetch_zori(force: bool = False) -> Optional[Dict[str, Any]]:
    """Return latest ZORI data for the DC MSA. Returns dict or None on failure."""
    cache_path = os.path.join(CACHE_DIR, "zori_dc.json")

    if not force and os.path.exists(cache_path):
        age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
        if age_hours < 24:
            with open(cache_path) as f:
                return json.load(f)

    print("  [API] Fetching Zillow ZORI rent data...")
    try:
        req = urllib.request.Request(ZORI_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [WARN] Zillow ZORI fetch failed: {e}")
        return None

    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)

    dc_row = next((r for r in rows if DC_REGION in r.get("RegionName", "")), None)
    if dc_row is None:
        print("  [WARN] DC region not found in ZORI data.")
        return None

    # Extract time-series columns (format: YYYY-MM-DD)
    date_cols = sorted(
        [k for k in dc_row if k and k[:4].isdigit() and len(k) == 10],
        reverse=True
    )
    if not date_cols:
        return None

    latest_col   = date_cols[0]
    prev_12m_col = date_cols[min(12, len(date_cols) - 1)]
    prev_24m_col = date_cols[min(24, len(date_cols) - 1)]

    def _v(col):
        try:
            return float(dc_row[col])
        except (ValueError, KeyError):
            return None

    latest_rent = _v(latest_col)
    rent_12m    = _v(prev_12m_col)
    rent_24m    = _v(prev_24m_col)

    result = {
        "source": "Zillow ZORI",
        "as_of": latest_col,
        "metro": DC_REGION,
        "median_rent_all": round(latest_rent, 0) if latest_rent else None,
        "rent_growth_yoy": round((latest_rent / rent_12m - 1) * 100, 2) if latest_rent and rent_12m else None,
        "rent_growth_2yr": round((latest_rent / rent_24m - 1) * 100, 2) if latest_rent and rent_24m else None,
        "fetched_at": datetime.utcnow().isoformat(),
    }

    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ---------------------------------------------------------------------------
# BLS Public API — Metro area unemployment & employment
# Series: LAUMT114790000000003 = DC-MD-VA-WV MSA unemployment rate
# ---------------------------------------------------------------------------

BLS_URL      = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
BLS_SERIES   = {
    "unemployment_rate": "LAUMT114790000000003",  # DC MSA unemployment rate
    "employment_level":  "LAUMT114790000000005",  # DC MSA employed
}


def fetch_bls(force: bool = False) -> Optional[Dict[str, Any]]:
    """Return latest BLS employment stats for the DC MSA."""
    cache_path = os.path.join(CACHE_DIR, "bls_dc.json")

    if not force and os.path.exists(cache_path):
        age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
        if age_hours < 24:
            with open(cache_path) as f:
                return json.load(f)

    print("  [API] Fetching BLS employment data...")
    payload = json.dumps({
        "seriesid": list(BLS_SERIES.values()),
        "latest":   True,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            BLS_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [WARN] BLS fetch failed: {e}")
        return None

    if data.get("status") != "REQUEST_SUCCEEDED":
        print(f"  [WARN] BLS API error: {data.get('message', 'unknown')}")
        return None

    result: Dict[str, Any] = {
        "source": "BLS Public API",
        "fetched_at": datetime.utcnow().isoformat(),
    }

    series_map = {v: k for k, v in BLS_SERIES.items()}
    for series in data.get("Results", {}).get("series", []):
        key  = series_map.get(series["seriesID"])
        data_pts = series.get("data", [])
        if key and data_pts:
            latest = data_pts[0]
            result[key] = float(latest["value"])
            result[f"{key}_period"] = f"{latest['year']}-{latest['period'].replace('M','')}"

    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ---------------------------------------------------------------------------
# Census ACS — Median household income for DC MSA
# No key needed for demo; add CENSUS_API_KEY env var for production use
# ---------------------------------------------------------------------------

CENSUS_URL = (
    "https://api.census.gov/data/2023/acs/acs1"
    "?get=B19013_001E,NAME"
    "&for=metropolitan+statistical+area/micropolitan+statistical+area:47900"
)


def fetch_census(force: bool = False) -> Optional[Dict[str, Any]]:
    """Return ACS median household income for the DC MSA (latest ACS 1-Year)."""
    cache_path = os.path.join(CACHE_DIR, "census_dc.json")

    if not force and os.path.exists(cache_path):
        age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
        if age_hours < 24 * 7:   # Census data is annual — cache for a week
            with open(cache_path) as f:
                return json.load(f)

    api_key = os.environ.get("CENSUS_API_KEY", "")
    url = CENSUS_URL + (f"&key={api_key}" if api_key else "")

    print("  [API] Fetching Census ACS income data...")
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [WARN] Census ACS fetch failed: {e}")
        return None

    if not data or len(data) < 2:
        return None

    headers, row = data[0], data[1]
    result = {
        "source": "Census ACS 1-Year 2023",
        "metro": row[headers.index("NAME")],
        "median_hh_income": int(row[headers.index("B19013_001E")]),
        "fetched_at": datetime.utcnow().isoformat(),
    }

    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ---------------------------------------------------------------------------
# Aggregate — returns a dict of live context merged into the analysis
# ---------------------------------------------------------------------------

def fetch_live_context(force: bool = False) -> Dict[str, Any]:
    """
    Fetch all live metrics for the DC MSA.
    Returns whatever succeeded; gracefully handles partial failures.
    """
    context: Dict[str, Any] = {"live": True, "sources": []}

    zori = fetch_zori(force)
    if zori:
        context.update({
            "zori_rent":        zori["median_rent_all"],
            "zori_growth_yoy":  zori["rent_growth_yoy"],
            "zori_growth_2yr":  zori["rent_growth_2yr"],
            "zori_as_of":       zori["as_of"],
        })
        context["sources"].append(f"Zillow ZORI (as of {zori['as_of']})")

    bls = fetch_bls(force)
    if bls:
        context.update({
            "bls_unemployment":       bls.get("unemployment_rate"),
            "bls_unemployment_period": bls.get("unemployment_rate_period"),
            "bls_employment":         bls.get("employment_level"),
        })
        context["sources"].append("BLS LAUS")

    census = fetch_census(force)
    if census:
        context.update({
            "census_median_income": census["median_hh_income"],
        })
        context["sources"].append("Census ACS 2023")

    if not context["sources"]:
        context["live"] = False
        print("  [WARN] All API fetches failed — using curated data only.")

    return context
