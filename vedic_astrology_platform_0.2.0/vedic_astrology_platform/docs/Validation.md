# Validation

Run locally from the repository root:

```bash
python -m unittest discover -s tests -v
```

Current automated checks cover:

- required chart set and output schema;
- Rahu/Ketu exact opposition;
- Moon as house 1 in the Moon chart;
- contiguous Vimshottari Mahadashas;
- ambiguous and nonexistent civil times;
- D2, D3, D4, and D12 boundary behavior.

External cross-validation against professional Jyotisha software is planned and must record software version, settings, ephemeris, ayanamsha, node mode, house system, and test input.
