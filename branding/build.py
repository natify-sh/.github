# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#     "fonttools>=4.67.0",
#     "skia-pathops>=0.9.2",
# ]
# ///
"""Generate natify-sh puzzle icons: mask and outline variants, black and color, neck 3/4 px."""

import math
import os
from itertools import pairwise

import pathops
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

K = 1000  # work at 1000x scale: Skia's stroker/ops tolerances are tuned for pixel units

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
BLUE, GREEN = "#2a6c96", "#3c915e"
SEAM_W, CODE_W = 0.75, 0.9
R = 2.5  # knob radius

# code lines as polylines (round caps / joins)
CODE_LINES = [
    [(2.5, 2), (5, 2)],
    [(2.5, 4), (3, 4)],
    [(5, 4), (9.5, 4)],
    [(2.5, 6), (5, 6)],
    [(7, 6), (7.5, 6)],
    [(17.5, 2), (20, 2)],
    [(20, 4), (24, 4)],
    [(20, 6), (24, 6)],
    [(18.5, 8), (20, 8)],
    [(22, 8), (24, 8)],
    [(18.5, 10), (22, 10)],
    [(2.5, 15.5), (4.5, 15.5)],
    [(0, 17.5), (2.5, 17.5)],
    [(4.5, 17.5), (5.5, 17.5)],
    [(0, 19.5), (4.5, 19.5)],
    [(4.5, 21.5), (6, 21.5)],
    [(14.5, 18.5), (17, 20), (14.5, 21.5)],
    [(19, 18.5), (21.5, 18.5)],
    [(19, 21.5), (21.5, 21.5)],
]


def _code_d():
    out = []
    for pts in CODE_LINES:
        (x0, y0), rest = pts[0], pts[1:]
        seg = f"M{fmt(x0)} {fmt(y0)}"
        for x, y in rest:
            if y == y0:
                seg += f"H{fmt(x)}"
            else:
                seg += f"L{fmt(x)} {fmt(y)}"
            x0, y0 = x, y
        out.append(seg)
    return "".join(out)


def fmt(v):
    s = f"{v:.3f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def geometry(neck):
    """neck = width of knob base (3 or 4). Returns seam path d and knob centers."""
    h = neck / 2  # half chord
    d = (R * R - h * h) ** 0.5  # center offset from seam
    a, b = 6 - h, 6 + h  # chord ends along a half-seam
    seams = (
        f"M12 0V{fmt(a)}A{R} {R} 0 1 1 12 {fmt(b)}V12"
        f"M24 12H{fmt(24 - a)}A{R} {R} 0 1 1 {fmt(24 - b)} 12H12"
        f"M12 24V{fmt(24 - a)}A{R} {R} 0 1 1 12 {fmt(24 - b)}V12"
        f"M0 12H{fmt(a)}A{R} {R} 0 1 1 {fmt(b)} 12H12"
    )
    # knob centers: owned by TL, TR, BR, BL respectively
    knobs = [(12 + d, 6), (18, 12 + d), (12 - d, 18), (6, 12 - d)]
    return seams, knobs


ROT = [
    (1, 0, 0, 1, 0, 0),
    (0, 1, -1, 0, 24, 0),
    (-1, 0, 0, -1, 24, 24),
    (0, -1, 1, 0, 0, 24),
]  # 0/90/180/270 cw about (12,12)


def P(d, m=(1, 0, 0, 1, 0, 0)):
    p = pathops.Path()
    xx, xy, yx, yy, dx, dy = m
    parse_path(
        d, TransformPen(p.getPen(), (K * xx, K * xy, K * yx, K * yy, K * dx, K * dy))
    )
    return p


def circle(cx, cy, r):
    return P(f"M{cx - r} {cy}A{r} {r} 0 1 0 {cx + r} {cy}A{r} {r} 0 1 0 {cx - r} {cy}Z")


def rect(x, y, w, h):
    return P(f"M{x} {y}H{x + w}V{y + h}H{x}Z")


ROUND = P("M2 0H22A2 2 0 0 1 24 2V22A2 2 0 0 1 22 24H2A2 2 0 0 1 0 22V2A2 2 0 0 1 2 0Z")


def op(a, b, o):
    for p in (a, b):
        p.convertConicsToQuads(5)
    return pathops.op(a, b, o, fix_winding=True)


def poly(pts, m=(1, 0, 0, 1, 0, 0)):
    return P("M" + "L".join(f"{x!r} {y!r}" for x, y in pts) + "Z", m)


def union(paths):
    acc = paths[0]
    for p in paths[1:]:
        acc = op(acc, p, pathops.PathOp.UNION)
    return acc


def capsule(p1, p2, hw):
    """Exact outline of a round-capped stroke segment: rectangle + two discs."""
    (x1, y1), (x2, y2) = p1, p2
    parts = [circle(x1, y1, hw), circle(x2, y2, hw)]
    L = math.hypot(x2 - x1, y2 - y1)
    if L > 0:
        nx, ny = -(y2 - y1) / L * hw, (x2 - x1) / L * hw
        parts.append(
            poly(
                [
                    (x1 + nx, y1 + ny),
                    (x2 + nx, y2 + ny),
                    (x2 - nx, y2 - ny),
                    (x1 - nx, y1 - ny),
                ]
            )
        )
    return union(parts)


