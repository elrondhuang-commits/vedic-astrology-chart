"""North Indian D1 chart SVG renderer.

House 1 is always the fixed upper-centre compartment. Signs rotate with the Ascendant.
"""
from __future__ import annotations

from html import escape
from typing import Any, Mapping

# Visual centres for the 12 fixed houses in a classic North Indian chart.
HOUSE_CENTRES = {
    1: (300, 105),
    2: (155, 70),
    3: (75, 155),
    4: (105, 300),
    5: (75, 445),
    6: (155, 530),
    7: (300, 495),
    8: (445, 530),
    9: (525, 445),
    10: (495, 300),
    11: (525, 155),
    12: (445, 70),
}

PLANET_ABBR = {
    "Ascendant": "As",
    "Sun": "Su",
    "Moon": "Mo",
    "Mars": "Ma",
    "Mercury": "Me",
    "Jupiter": "Ju",
    "Venus": "Ve",
    "Saturn": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke",
}


def _degree_text(value: float) -> str:
    return f"{value:.1f}°"


def render_north_indian_svg(
    chart: Mapping[str, Any],
    sign_labels: Mapping[str, str] | None = None,
    planet_labels: Mapping[str, str] | None = None,
) -> str:
    """Return a self-contained responsive SVG string."""
    sign_labels = sign_labels or {}
    planet_labels = planet_labels or {}
    asc_sign = int(chart["ascendant_sign_index"])

    by_house: dict[int, list[Mapping[str, Any]]] = {house: [] for house in range(1, 13)}
    for item in chart["positions"]:
        by_house[int(item["house"])].append(item)

    line_elements = """
      <rect x="20" y="20" width="560" height="560" rx="4" />
      <line x1="20" y1="20" x2="580" y2="580" />
      <line x1="580" y1="20" x2="20" y2="580" />
      <line x1="300" y1="20" x2="580" y2="300" />
      <line x1="580" y1="300" x2="300" y2="580" />
      <line x1="300" y1="580" x2="20" y2="300" />
      <line x1="20" y1="300" x2="300" y2="20" />
    """

    text_elements: list[str] = []
    for house in range(1, 13):
        x, y = HOUSE_CENTRES[house]
        sign_index = (asc_sign + house - 1) % 12
        sign_key = (
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
        )[sign_index]
        sign_text = sign_labels.get(sign_key, sign_key)

        text_elements.append(
            f'<text x="{x}" y="{y - 24}" class="sign" text-anchor="middle">'
            f'{escape(str(sign_text))} · H{house}</text>'
        )

        bodies = sorted(by_house[house], key=lambda p: (p["code"] != "Ascendant", p["longitude"]))
        lines: list[str] = []
        for body in bodies:
            code = str(body["code"])
            label = planet_labels.get(code, PLANET_ABBR.get(code, code))
            retro = " ℞" if body.get("retrograde") and code not in ("Rahu", "Ketu") else ""
            lines.append(f"{label} {_degree_text(float(body['degree_in_sign']))}{retro}")

        for idx, line in enumerate(lines[:5]):
            text_elements.append(
                f'<text x="{x}" y="{y + idx * 18}" class="body" text-anchor="middle">'
                f'{escape(line)}</text>'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" role="img" aria-label="North Indian D1 chart">
<style>
  rect, line {{ fill: none; stroke: currentColor; stroke-width: 2; vector-effect: non-scaling-stroke; }}
  text {{ fill: currentColor; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  .sign {{ font-size: 13px; font-weight: 700; }}
  .body {{ font-size: 13px; }}
</style>
{line_elements}
{''.join(text_elements)}
</svg>"""
