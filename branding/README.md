# natify-sh logo

Puzzle icon, 24×24. Neck = width of the knob base (3 or 4 px).
Colors: blue `#2a6c96`, green `#3c915e`, PCB ink `#8a97a4`.

| Folder | Content |
|---|---|
| `src/` | Icon 24×24, readable sources. `*-mask` = cutouts via `<mask>`; `*-outline` = flattened paths (no mask/stroke/id, renders everywhere) |
| `min/` | Same, optimized with svgo (`svgo.config.mjs`), mask ids prefixed per file |
| `pcb/` | `natify-pcb64-*` / `natify-pcb48-*`: icon + PCB traces continuing seams and code lines; `natify-mcu-*`: icon as QFP chip with leads, 32×32 |
| `social/` | GitHub social preview cards 1280×640, light and dark (`out/light/`, `out/dark/`), generator `build_social.py` (repos & descriptions in `REPOS`), bundled fonts Inter + JetBrains Mono (OFL) |
| `badges/` | shields.io badges (`badges.md`: brand / powered by / built with, dark + light), logos (simplified, seams only; `LOGO_STYLE = "full"` for the full icon), generator `build_badges.py` |
| `preview.png`, `previews/` | Renders of all variants |

Regenerate: `uv run build.py`, `uv run build_pcb.py`, then `npx svgo@3 --config svgo.config.mjs -f src -o min`.

## Badges

Ready-made shields.io badges (full URLs for all six variants: `badges/badges.md`, regenerate with `uv run badges/build_badges.py`).
The logo is the icon SVG, base64-encoded and passed in the `logo` query parameter:

```
https://img.shields.io/badge/<label>-<message>-<color>?labelColor=<color>&logo=data:image/svg+xml;base64,<BASE64>
```

URL-encode the `logo` value (`+` → `%2B`, `/` → `%2F`, `=` → `%3D`), and in label/message escape `-` as `--`, `_` as `__`, space as `_`.

**Markdown, inline:**

```markdown
[![built with natify-sh](https://img.shields.io/badge/built_with-natify--sh-000000?labelColor=000000&logo=...)](https://github.com/natify-sh)
```

**Markdown, reference-style** (keeps the long URL out of the text — recommended):

```markdown
[![built with natify-sh][natify-badge]][natify]

[natify]: https://github.com/natify-sh
[natify-badge]: https://img.shields.io/badge/built_with-natify--sh-000000?labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPG1hc2sgaWQ9Im0iPjxyZWN0IHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgcng9IjIiIGZpbGw9IiNmZmYiLz48cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMS42IiBkPSJNMTIgMFY0QTIuNSAyLjUgMCAxIDEgMTIgOFYxMk0yNCAxMkgyMEEyLjUgMi41IDAgMSAxIDE2IDEySDEyTTEyIDI0VjIwQTIuNSAyLjUgMCAxIDEgMTIgMTZWMTJNMCAxMkg0QTIuNSAyLjUgMCAxIDEgOCAxMkgxMiIvPjwvbWFzaz48cmVjdCB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIGZpbGw9IiNmZmYiIG1hc2s9InVybCgjbSkiLz48L3N2Zz4%3D
```

**HTML, switches with GitHub light/dark theme:**

```html
<a href="https://github.com/natify-sh">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/built_with-natify--sh-ffffff?labelColor=ffffff&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPG1hc2sgaWQ9Im0iPjxyZWN0IHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgcng9IjIiIGZpbGw9IiNmZmYiLz48cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMS42IiBkPSJNMTIgMFY0QTIuNSAyLjUgMCAxIDEgMTIgOFYxMk0yNCAxMkgyMEEyLjUgMi41IDAgMSAxIDE2IDEySDEyTTEyIDI0VjIwQTIuNSAyLjUgMCAxIDEgMTIgMTZWMTJNMCAxMkg0QTIuNSAyLjUgMCAxIDEgOCAxMkgxMiIvPjwvbWFzaz48ZyBtYXNrPSJ1cmwoI20pIj48cGF0aCBmaWxsPSIjMmE2Yzk2IiBkPSJNMCAwaDEydjEySDB6TTEyIDEyaDEydjEySDEyeiIvPjxwYXRoIGZpbGw9IiMzYzkxNWUiIGQ9Ik0xMiAwaDEydjEySDEyek0wIDEyaDEydjEySDB6Ii8%2BPGNpcmNsZSBjeD0iMTMuNSIgY3k9IjYiIHI9IjIuNSIgZmlsbD0iIzJhNmM5NiIvPjxjaXJjbGUgY3g9IjE4IiBjeT0iMTMuNSIgcj0iMi41IiBmaWxsPSIjM2M5MTVlIi8%2BPGNpcmNsZSBjeD0iMTAuNSIgY3k9IjE4IiByPSIyLjUiIGZpbGw9IiMyYTZjOTYiLz48Y2lyY2xlIGN4PSI2IiBjeT0iMTAuNSIgcj0iMi41IiBmaWxsPSIjM2M5MTVlIi8%2BPC9nPjwvc3ZnPg%3D%3D">
    <img alt="built with natify-sh" src="https://img.shields.io/badge/built_with-natify--sh-000000?labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI%2BPG1hc2sgaWQ9Im0iPjxyZWN0IHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgcng9IjIiIGZpbGw9IiNmZmYiLz48cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMS42IiBkPSJNMTIgMFY0QTIuNSAyLjUgMCAxIDEgMTIgOFYxMk0yNCAxMkgyMEEyLjUgMi41IDAgMSAxIDE2IDEySDEyTTEyIDI0VjIwQTIuNSAyLjUgMCAxIDEgMTIgMTZWMTJNMCAxMkg0QTIuNSAyLjUgMCAxIDEgOCAxMkgxMiIvPjwvbWFzaz48cmVjdCB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIGZpbGw9IiNmZmYiIG1hc2s9InVybCgjbSkiLz48L3N2Zz4%3D">
  </picture>
</a>
```

(On a dark page the white badge stands out; on a light page the black one. Swap the two if you prefer badges that blend in.)
