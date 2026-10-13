"""Übersichtsseiten aus einheiten.json erzeugen. Aufruf im Repository-Ordner: python3 werkzeug/build_index.py

- Pro Klasse eine eigene Übersicht: <klasse>-<fach>/index.html (z. B. 2ab-nawi/index.html) – nur diese Klasse sieht ihre Einheiten.
- Die Startseite index.html verlinkt KEINE Klassen (damit keine Klasse die Seiten der anderen sieht).
"""
import json, html, os, base64
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = json.load(open(os.path.join(ROOT, "werkzeug", "einheiten.json"), encoding="utf-8"))
LOGO = base64.b64encode(open(os.path.join(ROOT, "werkzeug", "logo.png"), "rb").read()).decode()
NAMEN = {"theorie.html": ("Theorie", "alt"), "aufgaben.html": ("Aufgaben", ""), "quiz.html": ("Quiz", ""), "projekt.html": ("Projekt", ""), "versuche.html": ("Versuche", ""), "gruppe.html": ("Gruppe", "")}
esc = html.escape

CSS = """
:root { --bg: #EEF3E4; --card: #FFFFFF; --ink: #1F2A1C; --olive: #3B4A2F; --teal: #2E7D8C; --muted: #5E6652; color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: Calibri, "Segoe UI", sans-serif; font-size: 18px; line-height: 1.45; }
main { max-width: 680px; margin: 0 auto; padding-inline: 16px; padding-block: 24px 48px; display: grid; gap: 12px; }
header { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
header img { width: 48px; height: auto; }
h1 { font-family: Cambria, Georgia, serif; color: var(--olive); margin: 0; font-size: 30px; }
.eyebrow { font-weight: 700; font-size: 14px; color: var(--teal); letter-spacing: .04em; }
section { background: var(--card); border-radius: 14px; padding: 14px 16px; box-shadow: 0 2px 6px rgba(31,42,28,.12); display: grid; gap: 8px; }
h3 { margin: 0; font-family: Cambria, Georgia, serif; color: var(--olive); font-size: 21px; }
.links { display: flex; flex-wrap: wrap; gap: 8px; }
a.btn { text-decoration: none; font-weight: 700; color: #fff; background: var(--olive); border-radius: 10px; padding: 9px 16px; }
a.btn.alt { background: var(--teal); }
a.btn:focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; }
p.note { margin: 12px 0 0; color: var(--muted); font-size: 15px; }
"""


def seite(titel, eyebrow, inhalt, logo_prefix=""):
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>{esc(titel)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
  <header><img alt="BHAK Wappen" src="data:image/png;base64,{LOGO}"><div><div class="eyebrow">{esc(eyebrow)}</div><h1>{esc(titel)}</h1></div></header>
  {inhalt}
</main>
</body>
</html>
"""


gruppen = {}
for e in E:
    gruppen.setdefault(e["ordner"].split("/")[0], []).append(e)

for ordner, es in gruppen.items():
    karten = []
    for e in es:
        unter = e["ordner"].split("/", 1)[1]
        links = "".join(f'<a class="btn {NAMEN.get(s, (s, ""))[1]}" href="{esc(unter)}/{s}">{esc(NAMEN.get(s, (s, ""))[0])}</a>' for s in e["seiten"])
        karten.append(f'<section><div class="eyebrow">{esc(e["kapitel"])}</div><h3>{esc(e["titel"])}</h3><div class="links">{links}</div></section>')
    k = es[0]
    inhalt = "".join(karten) + '<p class="note">Antworten bleiben nur auf deinem Handy gespeichert. Abgabe als PDF in LMS.</p>'
    open(os.path.join(ROOT, ordner, "index.html"), "w", encoding="utf-8").write(
        seite(f'{k["fach"]} {k["klasse"]}', "BHAK für Führung und Sicherheit · Unterricht am Handy", inhalt))
    print(ordner + "/index.html:", len(es), "Einheit(en)")

start = '<section><h3>Hallo!</h3><p style="margin:0">Scanne den QR-Code deiner Klasse oder öffne den Link aus LMS, um zu deinen Seiten zu kommen.</p></section>'
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(seite("Unterricht am Handy", "BHAK für Führung und Sicherheit", start))
print("index.html: Startseite ohne Klassenliste")
