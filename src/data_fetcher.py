"""
Live data fetcher — pulls from public APIs.

Sources:
  Zillow ZORI (metro)   — DC MSA rent index, monthly through present (no key)
  Zillow ZORI (zip)     — zip-code level rent index, mapped to DMV submarkets (no key)
  BLS Public API        — metro employment & unemployment, quarterly (no key)
  Census ACS API        — median household income (optional free key)

Submarket-level metrics that require paid data (occupancy, pipeline, crime)
are curated in dmv_data.py and updated manually.

Run `python analyze.py --refresh` to bypass the 24h cache and re-fetch.
"""

import json
import os
import io
import csv
import time
import urllib.request
from datetime import datetime
from typing import Optional, Dict, Any, List

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Zip codes mapped to each DMV submarket
# ---------------------------------------------------------------------------

SUBMARKET_ZIPS: Dict[str, List[str]] = {
    "Navy Yard / Capitol Riverfront (DC)": ["20003", "20024", "20032"],
    "Tysons / McLean (VA)":                ["22102", "22043", "22101", "22182"],
    "NoMa / H Street (DC)":               ["20002", "20001", "20017"],
    "Arlington / Rosslyn-Ballston (VA)":   ["22201", "22202", "22203", "22204"],
    "Silver Spring (MD)":                  ["20901", "20902", "20910", "20912"],
    "Alexandria / Old Town (VA)":          ["22301", "22302", "22314"],
    "Bethesda / Chevy Chase (MD)":         ["20814", "20815", "20816", "20817"],
    "Rockville (MD)":                      ["20850", "20851", "20852", "20853"],
    "Gaithersburg (MD)":                   ["20877", "20878", "20879", "20882"],
}

# ---------------------------------------------------------------------------
# Zillow ZORI — Metro level (DC MSA)
# ---------------------------------------------------------------------------

ZORI_METRO_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zori/"
    "Metro_zori_uc_sfrcondomfr_sm_month.csv"
)
DC_REGION = "Washington, DC"


def _download_csv(url: str, cache_file: str, force: bool = False) -> Optional[List[Dict]]:
    """Download a CSV from url, cache it, return list of row dicts."""
    cache_path = os.path.join(CACHE_DIR, cache_file)
    if not force and os.path.exists(cache_path):
        age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
        if age_hours < 24:
            with open(cache_path, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(raw)
        return list(csv.DictReader(io.StringIO(raw)))
    except Exception as e:
        print(f"  [WARN] Failed to download {url}: {e}")
        if os.path.exists(cache_path):
            print(f"  [INFO] Using cached version of {cache_file}")
            with open(cache_path, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        return None


def _date_cols(row: Dict) -> List[str]:
    """Return sorted date columns (YYYY-MM-DD) from a ZORI row, newest first."""
    return sorted(
        [k for k in row if k and len(k) == 10 and k[:4].isdigit()],
        reverse=True
    )


def _quarter_avg(row: Dict, year: int, quarter: int) -> Optional[float]:
    """Average the three months of a given quarter from a ZORI row."""
    month_map = {1: ["01", "02", "03"], 2: ["04", "05", "06"],
                 3: ["07", "08", "09"], 4: ["10", "11", "12"]}
    months = month_map.get(quarter, [])
    vals = []
    for m in months:
        col = f"{year}-{m}-"
        matches = [k for k in row if k.startswith(col)]
        for c in matches:
            try:
                vals.append(float(row[c]))
            except (ValueError, TypeError):
                pass
    return round(sum(vals) / len(vals), 0) if vals else None


def fetch_zori_metro(force: bool = False) -> Optional[Dict[str, Any]]:
    """DC MSA rent index — latest month + Q1 2026 average."""
    print("  [API] Zillow ZORI (metro)...")
    rows = _download_csv(ZORI_METRO_URL, "zori_metro.csv", force)
    if not rows:
        return None

    dc_row = next((r for r in rows if DC_REGION in r.get("RegionName", "")), None)
    if not dc_row:
        return None

    dcols  = _date_cols(dc_row)
    latest = dcols[0] if dcols else None

    def _v(col):
        try:    return float(dc_row[col])
        except: return None

    latest_rent = _v(latest) if latest else None
    yoy_col     = dcols[min(12, len(dcols)-1)] if dcols else None
    rent_yoy    = _v(yoy_col) if yoy_col else None

    q1_2026 = _quarter_avg(dc_row, 2026, 1)
    q4_2025 = _quarter_avg(dc_row, 2025, 4)
    q1_2025 = _quarter_avg(dc_row, 2025, 1)

    result: Dict[str, Any] = {
        "source":           "Zillow ZORI Metro",
        "as_of":            latest,
        "metro":            DC_REGION,
        "latest_rent":      latest_rent,
        "rent_growth_yoy":  round((latest_rent / rent_yoy - 1) * 100, 2) if latest_rent and rent_yoy else None,
        "q1_2026_avg":      q1_2026,
        "q4_2025_avg":      q4_2025,
        "q1_2025_avg":      q1_2025,
        "q1_yoy_growth":    round((q1_2026 / q1_2025 - 1) * 100, 2) if q1_2026 and q1_2025 else None,
        "q_over_q_growth":  round((q1_2026 / q4_2025 - 1) * 100, 2) if q1_2026 and q4_2025 else None,
        "fetched_at":       datetime.utcnow().isoformat(),
    }

    cache_path = os.path.join(CACHE_DIR, "zori_metro_parsed.json")
    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)
    return result


# ---------------------------------------------------------------------------
# Zillow ZORI — Zip-code level (submarket rent estimates)
# ---------------------------------------------------------------------------

ZORI_ZIP_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zori/"
    "Zip_zori_uc_sfrcondomfr_sm_month.csv"
)


