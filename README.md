# Vedic Natal Chart — Streamlit

A simple, database-free Vedic natal chart website designed for direct deployment to Streamlit Community Cloud.

## Features

- Python + Streamlit only
- Global city search through the free Open-Meteo Geocoding API
- City name, country, administrative area, latitude, longitude, and IANA timezone
- Historical timezone conversion with `zoneinfo` and `tzdata`
- Explicit detection of ambiguous and nonexistent local times
- Swiss Ephemeris calculations through `pyswisseph`
- Sidereal Lahiri ayanamsha
- True Node Rahu; Ketu is exactly 180° opposite Rahu
- Whole Sign houses
- Ascendant, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu
- Degree within sign, 27 Nakshatras, and 4 Padas
- North Indian D1 SVG chart with the first house fixed at the upper centre
- Traditional Chinese (`zh-TW`) and English (`en`)
- No database, no AI API, and no intentional storage of birth data

## Files

- `app.py` — Streamlit interface, localization, and Open-Meteo city search
- `astrology.py` — timezone validation and astrology calculations
- `north_indian_chart.py` — North Indian SVG rendering
- `requirements.txt` — Python dependencies
- `LICENSE` — GNU Affero General Public License v3.0

## Run locally

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
```

Activate the virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload all six project files to the repository root.
3. Sign in to Streamlit Community Cloud.
4. Create a new app and select the repository.
5. Set the entrypoint to `app.py`.
6. Deploy. No secrets or API keys are required.

## Calculation notes

The input local datetime is interpreted using the selected city's IANA timezone. The app validates both PEP 495 folds by converting through UTC:

- **Ambiguous time:** both folds round-trip correctly and map to distinct UTC instants. The user selects the applicable UTC offset.
- **Nonexistent time:** neither fold round-trips to the entered local time. The user must correct the time.

Swiss Ephemeris is configured with `SIDM_LAHIRI` and `FLG_SIDEREAL`. Planetary positions use UT. The Ascendant is returned from sidereal house calculation, while house assignment follows Whole Sign houses from the Ascendant sign.

## Data and privacy

City search requests are sent to Open-Meteo. The application itself has no database and does not intentionally persist birth data. Hosting providers and network infrastructure may retain ordinary access or error logs.

## Disclaimer

This project is for educational, cultural, and entertainment purposes only. It does not provide medical, psychological, legal, tax, financial, investment, or other professional advice.

## Attribution and licensing

- City data: Open-Meteo Geocoding API, based on GeoNames data.
- Astronomy: Swiss Ephemeris via `pyswisseph`. Review Swiss Ephemeris licensing obligations before public or commercial distribution.
- Project source code: GNU AGPL-3.0. See `LICENSE`.
