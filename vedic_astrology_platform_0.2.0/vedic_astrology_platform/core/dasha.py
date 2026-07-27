from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any
from .constants import DASHA_YEAR_DAYS, VIMSHOTTARI_ORDER, VIMSHOTTARI_TOTAL_YEARS, VIMSHOTTARI_YEARS
from .zodiac import normalize_longitude, position_metadata

def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()

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

    moon_longitude = normalize_longitude(moon_longitude)
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
    moon_meta = position_metadata(moon_longitude)

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

