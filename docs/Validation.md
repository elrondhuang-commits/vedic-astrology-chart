# Validation

## Automated checks

The test suite covers:

- Python import and schema-version stability
- Rahu/Ketu opposition
- Moon chart first-house rotation
- Vimshottari continuity
- Ambiguous and nonexistent local times
- Varga Registry bilingual completeness
- D2, D3, D4, D12, D16, D20, and D24 boundary behavior
- Full D16/D20/D24 chart generation with ten positions and an Ascendant in house 1

Run locally with:

```bash
python -m unittest discover -s tests -v
```

## External validation status

The project calculation conventions are documented, but a formal published comparison matrix against Jagannatha Hora, Parashara's Light, Kala, and AstroSage is still planned. Results should not yet be described as externally certified.

## Higher-varga caution

D16, D20, and D24 Ascendants can change with relatively small birth-time differences. Later releases will add stronger warnings for D27 through D60.
