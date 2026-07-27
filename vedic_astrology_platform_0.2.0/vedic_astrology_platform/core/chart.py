from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from .constants import DASHA_YEAR_DAYS, PROJECT_VERSION
from .dasha import calculate_vimshottari
from .ephemeris import calculate_d1, julian_day_utc
from .varga import calculate_moon_chart, calculate_varga_chart

def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()

def calculate_chart(utc_dt: datetime, latitude: float, longitude: float, current_utc: datetime | None = None) -> dict[str, Any]:
    if utc_dt.tzinfo is None: raise ValueError("utc_dt must be timezone-aware")
    if not -90.0 <= latitude <= 90.0: raise ValueError("latitude must be between -90 and 90")
    if not -180.0 <= longitude <= 180.0: raise ValueError("longitude must be between -180 and 180")
    utc_dt = utc_dt.astimezone(timezone.utc)
    jd_ut = julian_day_utc(utc_dt)
    d1 = calculate_d1(jd_ut, latitude, longitude)
    charts = {"D1": d1, "Moon": calculate_moon_chart(d1["positions"])}
    for division in (2, 3, 4, 7, 9, 10, 12):
        charts[f"D{division}"] = calculate_varga_chart(d1["positions"], division)
    moon = next((x for x in d1["positions"] if x["code"] == "Moon"), None)
    if moon is None: raise RuntimeError("Moon calculation failed")
    dasha = calculate_vimshottari(float(moon["longitude"]), utc_dt, current_utc=current_utc)
    return {
        "schema_version": PROJECT_VERSION,
        "utc_datetime": _iso_utc(utc_dt), "julian_day_ut": jd_ut,
        "latitude": latitude, "longitude": longitude, "ayanamsha": "Lahiri",
        "node_type": "True Node", "house_system": "Whole Sign", "varga_method": "Parashari",
        "dasha_system": "Vimshottari", "dasha_year_days": DASHA_YEAR_DAYS,
        "charts": charts, "dasha": dasha,
        "ascendant_sign_index": d1["ascendant_sign_index"], "positions": d1["positions"],
    }
