"""Core Vedic astrology calculations using Swiss Ephemeris.

Internal identifiers are intentionally English and stable. UI translation belongs in app.py.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

ZODIAC_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

NAKSHATRAS = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
)

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
}

TimeStatus = Literal["valid", "ambiguous", "nonexistent", "invalid_timezone"]


@dataclass(frozen=True)
class TimeResolution:
    status: TimeStatus
    timezone: str
    choices_utc: tuple[datetime, ...] = ()
    offsets: tuple[str, ...] = ()


@dataclass(frozen=True)
class BodyPosition:
    code: str
    longitude: float
    sign_index: int
    sign: str
    degree_in_sign: float
    nakshatra_index: int
    nakshatra: str
    pada: int
    house: int
    retrograde: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _offset_label(dt: datetime) -> str:
    offset = dt.utcoffset()
    if offset is None:
        return "UTC?"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"UTC{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def resolve_local_time(local_naive: datetime, timezone_name: str) -> TimeResolution:
    """Classify a naive local datetime using PEP 495 fold semantics and UTC round-trips."""
    if local_naive.tzinfo is not None:
        raise ValueError("local_naive must not contain tzinfo")

    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return TimeResolution("invalid_timezone", timezone_name)

    valid: list[tuple[datetime, str]] = []
    seen_utc: set[datetime] = set()

    for fold in (0, 1):
        aware = local_naive.replace(tzinfo=tz, fold=fold)
        utc_dt = aware.astimezone(timezone.utc)
        round_trip = utc_dt.astimezone(tz).replace(tzinfo=None)
        if round_trip == local_naive and utc_dt not in seen_utc:
            seen_utc.add(utc_dt)
            valid.append((utc_dt, _offset_label(aware)))

    if not valid:
        return TimeResolution("nonexistent", timezone_name)
    if len(valid) == 2:
        valid.sort(key=lambda item: item[0])
        return TimeResolution(
            "ambiguous", timezone_name,
            tuple(item[0] for item in valid),
            tuple(item[1] for item in valid),
        )
    return TimeResolution("valid", timezone_name, (valid[0][0],), (valid[0][1],))


def _normalize_longitude(value: float) -> float:
    return value % 360.0


def _position_metadata(longitude: float) -> tuple[int, str, float, int, str, int]:
    longitude = _normalize_longitude(longitude)
    sign_index = int(longitude // 30.0)
    degree_in_sign = longitude - sign_index * 30.0

    nak_span = 360.0 / 27.0
    pada_span = nak_span / 4.0
    nak_index = min(26, int(longitude // nak_span))
    within_nak = longitude - nak_index * nak_span
    pada = min(4, int(within_nak // pada_span) + 1)
    return (
        sign_index,
        ZODIAC_SIGNS[sign_index],
        degree_in_sign,
        nak_index,
        NAKSHATRAS[nak_index],
        pada,
    )


def _house_from_sign(sign_index: int, asc_sign_index: int) -> int:
    return ((sign_index - asc_sign_index) % 12) + 1


def _julian_day_utc(utc_dt: datetime) -> float:
    utc_dt = utc_dt.astimezone(timezone.utc)
    hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour, swe.GREG_CAL)


def calculate_chart(utc_dt: datetime, latitude: float, longitude: float) -> dict[str, Any]:
    """Calculate a sidereal Lahiri D1 chart with true lunar node and whole-sign houses."""
    if utc_dt.tzinfo is None:
        raise ValueError("utc_dt must be timezone-aware")
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude must be between -90 and 90")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude must be between -180 and 180")

    jd_ut = _julian_day_utc(utc_dt)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

    # Swiss Ephemeris house system W = whole sign. ascmc[0] is the sidereal Ascendant
    # because FLG_SIDEREAL is supplied.
    _cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    asc_lon = _normalize_longitude(float(ascmc[0]))
    asc_meta = _position_metadata(asc_lon)
    asc_sign_index = asc_meta[0]

    positions: list[BodyPosition] = [
        BodyPosition(
            code="Ascendant",
            longitude=asc_lon,
            sign_index=asc_meta[0],
            sign=asc_meta[1],
            degree_in_sign=asc_meta[2],
            nakshatra_index=asc_meta[3],
            nakshatra=asc_meta[4],
            pada=asc_meta[5],
            house=1,
            retrograde=False,
        )
    ]

    rahu_longitude: float | None = None
    for code, planet_id in PLANET_IDS.items():
        values, return_flags = swe.calc_ut(jd_ut, planet_id, flags)
        lon = _normalize_longitude(float(values[0]))
        speed = float(values[3])
        if code == "Rahu":
            rahu_longitude = lon
        meta = _position_metadata(lon)
        positions.append(
            BodyPosition(
                code=code,
                longitude=lon,
                sign_index=meta[0],
                sign=meta[1],
                degree_in_sign=meta[2],
                nakshatra_index=meta[3],
                nakshatra=meta[4],
                pada=meta[5],
                house=_house_from_sign(meta[0], asc_sign_index),
                retrograde=speed < 0.0,
            )
        )

    if rahu_longitude is None:
        raise RuntimeError("Rahu calculation failed")

    ketu_lon = _normalize_longitude(rahu_longitude + 180.0)
    ketu_meta = _position_metadata(ketu_lon)
    positions.append(
        BodyPosition(
            code="Ketu",
            longitude=ketu_lon,
            sign_index=ketu_meta[0],
            sign=ketu_meta[1],
            degree_in_sign=ketu_meta[2],
            nakshatra_index=ketu_meta[3],
            nakshatra=ketu_meta[4],
            pada=ketu_meta[5],
            house=_house_from_sign(ketu_meta[0], asc_sign_index),
            retrograde=True,
        )
    )

    return {
        "utc_datetime": utc_dt.astimezone(timezone.utc).isoformat(),
        "julian_day_ut": jd_ut,
        "latitude": latitude,
        "longitude": longitude,
        "ayanamsha": "Lahiri",
        "node_type": "True Node",
        "house_system": "Whole Sign",
        "ascendant_sign_index": asc_sign_index,
        "positions": [position.to_dict() for position in positions],
    }
