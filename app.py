from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components

from astrology import calculate_chart, resolve_local_time
from north_indian_chart import render_north_indian_svg

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

TEXT = {
    "zh-TW": {
        "page_title": "吠陀占星本命盤",
        "title": "吠陀占星本命盤（D1）",
        "language": "語言",
        "birth_date": "出生日期",
        "birth_time": "出生時間",
        "city_search": "出生城市",
        "city_help": "輸入至少 2 個字元，再從搜尋結果選擇正確城市。",
        "search": "搜尋城市",
        "select_city": "選擇城市",
        "timezone": "IANA 時區",
        "coordinates": "座標",
        "calculate": "計算本命盤",
        "enter_city": "請先搜尋並選擇出生城市。",
        "api_error": "城市搜尋暫時失敗，請稍後重試。",
        "no_results": "找不到城市，請嘗試加入國家名稱或改用其他拼法。",
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
        "city_search": "Birth city",
        "city_help": "Enter at least 2 characters, then select the correct result.",
        "search": "Search cities",
        "select_city": "Select city",
        "timezone": "IANA timezone",
        "coordinates": "Coordinates",
        "calculate": "Calculate chart",
        "enter_city": "Search for and select a birth city first.",
        "api_error": "City search is temporarily unavailable. Please try again.",
        "no_results": "No cities found. Try adding the country or another spelling.",
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


@st.cache_data(ttl=3600, show_spinner=False)
def search_cities(query: str, language: str) -> list[dict[str, Any]]:
    params = {
        "name": query.strip(),
        "count": 10,
        "language": "zh" if language == "zh-TW" else "en",
        "format": "json",
    }
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
            "admin1": item.get("admin1", ""),
            "latitude": float(item["latitude"]),
            "longitude": float(item["longitude"]),
            "timezone": item["timezone"],
        })
    return results


def city_label(city: dict[str, Any]) -> str:
    parts = [city["name"], city.get("admin1", ""), city.get("country", "")]
    place = ", ".join(part for part in parts if part)
    return f"{place} — {city['latitude']:.4f}, {city['longitude']:.4f} — {city['timezone']}"


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

left, right = st.columns([1, 1])
with left:
    birth_date = st.date_input(t["birth_date"], value=date(1990, 1, 1), min_value=date(1800, 1, 1), max_value=date.today())
with right:
    birth_time = st.time_input(t["birth_time"], value=time(12, 0), step=60)

query = st.text_input(t["city_search"], help=t["city_help"], placeholder="Taipei / 台北")
if st.button(t["search"], type="secondary", disabled=len(query.strip()) < 2):
    try:
        st.session_state["city_results"] = search_cities(query, language)
    except (requests.RequestException, ValueError):
        st.session_state["city_results"] = []
        st.error(t["api_error"])

results = st.session_state.get("city_results", [])
selected_city = None
if results:
    index = st.selectbox(
        t["select_city"],
        options=range(len(results)),
        format_func=lambda i: city_label(results[i]),
    )
    selected_city = results[index]
    c1, c2 = st.columns(2)
    c1.metric(t["timezone"], selected_city["timezone"])
    c2.metric(t["coordinates"], f"{selected_city['latitude']:.4f}, {selected_city['longitude']:.4f}")
elif query.strip() and "city_results" in st.session_state:
    st.info(t["no_results"])

utc_choice = None
time_resolution = None
if selected_city:
    local_naive = datetime.combine(birth_date, birth_time)
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
