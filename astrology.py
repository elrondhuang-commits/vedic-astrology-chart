"""Core Vedic astrology calculations using Swiss Ephemeris.

Internal identifiers are intentionally English and stable. User-interface translation
belongs in app.py.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe

ZODIAC_SIGNS = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

NAKSHATRAS = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
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

VARGA_NAMES = {
    1: "Rashi",
    2: "Hora",
    3: "Drekkana",
    4: "Chaturthamsha",
    7: "Saptamsha",
    9: "Navamsha",
    10: "Dashamsha",
    12: "Dwadashamsha",
}

# Vimshottari order begins with the ruler of Ashwini. The nine durations total 120 years.
VIMSHOTTARI_ORDER = (
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
)
VIMSHOTTARI_YEARS = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0,
}

# A classical text gives the dasha spans in years but does not uniquely define a modern
# civil-day conversion. This project uses the mean Gregorian year and states the choice
# in the interface and README so that date differences between software are auditable.
DASHA_YEAR_DAYS = 365.2425
VIMSHOTTARI_TOTAL_YEARS = 120.0

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
            "ambiguous",
            timezone_name,
            tuple(item[0] for item in valid),
            tuple(item[1] for item in valid),
        )
    return TimeResolution("valid", timezone_name, (valid[0][0],), (valid[0][1],))


def _normalize_longitude(value: float) -> float:
    return value % 360.0


def _position_metadata(longitude: float) -> tuple[int, str, float, int, str, int]:
    longitude = _normalize_longitude(longitude)
    sign_index = min(11, int(longitude // 30.0))
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


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def varga_longitude(longitude: float, division: int) -> float:
    """Transform a sidereal longitude into a supported Parashari varga longitude.

    Supported divisions:
    - D1 Rashi: unchanged.
    - D2 Hora: odd signs map first half to Leo and second half to Cancer;
      even signs reverse the order.
    - D3 Drekkana: the three decans map to the natal sign, fifth, and ninth.
    - D4 Chaturthamsha: the four quarters map to the natal sign, fourth,
      seventh, and tenth signs.
    - D7 Saptamsha: odd signs begin from themselves; even signs begin from
      the seventh sign.
    - D9 Navamsha: movable signs begin from themselves, fixed signs from the ninth,
      and dual signs from the fifth.
    - D10 Dashamsha: odd signs begin from themselves and even signs from the ninth.
    - D12 Dwadashamsha: the twelve parts proceed zodiacally from the natal sign.

    The returned longitude encodes both the resulting varga sign and the proportional
    degree within that sign.
    """
    longitude = _normalize_longitude(longitude)
    if division == 1:
        return longitude

    sign_index = min(11, int(longitude // 30.0))
    degree_in_sign = longitude - sign_index * 30.0

    if division == 2:
        part_index = 0 if degree_in_sign < 15.0 else 1
        within_part = degree_in_sign - part_index * 15.0
        if sign_index % 2 == 0:
            target_sign = 4 if part_index == 0 else 3  # Leo / Cancer
        else:
            target_sign = 3 if part_index == 0 else 4  # Cancer / Leo
        target_degree = within_part * 2.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    if division == 3:
        part_size = 10.0
        part_index = min(2, int(degree_in_sign // part_size))
        within_part = degree_in_sign - part_index * part_size
        target_sign = (sign_index + part_index * 4) % 12
        target_degree = within_part * 3.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    if division == 4:
        part_size = 7.5
        part_index = min(3, int(degree_in_sign // part_size))
        within_part = degree_in_sign - part_index * part_size
        target_sign = (sign_index + part_index * 3) % 12
        target_degree = within_part * 4.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    if division == 7:
        part_size = 30.0 / 7.0
        part_index = min(6, int(degree_in_sign // part_size))
        within_part = degree_in_sign - part_index * part_size
        start_sign = sign_index if sign_index % 2 == 0 else (sign_index + 6) % 12
        target_sign = (start_sign + part_index) % 12
        target_degree = within_part * 7.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    if division == 9:
        part_size = 30.0 / 9.0
        part_index = min(8, int(degree_in_sign // part_size))
        within_part = degree_in_sign - part_index * part_size

        # 0 = movable, 1 = fixed, 2 = dual within each group of three signs.
        modality = sign_index % 3
        if modality == 0:  # movable
            start_sign = sign_index
        elif modality == 1:  # fixed: ninth sign from the natal sign
            start_sign = (sign_index + 8) % 12
        else:  # dual: fifth sign from the natal sign
            start_sign = (sign_index + 4) % 12

        target_sign = (start_sign + part_index) % 12
        target_degree = within_part * 9.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    if division == 10:
        part_size = 3.0
        part_index = min(9, int(degree_in_sign // part_size))
        within_part = degree_in_sign - part_index * part_size

        # Zodiac sign numbers 1, 3, 5... are odd. With zero-based indexes, these
        # are indexes 0, 2, 4....
        if sign_index % 2 == 0:
            start_sign = sign_index
        else:
            start_sign = (sign_index + 8) % 12  # ninth sign from the natal sign

        target_sign = (start_sign + part_index) % 12
        target_degree = within_part * 10.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    if division == 12:
        part_size = 2.5
        part_index = min(11, int(degree_in_sign // part_size))
        within_part = degree_in_sign - part_index * part_size
        target_sign = (sign_index + part_index) % 12
        target_degree = within_part * 12.0
        return _normalize_longitude(target_sign * 30.0 + target_degree)

    raise ValueError(f"Unsupported varga division: D{division}")


def calculate_varga_chart(
    base_positions: Sequence[Mapping[str, Any]],
    division: int,
) -> dict[str, Any]:
    """Create a whole-sign divisional chart from D1 sidereal longitudes."""
    if division not in VARGA_NAMES:
        raise ValueError(f"Unsupported varga division: D{division}")

    transformed: list[dict[str, Any]] = []
    for base in base_positions:
        lon = varga_longitude(float(base["longitude"]), division)
        meta = _position_metadata(lon)
        transformed.append(
            {
                "code": str(base["code"]),
                "longitude": lon,
                "sign_index": meta[0],
                "sign": meta[1],
                "degree_in_sign": meta[2],
                "nakshatra_index": meta[3],
                "nakshatra": meta[4],
                "pada": meta[5],
                "retrograde": bool(base.get("retrograde", False)),
            }
        )

    ascendant = next((item for item in transformed if item["code"] == "Ascendant"), None)
    if ascendant is None:
        raise ValueError("base_positions must include Ascendant")
    asc_sign_index = int(ascendant["sign_index"])

    positions: list[dict[str, Any]] = []
    for item in transformed:
        item_with_house = dict(item)
        item_with_house["house"] = _house_from_sign(int(item["sign_index"]), asc_sign_index)
        if item_with_house["code"] == "Ascendant":
            item_with_house["house"] = 1
        positions.append(item_with_house)

    return {
        "chart_code": f"D{division}",
        "division": division,
        "name": VARGA_NAMES[division],
        "house_system": "Whole Sign",
        "ascendant_sign_index": asc_sign_index,
        "positions": positions,
    }


def _calculate_d1(jd_ut: float, latitude: float, longitude: float) -> dict[str, Any]:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

    # Swiss Ephemeris house system W = whole sign. ascmc[0] is the sidereal
    # Ascendant because FLG_SIDEREAL is supplied.
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
        values, _return_flags = swe.calc_ut(jd_ut, planet_id, flags)
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
        "chart_code": "D1",
        "division": 1,
        "name": "Rashi",
        "house_system": "Whole Sign",
        "ascendant_sign_index": asc_sign_index,
        "positions": [position.to_dict() for position in positions],
    }


def calculate_moon_chart(base_positions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Create a Chandra Lagna chart using the Moon sign as whole-sign house 1.

    This is a reference chart, not a divisional varga: sidereal longitudes stay
    unchanged and only the whole-sign house frame rotates to the Moon.
    """
    moon = next((item for item in base_positions if item["code"] == "Moon"), None)
    if moon is None:
        raise ValueError("base_positions must include Moon")
    moon_sign_index = int(moon["sign_index"])

    positions: list[dict[str, Any]] = []
    for base in base_positions:
        item = dict(base)
        item["house"] = _house_from_sign(int(item["sign_index"]), moon_sign_index)
        positions.append(item)

    return {
        "chart_code": "Moon",
        "division": None,
        "name": "Chandra Lagna",
        "house_system": "Whole Sign from Moon",
        "ascendant_sign_index": moon_sign_index,
        "positions": positions,
    }


