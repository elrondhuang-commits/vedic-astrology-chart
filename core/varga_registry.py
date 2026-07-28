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
    warnings: Mapping[str, str] | None = None

    def label(self, language: str) -> str:
        return self.labels.get(language, self.labels["en"])

    def description(self, language: str) -> str:
        return self.descriptions.get(language, self.descriptions["en"])

    def warning(self, language: str) -> str | None:
        if not self.warnings:
            return None
        return self.warnings.get(language, self.warnings.get("en"))


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
    "D16": VargaInfo(
        code="D16",
        division=16,
        sanskrit_name="Shodashamsha",
        labels={"zh-TW": "D16 十六分盤（Shodashamsha）", "en": "D16 Shodashamsha"},
        descriptions={
            "zh-TW": "D16 Shodashamsha 常用於交通工具、居住舒適、享受、內在安適與生活品質的輔助判讀。此分盤對出生時間較敏感。",
            "en": "D16 Shodashamsha is commonly consulted for vehicles, comforts, enjoyment, inner ease, and quality of life. This chart is relatively sensitive to birth-time accuracy.",
        },
        reference="Brihat Parashara Hora Shastra, chapter on the sixteen divisions of a sign",
    ),
    "D20": VargaInfo(
        code="D20",
        division=20,
        sanskrit_name="Vimshamsha",
        labels={"zh-TW": "D20 二十分盤（Vimshamsha）", "en": "D20 Vimshamsha"},
        descriptions={
            "zh-TW": "D20 Vimshamsha 常用於靈性修持、宗教傾向、祈禱、奉獻與內在修行的輔助判讀。",
            "en": "D20 Vimshamsha is commonly consulted for spiritual practice, religious inclination, prayer, devotion, and inner discipline.",
        },
        reference="Brihat Parashara Hora Shastra, chapter on the sixteen divisions of a sign",
    ),
    "D24": VargaInfo(
        code="D24",
        division=24,
        sanskrit_name="Chaturvimshamsha",
        labels={"zh-TW": "D24 二十四分盤（Chaturvimshamsha）", "en": "D24 Chaturvimshamsha"},
        descriptions={
            "zh-TW": "D24 Chaturvimshamsha 常用於教育、學習能力、知識累積、學術訓練與研習成果的輔助判讀。",
            "en": "D24 Chaturvimshamsha is commonly consulted for education, learning capacity, accumulated knowledge, academic training, and study outcomes.",
        },
        reference="Brihat Parashara Hora Shastra, chapter on the sixteen divisions of a sign",
    ),

    "D27": VargaInfo(
        code="D27",
        division=27,
        sanskrit_name="Saptavimshamsha",
        labels={"zh-TW": "D27 二十七分盤（Saptavimshamsha）", "en": "D27 Saptavimshamsha"},
        descriptions={
            "zh-TW": "D27 Saptavimshamsha（亦稱 Bhamsha）常用於先天強弱、耐力、恢復力與在壓力下維持功能的能力。",
            "en": "D27 Saptavimshamsha, also called Bhamsha, is commonly consulted for inherent strengths, stamina, resilience, and the capacity to function under pressure.",
        },
        reference="Brihat Parashara Hora Shastra, chapter on the sixteen divisions of a sign",
    ),
    "D30": VargaInfo(
        code="D30",
        division=30,
        sanskrit_name="Trimshamsha",
        labels={"zh-TW": "D30 三十分盤（Trimshamsha）", "en": "D30 Trimshamsha"},
        descriptions={
            "zh-TW": "D30 Trimshamsha 採五個不等長區段，常用於困難、摩擦、弱點、疾病傾向與逆境模式的輔助判讀。",
            "en": "D30 Trimshamsha uses five unequal spans and is commonly consulted for adversity, friction, vulnerabilities, illness tendencies, and patterns of difficulty.",
        },
        reference="Brihat Parashara Hora Shastra, classical unequal Trimshamsha rule",
    ),
    "D40": VargaInfo(
        code="D40",
        division=40,
        sanskrit_name="Khavedamsha",
        labels={"zh-TW": "D40 四十分盤（Khavedamsha）", "en": "D40 Khavedamsha"},
        descriptions={
            "zh-TW": "D40 Khavedamsha 常用於母系傳承、細微福德、吉凶積累與家族背景的輔助判讀。",
            "en": "D40 Khavedamsha is commonly consulted for maternal lineage, subtle merit, accumulated auspicious or inauspicious influences, and family background.",
        },
        reference="Brihat Parashara Hora Shastra, chapter on the sixteen divisions of a sign",
        warnings={
            "zh-TW": "D40 每一分段只有 45 角分，對出生時間相當敏感；若出生時間未經確認，請將結果視為暫定。",
            "en": "Each D40 segment is only 45 arc-minutes. Treat the result as provisional when the birth time is not well verified.",
        },
    ),
    "D45": VargaInfo(
        code="D45",
        division=45,
        sanskrit_name="Akshavedamsha",
        labels={"zh-TW": "D45 四十五分盤（Akshavedamsha）", "en": "D45 Akshavedamsha"},
        descriptions={
            "zh-TW": "D45 Akshavedamsha 常用於父系傳承、性格根基、價值取向與細微內在傾向的輔助判讀。",
            "en": "D45 Akshavedamsha is commonly consulted for paternal lineage, character foundations, values, and subtle inner tendencies.",
        },
        reference="Brihat Parashara Hora Shastra, chapter on the sixteen divisions of a sign",
        warnings={
            "zh-TW": "D45 每一分段只有 40 角分，對出生時間非常敏感；請優先使用可靠且精確的出生時間。",
            "en": "Each D45 segment is only 40 arc-minutes and is highly birth-time sensitive. Use a reliably recorded birth time.",
        },
    ),
    "D60": VargaInfo(
        code="D60",
        division=60,
        sanskrit_name="Shashtiamsha",
        labels={"zh-TW": "D60 六十分盤（Shashtiamsha）", "en": "D60 Shashtiamsha"},
        descriptions={
            "zh-TW": "D60 Shashtiamsha 是最細緻的標準分盤，常用於深層業力背景與整體命盤的細部交叉檢視。本版目前顯示 D60 星座與宮位，尚未加入六十位神祇名稱。",
            "en": "D60 Shashtiamsha is the finest standard varga and is commonly used for deep karmic context and fine cross-checking of the whole chart. This version displays D60 signs and houses; the sixty deity names are not yet included.",
        },
        reference="Brihat Parashara Hora Shastra, Chapter 6 Shashtiamsha rules",
        warnings={
            "zh-TW": "D60 每一分段只有 0°30′，上升點可能因約數分鐘的出生時間差而改變。未經校時的出生資料，不應單獨依賴 D60 判斷。",
            "en": "Each D60 segment is only 0°30′. A difference of a few birth-time minutes can change the D60 Ascendant. Do not rely on D60 alone when the birth time is unrectified.",
        },
    ),
}

SUPPORTED_VARGA_CODES: tuple[str, ...] = tuple(VARGA_REGISTRY)


def get_varga_info(code: str) -> VargaInfo:
    """Return metadata for a stable varga code or raise a clear error."""
    try:
        return VARGA_REGISTRY[code]
    except KeyError as exc:
        raise ValueError(f"Unsupported varga code: {code}") from exc
