"""Versuchsseite (versuche.html) für GitHub Pages aus den VS-Daten bauen."""
import base64, json, os, io, qrcode
from PIL import Image
SITE = "/home/claude/unterricht/2ab-nawi/k1-2-bindungen/"
URL = "https://stephanholzer12.github.io/unterricht/2ab-nawi/k1-2-bindungen/versuche.html"
src = open("ab_src.html").read()
css = src[src.index("<style>"):src.index("</style>") + 8]
extra = """<style>
details.vcard > summary { list-style: none; cursor: pointer; display: grid; gap: 6px; }
details.vcard > summary::-webkit-details-marker { display: none; }
details.vcard > summary::after { content: "Öffnen ▾"; justify-self: start; font-weight: 700; font-size: 15px; color: var(--teal); }
details.vcard[open] > summary::after { content: "Schließen ▴"; }
.vbody { display: grid; gap: 12px; margin-top: 6px; min-width: 0; }
h3 { margin: 6px 0 0; font-family: var(--font-head); color: var(--olive); font-size: 19px; }
.tag.kern { color: #fff; background: var(--olive); border-color: var(--olive); }
.tag.zusatz { color: var(--muted); }
.pill.book { background: #A33A2B; }
.warn { background: var(--rust-soft); border-left: 4px solid var(--rust); border-radius: 8px; padding: 10px 12px; color: var(--rust); }
.safety { border: 2px solid var(--rust); }
.safety h2 { color: var(--rust); }
.mat { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
.matitem { display: grid; gap: 4px; justify-items: center; text-align: center; font-size: 15px; background: var(--bg); border-radius: 10px; padding: 8px; }
.matitem img { width: 72px; height: auto; }
ol.steps, ul.steps { margin: 0; padding-left: 22px; display: grid; gap: 6px; }
.fig { margin: 0; display: grid; justify-items: center; }
.fig img { border-radius: 10px; border: 1px solid var(--line); }
.fieldwrap { display: grid; gap: 4px; }
.fieldwrap .q { font-size: 16px; color: var(--muted); }
.grp { font-weight: 700; font-size: 14px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin-top: 6px; }
.btns { display: flex; gap: 8px; flex-wrap: wrap; }
</style>"""
rd = lambda p: open(p).read().strip()
data = json.load(open("vs_data.json"))
q = qrcode.QRCode(border=2, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(URL); q.make()
b = io.BytesIO(); q.make_image(fill_color="#2C3424", back_color="white").save(b, format="PNG"); qrpng = b.getvalue()
Image.open(io.BytesIO(qrpng)).convert("RGB").resize((444, 444), Image.NEAREST).save("/home/claude/work/img/qr_versuche.png")
body = open("vs_body.html").read()
rep = {"__CAMO__": rd("/home/claude/w2/camo.b64"), "__LOGO__": rd("/home/claude/w2/logo.b64"), "__SMILEY__": rd("/home/claude/w2/smiley.b64"),
       "__QR__": base64.b64encode(qrpng).decode(), "__JSPDF__": "/* jsPDF 2.5.1 (MIT) */\n" + open("node_modules/jspdf/dist/jspdf.umd.min.js").read(),
       "__FONTR__": base64.b64encode(open("carlito-Regular.ttf", "rb").read()).decode(), "__FONTB__": base64.b64encode(open("carlito-Bold.ttf", "rb").read()).decode(),
       "__RANGES__": open("ranges.json").read(), "__DATA__": json.dumps(data, ensure_ascii=False)}
for k in ["__CAMO__", "__LOGO__", "__SMILEY__", "__QR__", "__FONTR__", "__FONTB__", "__RANGES__", "__DATA__", "__JSPDF__"]:
    body = body.replace(k, rep[k])
head = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,700&display=swap">\n'
page = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<meta name="robots" content="noindex">\n<title>Bindungs-Versuche</title>\n'
        + head + css + "\n" + extra + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
open(SITE + "versuche.html", "w").write(page)
os.makedirs(SITE + "vs-img", exist_ok=True)
used_i = {m[1] for v in data for m in v["mat"]}; used_d = {v["skizze"] for v in data}
for n in used_i:
    im = Image.open(f"/home/claude/work/wimg/i_{n}.png").convert("RGBA"); im.thumbnail((180, 120)); im.save(SITE + f"vs-img/i_{n}.png", optimize=True)
for n in used_d:
    im = Image.open(f"/home/claude/work/wimg/d_{n}.png").convert("RGB"); im.thumbnail((900, 700)); im.quantize(colors=128).save(SITE + f"vs-img/d_{n}.png", optimize=True)
print(len(page) // 1024, "KB;", len(used_i), "Icons,", len(used_d), "Skizzen")
