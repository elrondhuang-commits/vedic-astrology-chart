"""Metadata registry for supported divisional charts.

Calculation code uses stable English chart codes (for example ``D9``). The UI
reads localized labels and descriptions from this registry, so adding a varga
no longer requires duplicating translation keys throughout ``app.py``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class VargaInfo:
    code: str
    division: int
    sanskrit_name: str
    labels: Mapping[str, str]
    descriptions: Mapping[str, str]
    reference: str

    def label(self, language: str) -> str:
        return self.labels.get(language, self.labels["en"])

    def description(self, language: str) -> str:
        return self.descriptions.get(language, self.descriptions["en"])


VARGA_REGISTRY: dict[str, VargaInfo] = {
    "D2": VargaInfo(
        code="D2",
        division=2,
        sanskrit_name="Hora",
        labels={"zh-TW": "D2 二分盤（Hora）", "en": "D2 Hora"},
        descriptions={
            "zh-TW": "D2 Hora 常用於財富、資源、累積方式與物質支持的輔助判讀。本版本採傳統 Parashari 太陽／月亮 Hora。",
            "en": "D2 Hora is commonly consulted for wealth, resources, accumulation patterns, and material support. This version uses the classical Parashari Sun/Moon Hora.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
    "D3": VargaInfo(
        code="D3",
        division=3,
        sanskrit_name="Drekkana",
        labels={"zh-TW": "D3 三分盤（Drekkana）", "en": "D3 Drekkana"},
        descriptions={
            "zh-TW": "D3 Drekkana 常用於手足、勇氣、行動力、努力方式與生命活力的輔助判讀。",
            "en": "D3 Drekkana is commonly consulted for siblings, courage, initiative, effort, and vitality.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
    "D4": VargaInfo(
        code="D4",
        division=4,
        sanskrit_name="Chaturthamsha",
        labels={"zh-TW": "D4 四分盤（Chaturthamsha）", "en": "D4 Chaturthamsha"},
        descriptions={
            "zh-TW": "D4 Chaturthamsha 常用於居所、不動產、固定資產、生活基礎與內在安定的輔助判讀。",
            "en": "D4 Chaturthamsha is commonly consulted for residence, property, fixed assets, foundations, and inner stability.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
    "D7": VargaInfo(
        code="D7",
        division=7,
        sanskrit_name="Saptamsha",
        labels={"zh-TW": "D7 七分盤（Saptamsha）", "en": "D7 Saptamsha"},
        descriptions={
            "zh-TW": "D7 Saptamsha 常用於子女、後代、創造力、生育與延續性的輔助判讀。",
            "en": "D7 Saptamsha is commonly consulted for children, descendants, creativity, fertility, and continuity.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
    "D9": VargaInfo(
        code="D9",
        division=9,
        sanskrit_name="Navamsha",
        labels={"zh-TW": "D9 九分盤（Navamsha）", "en": "D9 Navamsha"},
        descriptions={
            "zh-TW": "D9 是最常用的分盤之一，常用於婚姻、關係、法則與行星成熟度的輔助判讀。",
            "en": "D9 is one of the most frequently used divisional charts and is commonly consulted for marriage, relationships, dharma, and planetary maturity.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
    "D10": VargaInfo(
        code="D10",
        division=10,
        sanskrit_name="Dashamsha",
        labels={"zh-TW": "D10 十分盤（Dashamsha）", "en": "D10 Dashamsha"},
        descriptions={
            "zh-TW": "D10 Dashamsha 常用於職涯、工作角色、責任與社會表現的輔助判讀。",
            "en": "D10 Dashamsha is commonly consulted for career, work roles, responsibility, and public expression.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
    "D12": VargaInfo(
        code="D12",
        division=12,
        sanskrit_name="Dwadashamsha",
        labels={"zh-TW": "D12 十二分盤（Dwadashamsha）", "en": "D12 Dwadashamsha"},
        descriptions={
            "zh-TW": "D12 Dwadashamsha 常用於父母、祖先、家族背景、傳承與先天特質的輔助判讀。",
            "en": "D12 Dwadashamsha is commonly consulted for parents, ancestors, family background, inheritance, and inherited traits.",
        },
        reference="Brihat Parashara Hora Shastra, divisional-chart rules",
    ),
}

SUPPORTED_VARGA_CODES: tuple[str, ...] = tuple(VARGA_REGISTRY)


def get_varga_info(code: str) -> VargaInfo:
    """Return metadata for a stable varga code or raise a clear error."""
    try:
        return VARGA_REGISTRY[code]
    except KeyError as exc:
        raise ValueError(f"Unsupported varga code: {code}") from exc
