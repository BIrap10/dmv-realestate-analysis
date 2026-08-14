"""
Interactive DMV Investment Heatmap
-----------------------------------
Generates a self-contained HTML map showing multifamily residential
investment intensity across the DC-Maryland-Virginia metro area.

Layers:
  1. Choropleth — zip-code polygons colored by submarket investment score
     (fetched from Census TIGER / fallback to circle approximation)
  2. HeatMap    — Gaussian intensity overlay weighted by composite score
  3. Markers    — Submarket centroids with full investment scorecards on click
  4. Layer control to toggle all three layers independently
"""

import json
import os
import io
import urllib.request
import time
from typing import Dict, Any, Optional, List

import folium
from folium.plugins import HeatMap
import branca.colormap as cm

# ---------------------------------------------------------------------------
# Submarket geography
# ---------------------------------------------------------------------------

CENTROIDS: Dict[str, tuple] = {
    "Navy Yard / Capitol Riverfront (DC)": (38.8752, -77.0042),
    "Tysons / McLean (VA)":               (38.9186, -77.2286),
    "NoMa / H Street (DC)":               (38.9093, -76.9969),
    "Arlington / Rosslyn-Ballston (VA)":   (38.8817, -77.0942),
    "Silver Spring (MD)":                  (38.9940, -77.0264),
    "Alexandria / Old Town (VA)":          (38.8048, -77.0469),
    "Bethesda / Chevy Chase (MD)":         (38.9842, -77.0947),
    "Rockville (MD)":                      (39.0840, -77.1528),
    "Gaithersburg (MD)":                   (39.1434, -77.2014),
}

# Zip codes per submarket (for choropleth coloring)
SUBMARKET_ZIPS: Dict[str, List[str]] = {
    "Navy Yard / Capitol Riverfront (DC)": ["20003", "20024", "20032"],
    "Tysons / McLean (VA)":               ["22102", "22043", "22101", "22182"],
    "NoMa / H Street (DC)":               ["20002", "20001", "20017"],
    "Arlington / Rosslyn-Ballston (VA)":   ["22201", "22202", "22203", "22204"],
    "Silver Spring (MD)":                  ["20901", "20902", "20910", "20912"],
    "Alexandria / Old Town (VA)":          ["22301", "22302", "22314"],
    "Bethesda / Chevy Chase (MD)":         ["20814", "20815", "20816", "20817"],
    "Rockville (MD)":                      ["20850", "20851", "20852", "20853"],
    "Gaithersburg (MD)":                   ["20877", "20878", "20879", "20882"],
}

# Reverse map: zip → submarket name
ZIP_TO_SUBMARKET = {
    z: name for name, zips in SUBMARKET_ZIPS.items() for z in zips
}

ALL_ZIPS = list(ZIP_TO_SUBMARKET.keys())

# ---------------------------------------------------------------------------
# Signal colours
# ---------------------------------------------------------------------------

SIGNAL_COLORS = {
    "STRONG BUY": "#2d6a4f",
    "BUY":        "#52b788",
    "WATCH":      "#f4a261",
    "AVOID":      "#c1121f",
}

def _signal(score: float) -> str:
    if score >= 72: return "STRONG BUY"
    if score >= 60: return "BUY"
    if score >= 48: return "WATCH"
    return "AVOID"


# ---------------------------------------------------------------------------
# Choropleth: fetch zip-code GeoJSON from Census TIGER
# ---------------------------------------------------------------------------

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
GEOJSON_CACHE = os.path.join(CACHE_DIR, "dmv_zips.geojson")

# Census TIGER Web Services — ZCTA layer
TIGER_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/"
    "TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/3/query"
)

# State GeoJSON files from OpenDataDE (fallback)
STATE_GEOJSON_URLS = [
    ("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON"
     "/master/dc_district_of_columbia_zip_codes_geo.min.json"),
    ("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON"
     "/master/md_maryland_zip_codes_geo.min.json"),
    ("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON"
     "/master/va_virginia_zip_codes_geo.min.json"),
]


