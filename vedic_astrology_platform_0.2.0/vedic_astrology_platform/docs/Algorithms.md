# Algorithms

## D1

Swiss Ephemeris, sidereal Lahiri ayanamsha, True Node, and Whole Sign houses.
Ketu is derived as Rahu + 180 degrees.

## Reference chart

The Moon chart rotates Whole Sign house 1 to the Moon's D1 sign. Longitudes are unchanged.

## Supported vargas

D2, D3, D4, D7, D9, D10, and D12. Each transformation is isolated in `core/varga.py` and covered by boundary tests.

## Vimshottari

The Moon's nakshatra selects the starting lord. The elapsed nakshatra fraction determines the elapsed starting Mahadasha. Antardasha duration is `Mahadasha years × Antardasha-lord years / 120`. Civil dates use a mean Gregorian year of 365.2425 days.
