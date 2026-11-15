# Biệt thự Tam Quan · La Rotonda B

A static site for the La Rotonda B drawing set (RB0–RB7, plus RB4b), taken from the
[design canvas](https://claude.ai/code/artifact/7f50b71b-e25f-4a45-9de9-66d8f274766d).
It is plain HTML and CSS with no dependencies, so any static host works, including GitHub Pages.

- `index.html`: gallery of all boards
- `view.html#<slug>`: one board at a time, either fitted to the screen or at 1:1. Use the
  arrow buttons or the ← → keys to page through.
- `boards/<slug>.html`: each board on its own, exactly as drawn (1480 × 1060 px; RB0 is 1000 × 1060)

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Opening `index.html` directly from disk also works.

## How it is built

The original canvas artboards are kept in `design/rotonda-b/*.dc.html`. Board order, codes and
titles come from `design/rotonda-b/manifest.json`. `tools/build.py` unwraps each artboard into a
plain HTML page without changing its markup or SVG, then regenerates `boards/`, `assets/boards.js`
and `index.html`:

```bash
python3 tools/build.py design/rotonda-b
```

The generated files are committed, so the site runs without a build step. Do not edit them by hand.
Edit the sources and run the build again. `view.html`, `assets/site.css` and `assets/viewer.js`
are written by hand.

To add another set from the canvas (for example CHỐT or the MT facade studies), put its
`.dc.html` files and a `manifest.json` in a new `design/<set>/` folder. The converter only accepts
static artboards. It stops with an error if an artboard uses template holes, `sc-*` / `dc-import`
elements or uploaded `/_blob/` assets.