def _fetch_tiger_geojson(force: bool = False) -> Optional[dict]:
    """Fetch ZCTA boundaries from Census TIGER for our DMV zip codes."""
    if not force and os.path.exists(GEOJSON_CACHE):
        age_hours = (time.time() - os.path.getmtime(GEOJSON_CACHE)) / 3600
        if age_hours < 24 * 30:   # cache for 30 days — boundaries don't change
            with open(GEOJSON_CACHE) as f:
                return json.load(f)

    # Try Census TIGER first
    zip_list = ",".join(f"'{z}'" for z in ALL_ZIPS)
    params = (
        f"?where=ZCTA5+IN+({zip_list})"
        "&outFields=ZCTA5"
        "&returnGeometry=true"
        "&f=geojson"
        "&outSR=4326"
    )
    print("  [MAP] Fetching zip-code boundaries from Census TIGER...")
    try:
        url = TIGER_URL + params
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("features"):
            print(f"  [MAP] Census TIGER: {len(data['features'])} zip boundaries loaded.")
            with open(GEOJSON_CACHE, "w") as f:
                json.dump(data, f)
            return data
    except Exception as e:
        print(f"  [MAP] TIGER fetch failed ({e}), trying state files...")

    # Fallback: state-level GeoJSON files (filter to our zips)
    combined = {"type": "FeatureCollection", "features": []}
    zip_set  = set(ALL_ZIPS)

    for url in STATE_GEOJSON_URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                state_data = json.loads(resp.read().decode("utf-8"))
            for feat in state_data.get("features", []):
                props = feat.get("properties", {})
                # Different files use different field names
                z = (props.get("ZCTA5CE10")
                     or props.get("ZCTA5CE20")
                     or props.get("ZIP")
                     or props.get("GEOID10")
                     or props.get("GEOID20")
                     or "")
                if str(z) in zip_set:
                    feat["properties"]["ZCTA5"] = str(z)
                    combined["features"].append(feat)
        except Exception as e:
            print(f"  [MAP] State file failed ({e})")

    if combined["features"]:
        print(f"  [MAP] State fallback: {len(combined['features'])} boundaries loaded.")
        with open(GEOJSON_CACHE, "w") as f:
            json.dump(combined, f)
        return combined

    print("  [MAP] No zip boundaries available — using circle markers only.")
    return None


# ---------------------------------------------------------------------------
# Popup HTML for each submarket marker
# ---------------------------------------------------------------------------

def _popup_html(row: Any) -> str:
    name    = row["submarket_name"]
    score   = row["score"]
    signal  = _signal(score)
    color   = SIGNAL_COLORS[signal]
    sig_bg  = color + "22"   # translucent

    score_bar_width = int(score)
    bar_color = color

    def fmt_row(label, value):
        return f"""
        <tr>
          <td style="color:#9a9182;font-size:11px;padding:2px 6px 2px 0">{label}</td>
          <td style="color:#e8e0d0;font-size:11px;font-weight:600;padding:2px 0">{value}</td>
        </tr>"""

    html = f"""
    <div style="background:#1a1d27;border:1px solid #2e3147;border-radius:8px;
                padding:14px;min-width:270px;font-family:sans-serif;">
      <div style="font-size:13px;font-weight:700;color:#c9a84c;margin-bottom:4px">
        {name}
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
        <div style="font-size:28px;font-weight:800;color:#e8e0d0">{score:.0f}</div>
        <div>
          <div style="font-size:10px;color:#9a9182">/ 100</div>
          <div style="background:{sig_bg};color:{color};border:1px solid {color};
                      border-radius:4px;padding:1px 7px;font-size:10px;font-weight:700;
                      display:inline-block;margin-top:2px">{signal}</div>
        </div>
      </div>
      <div style="background:#0f1117;border-radius:4px;height:6px;margin-bottom:12px">
        <div style="background:{bar_color};width:{score_bar_width}%;height:6px;border-radius:4px"></div>
      </div>
      <table style="border-collapse:collapse;width:100%">
        {fmt_row("1BR Effective Rent", f"${row['avg_rent_1br']:,}")}
        {fmt_row("Rent Growth YoY", f"{row['rent_growth_yoy']:+.1f}%")}
        {fmt_row("Occupancy", f"{row['occupancy_rate']:.1f}%")}
        {fmt_row("Absorption", f"{row['absorption_rate']}%")}
        {fmt_row("Cap Rate", f"{row['cap_rate_market']:.1f}%")}
        {fmt_row("Price / Unit", f"${row['price_per_unit']:,}")}
        {fmt_row("NOI / Unit / yr", f"${row['avg_noi_per_unit']:,}")}
        {fmt_row("Job Growth", f"{row['job_growth_yoy']:+.1f}% YoY")}
        {fmt_row("Federal Risk", f"{row['federal_workforce_risk']}/100")}
        {fmt_row("Class", row['class'])}
      </table>
      <div style="margin-top:10px;font-size:10px;color:#9a9182">
        {"  ·  ".join(row["major_employers"][:2])}
      </div>
    </div>
    """
    return html


