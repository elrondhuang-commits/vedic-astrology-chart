from __future__ import annotations

from typing import Any, Mapping, Sequence

from .constants import VARGA_NAMES
from .zodiac import house_from_sign, normalize_longitude, position_metadata


def _equal_division(
    sign_index: int,
    degree: float,
    division: int,
    start_sign: int,
    *,
    direction: int = 1,
) -> float:
    """Map one equal subdivision to a target sign and preserve intra-division position."""
    size = 30.0 / division
    part = min(division - 1, int(degree // size))
    within = degree - part * size
    target = (start_sign + direction * part) % 12
    return normalize_longitude(target * 30.0 + within * division)


def varga_longitude(longitude: float, division: int) -> float:
    """Return the Parashari divisional longitude for a sidereal D1 longitude.

    The returned longitude contains both the mapped varga sign and the degree
    within that sign. Stable English chart codes and metadata are managed in
    ``core.varga_registry``; this function contains calculation rules only.
    """
    longitude = normalize_longitude(longitude)
    if division == 1:
        return longitude

    sign_index = min(11, int(longitude // 30.0))
    degree = longitude - sign_index * 30.0

    if division == 2:
        part = 0 if degree < 15.0 else 1
        within = degree - part * 15.0
        target = (4 if part == 0 else 3) if sign_index % 2 == 0 else (3 if part == 0 else 4)
        return normalize_longitude(target * 30.0 + within * 2.0)

    if division == 3:
        part = min(2, int(degree // 10.0))
        within = degree - part * 10.0
        return normalize_longitude(((sign_index + part * 4) % 12) * 30.0 + within * 3.0)

    if division == 4:
        return _equal_division(sign_index, degree, 4, sign_index, direction=3)

    if division == 7:
        start = sign_index if sign_index % 2 == 0 else (sign_index + 6) % 12
        return _equal_division(sign_index, degree, 7, start)

    if division == 9:
        modality = sign_index % 3
        start = sign_index if modality == 0 else ((sign_index + 8) % 12 if modality == 1 else (sign_index + 4) % 12)
        return _equal_division(sign_index, degree, 9, start)

    if division == 10:
        start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
        return _equal_division(sign_index, degree, 10, start)

    if division == 12:
        return _equal_division(sign_index, degree, 12, sign_index)

    if division == 16:
        # Movable signs start from Aries, fixed signs from Leo, and dual signs
        # from Sagittarius. Each subsequent amsha advances zodiacally.
        start_by_modality = {0: 0, 1: 4, 2: 8}
        return _equal_division(sign_index, degree, 16, start_by_modality[sign_index % 3])

    if division == 20:
        # Movable signs start from Aries, fixed signs from Sagittarius, and
        # dual signs from Leo. Each subsequent amsha advances zodiacally.
        start_by_modality = {0: 0, 1: 8, 2: 4}
        return _equal_division(sign_index, degree, 20, start_by_modality[sign_index % 3])

    if division == 24:
        # Mainstream Parashari/Santhanam convention: odd signs start from Leo,
        # even signs start from Cancer, and the amshas advance zodiacally.
        start = 4 if sign_index % 2 == 0 else 3
        return _equal_division(sign_index, degree, 24, start)

    raise ValueError(f"Unsupported varga division: D{division}")


def calculate_varga_chart(
    base_positions: Sequence[Mapping[str, Any]], division: int
) -> dict[str, Any]:
    if division not in VARGA_NAMES:
        raise ValueError(f"Unsupported varga division: D{division}")

    transformed: list[dict[str, Any]] = []
    for base in base_positions:
        lon = varga_longitude(float(base["longitude"]), division)
        meta = position_metadata(lon)
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

    asc = next((item for item in transformed if item["code"] == "Ascendant"), None)
    if asc is None:
        raise ValueError("base_positions must include Ascendant")

    asc_sign = int(asc["sign_index"])
    positions: list[dict[str, Any]] = []
    for item in transformed:
        row = dict(item)
        row["house"] = 1 if row["code"] == "Ascendant" else house_from_sign(int(row["sign_index"]), asc_sign)
        positions.append(row)

    return {
        "chart_code": f"D{division}",
        "division": division,
        "name": VARGA_NAMES[division],
        "house_system": "Whole Sign",
        "ascendant_sign_index": asc_sign,
        "positions": positions,
    }


def calculate_moon_chart(base_positions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    moon = next((item for item in base_positions if item["code"] == "Moon"), None)
    if moon is None:
        raise ValueError("base_positions must include Moon")

    moon_sign = int(moon["sign_index"])
    positions: list[dict[str, Any]] = []
    for base in base_positions:
        row = dict(base)
        row["house"] = house_from_sign(int(row["sign_index"]), moon_sign)
        positions.append(row)

    return {
        "chart_code": "Moon",
        "division": None,
        "name": "Chandra Lagna",
        "house_system": "Whole Sign from Moon",
        "ascendant_sign_index": moon_sign,
        "positions": positions,
    }
