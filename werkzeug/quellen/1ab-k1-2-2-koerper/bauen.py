"""Handy-Seiten für NAWI 1AB · K1.2.2 »Messen wie die Profis« bauen (Doppelstunde: Länge, Schätzen, Körpergröße, Messfehler, Reaktionszeit).
Aufruf im Repository-Ordner:  python3 werkzeug/quellen/1ab-k1-2-2-koerper/bauen.py <bilder-ordner> <jspdf.min.js>
Schreibt 1ab-nawi/k1-2-2-koerper/{theorie,aufgaben,quiz}.html und img/."""
import base64, html, io, json, os, re, shutil, sys
import qrcode
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WZ = os.path.join(ROOT, "werkzeug")
IMGSRC, JSPDF = sys.argv[1], sys.argv[2]
UNIT = "1ab-nawi/k1-2-2-koerper/"
DST = os.path.join(ROOT, UNIT)
BASE = "https://stephanholzer12.github.io/unterricht/"
os.makedirs(DST + "img", exist_ok=True)
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
CAMO, LOGO, SMILEY = b64(WZ + "/camo.png"), b64(WZ + "/logo.png"), b64(WZ + "/smiley.png")
esc = html.escape
EYEBROW = "NAWI · 1AB · K1.2.2 Messen und Messfehler"


