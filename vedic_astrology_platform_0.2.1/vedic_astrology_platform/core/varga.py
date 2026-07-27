from __future__ import annotations
from typing import Any, Mapping, Sequence
from .constants import VARGA_NAMES
from .zodiac import house_from_sign, normalize_longitude, position_metadata

def varga_longitude(longitude: float, division: int) -> float:
    longitude = normalize_longitude(longitude)
    if division == 1: return longitude
    sign_index = min(11, int(longitude // 30.0))
    degree = longitude - sign_index * 30.0
    if division == 2:
        part = 0 if degree < 15.0 else 1; within = degree - part * 15.0
        target = (4 if part == 0 else 3) if sign_index % 2 == 0 else (3 if part == 0 else 4)
        return normalize_longitude(target * 30.0 + within * 2.0)
    if division == 3:
        size = 10.0; part = min(2, int(degree // size)); within = degree - part * size
        return normalize_longitude(((sign_index + part * 4) % 12) * 30.0 + within * 3.0)
    if division == 4:
        size = 7.5; part = min(3, int(degree // size)); within = degree - part * size
        return normalize_longitude(((sign_index + part * 3) % 12) * 30.0 + within * 4.0)
    if division == 7:
        size = 30.0 / 7.0; part = min(6, int(degree // size)); within = degree - part * size
        start = sign_index if sign_index % 2 == 0 else (sign_index + 6) % 12
        return normalize_longitude(((start + part) % 12) * 30.0 + within * 7.0)
    if division == 9:
        size = 30.0 / 9.0; part = min(8, int(degree // size)); within = degree - part * size
        modality = sign_index % 3
        start = sign_index if modality == 0 else ((sign_index + 8) % 12 if modality == 1 else (sign_index + 4) % 12)
        return normalize_longitude(((start + part) % 12) * 30.0 + within * 9.0)
    if division == 10:
        size = 3.0; part = min(9, int(degree // size)); within = degree - part * size
        start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
        return normalize_longitude(((start + part) % 12) * 30.0 + within * 10.0)
    if division == 12:
        size = 2.5; part = min(11, int(degree // size)); within = degree - part * size
        return normalize_longitude(((sign_index + part) % 12) * 30.0 + within * 12.0)
    raise ValueError(f"Unsupported varga division: D{division}")

def calculate_varga_chart(base_positions: Sequence[Mapping[str, Any]], division: int) -> dict[str, Any]:
    if division not in VARGA_NAMES: raise ValueError(f"Unsupported varga division: D{division}")
    transformed: list[dict[str, Any]] = []
    for base in base_positions:
        lon = varga_longitude(float(base["longitude"]), division); meta = position_metadata(lon)
        transformed.append({
            "code": str(base["code"]), "longitude": lon, "sign_index": meta[0], "sign": meta[1],
            "degree_in_sign": meta[2], "nakshatra_index": meta[3], "nakshatra": meta[4], "pada": meta[5],
            "retrograde": bool(base.get("retrograde", False)),
        })
    asc = next((x for x in transformed if x["code"] == "Ascendant"), None)
    if asc is None: raise ValueError("base_positions must include Ascendant")
    asc_sign = int(asc["sign_index"])
    positions = []
    for item in transformed:
        row = dict(item); row["house"] = 1 if row["code"] == "Ascendant" else house_from_sign(int(row["sign_index"]), asc_sign); positions.append(row)
    return {"chart_code": f"D{division}", "division": division, "name": VARGA_NAMES[division], "house_system": "Whole Sign", "ascendant_sign_index": asc_sign, "positions": positions}

def calculate_moon_chart(base_positions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    moon = next((x for x in base_positions if x["code"] == "Moon"), None)
    if moon is None: raise ValueError("base_positions must include Moon")
    moon_sign = int(moon["sign_index"])
    positions = []
    for base in base_positions:
        row = dict(base); row["house"] = house_from_sign(int(row["sign_index"]), moon_sign); positions.append(row)
    return {"chart_code": "Moon", "division": None, "name": "Chandra Lagna", "house_system": "Whole Sign from Moon", "ascendant_sign_index": moon_sign, "positions": positions}
