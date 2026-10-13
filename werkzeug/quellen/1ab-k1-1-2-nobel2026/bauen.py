"""Handy-Seiten für NAWI 1AB · K1.1.2 »Nobelpreise 2026« bauen.
Aufruf im Repository-Ordner:  python3 werkzeug/quellen/1ab-k1-1-2-nobel2026/bauen.py <inhalt-ordner> <jspdf.umd.min.js>
<inhalt-ordner> enthält inhalt.py und img/ (Grafiken, GIFs) – liegt mit den Lösungen im Lehrer-Paket, bewusst nicht im öffentlichen Repository. Schreibt 1ab-nawi/k1-1-2-nobel2026/{theorie,aufgaben,quiz}.html und img/.
Das Arbeitsblatt baut auf quellen/1ab-k1-2-2-koerper/aufgaben_src.html auf (gleiche Speicher-, PDF- und Kopierfunktion)."""
import base64, html, io, json, os, re, shutil, sys
import qrcode
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WZ = os.path.join(ROOT, "werkzeug")
SRC, JSPDF = sys.argv[1], sys.argv[2]
sys.path.insert(0, SRC)
import inhalt as I

UNIT = I.ORDNER + "/"
DST = os.path.join(ROOT, UNIT)
BASE = I.BASE
os.makedirs(DST + "img", exist_ok=True)
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
CAMO, LOGO, SMILEY = b64(WZ + "/camo.png"), b64(WZ + "/logo.png"), b64(WZ + "/smiley.png")
esc = html.escape
EYEBROW = I.EYEBROW
nb = lambda s: re.sub(r"(?<=\d) (?=\d{3}\b)", " ", s)
md = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(nb(s)))
plain = lambda s: nb(s).replace("**", "")


