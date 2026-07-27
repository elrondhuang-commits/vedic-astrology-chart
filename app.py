from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
import streamlit as st
import streamlit.components.v1 as components

from astrology import calculate_chart, resolve_local_time
from north_indian_chart import render_north_indian_svg

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Common Traditional Chinese Taiwan place names are converted to the canonical
# English names used by the geocoder, then restricted to Taiwan. This keeps the
# global search unchanged while fixing common searches such as "台南".
TAIWAN_CITY_ALIASES = {
    "台北": "Taipei",
    "新北": "New Taipei",
    "桃園": "Taoyuan",
    "台中": "Taichung",
    "台南": "Tainan",
    "高雄": "Kaohsiung",
    "基隆": "Keelung",
    "新竹": "Hsinchu",
    "嘉義": "Chiayi",
    "苗栗": "Miaoli",
    "彰化": "Changhua",
    "南投": "Nantou",
    "雲林": "Yunlin",
    "屏東": "Pingtung",
    "宜蘭": "Yilan",
    "花蓮": "Hualien",
    "台東": "Taitung",
    "澎湖": "Penghu",
    "金門": "Kinmen",
}

TEXT = {
    "zh-TW": {
        "page_title": "吠陀占星本命盤",
        "title": "吠陀占星本命盤",
        "subtitle": "D1 本命盤、月亮盤、D2／D3／D9／D10 分盤與 Vimshottari 大運",
        "language": "語言",
        "birth_date": "出生日期",
        "birth_time": "出生時間",
        "time_select": "分開選擇小時與分鐘",
        "time_manual": "自行輸入",
        "birth_hour": "小時（24 小時制）",
        "birth_minute": "分鐘",
        "manual_birth_time": "自行輸入時間（HH:MM）",
        "manual_time_help": "請使用 24 小時制，例如 08:05 或 23:40。可使用半形或全形冒號。",
        "invalid_time": "時間格式不正確。請輸入 00:00 到 23:59，例如 08:05。",
        "time_tip": "可分開調整小時與分鐘，也可切換為自行輸入完整時間。",
        "city_search": "出生城市",
        "city_notice": "城市搜尋建議使用英文或羅馬拼音，例如 Tainan、Taipei。系統會自動辨識部分常見的台灣中文縣市名稱；請核對國家／地區、行政區、座標與 IANA 時區。",
        "city_help": "建議輸入英文或羅馬拼音，例如 Tainan、Taipei 或 Tokyo。輸入至少 2 個字元，再從結果中選擇正確城市。",
        "city_placeholder": "例如 Tainan、Taipei、Tokyo",
        "taiwan_alias": "已將「{original}」辨識為台灣地名，改用「{canonical}」並限定台灣（TW）搜尋。",
        "search": "搜尋城市",
        "select_city": "選擇城市",
        "timezone": "IANA 時區",
        "coordinates": "座標",
        "calculate": "計算星盤與大運",
        "enter_city": "請先搜尋並選擇出生城市。",
        "api_error": "城市搜尋暫時失敗，請稍後重試。",
        "no_results": "找不到城市。請改用英文／羅馬拼音、檢查拼字，或嘗試較大的鄰近城市。",
        "ambiguous": "此出生時間因夏令時間結束而出現兩次，請選擇正確的 UTC 位移。",
        "choose_offset": "選擇當時的 UTC 位移",
        "nonexistent": "此本地時間因夏令時間開始而不存在。請修正出生時間。",
        "invalid_timezone": "城市提供的時區無效，請選擇其他搜尋結果。",
        "tab_d1": "D1 本命盤",
        "tab_moon": "月亮盤",
        "tab_vargas": "分盤",
        "tab_dasha": "大運",
        "tab_positions": "行星表",
        "tab_notes": "計算說明",
        "d1_chart": "北印度式 D1 本命盤",
        "moon_chart": "北印度式月亮盤（Chandra Lagna）",
        "moon_description": "月亮盤不是另一張分盤，而是以月亮所在星座作為第一宮，將 D1 的星體依 Whole Sign 重新排宮；星體黃經本身不變。",
        "moon_positions": "月亮盤行星位置",
        "division_select": "選擇分盤",
        "d2_label": "D2 二分盤（Hora）",
        "d3_label": "D3 三分盤（Drekkana）",
        "d9_label": "D9 九分盤（Navamsha）",
        "d10_label": "D10 十分盤（Dashamsha）",
        "d2_description": "D2 Hora 常用於財富、資源、累積方式與物質支持的輔助判讀。此版本採傳統 Parashari 太陽／月亮 Hora。",
        "d3_description": "D3 Drekkana 常用於手足、勇氣、行動力、努力方式與生命活力的輔助判讀。",
        "d9_description": "D9 是最常用的分盤之一，常用於婚姻、關係、法則與行星成熟度的輔助判讀。",
        "d10_description": "D10 常用於職涯、工作角色、責任與社會表現的輔助判讀。",
        "varga_positions": "分盤行星位置",
        "positions": "D1 行星位置",
        "body": "天體",
        "sign": "星座",
        "degree": "星座內度數",
        "varga_degree": "分盤星座內度數",
        "nakshatra": "宿（Nakshatra）",
        "pada": "Pada",
        "house": "宮位",
        "motion": "狀態",
        "direct": "順行",
        "retrograde": "逆行",
        "dasha_title": "Vimshottari 大運",
        "birth_nakshatra": "出生月亮星宿",
        "birth_mahadasha": "出生時大運",
        "balance_at_birth": "出生時剩餘",
        "balance_ends": "出生時大運結束",
        "current_period": "目前期間",
        "current_summary": "目前大運與次運",
        "remaining": "剩餘時間",
        "elapsed": "已經過",
        "progress": "期間進度",
        "period_dates": "期間",
        "timeline": "大運時間軸",
        "duration_explanation": "大運年數是 Vimshottari 系統的固定完整期間；次運年數會依比例產生小數。",
        "current_as_of": "「目前」判定時間",
        "mahadasha_table": "大運表",
        "antardasha_table": "次運表",
        "select_mahadasha": "查看哪一個大運的次運",
        "mahadasha": "大運",
        "antardasha": "次運",
        "start": "開始",
        "end": "結束",
        "duration_years": "年數（年）",
        "duration_readable": "約略期間",
        "status": "標記",
        "at_birth": "出生時",
        "current": "目前",
        "none": "無",
        "dasha_date_note": "所有大運日期均換算為出生地時區：{timezone}。期間以開始時間包含、結束時間不包含。",
        "dasha_convention": "日期換算採平均公曆年 365.2425 日。不同軟體若使用平均恆星年、365.25 日或 360 日年，邊界日期可能略有差異。",
        "calculation_context": "本次計算資料",
        "local_birth_time": "出生地當地時間",
        "calculated_city": "出生地",
        "settings": "計算設定",
        "settings_text": "恆星黃道 Lahiri ayanamsha；True Node；Whole Sign houses；月亮盤；Parashari D2/D3/D9/D10；Vimshottari 120 年週期。",
        "varga_method_note": "月亮盤：以月亮星座作第一宮，D1 黃經不變。D2：奇數星座前半為太陽 Hora（獅子）、後半為月亮 Hora（巨蟹）；偶數星座相反。D3：每 10° 一段，依序落入本星座、第五與第九星座。D9：活動星座從本星座起、固定星座從第九星座起、雙體星座從第五星座起。D10：奇數星座從本星座起，偶數星座從第九星座起。",
        "dasha_method_note": "起始大運依出生月亮所在 Nakshatra 的守護星決定；出生時剩餘比例依月亮尚未走完的星宿比例計算。次運長度＝大運年數 × 次運守護星年數 ÷ 120。",
        "privacy": "隱私",
        "privacy_text": "本網站不使用資料庫，不會主動儲存你輸入的出生資料。Streamlit 與網路基礎設施仍可能產生一般技術日誌。",
        "sources": "資料來源",
        "sources_text": "城市資料：Open-Meteo Geocoding API（基於 GeoNames）。天文計算：Swiss Ephemeris / pyswisseph。歷史時區：Python zoneinfo 與 tzdata。",
        "disclaimer": "聲明",
        "disclaimer_text": "本網站內容僅供教育、文化與娛樂用途，不構成醫療、心理、法律、稅務、投資或其他專業建議。重大決策請諮詢合格專業人士。分盤與大運不應作為單一決策依據。",
        "license": "本專案採 AGPL-3.0 授權。",
        "request_error": "無法完成計算：",
        "chart_missing": "目前工作階段中的舊資料格式已失效，請重新按一次「計算星盤與大運」。",
    },
    "en": {
        "page_title": "Vedic Natal Chart",
        "title": "Vedic Natal Chart",
        "subtitle": "D1 Rashi, Moon chart, D2/D3/D9/D10 vargas, and Vimshottari dasha",
        "language": "Language",
        "birth_date": "Birth date",
        "birth_time": "Birth time",
        "time_select": "Select hour and minute separately",
        "time_manual": "Enter manually",
        "birth_hour": "Hour (24-hour clock)",
        "birth_minute": "Minute",
        "manual_birth_time": "Enter time (HH:MM)",
        "manual_time_help": "Use the 24-hour clock, for example 08:05 or 23:40.",
        "invalid_time": "Invalid time. Enter a value from 00:00 to 23:59, for example 08:05.",
        "time_tip": "Adjust the hour and minute separately, or switch to manual entry.",
        "city_search": "Birth city",
        "city_notice": "For the most reliable search, enter the city in English or romanized form, such as Tainan or Taipei. Always verify the country/region, administrative area, coordinates, and IANA timezone.",
        "city_help": "Enter at least 2 characters, preferably an English or romanized city name, then select the correct result.",
        "city_placeholder": "For example Tainan, Taipei, or Tokyo",
        "taiwan_alias": "Recognized “{original}” as a Taiwan place name. Searching for “{canonical}” within Taiwan (TW).",
        "search": "Search cities",
        "select_city": "Select city",
        "timezone": "IANA timezone",
        "coordinates": "Coordinates",
        "calculate": "Calculate charts and dasha",
        "enter_city": "Search for and select a birth city first.",
        "api_error": "City search is temporarily unavailable. Please try again.",
        "no_results": "No cities found. Try an English/romanized spelling or a larger nearby city.",
        "ambiguous": "This local time occurred twice when daylight saving time ended. Select the correct UTC offset.",
        "choose_offset": "Select the UTC offset in effect",
        "nonexistent": "This local time did not exist because daylight saving time began. Correct the birth time.",
        "invalid_timezone": "The selected result has an invalid timezone. Choose another result.",
        "tab_d1": "D1 Rashi",
        "tab_moon": "Moon chart",
        "tab_vargas": "Divisional charts",
        "tab_dasha": "Dasha",
        "tab_positions": "Planet table",
        "tab_notes": "Calculation notes",
        "d1_chart": "North Indian D1 Rashi chart",
        "moon_chart": "North Indian Moon chart (Chandra Lagna)",
        "moon_description": "The Moon chart is not a separate varga. It uses the Moon's sign as whole-sign house 1 and recalculates houses from the unchanged D1 sidereal longitudes.",
        "moon_positions": "Moon-chart positions",
        "division_select": "Select a divisional chart",
        "d2_label": "D2 Hora",
        "d3_label": "D3 Drekkana",
        "d9_label": "D9 Navamsha",
        "d10_label": "D10 Dashamsha",
        "d2_description": "D2 Hora is commonly consulted for wealth, resources, accumulation patterns, and material support. This version uses the classical Parashari Sun/Moon Hora.",
        "d3_description": "D3 Drekkana is commonly consulted for siblings, courage, initiative, effort, and vitality.",
        "d9_description": "D9 is one of the most frequently used divisional charts and is commonly consulted for marriage, relationships, dharma, and planetary maturity.",
        "d10_description": "D10 is commonly consulted for career, work roles, responsibility, and public expression.",
        "varga_positions": "Divisional positions",
        "positions": "D1 planetary positions",
        "body": "Body",
        "sign": "Sign",
        "degree": "Degree in sign",
        "varga_degree": "Degree in varga sign",
        "nakshatra": "Nakshatra",
        "pada": "Pada",
        "house": "House",
        "motion": "Motion",
        "direct": "Direct",
        "retrograde": "Retrograde",
        "dasha_title": "Vimshottari dasha",
        "birth_nakshatra": "Birth Moon nakshatra",
        "birth_mahadasha": "Mahadasha at birth",
        "balance_at_birth": "Balance at birth",
        "balance_ends": "Birth Mahadasha ends",
        "current_period": "Current period",
        "current_summary": "Current Mahadasha and Antardasha",
        "remaining": "Time remaining",
        "elapsed": "Elapsed",
        "progress": "Period progress",
        "period_dates": "Period",
        "timeline": "Mahadasha timeline",
        "duration_explanation": "Mahadasha years are the fixed full lengths in Vimshottari; Antardasha years are proportional and therefore usually decimal values.",
        "current_as_of": "Current as of",
        "mahadasha_table": "Mahadasha timeline",
        "antardasha_table": "Antardasha timeline",
        "select_mahadasha": "Choose a Mahadasha to inspect",
        "mahadasha": "Mahadasha",
        "antardasha": "Antardasha",
        "start": "Start",
        "end": "End",
        "duration_years": "Years",
        "duration_readable": "Approx. duration",
        "status": "Marker",
        "at_birth": "At birth",
        "current": "Current",
        "none": "None",
        "dasha_date_note": "All dasha dates are shown in the birth-place timezone: {timezone}. Start times are inclusive and end times are exclusive.",
        "dasha_convention": "Civil dates use a mean Gregorian year of 365.2425 days. Software using a mean sidereal year, 365.25 days, or a 360-day year can show slightly different boundaries.",
        "calculation_context": "Calculation context",
        "local_birth_time": "Local birth time",
        "calculated_city": "Birth place",
        "settings": "Calculation settings",
        "settings_text": "Sidereal Lahiri ayanamsha; True Node; Whole Sign houses; Moon chart; Parashari D2/D3/D9/D10; 120-year Vimshottari cycle.",
        "varga_method_note": "Moon chart: the Moon sign becomes house 1 while D1 longitudes remain unchanged. D2: in odd signs the first half is Sun Hora (Leo) and the second half Moon Hora (Cancer), reversed in even signs. D3: each 10-degree decan maps to the natal sign, fifth, and ninth. D9 and D10 use the stated Parashari mappings.",
        "dasha_method_note": "The birth Moon's Nakshatra ruler starts the Mahadasha. The balance at birth follows the untraversed fraction of that Nakshatra. Antardasha length = Mahadasha years × Antardasha-lord years ÷ 120.",
        "privacy": "Privacy",
        "privacy_text": "This app uses no database and does not intentionally store birth data you enter. Streamlit and network infrastructure may still produce ordinary technical logs.",
        "sources": "Data sources",
        "sources_text": "Cities: Open-Meteo Geocoding API (based on GeoNames). Astronomy: Swiss Ephemeris / pyswisseph. Historical timezones: Python zoneinfo and tzdata.",
        "disclaimer": "Disclaimer",
        "disclaimer_text": "For educational, cultural, and entertainment purposes only. This is not medical, psychological, legal, tax, investment, or other professional advice. Divisional charts and dasha periods should not be used as a sole basis for important decisions.",
        "license": "Licensed under AGPL-3.0.",
        "request_error": "Unable to calculate: ",
        "chart_missing": "Old session data no longer matches this version. Press “Calculate charts and dasha” again.",
    },
}

