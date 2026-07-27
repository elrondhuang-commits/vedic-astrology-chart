# Release notes — 0.3.0

## New charts

- D16 Shodashamsha
- D20 Vimshamsha
- D24 Chaturvimshamsha

## Calculation conventions

- D16: movable signs begin at Aries, fixed signs at Leo, dual signs at Sagittarius.
- D20: movable signs begin at Aries, fixed signs at Sagittarius, dual signs at Leo.
- D24: odd signs begin at Leo and even signs at Cancer; divisions proceed zodiacally.

## Files changed

- `app.py`
- `core/constants.py`
- `core/varga.py`
- `core/varga_registry.py`
- `tests/test_core.py`
- `tests/test_varga.py`
- `tests/test_varga_registry.py`
- `tests/test_release_030.py`
- `README.md`
- `CHANGELOG.md`
- `docs/Algorithms.md`
- `docs/Roadmap.md`
- `docs/Validation.md`
- `VERSION`

## Validation

`python -m unittest discover -s tests -v` passes 22 tests.