def qr_b64(url):
    q = qrcode.QRCode(border=2, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    b = io.BytesIO(); q.make_image(fill_color="#2C3424", back_color="white").save(b, format="PNG"); return base64.b64encode(b.getvalue()).decode()


def wrap(src):
    te = src.index("</title>") + 8; rest = src[te:]; bs = rest.index("<header")
    return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="robots" content="noindex">\n' + src[:te] + "\n" + rest[:bs] + "</head>\n<body>\n" + rest[bs:] + "\n</body>\n</html>\n")


# ---------------------------------------------------------------- Bilder (verkleinert für das Handy)
SZ = {}
for n in ["icecube.png", "spiegelbild.png", "alge.png"]:
    im = Image.open(os.path.join(SRC, "img", n)).convert("RGB")
    if im.width > 900: im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
    im.quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(DST + "img/" + n, optimize=True); SZ[n] = im.size
for n in ["neutrino.gif", "autokatalyse.gif", "optogenetik.gif"]:
    im = Image.open(os.path.join(SRC, "img", n)); frames, durs = [], []
    W = 640
    for k in range(im.n_frames):
        im.seek(k); fr = im.convert("RGB"); fr = fr.resize((W, round(fr.height * W / fr.width)), Image.LANCZOS)
        frames.append(fr.convert("P", palette=Image.ADAPTIVE, colors=96)); durs.append(im.info.get("duration", 120))
    frames[0].save(DST + "img/" + n, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True, disposal=2); SZ[n] = frames[0].size

# ---------------------------------------------------------------- Arbeitsblatt
def js_tasks():
    T = []
    for A in I.AUFGABEN:
        t = {"id": f"a{A['nr']}", "nr": A["nr"], "title": A["titel"], "src": A["quelle"], "h": A["std"], "q": nb(A["frage"])}
        if A["typ"] == "gaps":
            t["type"] = "gaps"; t["sents"] = [[p if isinstance(p, str) else p for p in s] for s in A["saetze"]]
        elif A["typ"] == "assign":
            t.update(type="assign", rows=A["zeilen"], cols=A["spalten"])
        elif A["typ"] == "choose":
            t.update(type="multichoose", opts=A["optionen"], items=A["items"], q=nb(A["frage"]) + " Tippe an.")
        elif A["typ"] == "choose1":
            t.update(type="choose", opts=A["optionen"], items=A["items"])
        elif A["typ"] == "order":
            t.update(type="order", items=A["items"])
        elif A["typ"] == "calc":
            t.update(type="multi", parts=[[k, q] for k, q in A["teile"]])
        elif A["typ"] == "myth":
            t.update(type="myth", items=A["items"], opts=["Mythos", "Fakt"])
        elif A["typ"] == "text":
            t.update(type="multi", parts=[["t", "Deine Bewertung (3 Sätze)"]])
        T.append(t)
    return json.dumps(T, ensure_ascii=False, indent=1)


RENDER_JS = r"""
function renderTask(t) {
  const card = el("section", { class: "card", id: "card_" + t.id });
  card.append(el("div", { class: "head" },
    el("span", { class: "nr" }, el("span", { class: "check", "aria-hidden": "true", text: "✓" }), "Aufgabe " + t.nr + " · Stunde " + t.h),
    el("span", { class: "pill theory", text: t.src })));
  card.append(el("h2", { text: t.title }));
  card.append(el("p", { class: "q", text: t.q }));
  const chips = (key, opts, multi, aria) => {
    const btns = opts.map(o => el("button", { class: "chip", type: "button", text: o, "aria-pressed": "false" }));
    const cur = () => A(t.id)[key];
    const paint = () => btns.forEach((b, oi) => b.setAttribute("aria-pressed", String(multi ? (cur() || []).includes(oi) : cur() === oi)));
    btns.forEach((b, oi) => b.addEventListener("click", () => {
      if (multi) { const a = (cur() || []).slice(); const k = a.indexOf(oi); if (k >= 0) a.splice(k, 1); else a.push(oi); A(t.id)[key] = a.sort(); }
      else A(t.id)[key] = cur() === oi ? undefined : oi;
      paint(); update(); save(); }));
    paint();
    return el("div", { class: "choose", role: "group", "aria-label": aria }, ...btns);
  };
  if (t.type === "gaps") {
    const box = el("div", { class: "rows" });
    t.sents.forEach((parts, si) => {
      const p = el("div", { class: "sent2" }); p.append((si + 1) + "  ");
      parts.forEach(part => { if (typeof part === "string") p.append(part); else p.append(input(t.id, "g" + part, { cls: "gap", aria: "Lücke " + (part + 1) })); });
      box.append(p);
    });
    card.append(box);
  }
  if (t.type === "assign") {
    const box = el("div", { class: "rows" });
    t.rows.forEach((r, i) => box.append(el("div", { class: "row" }, el("div", { class: "stoff", text: r }),
      ...t.cols.map((c, j) => labeled(t.id, "r" + i + "c" + j, c, { multi: j > 0 })))));
    card.append(box);
  }
  if (t.type === "multichoose" || t.type === "choose") {
    const box = el("div", { class: "rows" });
    t.items.forEach((it, i) => box.append(el("div", { class: "row" }, el("div", { text: it }), chips("c" + i, t.opts, t.type === "multichoose", it))));
    card.append(box);
  }
  if (t.type === "order") {
    const box = el("div", { class: "rows" });
    const nums = t.items.map((_, k) => String(k + 1));
    t.items.forEach((it, i) => box.append(el("div", { class: "row" }, el("div", { text: it }), el("div", {}, el("label", { class: "lbl", text: "Schritt Nr." }), select(t.id, "o" + i, nums, "Schritt Nr. für: " + it)))));
    card.append(box);
  }
  if (t.type === "myth") {
    const box = el("div", { class: "rows" });
    t.items.forEach((it, i) => box.append(el("div", { class: "row" }, el("div", { class: "stoff", text: "»" + it + "«" }), chips("c" + i, t.opts, false, it),
      labeled(t.id, "r" + i, "Begründung", {}))));
    card.append(box);
  }
  if (t.type === "multi") t.parts.forEach(([k, lab]) => card.append(labeled(t.id, k, lab, { multi: true })));
  return card;
}
"""

DONE_JS = r"""
function isDone(t) {
  const a = S.a[t.id] || {};
  if (t.type === "gaps") return t.sents.every(p => p.filter(x => typeof x !== "string").every(g => filled(a["g" + g])));
  if (t.type === "assign") return t.rows.every((_, i) => t.cols.every((_, j) => filled(a["r" + i + "c" + j])));
  if (t.type === "multichoose") return t.items.every((_, i) => (a["c" + i] || []).length > 0);
  if (t.type === "choose") return t.items.every((_, i) => a["c" + i] != null);
  if (t.type === "order") return t.items.every((_, i) => filled(a["o" + i]));
  if (t.type === "myth") return t.items.every((_, i) => a["c" + i] != null && filled(a["r" + i]));
  if (t.type === "multi") return t.parts.every(([k]) => filled(a[k]));
}
"""

LINES_JS = r"""
function answerLines(t) {
  const a = S.a[t.id] || {}, L = [];
  if (t.type === "gaps") t.sents.forEach((parts, si) => L.push((si + 1) + ". " + parts.map(p => typeof p === "string" ? p : "[" + v(a["g" + p]) + "]").join("")));
  if (t.type === "assign") t.rows.forEach((r, i) => L.push(r + ": " + t.cols.map((c, j) => c + " " + v(a["r" + i + "c" + j])).join(" · ")));
  if (t.type === "multichoose") t.items.forEach((it, i) => L.push(it + " → " + ((a["c" + i] || []).map(k => t.opts[k]).join(", ") || "?")));
  if (t.type === "choose") t.items.forEach((it, i) => L.push(it + ": " + (a["c" + i] != null ? t.opts[a["c" + i]] : "?")));
  if (t.type === "order") t.items.forEach((it, i) => L.push(v(a["o" + i]) + " – " + it));
  if (t.type === "myth") t.items.forEach((it, i) => L.push("»" + it + "«: " + (a["c" + i] != null ? t.opts[a["c" + i]] : "?") + " – " + v(a["r" + i])));
  if (t.type === "multi") t.parts.forEach(([k, lab]) => { L.push(lab); L.push("   " + (filled(a[k]) ? a[k].trim() : none)); });
  return L;
}
"""


def cut(src, start, end, new):
    a = src.index(start); b = src.index(end, a)
    return src[:a] + new + src[b:]


src = open(os.path.join(WZ, "quellen", "1ab-k1-2-2-koerper", "aufgaben_src.html"), encoding="utf-8").read()
src = src.replace("<title>Wie groß bist du wirklich? – Arbeitsblatt</title>", f"<title>{I.TITEL} – Arbeitsblatt</title>")
src = src.replace("NAWI · 1AB · K1.2.2 Messen und Messfehler", EYEBROW)
src = src.replace("<h1>Wie groß bist du wirklich?</h1>", f"<h1>{I.TITEL}</h1>")
src = src.replace("Stunde 1: Aufgaben 1–4 · Stunde 2: Aufgaben 5–10.", "Stunde 1: Aufgaben 1–4 · Stunde 2: Aufgaben 5–8.")
src = src.replace("Schulbuch (Trauner) S. 17–19", "Schulbuch (Trauner) S. 11–14")
src = src.replace('<span id="count">0 von 10 bearbeitet</span>', f'<span id="count">0 von {len(I.AUFGABEN)} bearbeitet</span>')
src = src.replace('const KEY = "26-27-1AB-K1.2.2-Koerper-UE-Handy-v1";', f'const KEY = "{I.PRE}-TH-Handy-v1";')
src = src.replace('const TITLE = "K1.2.2 Wie groß bist du wirklich?";', f'const TITLE = "{I.KAP} {I.TITEL}";')
src = cut(src, "const GERAETE", "// ---------- Zustand", "const T = " + js_tasks() + ";\n\n")
src = cut(src, "// ---------- Säulendiagramm zum Antippen ----------", "// ---------- Fortschritt ----------", RENDER_JS + "\n")
src = cut(src, "function isDone(t) {", "function update() {", DONE_JS.lstrip("\n").replace("function isDone", "function isDone", 1) + "")
src = cut(src, "function answerLines(t) {", "function asText() {", LINES_JS.lstrip("\n"))
src = src.replace('clean("NAWI · 1AB · K1.2.2 Messen und Messfehler · Schulbuch S. 17–19")', f'clean("{EYEBROW} · Schulbuch S. 11–14")')
src = src.replace('clean("Wie groß bist du wirklich?")', f'clean("{I.TITEL}")')
src = src.replace('clean("K1.2.2 Körpergröße · " + (S.name', f'clean("{I.KAP} {I.TITEL} · " + (S.name')
src = src.replace('const filename = "K1.2.2-Koerper-" + slug(S.name) + ".pdf";', f'const filename = "{I.KAP}-{I.THEMA}-" + slug(S.name) + ".pdf";')
# Tabellen-/Diagramm-Teil der PDF-Ausgabe wird nicht gebraucht (kein Diagramm-Typ), bleibt aber unschädlich
for bad in ["BINS[", "Körpergröße", "K1.2.2", "Wie groß"]:
    assert bad not in src.split("// ---------- PDF ----------")[0] or bad == "BINS[", bad
rep = {"__BASECSS__": None, "__CAMO__": CAMO, "__LOGO__": LOGO, "__SMILEY__": SMILEY,
       "__FONTR__": b64(WZ + "/schriften/carlito-Regular.ttf"), "__FONTB__": b64(WZ + "/schriften/carlito-Bold.ttf"),
       "__RANGES__": open(WZ + "/schriften/ranges.json").read().strip(), "__QR__": qr_b64(BASE + UNIT + "aufgaben.html"),
       "__JSPDF__": open(JSPDF, encoding="utf-8").read()}
tpl = open(os.path.join(WZ, "vorlagen", "aufgaben_K1.2_vorlage.html"), encoding="utf-8").read()
rep["__BASECSS__"] = tpl[tpl.index("<style>"):tpl.index("</style>") + 8]
for k, v_ in rep.items(): src = src.replace(k, v_)
src = src.replace("</style>\n\n<header", ".row .choose { margin-top: 4px; }\n</style>\n\n<header", 1)
assert not re.search(r"__[A-Z]+__", src)
open(DST + "aufgaben.html", "w", encoding="utf-8").write(wrap(src))

# ---------------------------------------------------------------- Quiz
qs = ",\n".join("  { t: %s, q: %s, a: %s, e: %s, p: %s }" % tuple(json.dumps(x, ensure_ascii=False) for x in (t, nb(q), [nb(z) for z in a], nb(e), p)) for t, q, a, e, p in I.QUIZ)
qv = open(os.path.join(WZ, "vorlagen", "quiz_vorlage.html"), encoding="utf-8").read()
qv = qv.replace("<title>Bindungs-Check</title>", "<title>Nobel-Check – Quiz</title>")
qv = qv.replace("NAWI · 2AB · K1.2 Die Bindungsarten", EYEBROW)
qv = qv.replace("<h1>Bindungs-Check</h1>", "<h1>Nobel-Check</h1>").replace("<h2>Bindungs-Check am Handy</h2>", "<h2>Nobel-Check am Handy</h2>")
qv = qv.replace('alt="QR-Code zum Bindungs-Check"', 'alt="QR-Code zum Nobel-Check"')
qv = qv.replace('Frage 1 von 16', f'Frage 1 von {len(I.QUIZ)}')
a, b = qv.index("const Q = ["), qv.index("];", qv.index("const Q = [")) + 2
qv = qv[:a] + "const Q = [\n" + qs + "\n];" + qv[b:]
qv = qv.replace("if (p >= 13) return", f"if (p >= {len(I.QUIZ) - 3}) return").replace("if (p >= 9) return", f"if (p >= {len(I.QUIZ) // 2 + 2}) return")
if "[hidden]" not in qv: qv = qv.replace("<style>", "<style>\n[hidden] { display: none !important; }", 1)
for k, v_ in {"__CAMO__": CAMO, "__LOGO__": LOGO, "__SMILEY__": SMILEY, "__QR__": qr_b64(BASE + UNIT + "quiz.html")}.items(): qv = qv.replace(k, v_)
assert not re.search(r"__[A-Z]+__", qv) and "Bindung" not in qv
open(DST + "quiz.html", "w", encoding="utf-8").write(wrap(qv))
QUIZ_STANDALONE = wrap(qv)

# ---------------------------------------------------------------- Lernseite
def fig(name, alt, anim=False, cap=None):
    w, h = SZ[name]
    c = f'<figcaption>{esc(cap)}</figcaption>' if cap else ('<figcaption>Animation</figcaption>' if anim else "")
    return f'<figure class="fig{" anim" if anim else ""}"><img src="img/{name}" width="{w}" height="{h}" loading="lazy" alt="{esc(alt)}">{c}</figure>'

def slide(title, body, pill=None):
    head = f'<div class="slidehead"><h3>{esc(title)}</h3>' + (f'<span class="pill">{esc(pill)}</span>' if pill else "") + "</div>"
    return f'<article class="slide">{head}{body}</article>'

def tiles(items):
    return '<div class="tiles">' + "".join(f'<div class="tile"><h4>{esc(h)}</h4>{"".join("<p>" + md(x) + "</p>" for x in (b if isinstance(b, list) else [b]) if x)}</div>' for h, b in items) + "</div>"

def table(rows):
    h = "".join(f"<th>{esc(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join((f"<th scope=row>{md(c)}</th>" if k == 0 else f"<td>{md(c)}</td>") for k, c in enumerate(r)) + "</tr>" for r in rows[1:])
    return f'<div class="tablewrap"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'

ul = lambda xs: "<ul class=\"pts\">" + "".join(f"<li>{md(x)}</li>" for x in xs) + "</ul>"
ol = lambda xs: "<ol class=\"goals\">" + "".join(f"<li>{md(x)}</li>" for x in xs) + "</ol>"
merke = lambda s: f'<div class="merke">{md(s)}</div>'
fuss = lambda s: f'<p class="hint">{md(s)}</p>'
ALT = {"icecube.png": "Schnitt durch das Eis am Südpol: 86 Kabel mit Lichtsensoren zwischen 1450 und 2450 m Tiefe",
       "neutrino.gif": "Animation: Ein Neutrino trifft im Eis einen Atomkern, ein blauer Lichtblitz breitet sich aus, die Sensoren leuchten auf",
       "spiegelbild.png": "Ein Kohlenstoffatom mit vier verschiedenen Partnern und daneben sein Spiegelbild",
       "autokatalyse.gif": "Animation: Säulen für Form A und Form B – aus 52 zu 48 Prozent werden 99,5 zu 0,5 Prozent",
       "alge.png": "Grünalge Chlamydomonas mit zwei Geißeln, Chloroplast und rotem Augenfleck",
       "optogenetik.gif": "Animation: Blaues Licht öffnet einen Kanal in der Zellmembran, Ionen strömen hinein, ein elektrisches Signal entsteht"}


def th_html(f):
    a = f["art"]; P = f.get("pill")
    if a == "einstieg_story":
        h, paras = f["story"]; h2, ms = f["mythen"]
        return slide(f["titel"], tiles([(h, paras)]) + f'<div class="tile myth"><h4>{esc(h2)}</h4>{ol(ms)}</div>'
                     + '<details class="reveal"><summary>Auflösung anzeigen</summary>'
                     + "".join(f"<p><strong>{k + 1} {esc(m)}</strong> – {esc(plain(s))}</p>" for k, (m, s) in enumerate(I.AUFGABEN[6]["loesung"][:3])) + "</details>")
    if a == "karten":
        return slide(f["titel"], tiles(f["karten"]) + (merke(f["merke"]) if f.get("merke") else "") + (fuss(f["fuss"]) if f.get("fuss") else ""), P)
    if a == "text_karte":
        return slide(f["titel"], ul(f["text"]) + tiles([f["karte"]]), P)
    if a == "text_zahl":
        z, t = f["zahl"]
        return slide(f["titel"], ul(f["text"]) + f'<div class="stat"><b>{esc(z)}</b><span>{md(t)}</span></div>', P)
    if a in ("text_bild", "bild_text"):
        return slide(f["titel"], fig(f["bild"], ALT[f["bild"]], anim=f.get("animiert", False)) + ul(f["text"]) + (merke(f["merke"]) if f.get("merke") else ""), P)
    if a == "schritte":
        return slide(f["titel"], ol(f["schritte"]) + (merke(f["merke"]) if f.get("merke") else ""), P)
    if a == "schritte_bild":
        return slide(f["titel"], fig(f["bild"], ALT[f["bild"]], anim=True) + ol(f["schritte"]) + (merke(f["merke"]) if f.get("merke") else ""), P)
    if a == "zeitleiste":
        return slide(f["titel"], table([["Jahr", "Entdeckung"]] + [[y, t] for y, t in f["punkte"]]) + merke(f["merke"]) + fuss(f["fuss"]), P)
    if a == "zahlen":
        return slide(f["titel"], "".join(f'<div class="stat"><b>{esc(z)}</b><span>{md(t)}</span></div>' for z, t in f["zahlen"]) + merke(f["merke"]), P)
    if a == "tabelle":
        return slide(f["titel"], table(f["tabelle"]) + (merke(f["merke"]) if f.get("merke") else ""), P)
    raise ValueError(a)


parts, cur, labels = [], None, []
for f in I.TH:
    if f["art"] == "ziele":
        cur[2].append(slide("Das kannst du nach dieser Einheit", ol(I.LERNZIELE))); continue
    if f["art"] == "abschnitt":
        cur = [f"teil{len(parts)}", f["eyebrow"], [], f["titel"]]; parts.append(cur); continue
    if cur is None:
        cur = ["einstieg", "Einstieg", [], "Worum geht es?"]; parts.append(cur)
    cur[2].append(th_html(f))
parts.append(["begriffe", "Zum Nachschlagen", [slide("Fachbegriffe · " + lab, table(rows)) for lab, rows in I.FACHBEGRIFFE], "Fachbegriffe"])
TOCLAB = {"einstieg": "Einstieg", "begriffe": "Begriffe"}
toc = "".join(f'<a href="#{p[0]}">{esc(TOCLAB.get(p[0], p[1].split(" · ")[0] if p[0] != "teil5" else "Teil 5"))}</a>' for p in parts) + '<a href="#weiter">Aufgaben</a>'
body = "".join(f'<section class="part" id="{p[0]}"><div class="band"><div class="eyebrow">{esc(p[1])}</div><h2>{esc(p[3])}</h2></div>{"".join(p[2])}</section>' for p in parts)
bt = open(os.path.join(WZ, "vorlagen", "build_theorie.py"), encoding="utf-8").read()
tcss = bt[bt.index("<style>"):bt.index("</style>") + 8].replace("{{", "{").replace("}}", "}")
tcss = tcss.replace("</style>", """.merke { background: var(--olive); color: #fff; border-radius: 12px; padding: 12px 14px; }
.merke strong { color: #C9D8A8; }
ol.goals, ul.pts { margin: 0; padding-left: 24px; display: grid; gap: 6px; }
details.reveal { border: 2px solid #D9772B; border-radius: 12px; padding: 10px 14px; }
details.reveal summary { cursor: pointer; font-weight: 700; color: #D9772B; }
details.reveal p { margin: 8px 0 0; }
.tile.myth { border: 2px solid #D9772B; }
.stat { background: #2E7D8C; color: #fff; border-radius: 12px; padding: 12px 14px; display: grid; gap: 4px; }
.stat b { font-family: Cambria, "Source Serif 4", Georgia, serif; font-size: 28px; }
.stat strong { color: #fff; }
</style>""")
page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>{esc(I.TITEL)} – Lernseite</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,700&display=swap">
{tcss}
</head>
<body>
<header class="top">
  <img class="camo" alt="" src="data:image/png;base64,{CAMO}">
  <img class="logo" alt="BHAK Wappen" src="data:image/png;base64,{LOGO}">
  <div class="top-inner">
    <div class="top-text"><div class="eyebrow">{esc(EYEBROW)} · {esc(I.BUCH)}</div><h1>{esc(I.TITEL)}</h1></div>
    <img class="smiley" alt="" src="data:image/png;base64,{SMILEY}">
  </div>
</header>
<nav class="toc" aria-label="Inhalt"><div>{toc}</div></nav>
<main>
{body}
<section class="next" id="weiter">
  <div class="eyebrow">Weiter geht's</div>
  <h2>Jetzt bist du dran</h2>
  <div class="btns"><a class="btn" href="aufgaben.html">Arbeitsblatt A1–A{len(I.AUFGABEN)}</a><a class="btn alt" href="quiz.html">Nobel-Check (Quiz)</a></div>
  <p class="hint">Theorie zum Nachlesen im Schulbuch (Trauner) S. 11–14, 29, 115, 129, 140, 164. Grafiken und Animationen: selbst erstellt.</p>
</section>
</main>
</body>
</html>
"""
open(DST + "theorie.html", "w", encoding="utf-8").write(page)
# Quiz zusätzlich als einzelne Datei für das Unterrichtspaket
if len(sys.argv) > 3: open(sys.argv[3], "w", encoding="utf-8").write(QUIZ_STANDALONE)
for f in ["theorie.html", "aufgaben.html", "quiz.html"]:
    print(f, os.path.getsize(DST + f) // 1024, "KB")