def _period_contains(start: datetime, end: datetime, moment: datetime | None) -> bool:
    return moment is not None and start <= moment < end


def calculate_vimshottari(
    moon_longitude: float,
    birth_utc: datetime,
    current_utc: datetime | None = None,
) -> dict[str, Any]:
    """Calculate Vimshottari Mahadasha and Antardasha intervals.

    The Moon's sidereal nakshatra determines the starting lord. The expired fraction
    of that nakshatra determines the elapsed fraction of the starting Mahadasha.
    Antardasha durations are Mahadasha years × Antardasha-lord years / 120.
    """
    if birth_utc.tzinfo is None:
        raise ValueError("birth_utc must be timezone-aware")
    birth_utc = birth_utc.astimezone(timezone.utc)

    if current_utc is None:
        current_utc = datetime.now(timezone.utc)
    elif current_utc.tzinfo is None:
        raise ValueError("current_utc must be timezone-aware")
    else:
        current_utc = current_utc.astimezone(timezone.utc)

    moon_longitude = _normalize_longitude(moon_longitude)
    nak_span = 360.0 / 27.0
    nak_index = min(26, int(moon_longitude // nak_span))
    within_nak = moon_longitude - nak_index * nak_span
    fraction_elapsed = within_nak / nak_span

    birth_lord = VIMSHOTTARI_ORDER[nak_index % len(VIMSHOTTARI_ORDER)]
    birth_lord_index = VIMSHOTTARI_ORDER.index(birth_lord)
    birth_md_years = VIMSHOTTARI_YEARS[birth_lord]
    elapsed_days = fraction_elapsed * birth_md_years * DASHA_YEAR_DAYS
    cycle_start = birth_utc - timedelta(days=elapsed_days)

    display_end = birth_utc + timedelta(days=VIMSHOTTARI_TOTAL_YEARS * DASHA_YEAR_DAYS)
    current_for_highlight = current_utc if current_utc >= birth_utc else None
    generation_target = max(display_end, current_for_highlight or display_end)

    mahadashas: list[dict[str, Any]] = []
    current_summary: dict[str, Any] | None = None
    birth_md_end: datetime | None = None
    md_start = cycle_start
    sequence_offset = 0

    # The first period starts before birth. Ten periods normally cover the full
    # 120-year window measured forward from birth. A higher cap also supports old
    # historical dates while keeping accidental infinite loops impossible.
    while sequence_offset < 40:
        md_lord = VIMSHOTTARI_ORDER[(birth_lord_index + sequence_offset) % 9]
        md_years = VIMSHOTTARI_YEARS[md_lord]
        md_duration = timedelta(days=md_years * DASHA_YEAR_DAYS)
        md_end = md_start + md_duration

        at_birth = _period_contains(md_start, md_end, birth_utc)
        is_current = _period_contains(md_start, md_end, current_for_highlight)
        if at_birth:
            birth_md_end = md_end

        antardashas: list[dict[str, Any]] = []
        cumulative_fraction = 0.0
        for ad_offset in range(9):
            ad_lord = VIMSHOTTARI_ORDER[
                (VIMSHOTTARI_ORDER.index(md_lord) + ad_offset) % 9
            ]
            ad_years = md_years * VIMSHOTTARI_YEARS[ad_lord] / VIMSHOTTARI_TOTAL_YEARS
            ad_start = md_start + md_duration * cumulative_fraction
            cumulative_fraction += VIMSHOTTARI_YEARS[ad_lord] / VIMSHOTTARI_TOTAL_YEARS
            ad_end = md_end if ad_offset == 8 else md_start + md_duration * cumulative_fraction

            ad_at_birth = _period_contains(ad_start, ad_end, birth_utc)
            ad_is_current = _period_contains(ad_start, ad_end, current_for_highlight)
            antardashas.append(
                {
                    "lord": ad_lord,
                    "start_utc": _iso_utc(ad_start),
                    "end_utc": _iso_utc(ad_end),
                    "duration_years": ad_years,
                    "at_birth": ad_at_birth,
                    "current": ad_is_current,
                }
            )
            if ad_is_current:
                current_summary = {
                    "mahadasha": md_lord,
                    "antardasha": ad_lord,
                    "mahadasha_start_utc": _iso_utc(md_start),
                    "mahadasha_end_utc": _iso_utc(md_end),
                    "antardasha_start_utc": _iso_utc(ad_start),
                    "antardasha_end_utc": _iso_utc(ad_end),
                }

        mahadashas.append(
            {
                "lord": md_lord,
                "start_utc": _iso_utc(md_start),
                "end_utc": _iso_utc(md_end),
                "duration_years": md_years,
                "at_birth": at_birth,
                "current": is_current,
                "within_display_window": md_end > birth_utc and md_start < display_end,
                "antardashas": antardashas,
            }
        )

        if md_end >= generation_target and (current_for_highlight is None or md_end > current_for_highlight):
            break
        md_start = md_end
        sequence_offset += 1

    if birth_md_end is None:
        raise RuntimeError("Unable to identify the Mahadasha operating at birth")

    balance_days = (birth_md_end - birth_utc).total_seconds() / 86400.0
    balance_years = balance_days / DASHA_YEAR_DAYS
    moon_meta = _position_metadata(moon_longitude)

    return {
        "system": "Vimshottari",
        "cycle_years": VIMSHOTTARI_TOTAL_YEARS,
        "year_definition": "Mean Gregorian year",
        "year_days": DASHA_YEAR_DAYS,
        "birth_nakshatra_index": moon_meta[3],
        "birth_nakshatra": moon_meta[4],
        "birth_pada": moon_meta[5],
        "birth_lord": birth_lord,
        "nakshatra_fraction_elapsed": fraction_elapsed,
        "birth_balance_years": balance_years,
        "birth_balance_end_utc": _iso_utc(birth_md_end),
        "display_start_utc": _iso_utc(birth_utc),
        "display_end_utc": _iso_utc(display_end),
        "current_utc": _iso_utc(current_utc),
        "current": current_summary,
        "mahadashas": mahadashas,
    }


def calculate_chart(
    utc_dt: datetime,
    latitude: float,
    longitude: float,
    current_utc: datetime | None = None,
) -> dict[str, Any]:
    """Calculate Lahiri D1, Moon, D2, D3, D4, D7, D9, D10, D12, and Vimshottari data."""
    if utc_dt.tzinfo is None:
        raise ValueError("utc_dt must be timezone-aware")
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude must be between -90 and 90")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude must be between -180 and 180")

    utc_dt = utc_dt.astimezone(timezone.utc)
    jd_ut = _julian_day_utc(utc_dt)
    d1 = _calculate_d1(jd_ut, latitude, longitude)
    moon_chart = calculate_moon_chart(d1["positions"])
    d2 = calculate_varga_chart(d1["positions"], 2)
    d3 = calculate_varga_chart(d1["positions"], 3)
    d4 = calculate_varga_chart(d1["positions"], 4)
    d7 = calculate_varga_chart(d1["positions"], 7)
    d9 = calculate_varga_chart(d1["positions"], 9)
    d10 = calculate_varga_chart(d1["positions"], 10)
    d12 = calculate_varga_chart(d1["positions"], 12)

    moon = next((item for item in d1["positions"] if item["code"] == "Moon"), None)
    if moon is None:
        raise RuntimeError("Moon calculation failed")
    dasha = calculate_vimshottari(float(moon["longitude"]), utc_dt, current_utc=current_utc)

    return {
        "utc_datetime": _iso_utc(utc_dt),
        "julian_day_ut": jd_ut,
        "latitude": latitude,
        "longitude": longitude,
        "ayanamsha": "Lahiri",
        "node_type": "True Node",
        "house_system": "Whole Sign",
        "varga_method": "Parashari",
        "dasha_system": "Vimshottari",
        "dasha_year_days": DASHA_YEAR_DAYS,
        "charts": {
            "D1": d1,
            "Moon": moon_chart,
            "D2": d2,
            "D3": d3,
            "D4": d4,
            "D7": d7,
            "D9": d9,
            "D10": d10,
            "D12": d12,
        },
        "dasha": dasha,
        # Backward-compatible D1 aliases for older app versions or external callers.
        "ascendant_sign_index": d1["ascendant_sign_index"],
        "positions": d1["positions"],
    }
