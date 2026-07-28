# 吠陀星盤 — Streamlit

**Version 0.4.0 — Complete Shodashavarga**

一個以透明、正確、可驗證及遵循古典 Jyotisha 為核心的開源吠陀占星平台。此版本完成經典 Shodashavarga 16 分盤，新增 D27、D30、D40、D45、D60，並加入高階分盤出生時間精度警告與完整邊界測試。

> 現有 GitHub 專案升級時，請上傳所有檔案與 `core/`、`charts/`、`tests/`、`docs/` 四個資料夾，並維持其資料夾結構。

A simple, database-free Vedic astrology website designed for direct deployment to Streamlit Community Cloud. The interface supports Traditional Chinese (`zh-TW`) and English (`en`).

## Features

- Python + Streamlit only
- Global city search through the free Open-Meteo Geocoding API
- City name, country/region, administrative area, latitude, longitude, and IANA timezone
- Common Taiwan Chinese place-name aliases such as 台北、台中、台南、高雄
- Taiwan results are displayed as `台灣` / `Taiwan`, without a redundant `台灣省` / `Taiwan Province` label
- Historical timezone conversion with `zoneinfo` and `tzdata`
- Explicit detection of ambiguous and nonexistent local times
- Swiss Ephemeris calculations through `pyswisseph`
- Sidereal Lahiri ayanamsha
- True Node Rahu; Ketu is exactly 180° opposite Rahu in D1
- Whole Sign houses
- Ascendant, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu
- Degree within sign, 27 Nakshatras, and 4 Padas
- North Indian SVG charts with the first house fixed at the upper centre
- D1 Rashi natal chart
- Moon chart (Chandra Lagna)
- D2 Hora divisional chart
- D3 Drekkana divisional chart
- D4 Chaturthamsha divisional chart
- D7 Saptamsha divisional chart
- D9 Navamsha divisional chart
- D10 Dashamsha divisional chart
- D12 Dwadashamsha divisional chart
- D16 Shodashamsha divisional chart
- D20 Vimshamsha divisional chart
- D24 Chaturvimshamsha divisional chart
- D27 Saptavimshamsha divisional chart
- D30 Trimshamsha divisional chart
- D40 Khavedamsha divisional chart
- D45 Akshavedamsha divisional chart
- D60 Shashtiamsha divisional chart
- Vimshottari Mahadasha and Antardasha timelines
- Birth Mahadasha balance and current Maha/Antardasha marker
- No database, no AI API, and no intentional storage of birth data

## Files

- `app.py` — Streamlit interface, localization, city search, and tables
- `core/` — deterministic chart, varga, dasha, timezone, ephemeris, and metadata modules
- `core/varga_registry.py` — stable varga codes plus bilingual names, descriptions, order, and references
- `charts/` — reusable chart renderers
- `tests/` — boundary and regression tests
- `docs/` — architecture, algorithms, validation, and roadmap
- `astrology.py` / `north_indian_chart.py` — backward-compatible import wrappers
- `requirements.txt` — Python dependencies
- `LICENSE` — GNU Affero General Public License v3.0

## Run locally

Python **3.11** is recommended because the pinned `pyswisseph` release has reliable Linux wheels for that version.

```bash
python -m venv .venv
```

Activate the virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload all root files plus the `core/`, `charts/`, `tests/`, and `docs/` folders while preserving their structure.
3. Sign in to Streamlit Community Cloud.
4. Create a new app and select the repository.
5. Set the main file path to `app.py`.
6. In the app settings, select Python `3.11`.
7. Deploy. No secrets or API keys are required.

## Timezone handling

The input local datetime is interpreted using the selected city's IANA timezone. The app validates both PEP 495 folds by converting through UTC:

- **Ambiguous time:** both folds round-trip correctly and map to distinct UTC instants. The user selects the applicable UTC offset.
- **Nonexistent time:** neither fold round-trips to the entered local time. The user must correct the time.

## Astronomical settings

Swiss Ephemeris is configured with:

- `SIDM_LAHIRI`
- `FLG_SIDEREAL`
- `FLG_SPEED`
- True lunar node (`TRUE_NODE`)
- Whole Sign houses

Planetary positions are calculated in UT. The sidereal Ascendant comes from the Swiss Ephemeris house calculation. Ketu is generated as Rahu + 180°.

## Divisional-chart rules

The app currently implements these standard Parashari mappings:

### D2 Hora

Each sign is divided into two 15° halves. Odd signs map the first half to Leo and the second half to Cancer; even signs reverse that order.

### D3 Drekkana

Each sign is divided into three 10° parts, mapped to the natal sign, fifth sign, and ninth sign.

### D4 Chaturthamsha

Each sign is divided into four 7°30′ parts, mapped to the natal sign, fourth sign, seventh sign, and tenth sign.

### D7 Saptamsha

Each sign is divided into seven equal parts. Odd signs begin from the natal sign; even signs begin from the seventh sign.

### D9 Navamsha

Every sign is divided into nine parts of 3°20′.

- Movable signs begin from the same sign.
- Fixed signs begin from the ninth sign.
- Dual signs begin from the fifth sign.

### D10 Dashamsha

