# Validation

## Automated coverage

The test suite covers:

- D1 chart generation and Rahu/Ketu opposition
- Moon-chart first-house behavior
- ambiguous and nonexistent historical local times
- contiguous Vimshottari Mahadasha periods
- boundary behavior for D2, D3, D4, D12, D16, D20, D24, D27, D30, D40, D45, and D60
- classical unequal D30 span transitions in odd and even signs
- complete generation of all fifteen D-number vargas with ten positions and an Ascendant in house 1
- bilingual registry labels, descriptions, references, and warnings

## Precision caveat

D40, D45, and especially D60 are highly sensitive to birth-time accuracy. D60 contains half-degree segments; a small clock-time difference can change the divisional Ascendant. The interface therefore shows explicit warnings for the most sensitive charts.

## External validation

Automated tests verify internal consistency and documented boundaries. Cross-software fixtures against established Jyotisha software remain a planned validation milestone.
