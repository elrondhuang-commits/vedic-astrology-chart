from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, time
from typing import Any

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
        "title": "吠陀占星本命盤（D1）",
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
        "city_notice": "城市搜尋建議使用英文或羅馬拼音，例如 Tainan、Taipei。系統會自動辨識部分常見的台灣中文縣市名稱；無論使用哪種語言，都請核對國家／地區、行政區、座標與 IANA 時區。",
        "city_help": "建議輸入英文或羅馬拼音，例如 Tainan、Taipei 或 Tokyo。輸入至少 2 個字元，再從結果中選擇正確城市。",
        "city_placeholder": "例如 Tainan、Taipei、Tokyo",
        "taiwan_alias": "已將「{original}」辨識為台灣地名，改用「{canonical}」並限定台灣（TW）搜尋。",
        "search": "搜尋城市",
        "select_city": "選擇城市",
        "timezone": "IANA 時區",
        "coordinates": "座標",
        "calculate": "計算本命盤",
        "enter_city": "請先搜尋並選擇出生城市。",
        "api_error": "城市搜尋暫時失敗，請稍後重試。",
        "no_results": "找不到城市。請改用英文／羅馬拼音、檢查拼字，或嘗試較大的鄰近城市。",
        "ambiguous": "此出生時間因夏令時間結束而出現兩次，請選擇正確的 UTC 位移。",
        "choose_offset": "選擇當時的 UTC 位移",
        "nonexistent": "此本地時間因夏令時間開始而不存在。請修正出生時間。",
        "invalid_timezone": "城市提供的時區無效，請選擇其他搜尋結果。",
        "chart": "北印度式 D1 星盤",
        "positions": "行星位置",
        "body": "天體",
        "sign": "星座",
        "degree": "星座內度數",
        "nakshatra": "宿（Nakshatra）",
        "pada": "Pada",
        "house": "宮位",
        "motion": "狀態",
        "direct": "順行",
        "retrograde": "逆行",
        "settings": "計算設定",
        "privacy": "隱私",
        "privacy_text": "本網站不使用資料庫，不會主動儲存你輸入的出生資料。Streamlit 與網路基礎設施仍可能產生一般技術日誌。",
        "sources": "資料來源",
        "sources_text": "城市資料：Open-Meteo Geocoding API（基於 GeoNames）。天文計算：Swiss Ephemeris / pyswisseph。歷史時區：Python zoneinfo 與 tzdata。",
        "disclaimer": "聲明",
        "disclaimer_text": "本網站內容僅供教育、文化與娛樂用途，不構成醫療、心理、法律、稅務、投資或其他專業建議。重大決策請諮詢合格專業人士。",
        "license": "本專案採 AGPL-3.0 授權。",
        "request_error": "無法完成計算：",
    },
    "en": {
        "page_title": "Vedic Natal Chart",
        "title": "Vedic Natal Chart (D1)",
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
        "calculate": "Calculate chart",
        "enter_city": "Search for and select a birth city first.",
        "api_error": "City search is temporarily unavailable. Please try again.",
        "no_results": "No cities found. Try an English/romanized spelling or a larger nearby city.",
        "ambiguous": "This local time occurred twice when daylight saving time ended. Select the correct UTC offset.",
        "choose_offset": "Select the UTC offset in effect",
        "nonexistent": "This local time did not exist because daylight saving time began. Correct the birth time.",
        "invalid_timezone": "The selected result has an invalid timezone. Choose another result.",
        "chart": "North Indian D1 chart",
        "positions": "Planetary positions",
        "body": "Body",
        "sign": "Sign",
        "degree": "Degree in sign",
        "nakshatra": "Nakshatra",
        "pada": "Pada",
        "house": "House",
        "motion": "Motion",
        "direct": "Direct",
        "retrograde": "Retrograde",
        "settings": "Calculation settings",
        "privacy": "Privacy",
        "privacy_text": "This app uses no database and does not intentionally store birth data you enter. Streamlit and network infrastructure may still produce ordinary technical logs.",
        "sources": "Data sources",
        "sources_text": "Cities: Open-Meteo Geocoding API (based on GeoNames). Astronomy: Swiss Ephemeris / pyswisseph. Historical timezones: Python zoneinfo and tzdata.",
        "disclaimer": "Disclaimer",
        "disclaimer_text": "For educational, cultural, and entertainment purposes only. This is not medical, psychological, legal, tax, investment, or other professional advice. Consult qualified professionals for important decisions.",
        "license": "Licensed under AGPL-3.0.",
        "request_error": "Unable to calculate chart: ",
    },
}

