from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Literal

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
