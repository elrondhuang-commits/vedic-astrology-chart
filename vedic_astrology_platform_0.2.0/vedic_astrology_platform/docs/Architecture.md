# Architecture

Version 0.2.0 introduces a compatibility-first modular core.

- `app.py`: Streamlit UI and translations.
- `core/`: deterministic calculation logic only.
- `charts/`: chart renderers.
- `tests/`: regression and boundary tests.
- `docs/`: architecture, algorithms, validation, and roadmap.
- `astrology.py` and `north_indian_chart.py`: compatibility wrappers. They may be removed only in a future major version.

The refactor deliberately keeps UI behavior unchanged. Future vargas should be added in `core/varga.py`, and future dasha systems in their own core modules, without coupling them to Streamlit.
