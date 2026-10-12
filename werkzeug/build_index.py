"""Übersichtsseite (index.html) aus einheiten.json erzeugen. Aufruf im Repository-Ordner: python3 werkzeug/build_index.py"""
import json, html, os, base64
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(ROOT, "werkzeug", "einheiten.json"), encoding="utf-8"))
LOGO = base64.b64encode(open(os.path.join(ROOT, "werkzeug", "logo.png"), "rb").read()).decode()
NAMEN = {"theorie.html": ("Theorie", "alt"), "aufgaben.html": ("Aufgaben", ""), "quiz.html": ("Quiz", "")}
esc = html.escape
gruppen = {}
for e in E: gruppen.setdefault(f'{e["klasse"]} · {e["fach"]}', []).append(e)
blocks = []
for g, es in gruppen.items():
    karten = []
    for e in es:
        links = "".join(f'<a class="btn {NAMEN.get(s, (s, ""))[1]}" href="{esc(e["ordner"])}/{s}">{esc(NAMEN.get(s, (s, ""))[0])}</a>' for s in e["seiten"])
        karten.append(f'<section><div class="eyebrow">{esc(e["kapitel"])}</div><h3>{esc(e["titel"])}</h3><div class="links">{links}</div></section>')
    blocks.append(f'<h2>{esc(g)}</h2>' + "".join(karten))
page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unterricht am Handy</title>
<style>
:root {{ --bg: #EEF3E4; --card: #FFFFFF; --ink: #1F2A1C; --olive: #3B4A2F; --teal: #2E7D8C; --muted: #5E6652; color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Calibri, "Segoe UI", sans-serif; font-size: 18px; line-height: 1.45; }}
main {{ max-width: 680px; margin: 0 auto; padding-inline: 16px; padding-block: 24px 48px; display: grid; gap: 12px; }}
header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }}
header img {{ width: 48px; height: auto; }}
h1 {{ font-family: Cambria, Georgia, serif; color: var(--olive); margin: 0; font-size: 30px; }}
h2 {{ font-family: Cambria, Georgia, serif; color: var(--olive); margin: 14px 0 0; font-size: 22px; border-bottom: 2px solid var(--olive); padding-bottom: 4px; }}
.eyebrow {{ font-weight: 700; font-size: 14px; color: var(--teal); letter-spacing: .04em; }}
section {{ background: var(--card); border-radius: 14px; padding: 14px 16px; box-shadow: 0 2px 6px rgba(31,42,28,.12); display: grid; gap: 8px; }}
h3 {{ margin: 0; font-family: Cambria, Georgia, serif; color: var(--olive); font-size: 21px; }}
.links {{ display: flex; flex-wrap: wrap; gap: 8px; }}
a.btn {{ text-decoration: none; font-weight: 700; color: #fff; background: var(--olive); border-radius: 10px; padding: 9px 16px; }}
a.btn.alt {{ background: var(--teal); }}
a.btn:focus-visible {{ outline: 3px solid var(--teal); outline-offset: 2px; }}
p.note {{ margin: 12px 0 0; color: var(--muted); font-size: 15px; }}
</style>
</head>
<body>
<main>
  <header><img alt="BHAK Wappen" src="data:image/png;base64,{LOGO}"><div><div class="eyebrow">BHAK für Führung und Sicherheit</div><h1>Unterricht am Handy</h1></div></header>
  {"".join(blocks)}
  <p class="note">Antworten bleiben nur auf deinem Handy gespeichert. Abgabe als PDF in LMS.</p>
</main>
</body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
print("index.html:", len(E), "Einheit(en)")
