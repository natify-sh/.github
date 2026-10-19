# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#     "fonttools>=4.67.0",
#     "skia-pathops>=0.9.2",
# ]
# ///
"""Extended natify-sh logo: 24px puzzle icon centred on a 64x64 canvas, with PCB traces
continuing every seam / code line that exits the icon's edge."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import BLUE, CODE_W, GREEN, SEAM_W, R, _code_d, fmt, geometry

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pcb")
OFF = 20  # icon offset inside the 64x64 canvas
PAD_R, PAD_W = 0.8, 0.7  # via ring: centre radius, ring width

# Traces in canvas coords. Each: (stroke width, points). Last point = via centre.
# Starts 1.5 units off the icon edge, aligned with the line it continues.
TRACES = [
    # top seam -> up, jog right
    (SEAM_W, [(32, 18.5), (32, 14), (35, 11), (35, 5.8)]),
    # bottom seam -> down, jog left
    (SEAM_W, [(32, 45.5), (32, 50), (29, 53), (29, 58.2)]),
    # right seam -> right, jog down
    (SEAM_W, [(45.5, 32), (53, 32), (56, 35), (60.2, 35)]),
    # left seam -> left, jog up
    (SEAM_W, [(18.5, 32), (11, 32), (8, 29), (3.8, 29)]),
    # right code bus (rows y=4,6,8 of the icon) -> fan up-right to 3-unit pitch
    (CODE_W, [(45.5, 24), (49, 24), (54, 19), (59.8, 19)]),
    (CODE_W, [(45.5, 26), (50, 26), (54, 22), (56.8, 22)]),
    (CODE_W, [(45.5, 28), (51, 28), (54, 25), (59.8, 25)]),
    # left code bus (rows y=17.5,19.5) -> fan down-left to 3-unit pitch
    (CODE_W, [(18.5, 37.5), (13, 37.5), (9, 41.5), (4.2, 41.5)]),
    (CODE_W, [(18.5, 39.5), (14, 39.5), (9, 44.5), (7.2, 44.5)]),
]

# 48x48 canvas, icon at (12,12): exits at x/y = 10.5 and 37.5, pads stay >=1 unit inside
TRACES48 = [
    (SEAM_W, [(24, 10.5), (24, 8), (26, 6), (26, 2.2)]),
    (SEAM_W, [(24, 37.5), (24, 40), (22, 42), (22, 45.8)]),
    (SEAM_W, [(37.5, 24), (41, 24), (43, 26), (46.6, 26)]),
    (SEAM_W, [(10.5, 24), (7, 24), (5, 22), (1.4, 22)]),
    (CODE_W, [(37.5, 16), (39, 16), (42, 13), (46.6, 13)]),
    (CODE_W, [(37.5, 18), (40, 18), (42, 16), (43.8, 16)]),
    (CODE_W, [(37.5, 20), (41, 20), (42, 19), (46.6, 19)]),
    (CODE_W, [(10.5, 29.5), (9, 29.5), (6, 32.5), (1.4, 32.5)]),
    (CODE_W, [(10.5, 31.5), (10, 31.5), (6, 35.5), (4.2, 35.5)]),
]

LAYOUTS = {64: (20, TRACES), 48: (12, TRACES48)}


PIN_W, PIN_L, PIN_GAP = 1.2, 3, 0.5  # lead width, length, gap from body
PINS = [
    3,
    6,
    9,
    15,
    18,
    21,
]  # lead centres along a side, in icon units: 3 per quadrant, clear of the seams


def pins_svg(ink, off):
    """QFP-style leads on all four sides of the 24x24 body placed at (off, off)."""
    out = []
    for p in PINS:
        c = off + p - PIN_W / 2
        near, far = off - PIN_GAP - PIN_L, off + 24 + PIN_GAP
        out += [
            (c, near, PIN_W, PIN_L),
            (c, far, PIN_W, PIN_L),  # top, bottom
            (near, c, PIN_L, PIN_W),
            (far, c, PIN_L, PIN_W),
        ]  # left, right
    rects = "".join(
        f'    <rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="0.3"/>\n'
        for x, y, w, h in out
    )
    return f'  <g fill="{ink}">\n' + rects + "  </g>\n"


def trace_svg(ink, traces):
    out = []
    for w, pts in traces:
        *line, via = pts
        # stop the trace at the via ring, coming from the last segment's direction
        (px, py), (vx, vy) = line[-1], via
        dx, dy = vx - px, vy - py
        L = (dx * dx + dy * dy) ** 0.5
        ex, ey = vx - dx / L * PAD_R, vy - dy / L * PAD_R
        d = "M" + "L".join(f"{fmt(x)} {fmt(y)}" for x, y in line + [(ex, ey)])
        out.append(f'    <path stroke-width="{w}" d="{d}"/>\n')
        out.append(
            f'    <circle cx="{fmt(vx)}" cy="{fmt(vy)}" r="{PAD_R}" stroke-width="{PAD_W}"/>\n'
        )
    return (
        f'  <g fill="none" stroke="{ink}" stroke-linejoin="round">\n'
        + "".join(out)
        + "  </g>\n"
    )


def icon_svg(neck, color, mid, off):
    seams, k = geometry(neck)
    if color:
        cols = [BLUE, GREEN, BLUE, GREEN]
        fill = (
            f'    <g mask="url(#{mid})">\n'
            f'      <rect width="12" height="12" fill="{BLUE}"/>\n'
            f'      <rect x="12" width="12" height="12" fill="{GREEN}"/>\n'
            f'      <rect x="12" y="12" width="12" height="12" fill="{BLUE}"/>\n'
            f'      <rect y="12" width="12" height="12" fill="{GREEN}"/>\n'
            + "".join(
                f'      <circle cx="{fmt(x)}" cy="{fmt(y)}" r="{R}" fill="{c}"/>\n'
                for (x, y), c in zip(k, cols)
            )
            + "    </g>\n"
        )
    else:
        fill = f'    <rect width="24" height="24" fill="#000" mask="url(#{mid})"/>\n'
    return (
        f'  <g transform="translate({off} {off})">\n'
        f'    <mask id="{mid}">\n'
        '      <rect width="24" height="24" rx="2" fill="#fff"/>\n'
        f'      <g fill="none" stroke="#000" stroke-width="{SEAM_W}" stroke-linejoin="round">\n'
        f'        <path d="{seams}"/>\n'
        f'        <path stroke-width="{CODE_W}" stroke-linecap="round" d="{_code_d()}"/>\n'
        "      </g>\n"
        "    </mask>\n" + fill + "  </g>\n"
    )


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for size, (off, traces) in LAYOUTS.items():
        for neck in (3, 4):
            for color, ink in ((False, "#000"), (True, "#8a97a4")):
                name = f"natify-pcb{size}-{'color' if color else 'black'}-neck{neck}"
                svg = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n'
                    + trace_svg(ink, traces)
                    + icon_svg(neck, color, name + "-cut", off)
                    + "</svg>\n"
                )
                with open(os.path.join(OUT, name + ".svg"), "w") as f:
                    f.write(svg)
                print(name, len(svg))
    PAD = 0.5  # canvas padding around the leads: 24 + 2*(0.5+3.5) = 32, body lands on whole px (4..28)
    m = PAD + PIN_GAP + PIN_L
    size = fmt(24 + 2 * m)
    for neck in (3, 4):
        for color, ink in ((False, "#000"), (True, "#8a97a4")):
            name = f"natify-mcu-{'color' if color else 'black'}-neck{neck}"
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n'
                + pins_svg(ink, m)
                + icon_svg(neck, color, name + "-cut", fmt(m))
                + "</svg>\n"
            )
            with open(os.path.join(OUT, name + ".svg"), "w") as f:
                f.write(svg)
            print(name, len(svg))
