"""Test-Training NAWI 4AB · 1. Test (11.11.2026) – Quiz aus werkzeug/vorlagen/quiz_vorlage.html.
Aufruf im Repository-Ordner:  python3 werkzeug/quellen/4ab-test1-training/bauen.py
Schreibt 4ab-nawi/test1-training/quiz.html. Fragen in eigenen Worten; Seiten nach Trauner NAWI 4.
Für eine andere Klasse: Ordner kopieren, ORDNER/EYEBROW/TITEL/QUIZ anpassen."""
import base64, io, json, os, re
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WZ = os.path.join(ROOT, "werkzeug")
BASE = "https://stephanholzer12.github.io/unterricht/"
ORDNER = "4ab-nawi/test1-training"
EYEBROW = "NAWI · 4AB · Training für den 1. Test (11.11.)"
TITEL = "Test-Training"

# (Thema, Frage, [richtig, falsch, falsch, falsch], Erklärung, Seite)
QUIZ = [
 # 1 Ladungen
 ("Ladungen", "Welche Teilchen sind negativ geladen?", ["Elektronen", "Protonen", "Neutronen", "Atomkerne"],
  "Elektronen sind negativ, Protonen positiv, Neutronen ungeladen.", "Buch S. 10"),
 ("Ladungen", "Zwei Luftballons sind beide negativ geladen. Was passiert?", ["Sie stoßen sich ab.", "Sie ziehen sich an.", "Nichts – gleiche Ladungen wirken nicht.", "Sie entladen sich sofort."],
  "Gleichnamige Ladungen stoßen sich ab, ungleichnamige ziehen sich an.", "Buch S. 10"),
 ("Ladungen", "Du reibst einen Ballon am Pullover. Was wandert dabei?", ["Elektronen", "Protonen", "Atomkerne", "Neutronen"],
  "Nur die leichten Elektronen in der Hülle wechseln den Körper. Ein Körper hat dann zu viele, der andere zu wenige.", "Buch S. 10–11"),
 ("Ladungen", "Ein geladener Stab nähert sich einer Metallkugel, ohne sie zu berühren. Die Ladungen in der Kugel verschieben sich. Wie heißt das?", ["Influenz", "Induktion", "Reibung", "Erdung"],
  "Influenz: Ladungen trennen sich in einem Leiter durch ein nahes Feld – ganz ohne Berührung.", "Buch S. 11"),
 ("Ladungen", "Welcher Stoff ist ein Isolator?", ["Kunststoff", "Kupfer", "Aluminium", "Salzwasser"],
  "Isolatoren haben kaum frei bewegliche Ladungsträger – darum sind Kabel mit Kunststoff ummantelt.", "Buch S. 11"),
 ("Ladungen", "Warum hat ein Blitzableiter oben eine Spitze?", ["An Spitzen sammeln sich Ladungen besonders dicht – der Blitz schlägt dort ein und wird abgeleitet.", "Die Spitze stößt den Blitz ab.", "Die Spitze speichert die Ladung wie ein Akku.", "Spitzen sind nur Dekoration."],
  "Spitzenwirkung: An Spitzen ist das Feld am stärksten. Der Blitz wird über das Kabel sicher in die Erde geleitet.", "Buch S. 11"),
 # 2 Feld und Kondensator
 ("Elektrisches Feld", "Wie verlaufen die Feldlinien zwischen den Platten eines Plattenkondensators?", ["Parallel und gleich dicht – von + nach −", "Kreisförmig um die Platten", "Von − nach + und gekrümmt", "Es gibt dort keine Feldlinien."],
  "Zwischen den Platten ist das Feld homogen: parallele, gleich dichte Feldlinien von Plus nach Minus.", "Buch S. 12–13"),
 ("Elektrisches Feld", "Auf eine Ladung q = 0,002 C wirkt die Kraft F = 10 N. Wie groß ist die Feldstärke E = F / q?", ["5 000 N/C", "0,02 N/C", "20 N/C", "500 N/C"],
  "E = 10 N : 0,002 C = 5 000 N/C. Einheit nicht vergessen!", "Buch S. 13"),
 ("Elektrisches Feld", "Welche Einheit hat die elektrische Feldstärke?", ["N/C (gleich V/m)", "Tesla", "Farad", "A/m"],
  "E = F / q, also Newton pro Coulomb – gleichwertig: Volt pro Meter.", "Buch S. 13"),
 ("Kondensator", "Woraus besteht ein Plattenkondensator?", ["Zwei Metallplatten mit einem Isolator dazwischen", "Zwei Isolatorplatten mit Metall dazwischen", "Einer Spule mit Eisenkern", "Einem Magneten und einer Batterie"],
  "Zwei leitende Platten (Elektroden), dazwischen ein Isolator (Dielektrikum, z. B. Luft).", "Buch S. 13"),
 ("Kondensator", "Ein Kondensator speichert Q = 0,006 C bei U = 12 V. Wie groß ist C = Q / U?", ["0,0005 F (= 500 µF)", "0,072 F", "2 000 F", "0,5 F"],
  "C = 0,006 C : 12 V = 0,0005 F = 500 µF.", "Buch S. 13"),
 ("Kondensator", "Wie kannst du die Kapazität eines Plattenkondensators vergrößern?", ["Größere Platten und kleinerer Abstand", "Kleinere Platten und größerer Abstand", "Höhere Spannung anlegen", "Die Platten aus Kunststoff bauen"],
  "Die Kapazität hängt nur von der Bauform ab: Fläche, Abstand und Isolator. Die Spannung ändert sie nicht.", "Buch S. 13"),
 ("Kondensator", "Ein Lämpchen hängt an einem Kondensator. Du schaltest von »Laden« auf »Entladen«. Was siehst du?", ["Das Lämpchen blitzt kurz auf und wird dann dunkel.", "Das Lämpchen leuchtet dauerhaft.", "Das Lämpchen bleibt immer dunkel.", "Das Lämpchen wird immer heller."],
  "Strom fließt nur, solange sich der Kondensator lädt oder entlädt – danach ist er leer bzw. voll.", "Buch S. 15"),
 ("Kondensator", "Wo wird ein Kondensator genutzt, um in Sekundenbruchteilen viel Energie abzugeben?", ["Defibrillator", "Kompass", "Kühlschrankmagnet", "Thermometer"],
  "Der Defi lädt einen Kondensator auf und entlädt ihn in einem kurzen, starken Stromstoß.", "Buch S. 14–15"),
 ("Elektrisches Feld", "Warum darf man nie auf einen Bahnwaggon unter der Oberleitung klettern?", ["Bei 15 000 V kann der Strom schon ohne Berührung durch die Luft überschlagen.", "Weil man vom Magnetfeld angezogen wird.", "Weil die Oberleitung nur bei Berührung gefährlich ist.", "Weil der Waggon geladen ist wie ein Ballon."],
  "Luft hält nur ein begrenztes Feld aus (Durchschlagsfestigkeit). Kommt man zu nahe, entsteht ein Lichtbogen – lebensgefährlich.", "Unterricht · Buch S. 12–13"),
 # 3 Feldbegriff / Äther
 ("Feldbegriff", "Was versteht man in der Physik unter einem Feld?", ["Einen Raum, in dem an jedem Punkt eine Kraft wirkt bzw. ein Wert gemessen werden kann", "Eine Fläche aus Metall", "Nur den Raum zwischen zwei Magneten", "Eine Wiese im Labor"],
  "Ein Feld ist eine Eigenschaft des Raumes: Jeder Punkt hat einen Wert (z. B. Feldstärke und Richtung).", "Unterricht"),
 ("Feldbegriff", "Wozu nahm man früher den »Äther« an?", ["Als unsichtbaren Stoff, der Licht und Kräfte durch den leeren Raum tragen sollte", "Als Narkosemittel für Versuche", "Als Gas in Glühbirnen", "Als Isolator in Kondensatoren"],
  "Man dachte, Wellen brauchen immer einen Träger – wie Schall die Luft. Dieser Träger hieß Äther.", "Unterricht"),
 ("Feldbegriff", "Welcher Versuch zeigte, dass es keinen Äther gibt?", ["Michelson-Morley-Versuch", "Ørsted-Versuch", "Leiterschaukel", "Rutherford-Versuch"],
  "Michelson und Morley fanden keinen »Ätherwind« – das Licht ist in alle Richtungen gleich schnell.", "Unterricht"),
 # 4 Magnetismus
 ("Magnetismus", "Welche Stoffe werden von einem Magneten angezogen?", ["Eisen, Nickel, Kobalt", "Kupfer, Aluminium, Gold", "Alle Metalle", "Holz, Glas, Kunststoff"],
  "Nur ferromagnetische Stoffe wie Eisen, Nickel und Kobalt. Eine Alu-Dose bleibt liegen – darum trennt man im Recycling mit Magneten.", "Buch S. 26"),
 ("Magnetismus", "Du brichst einen Stabmagneten in der Mitte durch. Was hast du dann?", ["Zwei kleinere Magnete mit je Nord- und Südpol", "Einen Nordpol und einen Südpol getrennt", "Zwei unmagnetische Stücke", "Einen Magneten und ein Stück Eisen"],
  "Jedes Stück besteht aus Elementarmagneten – es entstehen immer wieder Nord- und Südpol.", "Buch S. 27"),
 ("Magnetismus", "Wie kann man einen Magneten entmagnetisieren?", ["Stark erhitzen oder heftig schlagen", "In Wasser legen", "In den Kühlschrank legen", "Mit einem Tuch abreiben"],
  "Hitze und Erschütterung bringen die geordneten Elementarmagnete wieder durcheinander. Ab der Curie-Temperatur ist der Magnetismus weg.", "Buch S. 27"),
 ("Magnetismus", "Wie verlaufen die Feldlinien außerhalb eines Stabmagneten?", ["Vom Nordpol zum Südpol", "Vom Südpol zum Nordpol", "Gerade nach außen weg", "Es gibt außen keine Feldlinien."],
  "Außen von N nach S, innen weiter von S nach N – Magnetfeldlinien sind immer geschlossen.", "Buch S. 27–28"),
 ("Magnetismus", "Die Nordspitze der Kompassnadel zeigt nach Norden. Welcher magnetische Pol liegt also in der Arktis?", ["Ein magnetischer Südpol", "Ein magnetischer Nordpol", "Gar kein Pol", "Abwechselnd beide"],
  "Ungleiche Pole ziehen sich an: Der Nordpol der Nadel wird von einem magnetischen Südpol angezogen.", "Buch S. 28"),
 ("Magnetismus", "Wie entstehen Polarlichter?", ["Teilchen von der Sonne werden vom Erdmagnetfeld zu den Polen gelenkt und bringen die Luft zum Leuchten.", "Das Eis an den Polen spiegelt das Sonnenlicht.", "Blitze in großer Höhe.", "Der Mond beleuchtet die Wolken."],
  "Die Magnetosphäre schützt uns vor dem Sonnenwind. An den Polen dringen die Teilchen ein und regen die Luft zum Leuchten an.", "Buch S. 28"),
 # 5 Elektromagnetismus
 ("Elektromagnetismus", "Was entdeckte Ørsted 1820?", ["Ein Draht mit Strom lenkt eine Kompassnadel ab.", "Magnete ziehen Kupfer an.", "Strom fließt nur in Spulen.", "Der Kompass zeigt immer nach Süden."],
  "Jeder Strom erzeugt ein Magnetfeld – das ist die Grundlage für Elektromagnet und Motor.", "Buch S. 29–30"),
 ("Elektromagnetismus", "Wie machst du einen Elektromagneten stärker?", ["Mehr Windungen, mehr Strom und ein Eisenkern", "Weniger Windungen und ein Kupferkern", "Den Strom ausschalten", "Die Spule länger auseinanderziehen"],
  "Θ = I · N: mehr Strom und mehr Windungen. Der Eisenkern verstärkt, weil sich seine Elementarmagnete ausrichten.", "Buch S. 30–31"),
 ("Elektromagnetismus", "Eine Spule hat N = 200 Windungen, es fließen I = 3 A. Wie groß ist die Durchflutung Θ = I · N?", ["600 A", "66,7 A", "203 A", "0,015 A"],
  "Θ = 3 A · 200 = 600 A.", "Buch S. 31"),
 ("Elektromagnetismus", "Was bewegt die Leiterschaukel, wenn Strom fließt?", ["Die Lorentzkraft im Magnetfeld", "Die Schwerkraft", "Der Luftdruck", "Die Wärme des Drahts"],
  "Auf einen Strom im Magnetfeld wirkt eine Kraft – die Lorentzkraft. Richtung: Linke-Hand-Regel.", "Buch S. 32"),
 ("Elektromagnetismus", "Wozu braucht ein Gleichstrom-Elektromotor den Kommutator?", ["Er polt den Strom jede halbe Umdrehung um, damit der Rotor weiterdreht.", "Er kühlt den Motor.", "Er misst die Drehzahl.", "Er speichert Energie wie ein Kondensator."],
  "Ohne Umpolen bliebe der Rotor stehen. Der Kommutator dreht die Stromrichtung im richtigen Moment um.", "Buch S. 33"),
 ("Elektromagnetismus", "Ein Magnet hängt an einem Bügel, der fest am Auto montiert ist, und zieht das Auto an. Was passiert?", ["Das Auto bleibt stehen – die Kräfte heben sich auf.", "Das Auto fährt immer weiter.", "Das Auto fährt, bis der Magnet leer ist.", "Das Auto fährt rückwärts."],
  "Der Auto-Magnet zieht den Bügel genauso stark zurück. Beide Kräfte wirken auf dasselbe Auto: Summe 0 (actio = reactio).", "Lernseite K1.5a Teil 2"),
]

