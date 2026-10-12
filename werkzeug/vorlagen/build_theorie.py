"""Lernseite (Theorie am Handy) aus der TH-Kadetten-PPP – für GitHub Pages."""
import json, html, os, shutil
from PIL import Image

S = json.load(open("/home/claude/handy/slides.json"))
DST = "/home/claude/nawi/2ab-nawi/k1-2-bindungen/"
os.makedirs(DST + "img", exist_ok=True)
rd = lambda p: open(p).read().strip()
CAMO, LOGO, SMILEY = rd("/home/claude/w2/camo.b64"), rd("/home/claude/w2/logo.b64"), rd("/home/claude/w2/smiley.b64")
esc = html.escape


def para(p):
    return "".join(f"<strong>{esc(r['t'])}</strong>" if r["b"] else esc(r["t"]) for r in p)


def txt(b):
    return " ".join("".join(r["t"] for r in p) for p in b.get("p", []))


def bild(it, alt):
    src = it.get("gif") or it["f"]
    name = os.path.basename(src)
    if src.endswith(".png"):   # verkleinern + palettieren für schnelles Laden
        im = Image.open("/home/claude/handy/" + src).convert("RGB")
        if im.width > 1100: im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
        im.quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(DST + "img/" + name, optimize=True)
    else:
        shutil.copy("/home/claude/handy/" + src, DST + "img/" + name)
    w, h = Image.open(DST + "img/" + name).size
    cls = "fig anim" if src.endswith(".gif") else "fig"
    cap = '<figcaption>Animation</figcaption>' if src.endswith(".gif") else ""
    return f'<figure class="{cls}"><img src="img/{name}" width="{w}" height="{h}" loading="lazy" alt="{esc(alt)}">{cap}</figure>'


def karte(items, alt):
    out, first = [], True
    textual = [i for i in items if i["type"] != "img"]
    for it in items:
        if it["type"] == "img":
            out.append(bild(it, alt)); continue
        for k, p in enumerate(it["p"]):
            s = "".join(r["t"] for r in p)
            head = first and k == 0 and len(s) < 45 and (len(textual) > 1 or len(it["p"]) > 1)
            out.append(f"<h4>{esc(s)}</h4>" if head else f"<p>{para(p)}</p>")
        first = False
    if not textual:
        return "".join(out)
    return '<div class="tile">' + "".join(out) + "</div>"


def merge(blocks):
    out, skip = [], set()
    for i, a in enumerate(blocks):
        if i in skip: continue
        if a["type"] == "text" and len(a["p"]) == 1 and len(txt(a)) < 30:
            j = next((k for k, b in enumerate(blocks) if k != i and k not in skip and b["type"] == "text" and abs(b["x"] - a["x"]) < 0.25 and 0 < b["y"] - a["y"] < 1.3), None)
            if j is not None:
                skip.add(j); out.append({"type": "card", "x": a["x"], "y": a["y"], "items": [a, blocks[j]]}); continue
        out.append(a)
    return sorted(out, key=lambda b: (round(b["y"] * 2), b["x"]))