Every sign is divided into ten parts of 3°.

- Odd-numbered signs begin from the same sign.
- Even-numbered signs begin from the ninth sign.

### D12 Dwadashamsha

Each sign is divided into twelve 2°30′ parts, proceeding zodiacally from the natal sign.

### D16 Shodashamsha

Each sign is divided into sixteen parts of 1°52′30″. Movable signs begin from Aries, fixed signs from Leo, and dual signs from Sagittarius. Subsequent parts advance zodiacally.

### D20 Vimshamsha

Each sign is divided into twenty parts of 1°30′. Movable signs begin from Aries, fixed signs from Sagittarius, and dual signs from Leo. Subsequent parts advance zodiacally.

### D24 Chaturvimshamsha

Each sign is divided into twenty-four parts of 1°15′. Under the mainstream Parashari/Santhanam convention used here, odd signs begin from Leo and even signs from Cancer; subsequent parts advance zodiacally. Some modern schools use a reversed sequence for even signs, so the convention is stated explicitly.

The divisional Ascendant and all body placements are mapped from their D1 sidereal longitudes. Houses in each divisional chart are Whole Sign houses counted from that divisional Ascendant.

## Vimshottari dasha rules

The Mahadasha sequence is:

```text
Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury
```

The corresponding durations are:

```text
7, 20, 6, 10, 7, 18, 16, 19, 17 years
```

The birth Moon's Nakshatra ruler determines the Mahadasha operating at birth. The elapsed fraction of the Moon's Nakshatra determines the elapsed fraction of that Mahadasha. Antardasha duration is calculated as:

```text
Mahadasha years × Antardasha-lord years ÷ 120
```

### Dasha-year convention

The classical durations are stated in years, but modern software does not use one universal civil-day conversion. This project uses a **mean Gregorian year of 365.2425 days** and displays that convention in the app. Programs using a mean sidereal year, 365.25 days, or a 360-day year can show different boundary dates.

All displayed dasha dates are converted from UTC to the selected birth-place IANA timezone. Period starts are inclusive and period ends are exclusive.

## Data and privacy

City search requests are sent to Open-Meteo. The application itself has no database and does not intentionally persist birth data. Streamlit, hosting providers, and network infrastructure may retain ordinary access or error logs.

## Disclaimer

This project is for educational, cultural, and entertainment purposes only. It does not provide medical, psychological, legal, tax, financial, investment, or other professional advice. Divisional charts and dasha periods should not be used as the sole basis for important decisions.

## Attribution and licensing

- City data: Open-Meteo Geocoding API, based on GeoNames data.
- Astronomy: Swiss Ephemeris via `pyswisseph`.
- Project source code: GNU AGPL-3.0. See `LICENSE`.

Swiss Ephemeris is dual-licensed. This AGPL project is intended to follow the open-source licensing path; review Astrodienst's current licensing terms before changing the distribution model or using a proprietary deployment.

## v5 dasha interface

- Current Mahadasha and Antardasha summary cards
- Remaining time and period progress
- Mahadasha timeline
- Full Mahadasha year lengths retained
- Decimal Antardasha years plus readable approximate duration


## v7.1 interface refinements

- Removed Streamlit heading anchor icons.
- Unified section-title spacing and typography.
- Improved tab behavior and page padding on mobile screens.
- Refined chart spacing and table column widths.

## v8 divisional charts

- Added D4 Chaturthamsha.
- Added D7 Saptamsha.
- Added D12 Dwadashamsha.
- Expanded the divisional-chart selector and calculation notes.

## 0.3.0 changes

- Added D16 Shodashamsha, D20 Vimshamsha, and D24 Chaturvimshamsha.
- Extended the Varga Registry and Streamlit selector automatically through stable chart codes.
- Added exact segment-boundary tests for 1°52′30″, 1°30′, and 1°15′ divisions.
- Added `CHANGELOG.md` and updated architecture, algorithm, roadmap, and validation documents.
- Kept the existing D1, Moon chart, Vimshottari, Taiwan city search, privacy behavior, and deployment requirements unchanged.

### D27 Saptavimshamsha

Each sign is divided into 27 equal parts. Fire, earth, air, and water signs start from Aries, Cancer, Libra, and Capricorn respectively.

### D30 Trimshamsha

The classical unequal Parashari five-span mapping is used. Odd and even signs follow their respective Mars/Saturn/Jupiter/Mercury/Venus sequences and target signs.

### D40 Khavedamsha

Each sign is divided into 40 equal 45′ parts. Odd signs begin from Aries and even signs from Libra.

### D45 Akshavedamsha

Each sign is divided into 45 equal 40′ parts. Movable, fixed, and dual signs begin from Aries, Leo, and Sagittarius respectively.

### D60 Shashtiamsha

Each sign is divided into 60 equal 0°30′ parts. The app displays the D60 signs and houses and warns that a small birth-time error can alter the D60 Ascendant. The sixty deity names are not yet displayed.

## 0.4.0 changes

- Completed the classical Shodashavarga set with D27, D30, D40, D45, and D60.
- Added localized birth-time precision warnings for D40, D45, and D60.
- Expanded boundary and full-chart regression tests.
