# Vedic Natal Chart — Streamlit

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
- D9 Navamsha divisional chart
- D10 Dashamsha divisional chart
- Vimshottari Mahadasha and Antardasha timelines
- Birth Mahadasha balance and current Maha/Antardasha marker
- No database, no AI API, and no intentional storage of birth data

## Files

- `app.py` — Streamlit interface, localization, city search, and tables
- `astrology.py` — timezone validation, D1/D9/D10 calculations, and Vimshottari dasha
- `north_indian_chart.py` — reusable North Indian SVG rendering
- `requirements.txt` — Python dependencies
- `README.md` — setup and calculation documentation
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
2. Upload all six project files to the repository root.
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

The app currently implements the standard Parashari rules for D9 and D10:

### D9 Navamsha

Every sign is divided into nine parts of 3°20′.

- Movable signs begin from the same sign.
- Fixed signs begin from the ninth sign.
- Dual signs begin from the fifth sign.

### D10 Dashamsha

Every sign is divided into ten parts of 3°.

- Odd-numbered signs begin from the same sign.
- Even-numbered signs begin from the ninth sign.

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
