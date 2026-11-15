#!/usr/bin/env python3
"""Build the static board site from the design sources.

Every design/<set>/manifest.json is one board set; sets are shown in their "order".
For each set the .dc.html artboards next to the manifest are unwrapped into:

  boards/<slug>.html   each artboard as a plain, standalone HTML page (markup and SVG unchanged)

and, for all sets together:

  assets/boards.js     the board lists used by view.html
  index.html           the gallery page (texts for its header come from design/site.json)

Usage: python3 tools/build.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design"


def parse_artboard(text: str, name: str) -> dict:
    """Split a Design Component artboard into title, <head> extras and body markup.

    Only static artboards are supported: the converter refuses anything that needs the
    canvas runtime (template holes, repeats, imports, uploaded assets).
    """
    for marker, why in (("{{", "template holes"), ("<sc-", "sc-for / sc-if"),
                        ("<dc-import", "dc-import"), ("<x-import", "x-import"), ("/_blob/", "uploaded assets")):
        if marker in text:
            sys.exit(f"{name}: uses {why}; this converter only handles static artboards")

    def grab(pattern: str, what: str) -> str:
        m = re.search(pattern, text, re.S)
        if not m:
            sys.exit(f"{name}: no {what} found")
        return m.group(1)

    title = grab(r"<title>(.*?)</title>", "<title>")
    helmet = grab(r"<helmet>\s*(.*?)\s*</helmet>", "<helmet>")
    body = grab(r"</helmet>\s*(.*?)\s*</x-dc>", "artboard root")
    props = json.loads(html.unescape(grab(r"data-props='(.*?)'", "data-props")))
    preview = props.get("$preview", {})
    return {"title": title, "head": helmet, "body": body,
            "w": preview.get("width"), "h": preview.get("height")}


BOARD_PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{head}
</head>
<body>
{body}
</body>
</html>
"""

INDEX_PAGE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{heading} · {project}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&amp;family=Be+Vietnam+Pro:wght@400;500;600&amp;display=swap">
<link rel="stylesheet" href="assets/site.css">
</head>
<body class="gallery">
<header class="gallery-head">
<div class="eyebrow">{eyebrow}</div>
<h1 class="display">{heading}</h1>
<p class="lede">{summary}</p>
<nav class="set-nav" aria-label="Các bộ bản vẽ">
{nav}
</nav>
</header>
<main>
{sections}
</main>
</body>
</html>
"""

NAV_ITEM = '<a href="#{id}"><span class="code">{count} bản</span>{set}</a>'

SECTION = """<section class="set" id="{id}" aria-labelledby="{id}-title">
<div class="set-head">
<div class="eyebrow">{eyebrow}</div>
<h2 class="display" id="{id}-title">{heading}</h2>
<p class="lede">{summary}</p>
<div class="gallery-meta"><span>{count} bản vẽ</span><a href="view.html#{first}">Xem lần lượt từng bản</a></div>
</div>
<ol class="board-grid">
{cards}
</ol>
</section>"""

CARD = """<li>
<a class="board-card" href="view.html#{slug}">
<div class="thumb" style="--w: {w}; --h: {h}">
<iframe src="boards/{slug}.html" title="{code} · {title_attr}" loading="lazy" tabindex="-1" aria-hidden="true" scrolling="no"></iframe>
</div>
<div class="card-text">
<span class="code">{code}</span>
<span class="card-title">{title}</span>
</div>
</a>
</li>"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def build_set(set_dir: Path, seen: set) -> dict:
    manifest = json.loads((set_dir / "manifest.json").read_text(encoding="utf-8"))
    boards = []
    for b in manifest["boards"]:
        if b["slug"] in seen:
            sys.exit(f"{set_dir.name}: slug {b['slug']} is used twice")
        seen.add(b["slug"])
        art = parse_artboard((set_dir / b["file"]).read_text(encoding="utf-8"), b["file"])
        if (art["w"], art["h"]) != (b["w"], b["h"]):
            sys.exit(f"{b['file']}: manifest size {b['w']}x{b['h']} != artboard {art['w']}x{art['h']}")
        page = BOARD_PAGE.format(**art)
        (ROOT / "boards" / f"{b['slug']}.html").write_text(page, encoding="utf-8")
        boards.append({k: b[k] for k in ("code", "slug", "title", "w", "h")})
        print(f"boards/{b['slug']}.html  {len(page.encode()):>7} bytes")
    return {"id": set_dir.name, "order": manifest.get("order", 99), "set": manifest["set"],
            "eyebrow": manifest["eyebrow"], "heading": manifest["heading"],
            "summary": manifest["summary"], "boards": boards}


def build() -> None:
    (ROOT / "boards").mkdir(exist_ok=True)
    seen: set = set()
    sets = sorted((build_set(m.parent, seen) for m in DESIGN.glob("*/manifest.json")),
                  key=lambda s: (s["order"], s["id"]))
    site = json.loads((DESIGN / "site.json").read_text(encoding="utf-8"))

    stale = {p.stem for p in (ROOT / "boards").glob("*.html")} - seen
    for slug in sorted(stale):
        (ROOT / "boards" / f"{slug}.html").unlink()
        print(f"removed boards/{slug}.html")

    (ROOT / "assets" / "boards.js").write_text(
        "// Generated by tools/build.py from design/*/manifest.json\n"
        "window.BOARD_SETS = " + json.dumps(
            [{"id": s["id"], "set": s["set"], "boards": s["boards"]} for s in sets],
            ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8")

    sections, nav = [], []
    for s in sets:
        cards = [CARD.format(slug=b["slug"], code=b["code"], w=b["w"], h=b["h"], title=esc(b["title"]),
                             title_attr=html.escape(b["title"])) for b in s["boards"]]
        sections.append(SECTION.format(id=s["id"], eyebrow=esc(s["eyebrow"]), heading=esc(s["heading"]),
                                       summary=esc(s["summary"]), count=len(s["boards"]),
                                       first=s["boards"][0]["slug"], cards="\n".join(cards)))
        nav.append(NAV_ITEM.format(id=s["id"], count=len(s["boards"]), set=esc(s["heading"])))
    (ROOT / "index.html").write_text(INDEX_PAGE.format(
        project=esc(site["project"]), eyebrow=esc(site["eyebrow"]), heading=esc(site["heading"]),
        summary=esc(site["summary"]), nav="\n".join(nav), sections="\n".join(sections)), encoding="utf-8")
    print(f"assets/boards.js, index.html · {len(sets)} sets, {len(seen)} boards")


if __name__ == "__main__":
    build()
