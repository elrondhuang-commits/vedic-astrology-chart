
我應該是上傳了嗎?


今天 上午9:39

處理時間為 4m 7s
你已經成功部署到 Streamlit，現在遇到的是 Python 版本與 pyswisseph 的相容性問題，不是檔案上傳錯誤。

錯誤發生在：

import swisseph as swe
這一行本身是正確的。安裝套件名稱是 pyswisseph，但 Python 匯入名稱就是 swisseph，不要把它改成 import pyswisseph。官方 PyPI 範例也是使用 import swisseph as swe。

我也檢查了你目前的 GitHub Repository，你的 requirements.txt 已正確包含：

pyswisseph==2.10.3.2
所以不需要修改程式碼或 requirements.txt。

問題原因
pyswisseph==2.10.3.2 在 PyPI 提供的 Linux 預先編譯版本只到：

Python 3.10
Python 3.11
沒有 Python 3.12、3.13 或 3.14 的正式 wheel。你很可能在部署時使用了較新的 Python，因此 swisseph 這個二進位模組無法正常載入。

請這樣修正
第一步：刪除目前的 Streamlit App
在目前錯誤頁面的右下角點：

Manage app
然後進入：

Settings
找到：

Delete app
並確認刪除。

不要只按 Reboot。 Streamlit 官方文件說明，部署完成後無法直接更改 Python 版本；要更換 Python，必須刪除後重新部署。

刪除 Streamlit App 不會刪除你的 GitHub 程式碼。

第二步：重新建立 App
回到 Streamlit Community Cloud 工作區，點：

Create app
填入：

Repository:
elrondhuang-commits/vedic-astrology-chart

Branch:
main

Main file path:
app.py
第三步：設定 Python 3.11
在按 Deploy 之前，點：

Advanced settings
找到 Python version，務必選：

Python 3.11
請不要選：

Python 3.12
Python 3.13
Python 3.14
其他設定不需要填：

不需要 Secrets

不需要 API Key

不需要資料庫

不需要新增 packages.txt

最後按：

Deploy
正確設定總覽
Repository:     elrondhuang-commits/vedic-astrology-chart
Branch:         main
Main file path: app.py
Python version: 3.11
重新部署通常需要幾分鐘。若使用 Python 3.11 後仍然出現錯誤，請開啟：

Manage app → Logs
把日誌最後從 ImportError: 開始的約 15～20 行貼上；公開錯誤頁會隱藏真正的錯誤訊息，但 Logs 會顯示完整內容。Streamlit 官方也建議透過 Manage app 的日誌診斷部署錯誤。


我找不到Delete app，但我有看到Python版本選擇。

處理時間為 2m 9s
對，你已經找到最關鍵的地方了。畫面顯示目前使用的是 Python 3.14，這正是 swisseph 匯入失敗的主要原因；你專案固定使用的 pyswisseph==2.10.3.2，PyPI 提供的 Linux 預編譯版本最高到 Python 3.11，沒有 Python 3.14 的版本。

請先直接嘗試修改
點擊 Python version 右側的向下箭頭。

選擇：

3.11
選完後，看看右下角的：

Save changes
是否變成可以點擊。

點 Save changes。

關閉視窗，等待約幾分鐘，讓 Streamlit 重新建置。

若這樣可以儲存，就不必刪除 App。重新建置期間可能會看到：

Your app is in the oven
或暫時載入中的畫面，這是正常的。

若不能儲存 Python 3.11
Streamlit 官方文件目前仍寫明：已部署的 App 若要改 Python 版本，通常需要刪除後重新部署。

你找不到 Delete app，是因為它不在目前這個「App settings」視窗裡。請這樣找：

點右上角的 ×，關閉目前視窗。

回到 Manage app 的日誌畫面。

找日誌面板底部的三點選單：

⋮
點開後選：

Delete app
另一種方式是在 Streamlit 工作區的 App 卡片右側點三點選單，再選 Delete。官方文件確認這兩個位置都可以刪除部署。

刪除只會移除 Streamlit 上的部署，不會刪掉 GitHub 裡的程式碼。

重新部署時填：

Repository:
elrondhuang-commits/vedic-astrology-chart

Branch:
main

Main file path:
app.py

