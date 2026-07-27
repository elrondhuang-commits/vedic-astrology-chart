from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import swisseph as swe
from .constants import PLANET_IDS
from .models import BodyPosition
from .zodiac import house_from_sign, normalize_longitude, position_metadata

def julian_day_utc(utc_dt: datetime) -> float:
    utc_dt = utc_dt.astimezone(timezone.utc)
    hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0 + utc_dt.microsecond / 3_600_000_000.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour, swe.GREG_CAL)

def calculate_d1(jd_ut: float, latitude: float, longitude: float) -> dict[str, Any]:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    _cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    asc_lon = normalize_longitude(float(ascmc[0]))
    asc_meta = position_metadata(asc_lon)
    asc_sign_index = asc_meta[0]
    positions: list[BodyPosition] = [BodyPosition(
        code="Ascendant", longitude=asc_lon, sign_index=asc_meta[0], sign=asc_meta[1],
        degree_in_sign=asc_meta[2], nakshatra_index=asc_meta[3], nakshatra=asc_meta[4],
        pada=asc_meta[5], house=1, retrograde=False,
    )]
    rahu_longitude: float | None = None
    for code, planet_id in PLANET_IDS.items():
        values, _return_flags = swe.calc_ut(jd_ut, planet_id, flags)
        lon = normalize_longitude(float(values[0]))
        speed = float(values[3])
        if code == "Rahu": rahu_longitude = lon
        meta = position_metadata(lon)
        positions.append(BodyPosition(
            code=code, longitude=lon, sign_index=meta[0], sign=meta[1], degree_in_sign=meta[2],
            nakshatra_index=meta[3], nakshatra=meta[4], pada=meta[5],
            house=house_from_sign(meta[0], asc_sign_index), retrograde=speed < 0.0,
        ))
    if rahu_longitude is None:
        raise RuntimeError("Rahu calculation failed")
    ketu_lon = normalize_longitude(rahu_longitude + 180.0)
    meta = position_metadata(ketu_lon)
    positions.append(BodyPosition(
        code="Ketu", longitude=ketu_lon, sign_index=meta[0], sign=meta[1], degree_in_sign=meta[2],
        nakshatra_index=meta[3], nakshatra=meta[4], pada=meta[5],
        house=house_from_sign(meta[0], asc_sign_index), retrograde=True,
    ))
    return {
        "chart_code": "D1", "division": 1, "name": "Rashi", "house_system": "Whole Sign",
        "ascendant_sign_index": asc_sign_index, "positions": [p.to_dict() for p in positions],
    }
