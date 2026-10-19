"""GitHub social preview cards (1280x640) for natify-sh repos, laid out on GitHub's
Repo Card Template: everything important stays inside the 80 px safe border.

    python3 build_social.py                         # all repos, both themes -> out/<theme>/<repo>.{svg,png}
    python3 build_social.py wasmhost --theme dark   # one repo, black background / white text

Needs: resvg_py, Pillow, fonttools, uharfbuzz. Fonts are bundled in fonts/ (Inter, JetBrains Mono; OFL).
Text is converted to outlines, so the SVGs look the same in every viewer (no font dependency).
"""
import io, os, re, sys
from xml.sax.saxutils import escape
from PIL import ImageFont
import resvg_py
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "out")
LOGO = os.path.join(HERE, "..", "pcb", "natify-mcu-color-neck4.svg")

ORG = "natify-sh"
REPOS = {
    "wasmhost": "WebAssembly from CPython, PyPy and Pythonista, with the JavaScript WebAssembly API",
    "wasmext": "Turn WebAssembly modules into native CPython extensions",
    "wabt-package": "WABT, the WebAssembly Binary Toolkit, as prebuilt binaries and the wasm2c runtime",
    "flutpak": "Flatpak manifests for sandboxed builds of Flutter apps",
    "cibuildmp": "cibuildwheel for MicroPython: build usermod and natmod native modules",
    "rp2040py": "RP2040 emulator in pure Python",
    "micropython-wasm3": "Wasm3 WebAssembly interpreter as a MicroPython native module",
}

W, H, SAFE = 1280, 640, 80
THEMES = {  # background, wordmark, title, description
    "light": dict(bg="#ffffff", ink="#1b2a3a", title="#1f2328", body="#3d444d"),
    "dark":  dict(bg="#000000", ink="#ffffff", title="#ffffff", body="#c9d1d9"),
}

# layout (px)
LOGO_SIZE = 150
LOGO_TOP = 104
MARK_SIZE = 104          # wordmark font size
GAP = 36                 # logo <-> wordmark
TITLE_SIZE, TITLE_Y = 68, 388
DESC_SIZE, DESC_Y, DESC_LH, DESC_MAX_W = 32, 452, 46, W - 2 * SAFE - 120

f_mark = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono-ExtraBold.ttf"), MARK_SIZE)
f_title = ImageFont.truetype(os.path.join(FONTS, "Inter-Bold.otf"), TITLE_SIZE)
f_desc = ImageFont.truetype(os.path.join(FONTS, "Inter-Regular.otf"), DESC_SIZE)


_shapers = {}


def _shaper(file):
    if file not in _shapers:
        path = os.path.join(FONTS, file)
        _shapers[file] = (hb.Font(hb.Face(hb.Blob.from_file_path(path))), TTFont(path))
    return _shapers[file]


def text_path(file, text, size, x, y, fill, anchor="start", extra=""):
    """Text as an SVG <path> of glyph outlines, shaped with HarfBuzz (kerning included).
    Returns (svg, width); anchor is "start" or "middle" around x, y is the baseline."""
    hbfont, tt = _shaper(file)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf)
    scale = size / tt["head"].unitsPerEm
    width = sum(p.x_advance for p in buf.glyph_positions) * scale
    cx = x - width / 2 if anchor == "middle" else x
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        t = (scale, 0, 0, -scale, cx + pos.x_offset * scale, y - pos.y_offset * scale)
        gs[order[info.codepoint]].draw(TransformPen(pen, t))
        cx += pos.x_advance * scale
    return f'<path fill="{fill}" {extra}d="{pen.getCommands()}"/>', width


def wrap(text, font, max_w):
    """One line if it fits, else the 2-line split with the most even widths (no orphans)."""
    if font.getlength(text) <= max_w:
        return [text]
    words = text.split()
    splits = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
    splits = [s for s in splits if max(map(font.getlength, s)) <= max_w]
    if not splits:
        raise ValueError(f"description too long for 2 lines: {text!r}")
    return list(min(splits, key=lambda s: max(map(font.getlength, s))))


def logo_inner():
    """Logo SVG as a nested <svg> (keeps its own viewBox; mask id is file-unique already)."""
    src = open(LOGO).read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    body = src[src.index(">") + 1: src.rindex("</svg>")]
    return vb, body


def card(repo, desc, theme="light"):
    t = THEMES[theme]
    vb, body = logo_inner()
    mark_w = f_mark.getlength(ORG)
    top, bottom = f_mark.getbbox(ORG, anchor="ls")[1::2]   # glyph extent around baseline
    group_w = LOGO_SIZE + GAP + mark_w
    x0 = (W - group_w) / 2
    cy = LOGO_TOP + LOGO_SIZE / 2
    mark_base = cy - (top + bottom) / 2

    title_w = f_title.getlength(repo)
    if title_w > W - 2 * SAFE:
        raise ValueError(f"title too wide: {repo}")
    lines = wrap(desc, f_desc, DESC_MAX_W)

    desc_svg = "".join("  " + text_path("Inter-Regular.otf", l, DESC_SIZE, W / 2, DESC_Y + i * DESC_LH,
                                        t["body"], "middle")[0] + "\n" for i, l in enumerate(lines))
    mark_svg = text_path("JetBrainsMono-ExtraBold.ttf", ORG, MARK_SIZE, x0 + LOGO_SIZE + GAP, mark_base, t["ink"])[0]
    title_svg = text_path("Inter-Bold.otf", repo, TITLE_SIZE, W / 2, TITLE_Y, t["title"], "middle")[0]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'  <rect width="{W}" height="{H}" fill="{t["bg"]}"/>\n'
            f'  <svg x="{x0:.1f}" y="{LOGO_TOP}" width="{LOGO_SIZE}" height="{LOGO_SIZE}" viewBox="{vb}">{body}</svg>\n'
            f'  {mark_svg}\n  {title_svg}\n'
            + desc_svg + '</svg>\n')


def render(svg):
    return bytes(resvg_py.svg_to_bytes(svg_string=svg, font_dirs=[FONTS], skip_system_fonts=True))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="*", help="repo names from REPOS (default: all)")
    ap.add_argument("--theme", choices=[*THEMES, "all"], default="all",
                    help="light = white bg, dark = black bg / white text (default: all)")
    a = ap.parse_args()
    themes = list(THEMES) if a.theme == "all" else [a.theme]
    for theme in themes:
        os.makedirs(os.path.join(OUT, theme), exist_ok=True)
        for name in a.repos or list(REPOS):
            svg = card(name, REPOS[name], theme)
            png = render(svg)
            base = os.path.join(OUT, theme, name)
            open(base + ".svg", "w").write(svg)
            open(base + ".png", "wb").write(png)
            print(f"{theme}/{name}.png  {len(png)//1024} KB")