def fetch_zori_by_submarket(force: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    For each DMV submarket, average the ZORI values across its zip codes
    and return Q1 2026 rent estimate + YoY growth.
    """
    print("  [API] Zillow ZORI (zip-code level)...")
    rows = _download_csv(ZORI_ZIP_URL, "zori_zip.csv", force)
    if not rows:
        return {}

    # Index rows by RegionName (zip code string)
    zip_index: Dict[str, Dict] = {}
    for row in rows:
        region = row.get("RegionName", "").strip()
        if region:
            zip_index[region] = row

    results: Dict[str, Dict[str, Any]] = {}

    for submarket, zips in SUBMARKET_ZIPS.items():
        q1_2026_vals, q1_2025_vals, latest_vals = [], [], []

        for z in zips:
            row = zip_index.get(z)
            if not row:
                continue
            dcols = _date_cols(row)
            if not dcols:
                continue

            q1_26 = _quarter_avg(row, 2026, 1)
            q1_25 = _quarter_avg(row, 2025, 1)
            try:
                lat = float(row[dcols[0]])
            except (ValueError, TypeError):
                lat = None

            if q1_26:  q1_2026_vals.append(q1_26)
            if q1_25:  q1_2025_vals.append(q1_25)
            if lat:    latest_vals.append(lat)

        if not q1_2026_vals:
            results[submarket] = {"available": False}
            continue

        q1_26_avg = round(sum(q1_2026_vals) / len(q1_2026_vals), 0)
        q1_25_avg = round(sum(q1_2025_vals) / len(q1_2025_vals), 0) if q1_2025_vals else None
        lat_avg   = round(sum(latest_vals) / len(latest_vals), 0) if latest_vals else None

        results[submarket] = {
            "available":        True,
            "zori_q1_2026":     q1_26_avg,
            "zori_q1_2025":     q1_25_avg,
            "zori_latest":      lat_avg,
            "zori_yoy_growth":  round((q1_26_avg / q1_25_avg - 1) * 100, 2) if q1_25_avg else None,
            "zips_used":        [z for z in zips if z in zip_index],
        }

    cache_path = os.path.join(CACHE_DIR, "zori_submarket.json")
    with open(cache_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


# ---------------------------------------------------------------------------
# BLS — Metro employment & unemployment (quarterly)
# ---------------------------------------------------------------------------

BLS_URL    = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
BLS_SERIES = {
    "unemployment_rate": "LAUMT114790000000003",
    "employment_level":  "LAUMT114790000000005",
}


def fetch_bls(force: bool = False) -> Optional[Dict[str, Any]]:
    """DC MSA unemployment + employment — latest available + Q1 2026."""
    cache_path = os.path.join(CACHE_DIR, "bls_dc.json")
    if not force and os.path.exists(cache_path):
        if (time.time() - os.path.getmtime(cache_path)) / 3600 < 24:
            with open(cache_path) as f:
                return json.load(f)

    print("  [API] BLS employment data...")
    # Pull 24 months to capture Q1 2026
    payload = json.dumps({
        "seriesid":  list(BLS_SERIES.values()),
        "startyear": "2024",
        "endyear":   str(datetime.utcnow().year),
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            BLS_URL, data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [WARN] BLS fetch failed: {e}")
        return None

    if data.get("status") != "REQUEST_SUCCEEDED":
        return None

    series_map = {v: k for k, v in BLS_SERIES.items()}
    result: Dict[str, Any] = {"source": "BLS", "fetched_at": datetime.utcnow().isoformat()}

    for series in data.get("Results", {}).get("series", []):
        key   = series_map.get(series["seriesID"])
        pts   = series.get("data", [])
        if not key or not pts:
            continue

        # Latest reading
        result[key]               = float(pts[0]["value"])
        result[f"{key}_period"]   = f"{pts[0]['year']}-{pts[0]['period'].replace('M','')}"

        # Q1 2026 average (months M01, M02, M03 of 2026)
        q1_vals = [float(p["value"]) for p in pts
                   if p["year"] == "2026" and p["period"] in ("M01", "M02", "M03")]
        if q1_vals:
            result[f"{key}_q1_2026"] = round(sum(q1_vals) / len(q1_vals), 2)

        # Q1 2025 for YoY
        q1_25_vals = [float(p["value"]) for p in pts
                      if p["year"] == "2025" and p["period"] in ("M01", "M02", "M03")]
        if q1_25_vals:
            result[f"{key}_q1_2025"] = round(sum(q1_25_vals) / len(q1_25_vals), 2)

    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)
    return result


# ---------------------------------------------------------------------------
# Census ACS — median household income
# ---------------------------------------------------------------------------

CENSUS_URL = (
    "https://api.census.gov/data/2023/acs/acs1"
    "?get=B19013_001E,NAME"
    "&for=metropolitan+statistical+area/micropolitan+statistical+area:47900"
)


def fetch_census(force: bool = False) -> Optional[Dict[str, Any]]:
    cache_path = os.path.join(CACHE_DIR, "census_dc.json")
    if not force and os.path.exists(cache_path):
        if (time.time() - os.path.getmtime(cache_path)) / 3600 < 24 * 7:
            with open(cache_path) as f:
                return json.load(f)

    key = os.environ.get("CENSUS_API_KEY", "")
    url = CENSUS_URL + (f"&key={key}" if key else "")
    print("  [API] Census ACS income data...")
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
        "source":           "Census ACS 1-Year 2023",
        "median_hh_income": int(row[headers.index("B19013_001E")]),
        "fetched_at":       datetime.utcnow().isoformat(),
    }
    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)
    return result


# ---------------------------------------------------------------------------
# Aggregate — called by analyze.py
# ---------------------------------------------------------------------------

def fetch_live_context(force: bool = False) -> Dict[str, Any]:
    context: Dict[str, Any] = {"live": True, "sources": []}

    metro = fetch_zori_metro(force)
    if metro:
        context.update({
            "zori_latest":       metro["latest_rent"],
            "zori_as_of":        metro["as_of"],
            "zori_growth_yoy":   metro["rent_growth_yoy"],
            "zori_q1_2026":      metro["q1_2026_avg"],
            "zori_q1_yoy":       metro["q1_yoy_growth"],
            "zori_q_over_q":     metro["q_over_q_growth"],
        })
        context["sources"].append(f"Zillow ZORI metro (as of {metro['as_of']})")

    submarket_zori = fetch_zori_by_submarket(force)
    if submarket_zori:
        context["submarket_zori"] = submarket_zori
        hits = sum(1 for v in submarket_zori.values() if v.get("available"))
        context["sources"].append(f"Zillow ZORI zip-level ({hits}/9 submarkets matched)")

    bls = fetch_bls(force)
    if bls:
        context.update({
            "bls_unemployment":        bls.get("unemployment_rate"),
            "bls_unemployment_period": bls.get("unemployment_rate_period"),
            "bls_unemp_q1_2026":       bls.get("unemployment_rate_q1_2026"),
            "bls_unemp_q1_2025":       bls.get("unemployment_rate_q1_2025"),
        })
        context["sources"].append("BLS LAUS")

    census = fetch_census(force)
    if census:
        context["census_median_income"] = census["median_hh_income"]
        context["sources"].append("Census ACS 2023")

    if not context["sources"]:
        context["live"] = False
    return context