SIGN_ZH = {
    "Aries": "牡羊座",
    "Taurus": "金牛座",
    "Gemini": "雙子座",
    "Cancer": "巨蟹座",
    "Leo": "獅子座",
    "Virgo": "處女座",
    "Libra": "天秤座",
    "Scorpio": "天蠍座",
    "Sagittarius": "射手座",
    "Capricorn": "摩羯座",
    "Aquarius": "水瓶座",
    "Pisces": "雙魚座",
}
BODY_ZH = {
    "Ascendant": "上升",
    "Sun": "太陽",
    "Moon": "月亮",
    "Mars": "火星",
    "Mercury": "水星",
    "Jupiter": "木星",
    "Venus": "金星",
    "Saturn": "土星",
    "Rahu": "羅喉",
    "Ketu": "計都",
}
BODY_ABBR_ZH = {
    "Ascendant": "升",
    "Sun": "日",
    "Moon": "月",
    "Mars": "火",
    "Mercury": "水",
    "Jupiter": "木",
    "Venus": "金",
    "Saturn": "土",
    "Rahu": "羅",
    "Ketu": "計",
}

st.set_page_config(page_title="吠陀占星 | Vedic Astrology", page_icon="✨", layout="wide")
st.markdown(
    """
    <style>
      /* Main layout */
      .block-container {
        max-width: 1120px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
      }

      /* Hide Streamlit's automatic heading-anchor icon. */
      [data-testid="stHeaderActionElements"],
      [data-testid="stHeadingWithActionElements"] a,
      h1 > a, h2 > a, h3 > a, h4 > a, h5 > a, h6 > a,
      a.anchor-link {
        display: none !important;
      }

      /* Keep section titles visually consistent. */
      [data-testid="stHeadingWithActionElements"] h1,
      [data-testid="stHeadingWithActionElements"] h2,
      [data-testid="stHeadingWithActionElements"] h3 {
        letter-spacing: -0.015em;
        line-height: 1.3;
      }
      [data-testid="stHeadingWithActionElements"] h2,
      [data-testid="stHeadingWithActionElements"] h3 {
        margin-top: 0.35rem;
        margin-bottom: 0.65rem;
      }

      /* Metrics and tables */
      [data-testid="stMetricValue"] {font-size: 1.35rem;}
      [data-testid="stDataFrame"] {margin-top: 0.35rem; margin-bottom: 1rem;}

      /* Tabs remain usable on narrow screens instead of squeezing labels. */
      [data-baseweb="tab-list"] {
        gap: 0.35rem;
        overflow-x: auto;
        scrollbar-width: thin;
      }
      [data-baseweb="tab"] {white-space: nowrap;}

      @media (max-width: 700px) {
        .block-container {
          padding-left: 0.85rem;
          padding-right: 0.85rem;
          padding-top: 1rem;
        }
        [data-testid="stMetricValue"] {font-size: 1.15rem;}
        [data-testid="stHeadingWithActionElements"] h2 {font-size: 1.45rem;}
        [data-testid="stHeadingWithActionElements"] h3 {font-size: 1.2rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def prepare_city_search(query: str) -> tuple[str, str | None, bool]:
    """Return API query, optional country code, and whether a Taiwan alias was used."""
    cleaned = " ".join(query.strip().split())
    normalized = unicodedata.normalize("NFKC", cleaned).replace("臺", "台")
    compact = re.sub(r"[\s,，]+", "", normalized)

    for country_suffix in ("台灣", "台湾"):
        if compact.endswith(country_suffix):
            compact = compact[: -len(country_suffix)]
            break

    if compact.endswith(("市", "縣")):
        compact = compact[:-1]

    canonical = TAIWAN_CITY_ALIASES.get(compact)
    if canonical:
        return canonical, "TW", True
    return cleaned, None, False


@st.cache_data(ttl=3600, show_spinner=False)
def search_cities(query: str, language: str, country_code: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "name": query.strip(),
        "count": 10,
        "language": "zh" if language == "zh-TW" else "en",
        "format": "json",
    }
    if country_code:
        params["countryCode"] = country_code

    response = requests.get(GEOCODING_URL, params=params, timeout=12)
    response.raise_for_status()
    data = response.json()
    results: list[dict[str, Any]] = []
    for item in data.get("results", []):
        if not item.get("timezone"):
            continue
        results.append(
            {
                "id": item.get("id"),
                "name": item.get("name", ""),
                "country": item.get("country", ""),
                "country_code": item.get("country_code", ""),
                "admin1": item.get("admin1", ""),
                "latitude": float(item["latitude"]),
                "longitude": float(item["longitude"]),
                "timezone": item["timezone"],
            }
        )
    return results


def _place_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().casefold()
    normalized = normalized.replace("臺", "台").replace("湾", "灣")
    return re.sub(r"[\s,，._\-()（）]+", "", normalized)


def city_display_parts(city: Mapping[str, Any], language: str) -> list[str]:
    """Build normalized display parts without modifying raw geocoder data."""
    country_code = str(city.get("country_code", "")).upper()
    country = str(city.get("country", ""))
    admin1 = str(city.get("admin1", ""))

    if country_code == "TW":
        country = "台灣" if language == "zh-TW" else "Taiwan"
        province_labels = {
            "台灣",
            "台灣省",
            "taiwan",
            "taiwanprovince",
            "provinceoftaiwan",
            "taiwanprovinceofchina",
            "taiwanprovincechina",
        }
        if _place_key(admin1) in province_labels:
            admin1 = ""

    country_with_code = country
    if country_code and country_code != "TW":
        country_with_code = f"{country} ({country_code})" if country else country_code

    parts: list[str] = []
    seen: set[str] = set()
    for part in (str(city.get("name", "")), admin1, country_with_code):
        key = _place_key(part)
        if part and key not in seen:
            parts.append(part)
            seen.add(key)
    return parts


def city_label(city: Mapping[str, Any], language: str) -> str:
    place = ", ".join(city_display_parts(city, language))
    return f"{place} — {float(city['latitude']):.4f}, {float(city['longitude']):.4f} — {city['timezone']}"


def parse_manual_time(value: str) -> time | None:
    normalized = unicodedata.normalize("NFKC", value).strip()
    match = re.fullmatch(r"(\d{1,2})\s*:\s*(\d{1,2})", normalized)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        return None
    return time(hour, minute)


def format_degree(value: float) -> str:
    degrees = int(value)
    minutes_float = (value - degrees) * 60
    minutes = int(minutes_float)
    seconds = int(round((minutes_float - minutes) * 60))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    return f"{degrees:02d}° {minutes:02d}′ {seconds:02d}″"


def body_label(code: str, language: str) -> str:
    return BODY_ZH.get(code, code) if language == "zh-TW" else code


def sign_label(sign: str, language: str) -> str:
    return SIGN_ZH.get(sign, sign) if language == "zh-TW" else sign


def format_local_datetime(iso_utc: str, timezone_name: str) -> str:
    value = datetime.fromisoformat(iso_utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    try:
        local = value.astimezone(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        local = value.astimezone(timezone.utc)
    return local.strftime("%Y-%m-%d %H:%M %Z")



def parse_utc_datetime(value: str) -> datetime:
    """Parse an ISO UTC datetime produced by astrology.py."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def humanize_duration(start_utc: str, end_utc: str, language: str) -> str:
    """Return a readable approximate calendar duration."""
    seconds = max(0.0, (parse_utc_datetime(end_utc) - parse_utc_datetime(start_utc)).total_seconds())
    total_days = int(round(seconds / 86400.0))
    years, remaining_days = divmod(total_days, 365)
    months, days = divmod(remaining_days, 30)
    parts: list[str] = []
    if language == "zh-TW":
        if years:
            parts.append(f"{years} 年")
        if months:
            parts.append(f"{months} 個月")
        if days and not years:
            parts.append(f"{days} 天")
        return " ".join(parts) or "少於 1 天"
    if years:
        parts.append(f"{years} yr")
    if months:
        parts.append(f"{months} mo")
    if days and not years:
        parts.append(f"{days} d")
    return " ".join(parts) or "less than 1 day"


def humanize_remaining(end_utc: str, as_of_utc: str, language: str) -> str:
    end_dt = parse_utc_datetime(end_utc)
    as_of_dt = parse_utc_datetime(as_of_utc)
    if end_dt <= as_of_dt:
        return "已結束" if language == "zh-TW" else "Ended"
    return humanize_duration(as_of_utc, end_utc, language)


def period_progress(start_utc: str, end_utc: str, as_of_utc: str) -> float:
    start_dt = parse_utc_datetime(start_utc)
    end_dt = parse_utc_datetime(end_utc)
    as_of_dt = parse_utc_datetime(as_of_utc)
    duration = (end_dt - start_dt).total_seconds()
    if duration <= 0:
        return 0.0
    return max(0.0, min(1.0, (as_of_dt - start_dt).total_seconds() / duration))


def format_year_value(years: float, is_mahadasha: bool, language: str) -> str:
    """Keep whole Mahadasha years clear; show useful decimals for Antardasha."""
    unit = "年" if language == "zh-TW" else "years"
    if is_mahadasha and abs(years - round(years)) < 1e-9:
        return f"{int(round(years))} {unit}"
    return f"{years:.3f} {unit}"

def chart_rows(chart: Mapping[str, Any], language: str, include_nakshatra: bool) -> list[dict[str, Any]]:
    t = TEXT[language]
    rows: list[dict[str, Any]] = []
    for item in chart["positions"]:
        row: dict[str, Any] = {
            t["body"]: body_label(str(item["code"]), language),
            t["sign"]: sign_label(str(item["sign"]), language),
            t["degree"] if include_nakshatra else t["varga_degree"]: format_degree(float(item["degree_in_sign"])),
            t["house"]: int(item["house"]),
            t["motion"]: t["retrograde"] if item["retrograde"] else t["direct"],
        }
        if include_nakshatra:
            row[t["nakshatra"]] = item["nakshatra"]
            row[t["pada"]] = int(item["pada"])
        rows.append(row)
    return rows


def period_status(period: Mapping[str, Any], language: str) -> str:
    t = TEXT[language]
    markers: list[str] = []
    if period.get("at_birth"):
        markers.append(f"● {t['at_birth']}")
    if period.get("current"):
        markers.append(f"▶ {t['current']}")
    return " · ".join(markers) if markers else ""


def render_chart_svg(chart: Mapping[str, Any], language: str) -> None:
    svg = render_north_indian_svg(
        chart,
        sign_labels=SIGN_ZH if language == "zh-TW" else {},
        planet_labels=BODY_ABBR_ZH if language == "zh-TW" else {},
    )
    html = f"""
    <style>
      html, body {{ margin: 0; background: transparent; }}
      .chart-card {{
        max-width: 680px;
        margin: auto;
        padding: 8px;
        box-sizing: border-box;
        border-radius: 10px;
        background: #ffffff;
        color: #111827;
      }}
    </style>
    <div class="chart-card">{svg}</div>
    """
    components.html(html, height=680, scrolling=False)


language = st.sidebar.selectbox("Language / 語言", ["zh-TW", "en"], index=0)
t = TEXT[language]

st.title(t["title"])
st.caption(t["subtitle"])

with st.sidebar:
    st.markdown(f"### {t['settings']}")
    st.write("Sidereal · Lahiri")
    st.write("True Node · Whole Sign")
    st.write("D1 · Moon · D2 · D3 · D9 · D10")
    st.write("Vimshottari")
    st.caption(t["license"])

birth_date_column, birth_time_column = st.columns([1, 1])
with birth_date_column:
    birth_date = st.date_input(
        t["birth_date"],
        value=date(1990, 1, 1),
        min_value=date(1800, 1, 1),
        max_value=date.today(),
    )

with birth_time_column:
    time_mode = st.radio(
        t["birth_time"],
        options=["select", "manual"],
        format_func=lambda value: t["time_select"] if value == "select" else t["time_manual"],
        horizontal=True,
        key="birth_time_mode",
    )

    birth_time_value: time | None
    if time_mode == "select":
        hour_column, minute_column = st.columns(2)
        with hour_column:
            birth_hour = st.number_input(
                t["birth_hour"],
                min_value=0,
                max_value=23,
                value=12,
                step=1,
                format="%02d",
                key="birth_hour",
            )
        with minute_column:
            birth_minute = st.number_input(
                t["birth_minute"],
                min_value=0,
                max_value=59,
                value=0,
                step=1,
                format="%02d",
                key="birth_minute",
            )
        birth_time_value = time(int(birth_hour), int(birth_minute))
    else:
        manual_time_text = st.text_input(
            t["manual_birth_time"],
            value="12:00",
            help=t["manual_time_help"],
            placeholder="08:05",
            key="manual_birth_time",
        )
        birth_time_value = parse_manual_time(manual_time_text)
        if birth_time_value is None:
            st.error(t["invalid_time"])

    st.caption(t["time_tip"])

st.info(t["city_notice"])
query = st.text_input(
    t["city_search"],
    help=t["city_help"],
    placeholder=t["city_placeholder"],
)

if st.button(t["search"], type="secondary", disabled=len(query.strip()) < 2):
    api_query, country_code, alias_used = prepare_city_search(query)
    search_context = {
        "raw_query": query.strip(),
        "language": language,
        "api_query": api_query,
        "country_code": country_code,
        "alias_used": alias_used,
        "failed": False,
    }
    try:
        st.session_state["city_results"] = search_cities(api_query, language, country_code)
    except (requests.RequestException, ValueError):
        st.session_state["city_results"] = []
        search_context["failed"] = True
        st.error(t["api_error"])
    st.session_state["city_search_context"] = search_context
    st.session_state.pop("selected_city_index", None)

search_context = st.session_state.get("city_search_context", {})
is_current_search = (
    search_context.get("raw_query") == query.strip()
    and search_context.get("language") == language
)
results = st.session_state.get("city_results", []) if is_current_search else []

if is_current_search and search_context.get("alias_used"):
    st.caption(
        t["taiwan_alias"].format(
            original=search_context.get("raw_query", ""),
            canonical=search_context.get("api_query", ""),
        )
    )

selected_city: dict[str, Any] | None = None
if results:
    index = st.selectbox(
        t["select_city"],
        options=range(len(results)),
        format_func=lambda i: city_label(results[i], language),
        key="selected_city_index",
    )
    selected_city = results[index]
    metric_timezone, metric_coordinates = st.columns(2)
    metric_timezone.metric(t["timezone"], selected_city["timezone"])
    metric_coordinates.metric(
        t["coordinates"],
        f"{selected_city['latitude']:.4f}, {selected_city['longitude']:.4f}",
    )
elif is_current_search and not search_context.get("failed"):
    st.info(t["no_results"])

utc_choice: datetime | None = None
if selected_city and birth_time_value is not None:
    local_naive = datetime.combine(birth_date, birth_time_value)
    time_resolution = resolve_local_time(local_naive, selected_city["timezone"])
    if time_resolution.status == "ambiguous":
        st.warning(t["ambiguous"])
        choice_index = st.radio(
            t["choose_offset"],
            options=range(len(time_resolution.choices_utc)),
            format_func=lambda i: (
                f"{time_resolution.offsets[i]} → "
                f"{time_resolution.choices_utc[i].strftime('%Y-%m-%d %H:%M UTC')}"
            ),
            key=f"ambiguous_{birth_date}_{birth_time_value}_{selected_city['timezone']}",
        )
        utc_choice = time_resolution.choices_utc[choice_index]
    elif time_resolution.status == "valid":
        utc_choice = time_resolution.choices_utc[0]
    elif time_resolution.status == "nonexistent":
        st.error(t["nonexistent"])
    else:
        st.error(t["invalid_timezone"])

can_calculate = selected_city is not None and utc_choice is not None
if st.button(t["calculate"], type="primary", disabled=not can_calculate, use_container_width=True):
    try:
        assert selected_city is not None
        assert utc_choice is not None
        local_naive = datetime.combine(birth_date, birth_time_value)
        st.session_state.pop("selected_mahadasha_index", None)
        st.session_state["chart"] = calculate_chart(
            utc_choice,
            selected_city["latitude"],
            selected_city["longitude"],
        )
        st.session_state["chart_context"] = {
            "city": dict(selected_city),
            "birth_local": local_naive.isoformat(timespec="minutes"),
            "timezone": selected_city["timezone"],
        }
    except Exception as exc:
        st.error(f"{t['request_error']}{exc}")

if not selected_city:
    st.caption(t["enter_city"])

chart = st.session_state.get("chart")
chart_context = st.session_state.get("chart_context", {})
required_chart_codes = {"D1", "Moon", "D2", "D3", "D9", "D10"}
if chart and (
    "charts" not in chart
    or not required_chart_codes.issubset(set(chart.get("charts", {}).keys()))
):
    st.warning(t["chart_missing"])
    chart = None

if chart:
    st.divider()
    context_city = chart_context.get("city", {})
    context_timezone = str(chart_context.get("timezone", "UTC"))
    context_place = ", ".join(city_display_parts(context_city, language)) if context_city else ""

    with st.expander(t["calculation_context"], expanded=False):
        st.write(f"**{t['calculated_city']}：** {context_place}")
        st.write(
            f"**{t['local_birth_time']}：** {chart_context.get('birth_local', '')} "
            f"({context_timezone})"
        )
        st.write(
            f"**UTC：** {chart['utc_datetime']} · **JD(UT)：** {chart['julian_day_ut']:.6f}"
        )

    tab_d1, tab_moon, tab_vargas, tab_dasha, tab_positions, tab_notes = st.tabs(
        [
            t["tab_d1"],
            t["tab_moon"],
            t["tab_vargas"],
            t["tab_dasha"],
            t["tab_positions"],
            t["tab_notes"],
        ]
    )

    with tab_d1:
        st.subheader(t["d1_chart"])
        render_chart_svg(chart["charts"]["D1"], language)

    with tab_moon:
        st.info(t["moon_description"])
        st.subheader(t["moon_chart"])
        moon_chart = chart["charts"]["Moon"]
        render_chart_svg(moon_chart, language)
        st.subheader(t["moon_positions"])
        st.dataframe(
            chart_rows(moon_chart, language, include_nakshatra=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                t["body"]: st.column_config.TextColumn(width="small"),
                t["sign"]: st.column_config.TextColumn(width="small"),
                t["degree"]: st.column_config.TextColumn(width="medium"),
                t["nakshatra"]: st.column_config.TextColumn(width="medium"),
                t["pada"]: st.column_config.NumberColumn(width="small"),
                t["house"]: st.column_config.NumberColumn(width="small"),
                t["motion"]: st.column_config.TextColumn(width="small"),
            },
        )

    with tab_vargas:
        varga_labels = {
            "D2": t["d2_label"],
            "D3": t["d3_label"],
            "D9": t["d9_label"],
            "D10": t["d10_label"],
        }
        varga_descriptions = {
            "D2": t["d2_description"],
            "D3": t["d3_description"],
            "D9": t["d9_description"],
            "D10": t["d10_description"],
        }
        division_code = st.selectbox(
            t["division_select"],
            options=["D2", "D3", "D9", "D10"],
            format_func=lambda code: varga_labels[code],
            key="division_code",
        )
        st.info(varga_descriptions[division_code])

        varga_chart = chart["charts"][division_code]
        st.subheader(varga_labels[division_code])
        render_chart_svg(varga_chart, language)
        st.subheader(t["varga_positions"])
        st.dataframe(
            chart_rows(varga_chart, language, include_nakshatra=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                t["body"]: st.column_config.TextColumn(width="small"),
                t["sign"]: st.column_config.TextColumn(width="small"),
                t["varga_degree"]: st.column_config.TextColumn(width="medium"),
                t["house"]: st.column_config.NumberColumn(width="small"),
                t["motion"]: st.column_config.TextColumn(width="small"),
            },
        )

    with tab_dasha:
        dasha = chart["dasha"]
        current_period = dasha.get("current")
        current_text = t["none"]
        if current_period:
            current_text = (
                f"{body_label(current_period['mahadasha'], language)} / "
                f"{body_label(current_period['antardasha'], language)}"
            )

        summary_1, summary_2, summary_3, summary_4 = st.columns(4)
        summary_1.metric(
            t["birth_nakshatra"],
            f"{dasha['birth_nakshatra']} · Pada {dasha['birth_pada']}",
        )
        summary_2.metric(t["birth_mahadasha"], body_label(dasha["birth_lord"], language))
        balance_value = (
            f"{dasha['birth_balance_years']:.3f} 年"
            if language == "zh-TW"
            else f"{dasha['birth_balance_years']:.3f} years"
        )
        summary_3.metric(t["balance_at_birth"], balance_value)
        summary_4.metric(t["current_period"], current_text)

        if current_period:
            md_progress = period_progress(
                current_period["mahadasha_start_utc"],
                current_period["mahadasha_end_utc"],
                dasha["current_utc"],
            )
            ad_progress = period_progress(
                current_period["antardasha_start_utc"],
                current_period["antardasha_end_utc"],
                dasha["current_utc"],
            )
            with st.container(border=True):
                st.subheader(t["current_summary"])
                md_col, ad_col = st.columns(2)
                with md_col:
                    st.markdown(f"### {body_label(current_period['mahadasha'], language)}")
                    st.caption(
                        f"{format_local_datetime(current_period['mahadasha_start_utc'], context_timezone)} "
                        f"→ {format_local_datetime(current_period['mahadasha_end_utc'], context_timezone)}"
                    )
                    st.metric(
                        t["remaining"],
                        humanize_remaining(
                            current_period["mahadasha_end_utc"], dasha["current_utc"], language
                        ),
                    )
                    st.progress(md_progress, text=f"{t['progress']}：{md_progress * 100:.1f}%")
                with ad_col:
                    st.markdown(
                        f"### {body_label(current_period['mahadasha'], language)} / "
                        f"{body_label(current_period['antardasha'], language)}"
                    )
                    st.caption(
                        f"{format_local_datetime(current_period['antardasha_start_utc'], context_timezone)} "
                        f"→ {format_local_datetime(current_period['antardasha_end_utc'], context_timezone)}"
                    )
                    st.metric(
                        t["remaining"],
                        humanize_remaining(
                            current_period["antardasha_end_utc"], dasha["current_utc"], language
                        ),
                    )
                    st.progress(ad_progress, text=f"{t['progress']}：{ad_progress * 100:.1f}%")

        st.caption(
            f"{t['balance_ends']}："
            f"{format_local_datetime(dasha['birth_balance_end_utc'], context_timezone)}"
        )
        st.caption(
            f"{t['current_as_of']}: "
            f"{format_local_datetime(dasha['current_utc'], context_timezone)}"
        )
        st.caption(t["dasha_date_note"].format(timezone=context_timezone))
        st.info(t["duration_explanation"])
        st.warning(t["dasha_convention"])

        display_mahadashas = [
            period for period in dasha["mahadashas"] if period.get("within_display_window")
        ]
        current_mahadasha = next(
            (period for period in display_mahadashas if period.get("current")),
            None,
        )
        if current_mahadasha:
            st.subheader(t["timeline"])
            current_label = body_label(current_mahadasha["lord"], language)
            current_marker = period_status(current_mahadasha, language)
            current_heading = (
                f"**{current_label}** · "
                f"{format_year_value(float(current_mahadasha['duration_years']), True, language)}"
            )
            if current_marker:
                current_heading += f" · **{current_marker}**"
            st.markdown(current_heading)
            st.caption(
                f"{format_local_datetime(current_mahadasha['start_utc'], context_timezone)} → "
                f"{format_local_datetime(current_mahadasha['end_utc'], context_timezone)}"
            )
            current_md_progress = period_progress(
                current_mahadasha["start_utc"],
                current_mahadasha["end_utc"],
                dasha["current_utc"],
            )
            st.progress(
                current_md_progress,
                text=f"{t['progress']}：{current_md_progress * 100:.1f}%",
            )

        st.subheader(t["mahadasha_table"])
        mahadasha_rows = [
            {
                t["mahadasha"]: body_label(period["lord"], language),
                t["start"]: format_local_datetime(period["start_utc"], context_timezone),
                t["end"]: format_local_datetime(period["end_utc"], context_timezone),
                t["duration_years"]: format_year_value(float(period["duration_years"]), True, language),
                t["duration_readable"]: humanize_duration(period["start_utc"], period["end_utc"], language),
                t["status"]: period_status(period, language),
            }
            for period in display_mahadashas
        ]
        st.dataframe(
            mahadasha_rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                t["mahadasha"]: st.column_config.TextColumn(width="small"),
                t["start"]: st.column_config.TextColumn(width="medium"),
                t["end"]: st.column_config.TextColumn(width="medium"),
                t["duration_years"]: st.column_config.TextColumn(width="small"),
                t["duration_readable"]: st.column_config.TextColumn(width="small"),
                t["status"]: st.column_config.TextColumn(width="small"),
            },
        )

        default_md_index = next(
            (index for index, period in enumerate(display_mahadashas) if period.get("current")),
            next(
                (index for index, period in enumerate(display_mahadashas) if period.get("at_birth")),
                0,
            ),
        )
        selected_md_index = st.selectbox(
            t["select_mahadasha"],
            options=range(len(display_mahadashas)),
            index=default_md_index,
            format_func=lambda i: (
                f"{body_label(display_mahadashas[i]['lord'], language)} · "
                f"{format_local_datetime(display_mahadashas[i]['start_utc'], context_timezone)} → "
                f"{format_local_datetime(display_mahadashas[i]['end_utc'], context_timezone)}"
            ),
            key="selected_mahadasha_index",
        )
        selected_md = display_mahadashas[selected_md_index]

        st.subheader(t["antardasha_table"])
        antardasha_rows = [
            {
                t["mahadasha"]: body_label(selected_md["lord"], language),
                t["antardasha"]: body_label(period["lord"], language),
                t["start"]: format_local_datetime(period["start_utc"], context_timezone),
                t["end"]: format_local_datetime(period["end_utc"], context_timezone),
                t["duration_years"]: format_year_value(float(period["duration_years"]), False, language),
                t["duration_readable"]: humanize_duration(period["start_utc"], period["end_utc"], language),
                t["status"]: period_status(period, language),
            }
            for period in selected_md["antardashas"]
        ]
        st.dataframe(
            antardasha_rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                t["mahadasha"]: st.column_config.TextColumn(width="small"),
                t["antardasha"]: st.column_config.TextColumn(width="small"),
                t["start"]: st.column_config.TextColumn(width="medium"),
                t["end"]: st.column_config.TextColumn(width="medium"),
                t["duration_years"]: st.column_config.TextColumn(width="small"),
                t["duration_readable"]: st.column_config.TextColumn(width="small"),
                t["status"]: st.column_config.TextColumn(width="small"),
            },
        )

    with tab_positions:
        st.subheader(t["positions"])
        st.dataframe(
            chart_rows(chart["charts"]["D1"], language, include_nakshatra=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                t["body"]: st.column_config.TextColumn(width="small"),
                t["sign"]: st.column_config.TextColumn(width="small"),
                t["degree"]: st.column_config.TextColumn(width="medium"),
                t["nakshatra"]: st.column_config.TextColumn(width="medium"),
                t["pada"]: st.column_config.NumberColumn(width="small"),
                t["house"]: st.column_config.NumberColumn(width="small"),
                t["motion"]: st.column_config.TextColumn(width="small"),
            },
        )
        st.caption(f"UTC: {chart['utc_datetime']} · JD(UT): {chart['julian_day_ut']:.6f}")

    with tab_notes:
        st.subheader(t["settings"])
        st.write(t["settings_text"])
        st.write(t["varga_method_note"])
        st.write(t["dasha_method_note"])
        st.write(t["dasha_convention"])

        st.subheader(t["sources"])
        st.write(t["sources_text"])

        st.subheader(t["privacy"])
        st.write(t["privacy_text"])

        st.subheader(t["disclaimer"])
        st.write(t["disclaimer_text"])
        st.caption(t["license"])

st.divider()
st.caption(t["disclaimer_text"])
