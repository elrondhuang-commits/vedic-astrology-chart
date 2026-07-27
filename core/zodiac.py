from __future__ import annotations
from .constants import NAKSHATRAS, ZODIAC_SIGNS

def normalize_longitude(value: float) -> float:
    return value % 360.0

def position_metadata(longitude: float) -> tuple[int, str, float, int, str, int]:
    longitude = normalize_longitude(longitude)
    sign_index = min(11, int(longitude // 30.0))
    degree_in_sign = longitude - sign_index * 30.0
    nak_span = 360.0 / 27.0
    pada_span = nak_span / 4.0
    nak_index = min(26, int(longitude // nak_span))
    within_nak = longitude - nak_index * nak_span
    pada = min(4, int(within_nak // pada_span) + 1)
    return sign_index, ZODIAC_SIGNS[sign_index], degree_in_sign, nak_index, NAKSHATRAS[nak_index], pada

def house_from_sign(sign_index: int, asc_sign_index: int) -> int:
    return ((sign_index - asc_sign_index) % 12) + 1
