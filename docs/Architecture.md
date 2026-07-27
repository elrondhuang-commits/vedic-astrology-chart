# Architecture

Version 0.2.1 keeps the compatibility-first modular core and adds a centralized Varga Registry.

- `app.py`: Streamlit UI and translations.
- `core/`: deterministic calculation logic only.
- `charts/`: chart renderers.
- `tests/`: regression and boundary tests.
- `docs/`: architecture, algorithms, validation, and roadmap.
- `astrology.py` and `north_indian_chart.py`: compatibility wrappers. They may be removed only in a future major version.

The refactor deliberately keeps UI behavior unchanged. Future vargas should be added in `core/varga.py`, and future dasha systems in their own core modules, without coupling them to Streamlit.


## Varga Registry

`core/varga_registry.py` is the UI-facing source of truth for each supported divisional chart. Every entry contains a stable English code, division number, Sanskrit name, bilingual label, bilingual description, and reference note. `app.py` and `core/chart.py` consume this registry, preventing duplicated chart lists and missing translation keys. Numerical mapping rules remain in `core/varga.py`.