def tabelle(rows, first_bold=True):
    h = "".join(f"<th>{esc(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join((f"<th scope=row>{esc(c)}</th>" if k == 0 and first_bold else f"<td>{esc(c)}</td>") for k, c in enumerate(r)) + "</tr>" for r in rows[1:])
    return f'<div class="tablewrap"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'


def slide_html(s):
    blocks = [b for b in s["blocks"]]
    tag = next((b for b in blocks if b["type"] == "text" and b["y"] < 0.5), None)
    blocks = [b for b in blocks if b is not tag]
    pill = next((b for b in blocks if b["type"] == "pill"), None)
    blocks = [b for b in blocks if b["type"] != "pill"]
    head = f'<div class="slidehead"><h3>{esc(s["title"])}</h3>'
    if tag: head += f'<span class="tag">{esc(txt(tag))}</span>'
    if pill: head += f'<span class="pill">{esc(pill["t"].replace("|", " "))}</span>'
    head += "</div>"
    body = []
    if s["i"] == 33:
        body.append(tabelle([["Bindung", "Wo / was?", "Stärke"], ["Metallbindung", "Kationen + Elektronengas", "echt · sehr stark"], ["Ionenbindung", "Ionengitter (Salze)", "echt · stark"],
                             ["Atombindung", "Moleküle", "echt · stark"], ["Wasserstoffbrücken", "H an O, N, F", "zwischen Molekülen · schwach"], ["Van-der-Waals-Kräfte", "alle Moleküle", "zwischen Molekülen · sehr schwach"]]))
    else:
        tiles = []
        def flush():
            if tiles: body.append('<div class="tiles">' + "".join(tiles) + "</div>"); tiles.clear()
        for b in merge(blocks):
            if b["type"] == "card":
                items = sorted(b["items"], key=lambda a: (1 if a.get("gif") else 0) if a["type"] == "img" else 0) if all(a["type"] == "img" for a in b["items"]) else b["items"]
                c = karte(items, s["title"])
                if c.startswith('<div class="tile">'): tiles.append(c)
                else: flush(); body.append(c)
                continue
            flush()
            if b["type"] == "img": body.append(bild(b, s["title"]))
            elif b["type"] == "table": body.append(tabelle(b["rows"]))
            elif b["type"] == "text":
                if len(b["p"]) > 1 or b.get("filled"): tiles.append(karte([b], s["title"]))
                else: body.append(f"<p>{para(b['p'][0])}</p>")
        flush()
    return f'<article class="slide" id="f{s["i"]}">{head}{"".join(body)}</article>'


# ---------- Abschnitte ----------
sections, cur = [], {"id": "einstieg", "label": "Einstieg", "title": "Worum geht es?", "slides": []}
for s in S:
    if s["i"] == 1 or s["i"] >= 36: continue
    if s["layout"] == "Abschnitt":
        sections.append(cur)
        lbl = txt(s["blocks"][0]) if s["blocks"] else ""
        n = lbl.split("·")[0].strip().replace("Teil ", "")
        cur = {"id": "teil" + n, "label": "Teil " + n, "eyebrow": lbl, "title": s["title"], "slides": []}
        continue
    if s["i"] == 33:
        sections.append(cur); cur = {"id": "ueberblick", "label": "Überblick", "title": "Zusammenfassung", "slides": []}
    cur["slides"].append(s)
sections.append(cur)

toc = "".join(f'<a href="#{x["id"]}">{esc(x["label"])}</a>' for x in sections) + '<a href="#weiter">Aufgaben</a>'
secs = []
for x in sections:
    eb = x.get("eyebrow") or x["label"]
    secs.append(f'<section class="part" id="{x["id"]}"><div class="band"><div class="eyebrow">{esc(eb)}</div><h2>{esc(x["title"])}</h2></div>'
                + "".join(slide_html(s) for s in x["slides"]) + "</section>")

page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Bindungsarten – Theorie</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,700&display=swap">
<style>
/* Layout: eine Spalte, Handy zuerst – wie Aufgaben und Quiz (Folienmaster-Farben, Tarnmuster-Ecke, Wappen, Smiley). Bewusst nur hell. */
:root {{
  --bg: #EEF3E4; --card: #FFFFFF; --ink: #1F2A1C; --olive: #3B4A2F; --green: #7FA83A; --teal: #2E7D8C;
  --muted: #5E6652; --line: #D3DCC2; --tile: #F4F7EE;
  --font-head: Cambria, "Source Serif 4", Georgia, serif; --font-body: Calibri, "Source Sans 3", "Segoe UI", sans-serif;
  color-scheme: light;
}}
* {{ box-sizing: border-box; }}
[hidden] {{ display: none !important; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 64px; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
html, body {{ background: var(--bg); color: var(--ink); }}
body {{ margin: 0; font-family: var(--font-body); font-size: 18px; line-height: 1.5; }}
img {{ max-width: 100%; height: auto; }}
.top {{ background: var(--card); position: relative; border-bottom: 1px solid var(--line); }}
.top .camo {{ position: absolute; left: 0; top: 0; width: 190px; pointer-events: none; }}
.top .logo {{ position: absolute; left: 8px; top: 6px; width: 52px; }}
.top-inner {{ max-width: 720px; margin: 0 auto; padding: 18px 16px 16px; min-height: 104px; display: flex; align-items: center; gap: 12px; }}
.top-text {{ margin-left: 150px; flex: 1; min-width: 0; }}
.eyebrow {{ font-weight: 700; font-size: 14px; color: var(--teal); letter-spacing: .04em; }}
h1 {{ font-family: var(--font-head); color: var(--olive); font-size: 34px; line-height: 1.05; margin: 2px 0 0; }}
.top .smiley {{ width: 64px; height: 64px; flex: 0 0 64px; }}
@media (max-width: 520px) {{
  .top .camo {{ width: 112px; }} .top .logo {{ width: 32px; left: 6px; top: 4px; }}
  .top-inner {{ padding-top: 54px; min-height: 0; }} .top-text {{ margin-left: 0; }} h1 {{ font-size: 30px; }}
  .top .smiley {{ width: 52px; height: 52px; flex-basis: 52px; }}
}}
nav.toc {{ position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--olive); }}
nav.toc div {{ max-width: 720px; margin: 0 auto; display: flex; gap: 6px; overflow-x: auto; padding: 8px 16px; scrollbar-width: none; }}
nav.toc a {{ flex: 0 0 auto; color: #fff; text-decoration: none; font-weight: 700; font-size: 15px; padding: 5px 12px; border-radius: 999px; border: 1.5px solid rgba(255,255,255,.45); }}
nav.toc a:hover, nav.toc a:focus-visible {{ background: #fff; color: var(--olive); outline: none; }}
main {{ max-width: 720px; margin: 0 auto; padding-inline: 16px; padding-block: 18px 56px; display: grid; gap: 22px; }}
.part {{ display: grid; gap: 14px; }}
.band {{ background: var(--olive); color: #fff; border-radius: 14px; padding: 16px 18px; }}
.band .eyebrow {{ color: #C9D3B0; }}
.band h2 {{ font-family: var(--font-head); font-size: 26px; line-height: 1.15; margin: 2px 0 0; text-wrap: balance; }}
.slide {{ background: var(--card); border-radius: 14px; padding: 16px; display: grid; gap: 12px; box-shadow: 0 2px 6px rgba(31,42,28,.10); min-width: 0; }}
.slidehead {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; }}
.slidehead h3 {{ font-family: var(--font-head); color: var(--olive); font-size: 22px; line-height: 1.2; margin: 0; flex: 1 1 220px; text-wrap: balance; }}
.pill {{ background: var(--teal); color: #fff; font-weight: 700; font-size: 14px; border-radius: 999px; padding: 3px 12px; white-space: nowrap; }}
.tag {{ font-size: 13px; font-weight: 700; color: var(--muted); border: 1.5px solid var(--muted); border-radius: 999px; padding: 1px 9px; }}
.slide p {{ margin: 0; }}
.slide strong {{ color: var(--olive); }}
.tiles {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }}
.tile {{ background: var(--tile); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; display: grid; gap: 4px; align-content: start; min-width: 0; }}
.tile h4 {{ margin: 0; font-size: 19px; color: var(--olive); }}
.fig {{ margin: 0; display: grid; justify-items: center; gap: 4px; }}
.fig img {{ border-radius: 10px; }}
.fig.anim figcaption {{ font-size: 13px; font-weight: 700; color: var(--muted); letter-spacing: .04em; text-transform: uppercase; }}
.tablewrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 16px; }}
th, td {{ text-align: left; vertical-align: top; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
thead th {{ background: #DDE3D0; color: var(--olive); font-size: 15px; }}
tbody th {{ color: var(--olive); }}
tr:last-child th, tr:last-child td {{ border-bottom: 0; }}
@media (max-width: 460px) {{ table {{ font-size: 15px; }} th, td {{ padding: 7px 7px; }} }}
.next {{ background: var(--card); border-radius: 14px; padding: 18px 16px; display: grid; gap: 12px; box-shadow: 0 2px 6px rgba(31,42,28,.12); }}
.next h2 {{ font-family: var(--font-head); color: var(--olive); margin: 0; font-size: 24px; }}
.btns {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }}
.btn {{ display: block; text-align: center; text-decoration: none; font-weight: 700; font-size: 19px; color: #fff; background: var(--olive); border-radius: 12px; padding: 14px 18px; }}
.btn.alt {{ background: var(--teal); }}
.btn:focus-visible {{ outline: 3px solid var(--teal); outline-offset: 2px; }}
.hint {{ color: var(--muted); font-size: 15px; margin: 0; }}
</style>
</head>
<body>
<header class="top">
  <img class="camo" alt="" src="data:image/png;base64,{CAMO}">
  <img class="logo" alt="BHAK Wappen" src="data:image/png;base64,{LOGO}">
  <div class="top-inner">
    <div class="top-text"><div class="eyebrow">NAWI · 2AB · K1.2 · Buch S. 19–28</div><h1>Die Bindungsarten</h1></div>
    <img class="smiley" alt="" src="data:image/png;base64,{SMILEY}">
  </div>
</header>
<nav class="toc" aria-label="Inhalt"><div>{toc}</div></nav>
<main>
{"".join(secs)}
<section class="next" id="weiter">
  <div class="eyebrow">Weiter geht's</div>
  <h2>Jetzt bist du dran</h2>
  <div class="btns"><a class="btn" href="aufgaben.html">Aufgaben A1–A10</a><a class="btn alt" href="quiz.html">Bindungs-Check (Quiz)</a></div>
  <p class="hint">Theorie zum Nachlesen im Schulbuch (Trauner) S. 19–28.</p>
</section>
</main>
</body>
</html>
"""
open(DST + "theorie.html", "w").write(page)
print(len(page) // 1024, "KB,", len(os.listdir(DST + "img")), "Bilder")