b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
nb = lambda s: re.sub(r"(?<=\d) (?=\d{3}\b)", " ", s)


def qr_b64(url):
    q = qrcode.QRCode(border=2, box_size=12, error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    b = io.BytesIO(); q.make_image(fill_color="#2C3424", back_color="white").save(b, format="PNG"); return base64.b64encode(b.getvalue()).decode()


def wrap(src):
    te = src.index("</title>") + 8; rest = src[te:]; bs = rest.index("<header")
    return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="robots" content="noindex">\n' + src[:te] + "\n" + rest[:bs] + "</head>\n<body>\n" + rest[bs:] + "\n</body>\n</html>\n")


assert all(len(a) == 4 for _, _, a, _, _ in QUIZ)
qs = ",\n".join("  { t: %s, q: %s, a: %s, e: %s, p: %s }" % tuple(json.dumps(x, ensure_ascii=False) for x in (t, nb(q), [nb(z) for z in a], nb(e), p)) for t, q, a, e, p in QUIZ)
qv = open(os.path.join(WZ, "vorlagen", "quiz_vorlage.html"), encoding="utf-8").read()
qv = qv.replace("<title>Bindungs-Check</title>", f"<title>{TITEL} – 4AB</title>")
qv = qv.replace("NAWI · 2AB · K1.2 Die Bindungsarten", EYEBROW)
qv = qv.replace("<h1>Bindungs-Check</h1>", f"<h1>{TITEL}</h1>").replace("<h2>Bindungs-Check am Handy</h2>", f"<h2>{TITEL} am Handy</h2>")
qv = qv.replace('alt="QR-Code zum Bindungs-Check"', f'alt="QR-Code zum {TITEL}"')
qv = qv.replace("Frage 1 von 16", f"Frage 1 von {len(QUIZ)}")
a, b = qv.index("const Q = ["), qv.index("];", qv.index("const Q = [")) + 2
qv = qv[:a] + "const Q = [\n" + qs + "\n];" + qv[b:]
n = len(QUIZ)
qv = qv.replace("if (p >= 13) return", f"if (p >= {round(n * 0.85)}) return").replace("if (p >= 9) return", f"if (p >= {round(n * 0.6)}) return")
if "[hidden]" not in qv: qv = qv.replace("<style>", "<style>\n[hidden] { display: none !important; }", 1)
for k, v in {"__CAMO__": b64(WZ + "/camo.png"), "__LOGO__": b64(WZ + "/logo.png"), "__SMILEY__": b64(WZ + "/smiley.png"),
             "__QR__": qr_b64(BASE + ORDNER + "/quiz.html")}.items():
    qv = qv.replace(k, v)
assert not re.search(r"__[A-Z]+__", qv) and "Bindung" not in qv
os.makedirs(os.path.join(ROOT, ORDNER), exist_ok=True)
open(os.path.join(ROOT, ORDNER, "quiz.html"), "w", encoding="utf-8").write(wrap(qv))
print("quiz.html:", n, "Fragen")