def qr_b64(url):
    q = qrcode.QRCode(border=2, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    b = io.BytesIO(); q.make_image(fill_color="#2C3424", back_color="white").save(b, format="PNG"); return base64.b64encode(b.getvalue()).decode()


def wrap(src):
    """Vollständiger Dokumentrahmen um eine Quelle, die mit <title> beginnt und deren Körper mit <header startet."""
    te = src.index("</title>") + 8; rest = src[te:]; bs = rest.index("<header")
    return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="robots" content="noindex">\n' + src[:te] + "\n" + rest[:bs] + "</head>\n<body>\n" + rest[bs:] + "\n</body>\n</html>\n")


# ---------------------------------------------------------------- Bilder
def png(name, maxw=900):
    im = Image.open(os.path.join(IMGSRC, name)).convert("RGB")
    if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.quantize(colors=96, method=Image.Quantize.MEDIANCUT).save(DST + "img/" + name, optimize=True)
    return im.size
SZ = {n: png(n) for n in ["ziel_zufaellig.png", "ziel_systematisch.png", "lineal.png"]}
shutil.copy(os.path.join(IMGSRC, "diagramm.gif"), DST + "img/diagramm.gif")
shutil.copy(os.path.join(IMGSRC, "formel_weiss.png"), DST + "img/formel.png")
SZ["formel.png"] = Image.open(DST + "img/formel.png").size
SZ["diagramm.gif"] = Image.open(DST + "img/diagramm.gif").size

# ---------------------------------------------------------------- Arbeitsblatt
tpl = open(os.path.join(WZ, "vorlagen", "aufgaben_K1.2_vorlage.html"), encoding="utf-8").read()
css = tpl[tpl.index("<style>"):tpl.index("</style>") + 8]
src = open(os.path.join(HERE, "aufgaben_src.html"), encoding="utf-8").read()
rep = {"__BASECSS__": css, "__CAMO__": CAMO, "__LOGO__": LOGO, "__SMILEY__": SMILEY,
       "__FONTR__": b64(WZ + "/schriften/carlito-Regular.ttf"), "__FONTB__": b64(WZ + "/schriften/carlito-Bold.ttf"),
       "__RANGES__": open(WZ + "/schriften/ranges.json").read().strip(), "__QR__": qr_b64(BASE + UNIT + "aufgaben.html"),
       "__JSPDF__": open(JSPDF, encoding="utf-8").read()}
for k, v in rep.items(): src = src.replace(k, v)
assert not re.search(r"__[A-Z]+__", src)
open(DST + "aufgaben.html", "w", encoding="utf-8").write(wrap(src))

# ---------------------------------------------------------------- Quiz
Q = [
    ("Länge", "In welcher Einheit wird die Länge im SI angegeben?", ["Meter (m)", "Zentimeter (cm)", "Kilogramm (kg)", "Sekunde (s)"],
     "Die Länge ist eine der 7 Grundgrößen. Ihre SI-Einheit ist der Meter. Zentimeter und Millimeter sind Teile davon.", "Buch S. 19"),
    ("Länge", "Wie ist der Meter seit 1983 festgelegt?", ["Über die Strecke, die Licht in 1/299 792 458 Sekunde zurücklegt", "Über einen Metallstab in Paris", "Über die Länge eines Fußes", "Über den Umfang der Erde"],
     "Früher galt ein Metallstab in Paris (Urmeter). Heute ist der Meter über die Lichtgeschwindigkeit festgelegt – das ist überall auf der Welt gleich genau.", "Buch S. 19"),
    ("Messgeräte", "Womit misst du den Durchmesser einer Patrone (5,56 mm) am besten?", ["Messschieber", "Maßband", "Laser-Entfernungsmesser", "Meterstab"],
     "Der Messschieber misst Längen zwischen 1 mm und 10 cm auf 0,1 mm genau. Ein Maßband ist dafür zu grob.", "Buch S. 19"),
    ("Messgeräte", "Wie misst man die Entfernung zum Mond?", ["Ein Laser misst die Laufzeit des Lichts zu einem Spiegel am Mond und zurück.", "Mit einem sehr langen Maßband", "Mit einem Messschieber", "Man kann sie nur schätzen."],
     "Das ist eine indirekte Messung: Aus der Laufzeit (ca. 2,5 s hin und zurück) berechnet man die Entfernung – rund 384 000 km.", "Buch S. 19"),
    ("Schätzen", "Du solltest 10 cm zeichnen, gemessen sind 8,7 cm. Wie groß ist die Abweichung?", ["−1,3 cm", "+1,3 cm", "18,7 cm", "0,87 cm"],
     "Abweichung = gemessen − Ziel = 8,7 − 10 = −1,3 cm. Das Minus zeigt: Der Strich war zu kurz.", "Buch S. 17"),
    ("Genauigkeit", "Dein Maßband hat eine mm-Einteilung. Welches Ergebnis ist sinnvoll angegeben?", ["174,3 cm", "174,32 cm", "174,318 cm", "170 cm"],
     "Auf 1 mm genau heißt: eine Kommastelle bei cm. Mehr Kommastellen wären Scheingenauigkeit – so genau misst kein Maßband.", "Buch S. 17"),
    ("Mittelwert", "Annas Messwerte: 165,9 cm – 166,1 cm – 166,0 cm. Wie groß ist der Mittelwert?", ["166,0 cm", "166,1 cm", "498,0 cm", "165,9 cm"],
     "Alle Werte zusammenzählen und durch 3 teilen: 498,0 : 3 = 166,0 cm.", "Buch S. 17"),
    ("Messunsicherheit", "Lukas: 174,2 cm – 174,6 cm – 174,3 cm. Wie groß ist die Messunsicherheit?", ["± 0,2 cm", "± 0,4 cm", "± 0,1 cm", "± 174,4 cm"],
     "(größter − kleinster Wert) : 2 = (174,6 − 174,2) : 2 = 0,2 cm. Ergebnis: 174,4 cm ± 0,2 cm.", "Buch S. 17"),
    ("Messfehler", "Ein Kadett liest einmal schräg von oben ab. Welcher Fehler ist das?", ["ein zufälliger Fehler – der Mittelwert gleicht ihn aus", "ein systematischer Fehler", "gar kein Fehler", "ein Rechenfehler"],
     "Schräg ablesen passiert mal so, mal so – mal zu groß, mal zu klein. Mehrmals messen und den Mittelwert bilden hilft.", "Buch S. 17"),
    ("Messfehler", "Alle Kadetten wurden mit Schuhen gemessen. Was stimmt?", ["Alle Werte sind etwa 2–3 cm zu groß – der Mittelwert hilft nicht.", "Der Mittelwert gleicht das aus.", "Alle Werte sind zu klein.", "Das spielt keine Rolle."],
     "Ein systematischer Fehler verschiebt alle Werte in dieselbe Richtung. Da hilft nur: Ursache beheben – Schuhe aus!", "Buch S. 17"),
    ("Schießstand", "Am Schießstand liegen alle Treffer eng beisammen, aber rechts oben. Was ist die Ursache?", ["ein systematischer Fehler – das Visier ist verstellt", "zufällige Fehler – mehr schießen hilft", "Der Schütze zittert.", "Die Scheibe ist zu klein."],
     "Eng beisammen heißt: kaum zufällige Fehler. Dass alle Treffer daneben liegen, ist systematisch. Das Visier muss eingestellt werden.", "Buch S. 17"),
    ("Mythos oder Fakt?", "Warum bist du am Morgen etwas größer als am Abend?", ["Tagsüber drückt das Körpergewicht die Bandscheiben zusammen.", "Du wächst jede Nacht 2 cm.", "Das Maßband dehnt sich am Abend.", "Am Morgen steht man auf Zehenspitzen."],
     "Die Bandscheiben zwischen den Wirbeln werden tagsüber zusammengedrückt und erholen sich im Liegen. Der Unterschied beträgt ca. 1–2 cm.", "Buch S. 17"),
    ("Faktencheck", "„+2 cm in 2 Wochen!“ – vorher abends, nachher morgens gemessen. Was folgt daraus?", ["Der Unterschied kann allein von der Uhrzeit kommen – das beweist nichts.", "Die Einlagen wirken sicher.", "Morgens misst man immer falsch.", "2 cm kann man nicht messen."],
     "Ein fairer Vergleich braucht gleiche Bedingungen: gleiche Uhrzeit, ohne Schuhe, mehrmals messen, viele Personen mit und ohne Einlagen.", "Buch S. 17"),
    ("Reaktionszeit", "Deine Fallwege: 14 cm – 18 cm – 15 cm. Wie groß ist deine Reaktionszeit laut Tabelle (15 cm → 0,17 s, 17,5 cm → 0,19 s)?", ["ca. 0,18 s", "ca. 0,47 s", "ca. 0,10 s", "ca. 1,5 s"],
     "Mittelwert h = (14 + 18 + 15) : 3 = 15,7 cm. Der Wert liegt zwischen 15 und 17,5 cm, also t ≈ 0,18 s.", "Buch S. 18"),
    ("Reaktionszeit", "Bei 50 km/h fährt ein Auto ca. 14 m pro Sekunde. Wie weit fährt es ungebremst, wenn du 2 s aufs Handy schaust?", ["ca. 28 m", "ca. 3 m", "ca. 14 cm", "ca. 100 m"],
     "2 s · 14 m pro Sekunde = 28 m – so lang wie ein Klassenzimmer-Trakt. Dazu kommt noch der Bremsweg.", "Buch S. 18"),
    ("Auswerten", "Größte Person 186,2 cm, kleinste 157,4 cm. Wie groß ist die Spannweite?", ["28,8 cm", "343,6 cm", "171,8 cm", "186,2 cm"],
     "Spannweite = größter − kleinster Wert = 186,2 − 157,4 = 28,8 cm. Sie zeigt, wie weit die Werte auseinanderliegen.", "Buch S. 17"),
    ("Auswerten", "Wohin gehört ein Mittelwert von 170,0 cm in der Strichliste?", ["in den Bereich 170–174,9 cm", "in den Bereich 165–169,9 cm", "in beide Bereiche", "in keinen Bereich"],
     "165–169,9 cm endet knapp vor 170. Ab 170,0 cm beginnt der nächste Bereich.", "Buch S. 17"),
]
qs = ",\n".join("  { t: %s, q: %s, a: %s, e: %s, p: %s }" % (json.dumps(t, ensure_ascii=False), json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False), json.dumps(e, ensure_ascii=False), json.dumps(p, ensure_ascii=False)) for t, q, a, e, p in Q)
qv = open(os.path.join(WZ, "vorlagen", "quiz_vorlage.html"), encoding="utf-8").read()
qv = qv.replace("<title>Bindungs-Check</title>", "<title>Mess-Check – Quiz</title>")
qv = qv.replace("NAWI · 2AB · K1.2 Die Bindungsarten", EYEBROW)
qv = qv.replace("<h1>Bindungs-Check</h1>", "<h1>Mess-Check</h1>").replace("<h2>Bindungs-Check am Handy</h2>", "<h2>Mess-Check am Handy</h2>")
qv = qv.replace('alt="QR-Code zum Bindungs-Check"', 'alt="QR-Code zum Mess-Check"')
qv = qv.replace('Frage 1 von 16', f'Frage 1 von {len(Q)}')
a, b = qv.index("const Q = ["), qv.index("];", qv.index("const Q = [")) + 2
qv = qv[:a] + "const Q = [\n" + qs + "\n];" + qv[b:]
qv = qv.replace("if (p >= 13) return", f"if (p >= {len(Q) - 3}) return").replace("if (p >= 9) return", f"if (p >= {len(Q) // 2 + 2}) return")
if "[hidden]" not in qv: qv = qv.replace("<style>", "<style>\n[hidden] { display: none !important; }", 1)
for k, v in {"__CAMO__": CAMO, "__LOGO__": LOGO, "__SMILEY__": SMILEY, "__QR__": qr_b64(BASE + UNIT + "quiz.html")}.items(): qv = qv.replace(k, v)
assert not re.search(r"__[A-Z]+__", qv) and "Bindung" not in qv
open(DST + "quiz.html", "w", encoding="utf-8").write(wrap(qv))

