from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import TimeResolution

def _offset_label(dt: datetime) -> str:
    offset = dt.utcoffset()
    if offset is None:
        return "UTC?"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"UTC{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"

def resolve_local_time(local_naive: datetime, timezone_name: str) -> TimeResolution:
    """Detect valid, ambiguous, and nonexistent local civil times."""
    if local_naive.tzinfo is not None:
        raise ValueError("local_naive must not contain tzinfo")
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return TimeResolution("invalid_timezone", timezone_name)

    valid: list[tuple[datetime, str]] = []
    for fold in (0, 1):
        local = local_naive.replace(tzinfo=tz, fold=fold)
        utc_value = local.astimezone(timezone.utc)
        round_trip = utc_value.astimezone(tz).replace(tzinfo=None)
        if round_trip == local_naive:
            pair = (utc_value, _offset_label(local))
            if pair not in valid:
                valid.append(pair)

    if not valid:
        return TimeResolution("nonexistent", timezone_name)
    if len(valid) == 2 and valid[0][0] != valid[1][0]:
        valid.sort(key=lambda pair: pair[0])
        return TimeResolution(
            "ambiguous", timezone_name,
            tuple(item[0] for item in valid), tuple(item[1] for item in valid),
        )
    return TimeResolution("valid", timezone_name, (valid[0][0],), (valid[0][1],))
