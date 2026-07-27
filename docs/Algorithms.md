# Algorithms

## D1

Swiss Ephemeris with sidereal Lahiri ayanamsha, True Node, and Whole Sign houses. Ketu is derived as Rahu + 180 degrees.

## Reference chart

The Moon chart makes the Moon's D1 sign house 1. Planetary longitudes are unchanged.

## Supported vargas

`D2`, `D3`, `D4`, `D7`, `D9`, `D10`, `D12`, `D16`, `D20`, and `D24` are implemented in `core/varga.py`. Metadata and bilingual descriptions are registered separately in `core/varga_registry.py`.

### D16 Shodashamsha

A sign is divided into sixteen equal 1°52′30″ parts. Movable signs start from Aries, fixed signs from Leo, and dual signs from Sagittarius. Parts advance zodiacally.

### D20 Vimshamsha

A sign is divided into twenty equal 1°30′ parts. Movable signs start from Aries, fixed signs from Sagittarius, and dual signs from Leo. Parts advance zodiacally.

### D24 Chaturvimshamsha

A sign is divided into twenty-four equal 1°15′ parts. This project uses the mainstream Parashari/Santhanam convention: odd signs start from Leo and even signs from Cancer, with zodiacal progression. The convention is documented because alternative reverse-even mappings exist in some modern schools.

## Divisional longitude

Each equal segment is mapped to a target sign. The fractional position inside the source segment is multiplied by the division factor to produce the degree inside the mapped varga sign.

## Vimshottari

The Moon's nakshatra selects the starting lord. The elapsed nakshatra fraction determines the elapsed starting Mahadasha. Antardasha duration is `Mahadasha years × Antardasha-lord years / 120`. Civil dates use a mean Gregorian year of 365.2425 days.