# ---------------------------------------------------------------- Lernseite
def fig(name, alt, anim=False, cap=None):
    w, h = SZ[name]
    c = f'<figcaption>{esc(cap)}</figcaption>' if cap else ('<figcaption>Animation</figcaption>' if anim else "")
    return f'<figure class="fig{" anim" if anim else ""}"><img src="img/{name}" width="{w}" height="{h}" loading="lazy" alt="{esc(alt)}">{c}</figure>'

def slide(title, body, pill=None, tag=None):
    head = f'<div class="slidehead"><h3>{esc(title)}</h3>' + (f'<span class="tag">{esc(tag)}</span>' if tag else "") + (f'<span class="pill">{esc(pill)}</span>' if pill else "") + "</div>"
    return f'<article class="slide">{head}{body}</article>'

def tiles(*items):
    return '<div class="tiles">' + "".join(f'<div class="tile"><h4>{esc(h)}</h4>{b}</div>' for h, b in items) + "</div>"

def table(rows):
    h = "".join(f"<th>{esc(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join((f"<th scope=row>{esc(c)}</th>" if k == 0 else f"<td>{esc(c)}</td>") for k, c in enumerate(r)) + "</tr>" for r in rows[1:])
    return f'<div class="tablewrap"><table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>'

def part(pid, eyebrow, title, slides):
    return f'<section class="part" id="{pid}"><div class="band"><div class="eyebrow">{esc(eyebrow)}</div><h2>{esc(title)}</h2></div>{"".join(slides)}</section>'

P = lambda s: f"<p>{s}</p>"
parts = [
    part("einstieg", "Einstieg", "Worum geht es?", [
        slide("Mythos oder Fakt?", P("<strong>„Am Morgen bist du größer als am Abend.“</strong>")
              + tiles(("Im Weltall", P("Astronauten sind nach Monaten im All bis zu <strong>5 cm</strong> größer.")),
                      ("Bei der Stellung", P("Beim Bundesheer wird deine Körpergröße gemessen. Spielt die Uhrzeit eine Rolle?")))
              + '<details class="reveal"><summary>Auflösung anzeigen</summary><p><strong>Fakt!</strong> Tagsüber drückt dein Körpergewicht die Bandscheiben zusammen – abends bist du ca. 1–2 cm kleiner. In der Schwerelosigkeit dehnt sich die Wirbelsäule.</p></details>'),
        slide("Das kannst du nach dieser Doppelstunde", '<ol class="goals">'
              "<li>die <strong>Länge</strong> als Grundgröße mit der Einheit Meter erklären und das passende Messgerät wählen</li>"
              "<li><strong>schätzen</strong>, genau messen, den <strong>Mittelwert</strong> bilden und sinnvoll runden</li>"
              "<li><strong>zufällige und systematische Fehler</strong> unterscheiden</li>"
              "<li>Messwerte als <strong>Säulendiagramm</strong> darstellen und deine <strong>Reaktionszeit</strong> bestimmen</li></ol>"),
    ]),
    part("teil1", "Teil 1 · Stunde 1 · Buch S. 19", "Die Länge messen", [
        slide("Die Geschichte des Meters", table([["Jahr", "Was geschah?"], ["1791", "Frankreich: 1 m soll der 10-millionste Teil der Strecke vom Nordpol zum Äquator sein."],
                                                 ["1792–1798", "Zwei Forscher vermessen 7 Jahre lang die Strecke Dünkirchen – Barcelona."],
                                                 ["1799", "Ein Platin-Stab in Paris wird zum Ur-Meter."], ["1983", "Der Meter wird über das Licht festgelegt – überall gleich genau."]])
              + P("<strong>Auch Profis messen falsch:</strong> Der Ur-Meter war rund 0,2 mm zu kurz – ein systematischer Fehler bei der Vermessung der Erde."), "Buch S. 17–19"),
        slide("Die Länge", '<div class="merke"><strong>Merke:</strong> Die <strong>Länge l</strong> gibt den Abstand zwischen zwei Punkten bzw. die Ausdehnung eines Objekts in eine Richtung an. Einheit: <strong>Meter (m)</strong>.</div>'
              + tiles(("Grundgröße im SI", P("Die Länge ist eine der 7 Grundgrößen.") + P("<strong>1 m = 10 dm = 100 cm = 1000 mm</strong>")),
                      ("Wusstest du?", P("Seit 1983 ist der Meter über das Licht festgelegt: Licht legt 1 m in 1/299 792 458 s zurück."))), "Buch S. 19"),
        slide("Womit misst man Längen?", table([["Messgerät", "Messbereich", "genau auf", "Beispiel"],
                                               ["Maßband, Meterstab", "cm bis einige m", "1 mm", "Körpergröße"],
                                               ["Messschieber", "1 mm – 10 cm", "0,1 mm", "Durchmesser einer Patrone"],
                                               ["Bügelmessschraube", "0,1 mm – 1 cm", "0,01 mm", "Dicke von Papier"],
                                               ["Maßstab im Mikroskop", "mikroskopisch klein", "–", "Größe einer Zelle"],
                                               ["Laser (Laufzeit)", "große Entfernungen", "–", "Entfernung zum Ziel"]])
              + P("Je kleiner die Länge, desto <strong>feiner</strong> muss das Messgerät messen."), "Buch S. 19"),
        slide("Direkt oder indirekt messen?", tiles(("Direkte Messung", P("Vergleich mit einem <strong>geeichten</strong> Messgerät, z. B. Maßband an der Wand.")),
                                                    ("Indirekte Messung", P("Umweg über die Zeit: Ein Laser trifft einen Spiegel am Mond. Hin und zurück braucht das Licht ca. 2,5 s → ca. 384 000 km.")))
              + P("<strong>Bundesheer:</strong> Ein Laser-Entfernungsmesser misst die Laufzeit des Lichts zum Ziel und rechnet die Entfernung aus."), "Buch S. 19"),
        slide("Wie genau kann ich messen?", '<div class="merke">Die <strong>kleinste Einteilung</strong> der Skala bestimmt die Genauigkeit.</div>'
              + tiles(("174,3 cm ✔", P("Maßband mit mm-Einteilung: auf 1 mm genau.")),
                      ("174,32 cm ✘", P("<strong>Scheingenauigkeit:</strong> So genau misst kein Maßband.")),
                      ("Auf Augenhöhe", P("Lies gerade von vorne ab – nicht schräg von oben oder unten."))), "Buch S. 17"),
        slide("Schätzen wie die Profis", P("Wer ein Gefühl für Größen hat, merkt sofort, wenn ein Messwert nicht stimmen kann – z. B. 17,5 cm statt 175 cm Körpergröße.")
              + table([["Größe", "Schätzaufgabe", "Ziel"], ["Länge", "10-cm-Strich ohne Lineal", "10 cm"], ["Masse", "1 g Salz mit dem Löffel", "1 g"], ["Zeit", "leise „21 … 30“ zählen", "10 s"]])
              + '<div class="merke"><strong>Abweichung = gemessen − Ziel</strong> · Plus = zu viel, Minus = zu wenig. Beispiel: 8,7 cm − 10 cm = −1,3 cm</div>'
              + P("<strong>Bundesheer:</strong> Beim Entfernungsschätzen im Gelände vergleicht man mit bekannten Längen, z. B. Fußballfeld ≈ 100 m."), "Buch S. 17"),
        slide("So misst du deine Körpergröße", '<ol class="goals">'
              "<li><strong>Schätze</strong> zuerst deine Größe</li>"
              "<li><strong>3er-Gruppen:</strong> Messperson, Markierer, Ableser</li>"
              "<li><strong>Schuhe aus</strong> – Fersen, Po und Rücken an die Wand</li>"
              "<li>Buch <strong>waagrecht</strong> auf den Kopf, Post-it genau an die Unterkante</li>"
              "<li>Vom Boden bis zur <strong>Oberkante des Post-its</strong> messen</li>"
              "<li>Auf <strong>Augenhöhe</strong> ablesen – auf 1 mm genau</li>"
              "<li>Jeder <strong>3-mal</strong> – dazwischen weggehen und neu hinstellen</li></ol>", "Buch S. 17"),
    ]),
    part("teil2", "Teil 2 · Stunde 2 · Buch S. 17–18", "Messfehler und Reaktionszeit", [
        slide("So rechnest du – Beispiel Lukas", table([["Schritt", "Rechnung"],
                                                       ["Mittelwert", "(174,2 + 174,6 + 174,3) : 3 = 523,1 : 3 = 174,37"],
                                                       ["gerundet", "auf 1 mm genau → 174,4 cm"],
                                                       ["Messunsicherheit", "(größter − kleinster Wert) : 2 = (174,6 − 174,2) : 2 = 0,2 cm"],
                                                       ["Ergebnis", "174,4 cm ± 0,2 cm"],
                                                       ["Schätzfehler", "Mittelwert − Schätzung = 174,4 − 172 = +2,4 cm"]])
              + P("Schätzfehler: <strong>Plus</strong> = größer als gedacht · <strong>Minus</strong> = kleiner als gedacht."), "Buch S. 17"),
        slide("Zufällige und systematische Fehler",
              '<div class="tiles">'
              f'<div class="tile">{fig("ziel_zufaellig.png", "Zielscheibe: Treffer streuen rund um die Mitte")}<h4>Zufällige Fehler</h4><p>mal zu groß, mal zu klein – z. B. schräg abgelesen. <strong>Der Mittelwert hilft!</strong></p></div>'
              f'<div class="tile">{fig("ziel_systematisch.png", "Zielscheibe: alle Treffer eng beisammen rechts oben")}<h4>Systematische Fehler</h4><p>immer in dieselbe Richtung – z. B. mit Schuhen gemessen. <strong>Der Mittelwert hilft nicht!</strong></p></div>'
              "</div>"
              + P("<strong>Schießstand:</strong> Liegen alle Treffer rechts oben, ist das Visier verstellt – da helfen auch 100 Schüsse nichts. Ursache beheben!"), "Buch S. 17"),
        slide("Wie verlässlich ist ein Messwert?", '<div class="merke">Ein Messergebnis = <strong>Mittelwert ± Messunsicherheit</strong></div>'
              + tiles(("Beispiel", P("<strong>174,4 cm ± 0,2 cm</strong>: Der wahre Wert liegt ziemlich sicher zwischen 174,2 cm und 174,6 cm.")),
                      ("Vorsicht bei Zahlen!", P("„2 cm größer!“ – Ist das mehr als die Messunsicherheit? Wurde immer gleich gemessen (gleiche Uhrzeit, ohne Schuhe)?"))), "Buch S. 17"),
        slide("Von der Strichliste zum Säulendiagramm",
              P("<strong>Strichliste:</strong> Für jeden Mittelwert ein Strich im passenden 5-cm-Bereich – der 5. Strich geht quer über die ersten vier. <strong>Anzahl</strong> = Striche zählen.")
              + P("<strong>Säulendiagramm:</strong> x-Achse = Größenbereiche, y-Achse = Anzahl. Über jeden Bereich eine Säule, genau so hoch wie die Anzahl.")
              + fig("diagramm.gif", "Animation: Die Säulen einer Beispielklasse mit 24 Kadetten wachsen nacheinander.", anim=True, cap="Animation · Beispielklasse mit 24 Kadetten")
              + P("Typisch ist die <strong>Glockenform</strong>: In der Mitte die meisten, nach außen immer weniger."), "Buch S. 17"),
        slide("Reaktionszeit messen",
              '<div class="tiles"><div class="tile"><ol class="goals">'
              "<li>Zu zweit, <strong>Lineal ab 30 cm</strong> – besser 40–50 cm oder ein aufgeklappter Meterstab</li>"
              "<li>Lineal <strong>senkrecht</strong>, Null zwischen den offenen Fingern</li>"
              "<li><strong>Ohne Vorwarnung</strong> loslassen – fangen!</li>"
              "<li>Den <strong>Fallweg h</strong> in cm ablesen</li>"
              "<li><strong>3-mal</strong> messen, Mittelwert bilden, dann tauschen</li></ol>"
              "<p>Geodreieck (zu kurz) und Maßband (zu weich) sind ungeeignet.</p></div>"
              f'<div class="tile">{fig("lineal.png", "Skizze: Der Versuchsleiter hält das Lineal oben, unten sind die offenen Finger auf Höhe 0. Der Fallweg h ist markiert.")}</div></div>', "Buch S. 18"),
        slide("Reaktionszeit ablesen",
              f'<div class="merke formula"><img src="img/formel.png" width="{SZ["formel.png"][0]}" height="{SZ["formel.png"][1]}" alt="Formel: t gleich Wurzel aus 2 mal h durch 9,81"></div>'
              + P("<strong>h</strong> = Fallweg in Meter · <strong>9,81</strong> = Fallbeschleunigung der Erde. Einfacher: in der Tabelle ablesen!")
              + table([["h in cm", "5", "7,5", "10", "12,5", "15"], ["t in s", "0,10", "0,12", "0,14", "0,16", "0,17"]])
              + table([["h in cm", "17,5", "20", "22,5", "25", "30"], ["t in s", "0,19", "0,20", "0,21", "0,23", "0,25"]])
              + table([["h in cm", "35", "40", "45", "50"], ["t in s", "0,27", "0,29", "0,30", "0,32"]])
              + P("h liegt dazwischen? Wert dazwischen nehmen: 15,7 cm → ca. 0,18 s. Schwer oder leicht ist egal – ein Meterstab fällt genauso schnell wie ein Plastiklineal."), "Buch S. 18"),
        slide("Reaktionszeit im Verkehr", tiles(("Rechnung", P("50 km/h ≈ <strong>14 m pro Sekunde</strong>. In 0,2 s fährt das Auto fast 3 m – ohne zu bremsen.")),
                                                ("Handy am Steuer", P("Wer aufs Handy schaut, reagiert erst nach 1–2 s: <strong>14–28 m</strong> ungebremst. Genauso bei Müdigkeit, z. B. nach dem Wachdienst."))), "Buch S. 18"),
    ]),
    part("begriffe", "Zum Nachschlagen", "Fachbegriffe", [
        slide("Teil 1 · Länge", table([["Begriff", "Bedeutung"], ["Länge l", "Abstand zwischen zwei Punkten – Einheit Meter (m)"], ["Grundgröße", "eine der 7 Größen des SI, z. B. Länge, Masse, Zeit"],
                                       ["direkte Messung", "Vergleich mit einem geeichten Messgerät"], ["indirekte Messung", "Umweg über eine andere Größe, z. B. die Laufzeit"],
                                       ["geeicht", "Messgerät wurde amtlich mit einem genauen Maßstab geprüft"], ["Genauigkeit", "kleinste Einteilung auf der Skala, z. B. 1 mm"],
                                       ["Scheingenauigkeit", "mehr Kommastellen, als das Messgerät messen kann"], ["Abweichung", "gemessen − Ziel (Plus = zu viel, Minus = zu wenig)"]]), "Buch S. 17–19"),
        slide("Teil 2 · Messfehler und Reaktionszeit", table([["Begriff", "Bedeutung"], ["Mittelwert", "Summe aller Werte : Anzahl der Werte („Durchschnitt“)"],
                                            ["Messunsicherheit", "(größter − kleinster Wert) : 2 – so weit kann das Ergebnis danebenliegen"], ["Schätzfehler", "Mittelwert − Schätzung"],
                                            ["zufälliger Fehler", "mal zu groß, mal zu klein → Mittelwert hilft"], ["systematischer Fehler", "immer in dieselbe Richtung → Mittelwert hilft nicht"],
                                            ["Spannweite", "größter Wert − kleinster Wert der Klasse"], ["Strichliste", "pro Wert ein Strich, der 5. Strich quer über die vier"], ["Fallweg h", "so weit fällt das Lineal, bis du es fängst"], ["Reaktionszeit t", "Zeit vom Loslassen bis zum Fangen"]]), "Buch S. 17–18"),
    ]),
]
toc = "".join(f'<a href="#{i}">{esc(l)}</a>' for i, l in [("einstieg", "Einstieg"), ("teil1", "Teil 1"), ("teil2", "Teil 2"), ("begriffe", "Fachbegriffe"), ("weiter", "Aufgaben")])
bt = open(os.path.join(WZ, "vorlagen", "build_theorie.py"), encoding="utf-8").read()
tcss = bt[bt.index("<style>"):bt.index("</style>") + 8].replace("{{", "{").replace("}}", "}")
tcss = tcss.replace("</style>", """.merke { background: var(--olive); color: #fff; border-radius: 12px; padding: 12px 14px; }
.merke strong { color: #C9D8A8; }
ol.goals { margin: 0; padding-left: 24px; display: grid; gap: 6px; }
details.reveal { border: 2px solid #D9772B; border-radius: 12px; padding: 10px 14px; }
details.reveal summary { cursor: pointer; font-weight: 700; color: #D9772B; }
details.reveal p { margin: 8px 0 0; }
.tile .fig img { max-width: 220px; }
.merke.formula { display: flex; justify-content: center; }
.merke.formula img { width: 200px; height: auto; }
.tablewrap th:first-child { white-space: nowrap; }
.sqrt { display: inline-flex; align-items: center; border-top: 2px solid #fff; padding: 2px 6px 0 4px; position: relative; margin-left: 14px; }
.sqrt::before { content: "√"; position: absolute; left: -18px; bottom: -4px; font-size: 40px; line-height: 1; }
.frac { display: inline-grid; text-align: center; }
.frac span:first-child { border-bottom: 2px solid #fff; padding: 0 4px; }
</style>""")
page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>Messen wie die Profis – Lernseite</title>
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
    <div class="top-text"><div class="eyebrow">{esc(EYEBROW)} · Buch S. 17–19</div><h1>Messen wie die Profis</h1></div>
    <img class="smiley" alt="" src="data:image/png;base64,{SMILEY}">
  </div>
</header>
<nav class="toc" aria-label="Inhalt"><div>{toc}</div></nav>
<main>
{"".join(parts)}
<section class="next" id="weiter">
  <div class="eyebrow">Weiter geht's</div>
  <h2>Jetzt bist du dran</h2>
  <div class="btns"><a class="btn" href="aufgaben.html">Arbeitsblatt (TH + UE)</a><a class="btn alt" href="quiz.html">Mess-Check (Quiz)</a></div>
  <p class="hint">Theorie zum Nachlesen im Schulbuch (Trauner) S. 17–19.</p>
</section>
</main>
</body>
</html>
"""
open(DST + "theorie.html", "w", encoding="utf-8").write(page)
for f in ["theorie.html", "aufgaben.html", "quiz.html"]:
    print(f, os.path.getsize(DST + f) // 1024, "KB")