# ---------------------------------------------------------------------------
# Main map builder
# ---------------------------------------------------------------------------

def build_map(df, force_geojson: bool = False) -> str:
    """
    Build the interactive DMV investment heatmap.
    Returns the path to the saved HTML file.
    """
    import pandas as pd

    # Build score lookup
    score_by_name = dict(zip(df["submarket_name"], df["score"]))
    score_by_zip  = {z: score_by_name[name]
                     for name, zips in SUBMARKET_ZIPS.items()
                     for z in zips
                     if name in score_by_name}

    # -----------------------------------------------------------------------
    # Base map
    # -----------------------------------------------------------------------
    m = folium.Map(
        location=[38.97, -77.13],
        zoom_start=11,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    # -----------------------------------------------------------------------
    # Layer 1: Choropleth (zip code polygons)
    # -----------------------------------------------------------------------
    geojson = _fetch_tiger_geojson(force=force_geojson)

    colormap = cm.LinearColormap(
        colors=["#c1121f", "#f4a261", "#ffb703", "#52b788", "#2d6a4f"],
        vmin=0, vmax=100,
        caption="Investment Score (0–100)  ·  DMV Multifamily Residential"
    )
    colormap.add_to(m)

    if geojson and geojson.get("features"):
        choropleth_layer = folium.FeatureGroup(name="📊 Choropleth (score by zip)", show=True)

        def style_fn(feature):
            z     = feature["properties"].get("ZCTA5", "")
            score = score_by_zip.get(z, 0)
            return {
                "fillColor":   colormap(score),
                "fillOpacity": 0.55,
                "color":       "#ffffff",
                "weight":      0.4,
            }

        def highlight_fn(feature):
            return {"weight": 2, "color": "#c9a84c", "fillOpacity": 0.7}

        folium.GeoJson(
            geojson,
            style_function=style_fn,
            highlight_function=highlight_fn,
            tooltip=folium.GeoJsonTooltip(
                fields=["ZCTA5"],
                aliases=["ZIP Code"],
                style="background:#1a1d27;color:#e8e0d0;border:1px solid #2e3147;font-size:12px",
            ),
        ).add_to(choropleth_layer)

        choropleth_layer.add_to(m)

    # -----------------------------------------------------------------------
    # Layer 2: HeatMap (score-weighted intensity)
    # -----------------------------------------------------------------------
    heat_data = []
    for _, row in df.iterrows():
        name = row["submarket_name"]
        if name not in CENTROIDS:
            continue
        lat, lng = CENTROIDS[name]
        # Spread heat across nearby zip centroids for smoother gradient
        for dLat, dLng, w in [
            (0.00, 0.00, 1.0),
            (0.02, 0.02, 0.5), (0.02, -0.02, 0.5),
            (-0.02, 0.02, 0.5), (-0.02, -0.02, 0.5),
            (0.04, 0.00, 0.25), (0.00, 0.04, 0.25),
        ]:
            heat_data.append([lat + dLat, lng + dLng, row["score"] * w / 100])

    heat_layer = folium.FeatureGroup(name="🌡️ Heatmap overlay", show=True)
    HeatMap(
        heat_data,
        min_opacity=0.3,
        max_zoom=14,
        radius=55,
        blur=40,
        gradient={
            "0.0":  "#c1121f",
            "0.48": "#f4a261",
            "0.60": "#ffb703",
            "0.72": "#52b788",
            "1.0":  "#2d6a4f",
        },
    ).add_to(heat_layer)
    heat_layer.add_to(m)

    # -----------------------------------------------------------------------
    # Layer 3: Submarket markers with investment scorecards
    # -----------------------------------------------------------------------
    marker_layer = folium.FeatureGroup(name="📍 Submarket scorecards", show=True)

    for _, row in df.iterrows():
        name = row["submarket_name"]
        if name not in CENTROIDS:
            continue
        lat, lng  = CENTROIDS[name]
        score     = row["score"]
        signal    = _signal(score)
        color     = SIGNAL_COLORS[signal]
        radius    = 14 + int(score / 100 * 22)   # 14–36 px

        # Outer glow ring
        folium.CircleMarker(
            location=[lat, lng],
            radius=radius + 5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.15,
            weight=0,
        ).add_to(marker_layer)

        # Main circle
        folium.CircleMarker(
            location=[lat, lng],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
            popup=folium.Popup(
                folium.IFrame(_popup_html(row), width=300, height=370),
                max_width=310,
            ),
            tooltip=folium.Tooltip(
                f"<b style='color:#c9a84c'>{name}</b><br>"
                f"Score: <b>{score:.0f}</b> — <b style='color:{color}'>{signal}</b>",
                style="background:#1a1d27;color:#e8e0d0;border:1px solid #2e3147;"
                      "font-size:12px;padding:6px 10px;border-radius:6px",
            ),
        ).add_to(marker_layer)

        # Score label
        folium.Marker(
            location=[lat, lng],
            icon=folium.DivIcon(
                html=f"""<div style="font-size:11px;font-weight:800;color:#ffffff;
                                     text-shadow:0 1px 3px #000;
                                     text-align:center;line-height:1.1;
                                     pointer-events:none">
                           {score:.0f}
                         </div>""",
                icon_size=(40, 20),
                icon_anchor=(20, 10),
            ),
        ).add_to(marker_layer)

    marker_layer.add_to(m)

    # -----------------------------------------------------------------------
    # Title card
    # -----------------------------------------------------------------------
    title_html = """
    <div style="position:fixed;top:12px;left:50%;transform:translateX(-50%);
                background:#1a1d27ee;border:1px solid #c9a84c;border-radius:8px;
                padding:10px 20px;z-index:9999;text-align:center;
                font-family:sans-serif;pointer-events:none">
      <div style="color:#c9a84c;font-size:15px;font-weight:700;letter-spacing:0.5px">
        DMV MULTIFAMILY RESIDENTIAL — INVESTMENT HEATMAP
      </div>
      <div style="color:#9a9182;font-size:11px;margin-top:2px">
        Class-A/B Apartments · Q1 2026 · Click any marker for full scorecard
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # -----------------------------------------------------------------------
    # Signal legend
    # -----------------------------------------------------------------------
    legend_html = """
    <div style="position:fixed;bottom:30px;right:12px;
                background:#1a1d27ee;border:1px solid #2e3147;border-radius:8px;
                padding:12px 16px;z-index:9999;font-family:sans-serif;min-width:160px">
      <div style="color:#c9a84c;font-size:12px;font-weight:700;margin-bottom:8px">
        INVESTMENT SIGNAL
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
        <div style="width:12px;height:12px;border-radius:50%;background:#2d6a4f"></div>
        <span style="color:#e8e0d0;font-size:11px">STRONG BUY (≥ 72)</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
        <div style="width:12px;height:12px;border-radius:50%;background:#52b788"></div>
        <span style="color:#e8e0d0;font-size:11px">BUY (60–71)</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
        <div style="width:12px;height:12px;border-radius:50%;background:#f4a261"></div>
        <span style="color:#e8e0d0;font-size:11px">WATCH (48–59)</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px">
        <div style="width:12px;height:12px;border-radius:50%;background:#c1121f"></div>
        <span style="color:#e8e0d0;font-size:11px">AVOID (&lt; 48)</span>
      </div>
      <div style="color:#9a9182;font-size:9px;margin-top:10px;border-top:1px solid #2e3147;padding-top:6px">
        Bubble size ∝ composite score<br>
        Sources: Zillow, BLS, Census ACS
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Layer control
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "visualizations", "dmv_investment_map.html"
    )
    m.save(out_path)
    print(f"  [MAP] Saved → {os.path.abspath(out_path)}")
    return os.path.abspath(out_path)
