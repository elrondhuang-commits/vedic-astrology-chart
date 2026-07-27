"""Stable internal constants. UI translations must not be stored here."""
from __future__ import annotations

import swisseph as swe

PROJECT_VERSION = "0.3.0"

ZODIAC_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

NAKSHATRAS = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
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
    16: "Shodashamsha",
    20: "Vimshamsha",
    24: "Chaturvimshamsha",
}

VIMSHOTTARI_ORDER = (
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
)
VIMSHOTTARI_YEARS = {
    "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0,
    "Mars": 7.0, "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0,
}
DASHA_YEAR_DAYS = 365.2425
VIMSHOTTARI_TOTAL_YEARS = 120.0
