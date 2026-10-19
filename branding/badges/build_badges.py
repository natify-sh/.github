# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#     "fonttools>=4.67.0",
#     "skia-pathops>=0.9.2",
# ]
# ///
"""shields.io badges for natify-sh with the logo passed as a base64 data URI.

    uv run build_badges.py   # -> badges.md (markdown + raw URLs), logo-*.svg

Badge logo (LOGO_STYLE):
  "simple" (default) - seams only, thicker seams: reads cleanly at shields' 14 px logo size
  "full"             - the full 24x24 icon from ../min (code lines included)
"""

import base64
import os
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from build import BLUE, GREEN, R, fmt, geometry

NECK = 4
LOGO_STYLE = "simple"  # "full" | "simple"
SEAM = 1.6  # simple style only: ~0.9 px at 14 px


def logo(color):
    return logo_full(color) if LOGO_STYLE == "full" else logo_simple(color)


def logo_full(color):
    kind = "color" if color else "black"
    with open(
        os.path.join(HERE, "..", "min", f"puzzle-{kind}-neck{NECK}-mask.svg")
    ) as f:
        svg = f.read()
    if not color:  # white icon for the dark badge
        svg = svg.replace(
            '<path d="M0 0h24v24H0z" mask=', '<path fill="#fff" d="M0 0h24v24H0z" mask='
        )
        assert 'fill="#fff" d="M0 0h24v24H0z"' in svg
    return svg


def logo_simple(color):
    seams, k = geometry(NECK)
    if color:
        fill = (
            f'<g mask="url(#m)"><path fill="{BLUE}" d="M0 0h12v12H0zM12 12h12v12H12z"/>'
            f'<path fill="{GREEN}" d="M12 0h12v12H12zM0 12h12v12H0z"/>'
            + "".join(
                f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{R}" fill="{c}"/>'
                for (x, y), c in zip(k, [BLUE, GREEN, BLUE, GREEN])
            )
            + "</g>"
        )
    else:
        fill = '<rect width="24" height="24" fill="#fff" mask="url(#m)"/>'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<mask id="m"><rect width="24" height="24" rx="2" fill="#fff"/>'
        f'<path fill="none" stroke="#000" stroke-width="{SEAM}" d="{seams}"/></mask>'
        + fill
        + "</svg>"
    )


def data_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def esc(s):  # shields path escaping: '-' -> '--', '_' -> '__', ' ' -> '_'
    return s.replace("-", "--").replace("_", "__").replace(" ", "_")


THEMES = {"dark": ("000000", False), "light": ("ffffff", True)}
BADGES = {
    "brand": (None, "natify-sh"),
    "powered": ("powered by", "natify-sh"),
    "built": ("built with", "natify-sh"),
}
LINK = "https://github.com/natify-sh"

if __name__ == "__main__":
    md = ["# natify-sh badges\n"]
    for theme, (bg, color) in THEMES.items():
        svg = logo(color)
        with open(os.path.join(HERE, f"logo-{theme}.svg"), "w") as f:
            f.write(svg)
        logo_q = quote(data_uri(svg), safe="")
        md.append(f"## {theme}\n")
        for label, msg in BADGES.values():
            path = f"{esc(label)}-{esc(msg)}-{bg}" if label else f"-{esc(msg)}-{bg}"
            url = f"https://img.shields.io/badge/{path}?labelColor={bg}&logo={logo_q}"
            alt = f"{label} {msg}" if label else msg
            md.append(f"[![{alt}]({url})]({LINK})\n\n```\n{url}\n```\n")
    with open(os.path.join(HERE, "badges.md"), "w") as f:
        f.write("\n".join(md))
    print("\n".join(l for l in md if l.startswith("[!")))
