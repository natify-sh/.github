"""GitHub social preview cards (1280x640) for natify-sh repos, laid out on GitHub's
Repo Card Template: everything important stays inside the 80 px safe border.

    python3 build_social.py                         # all repos, both themes -> out/<theme>/<repo>.{svg,png}
    python3 build_social.py wasmhost --theme dark   # one repo, black background / white text

Needs: resvg_py, Pillow. Fonts are bundled in fonts/ (Inter, JetBrains Mono; OFL).
"""
import io, os, re, sys
from xml.sax.saxutils import escape
from PIL import ImageFont
import resvg_py

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "out")
LOGO = os.path.join(HERE, "..", "pcb", "natify-mcu-color-neck4.svg")

ORG = "natify-sh"
REPOS = {
    "wasmhost": "One Python facade over multiple WebAssembly runtimes",
    "wasmext": "Any wasm → wasm2c → native Python extension, with WASI preview 1",
    "wabt-package": "The WebAssembly Binary Toolkit (WABT), packaged for PyPI",
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

    desc_svg = "".join(
        f'  <text x="{W/2}" y="{DESC_Y + i*DESC_LH}" text-anchor="middle" font-family="Inter" '
        f'font-size="{DESC_SIZE}" fill="{t['body']}">{escape(l)}</text>\n' for i, l in enumerate(lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'  <rect width="{W}" height="{H}" fill="{t['bg']}"/>\n'
            f'  <svg x="{x0:.1f}" y="{LOGO_TOP}" width="{LOGO_SIZE}" height="{LOGO_SIZE}" viewBox="{vb}">{body}</svg>\n'
            f'  <text x="{x0 + LOGO_SIZE + GAP:.1f}" y="{mark_base:.1f}" font-family="JetBrains Mono" '
            f'font-weight="800" font-size="{MARK_SIZE}" fill="{t['ink']}">{ORG}</text>\n'
            f'  <text x="{W/2}" y="{TITLE_Y}" text-anchor="middle" font-family="Inter" font-weight="700" '
            f'font-size="{TITLE_SIZE}" fill="{t['title']}">{escape(repo)}</text>\n'
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