Python version:
3.11
目前先做第一件事：點開 Python version，選擇 3.11，再查看 Save changes 是否可以按。


水喔 可以使用了
但有個小問題 時間選擇如果可以將小時和分鐘分開就更好了，目前是要一路往下拖拉N多個選項，每一分鐘一個選項，太多啦。
還有如果時間同時間可以多一個自行輸入的選項就更好。
還有地點，例如我打台南會跑出大陸那邊的地名，要打tainan才會是台灣。
最好有個提醒可以寫在上面，提醒輸入英文地名之類的。

處理時間為 7m 20s
太好了，星盤已經正常運作了。你提到的三個操作問題，我已經一起修改完成。

這次修改的內容
1. 出生時間改成「小時、分鐘分開」
現在不需要再從一千多個時間選項一路往下滑。

預設會顯示：

小時：0～23
分鐘：0～59
兩個欄位都可以：

使用加減按鈕

點進欄位直接輸入數字

小時與分鐘分開調整

2. 增加「自行輸入時間」
出生時間上方會有兩種方式：

○ 分開選擇小時與分鐘
○ 自行輸入
選擇「自行輸入」後，可以輸入：

08:05
8:05
23:40
也支援中文輸入法可能產生的全形格式：

２３：４０
超過 23:59 或格式不正確時，系統會直接提醒，不會拿錯誤時間進行計算。

3. 改善台灣中文地名搜尋
現在輸入以下常見中文地名時，會自動轉成英文地名，並限定搜尋台灣：

台南
臺南市
台南 台灣
系統會自動改成：

Tainan
Country code: TW
因此比較不容易再跑出中國大陸的同名地點。

目前也包含台北、新北、桃園、台中、台南、高雄、基隆、新竹、嘉義、宜蘭、花蓮、台東、屏東等常見台灣地名。較小的鄉鎮或全球其他城市，仍建議使用英文或羅馬拼音。Open-Meteo 官方 API 支援以 countryCode 過濾指定國家／地區的搜尋結果，因此台灣中文城市轉換後會使用 TW 限定結果。

4. 加入醒目的地點搜尋提醒
出生城市欄位上方會顯示：

城市搜尋建議使用英文或羅馬拼音，例如 Tainan、Taipei。系統會自動辨識部分常見的台灣中文縣市名稱；無論使用哪種語言，都請核對國家／地區、行政區、座標與 IANA 時區。

搜尋結果也會顯示國家代碼，例如：

台南, 臺南市, 台灣 (TW)
22.9999, 120.2270
Asia/Taipei
這樣能更清楚分辨 TW、CN 或其他國家的同名城市。

下載更新檔案
你目前只需要更換 GitHub 裡的 app.py：

app.py

完整六個檔案的更新版也已整理好：

下載完整更新版專案 ZIP

我已完成 Python 語法檢查，以及中文台南轉換、手動時間格式與錯誤時間驗證測試。

更新 GitHub 的步驟
第一步：確認下載檔名
下載後，檔案名稱必須是：

app.py
假如 Windows 或瀏覽器把它命名成：

app (1).py
請先重新命名為：

app.py
第二步：回到 GitHub Repository 首頁
進入你目前的：

elrondhuang-commits/vedic-astrology-chart
確認目前是在檔案列表，也就是能看到：

app.py
astrology.py
north_indian_chart.py
requirements.txt
README.md
LICENSE
第三步：上傳新版 app.py
點選：

新增文件 ▼
再選：

上傳文件
把剛下載的新版：

app.py
拖進上傳區。

GitHub 會將原本的 app.py 更新為新版，不需要刪除其他檔案。

第四步：提交變更
頁面往下捲，提交訊息可以填：

Improve time and city inputs
然後按：

提交變更
只需要上傳 app.py。不需要修改：

requirements.txt
astrology.py
north_indian_chart.py
Python 3.11 設定
Streamlit Secrets
提交到 GitHub 後，Streamlit Community Cloud 會監看 Repository 的變更，Python 程式檔更新通常會自動反映到已部署的網站。

更新完成後，重新整理網站，直接測試：

時間：08:05
城市：台南
城市結果應顯示 TW 和 Asia/Taipei。


app.py


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
app.py


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