def seam_parts(neck, m):
    """Exact outline of one butt-capped, round-joined seam (top one, rotated by m)."""
    h = neck / 2
    d = (R * R - h * h) ** 0.5
    a, b = 6 - h, 6 + h
    w = SEAM_W / 2
    cx, cy = 12 + d, 6
    ro, ri = R + w, R - w
    t0, t1 = math.atan2(a - cy, 12 - cx), math.atan2(b - cy, 12 - cx)
    pt = lambda r, t: f"{cx + r * math.cos(t)!r} {cy + r * math.sin(t)!r}"
    sector = (
        f"M{pt(ro, t0)}A{ro} {ro} 0 1 1 {pt(ro, t1)}"
        f"L{pt(ri, t1)}A{ri} {ri} 0 1 0 {pt(ri, t0)}Z"
    )
    return [
        poly([(12 - w, 0), (12 + w, 0), (12 + w, a), (12 - w, a)], m),
        circle_m(12, a, w, m),
        P(sector, m),
        circle_m(12, b, w, m),
        poly([(12 - w, b), (12 + w, b), (12 + w, 12), (12 - w, 12)], m),
    ]


def circle_m(cx, cy, r, m):
    return P(
        f"M{cx - r} {cy}A{r} {r} 0 1 0 {cx + r} {cy}A{r} {r} 0 1 0 {cx - r} {cy}Z", m
    )


def cuts(neck):
    parts = []
    for m in ROT:
        parts += seam_parts(neck, m)
    hw = CODE_W / 2
    for pts in CODE_LINES:
        for p1, p2 in pairwise(pts):
            parts.append(capsule(p1, p2, hw))
    return union(parts)


def d_of(path):
    path.convertConicsToQuads(5)
    pen = SVGPathPen(None, ntos=fmt)
    path.draw(TransformPen(pen, (1 / K, 0, 0, 1 / K, 0, 0)))
    return pen.getCommands()


HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">\n'


def outline_black(neck):
    shape = op(ROUND, cuts(neck), pathops.PathOp.DIFFERENCE)
    return (
        HEAD + f'  <path fill="#000" fill-rule="evenodd" d="{d_of(shape)}"/>\n</svg>\n'
    )


def pieces(neck):
    _, k = geometry(neck)
    quads = [
        rect(0, 0, 12, 12),
        rect(12, 0, 12, 12),
        rect(12, 12, 12, 12),
        rect(0, 12, 12, 12),
    ]
    discs = [circle(x, y, R) for x, y in k]
    cut = cuts(neck)
    out = []
    for i in range(4):
        p = op(quads[i], discs[i], pathops.PathOp.UNION)  # own knob
        p = op(p, discs[(i - 1) % 4], pathops.PathOp.DIFFERENCE)  # neighbour's knob
        p = op(p, cut, pathops.PathOp.DIFFERENCE)
        p = op(p, ROUND, pathops.PathOp.INTERSECTION)
        out.append(p)
    return out


def outline_color(neck):
    cols = [BLUE, GREEN, BLUE, GREEN]  # TL, TR, BR, BL
    body = "".join(
        f'  <path fill="{c}" fill-rule="evenodd" d="{d_of(p)}"/>\n'
        for c, p in zip(cols, pieces(neck))
    )
    return HEAD + body + "</svg>\n"


def mask_svg(neck, color):
    seams, k = geometry(neck)
    seams_pretty = seams.replace("M", "\n               M").strip()
    code_pretty = _code_d().replace("M", "\n               M").strip()
    if color:
        cols = [BLUE, GREEN, BLUE, GREEN]
        fill = (
            '  <g mask="url(#cut)">\n'
            f'    <rect width="12" height="12" fill="{BLUE}"/>\n'
            f'    <rect x="12" width="12" height="12" fill="{GREEN}"/>\n'
            f'    <rect x="12" y="12" width="12" height="12" fill="{BLUE}"/>\n'
            f'    <rect y="12" width="12" height="12" fill="{GREEN}"/>\n'
            + "".join(
                f'    <circle cx="{fmt(x)}" cy="{fmt(y)}" r="{R}" fill="{c}"/>\n'
                for (x, y), c in zip(k, cols)
            )
            + "  </g>\n"
        )
    else:
        fill = '  <rect width="24" height="24" fill="#000" mask="url(#cut)"/>\n'
    return (
        HEAD + '  <mask id="cut">\n'
        '    <rect width="24" height="24" rx="2" fill="#fff"/>\n'
        f'    <g fill="none" stroke="#000" stroke-width="{SEAM_W}" stroke-linejoin="round">\n'
        "      <!-- puzzle seams -->\n"
        f'      <path d="{seams_pretty}"/>\n'
        "      <!-- code lines -->\n"
        f'      <path stroke-width="{CODE_W}" stroke-linecap="round"\n'
        f'            d="{code_pretty}"/>\n'
        "    </g>\n"
        "  </mask>\n" + fill + "</svg>\n"
    )


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for neck in (3, 4):
        files = {
            f"puzzle-black-neck{neck}-mask.svg": mask_svg(neck, False),
            f"puzzle-color-neck{neck}-mask.svg": mask_svg(neck, True),
            f"puzzle-black-neck{neck}-outline.svg": outline_black(neck),
            f"puzzle-color-neck{neck}-outline.svg": outline_color(neck),
        }
        for name, s in files.items():
            with open(os.path.join(OUT, name), "w") as f:
                f.write(s)
            print(name, len(s))