SIGN_ZH = {
    "Aries": "牡羊座", "Taurus": "金牛座", "Gemini": "雙子座", "Cancer": "巨蟹座",
    "Leo": "獅子座", "Virgo": "處女座", "Libra": "天秤座", "Scorpio": "天蠍座",
    "Sagittarius": "射手座", "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "雙魚座",
}
BODY_ZH = {
    "Ascendant": "上升", "Sun": "太陽", "Moon": "月亮", "Mars": "火星",
    "Mercury": "水星", "Jupiter": "木星", "Venus": "金星", "Saturn": "土星",
    "Rahu": "羅喉", "Ketu": "計都",
}
BODY_ABBR_ZH = {
    "Ascendant": "升", "Sun": "日", "Moon": "月", "Mars": "火", "Mercury": "水",
    "Jupiter": "木", "Venus": "金", "Saturn": "土", "Rahu": "羅", "Ketu": "計",
}

st.set_page_config(page_title="Vedic Natal Chart", page_icon="✨", layout="wide")


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
    results = []
    for item in data.get("results", []):
        if not item.get("timezone"):
            continue
        results.append({
            "id": item.get("id"),
            "name": item.get("name", ""),
            "country": item.get("country", ""),
            "country_code": item.get("country_code", ""),
            "admin1": item.get("admin1", ""),
            "latitude": float(item["latitude"]),
            "longitude": float(item["longitude"]),
            "timezone": item["timezone"],
        })
    return results


def city_label(city: dict[str, Any]) -> str:
    country = city.get("country", "")
    country_code = city.get("country_code", "")
    if country_code:
        country = f"{country} ({country_code})" if country else country_code

    parts: list[str] = []
    for part in (city.get("name", ""), city.get("admin1", ""), country):
        if part and part not in parts:
            parts.append(part)

    place = ", ".join(parts)
    return f"{place} — {city['latitude']:.4f}, {city['longitude']:.4f} — {city['timezone']}"


def parse_manual_time(value: str) -> time | None:
    """Parse a user-entered 24-hour time in H:MM or HH:MM form."""
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


language = st.sidebar.selectbox("Language / 語言", ["zh-TW", "en"], index=0)
t = TEXT[language]
st.title(t["title"])

with st.sidebar:
    st.markdown(f"### {t['settings']}")
    st.write("Sidereal · Lahiri")
    st.write("True Node · Whole Sign")
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

selected_city = None
if results:
    index = st.selectbox(
        t["select_city"],
        options=range(len(results)),
        format_func=lambda i: city_label(results[i]),
        key="selected_city_index",
    )
    selected_city = results[index]
    c1, c2 = st.columns(2)
    c1.metric(t["timezone"], selected_city["timezone"])
    c2.metric(t["coordinates"], f"{selected_city['latitude']:.4f}, {selected_city['longitude']:.4f}")
elif is_current_search and not search_context.get("failed"):
    st.info(t["no_results"])

utc_choice = None
time_resolution = None
if selected_city and birth_time_value is not None:
    local_naive = datetime.combine(birth_date, birth_time_value)
    time_resolution = resolve_local_time(local_naive, selected_city["timezone"])
    if time_resolution.status == "ambiguous":
        st.warning(t["ambiguous"])
        choice_index = st.radio(
            t["choose_offset"],
            options=range(len(time_resolution.choices_utc)),
            format_func=lambda i: f"{time_resolution.offsets[i]} → {time_resolution.choices_utc[i].strftime('%Y-%m-%d %H:%M UTC')}",
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
        st.session_state["chart"] = calculate_chart(
            utc_choice,
            selected_city["latitude"],
            selected_city["longitude"],
        )
        st.session_state["chart_city"] = selected_city
    except Exception as exc:
        st.error(f"{t['request_error']}{exc}")

if not selected_city:
    st.caption(t["enter_city"])

chart = st.session_state.get("chart")
if chart:
    st.divider()
    st.subheader(t["chart"])
    svg = render_north_indian_svg(
        chart,
        sign_labels=SIGN_ZH if language == "zh-TW" else {},
        planet_labels=BODY_ABBR_ZH if language == "zh-TW" else {},
    )
    components.html(f'<div style="max-width:720px;margin:auto;color:inherit">{svg}</div>', height=730, scrolling=False)

    st.subheader(t["positions"])
    rows = []
    for item in chart["positions"]:
        body = BODY_ZH.get(item["code"], item["code"]) if language == "zh-TW" else item["code"]
        sign = SIGN_ZH.get(item["sign"], item["sign"]) if language == "zh-TW" else item["sign"]
        rows.append({
            t["body"]: body,
            t["sign"]: sign,
            t["degree"]: format_degree(item["degree_in_sign"]),
            t["nakshatra"]: item["nakshatra"],
            t["pada"]: item["pada"],
            t["house"]: item["house"],
            t["motion"]: t["retrograde"] if item["retrograde"] else t["direct"],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(f"UTC: {chart['utc_datetime']} · JD(UT): {chart['julian_day_ut']:.6f}")

st.divider()
with st.expander(t["sources"], expanded=False):
    st.write(t["sources_text"])
with st.expander(t["privacy"], expanded=False):
    st.write(t["privacy_text"])
with st.expander(t["disclaimer"], expanded=True):
    st.write(t["disclaimer_text"])
