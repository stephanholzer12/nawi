# Werkzeug für die Handy-Seiten

Bauvorlagen für Lernseite (Theorie), Arbeitsblatt (Aufgaben) und Quiz – Stil wie der BHAK-Folienmaster.

## Ordner und Links
- Pro Einheit ein Ordner: `<klasse>-<fach>/k<kapitel>-<thema>/` (z. B. `2ab-nawi/k1-2-bindungen/`, `3bk-pbgw/k2-1-wahlen/`)
- Darin: `theorie.html`, `aufgaben.html`, `quiz.html`, Bilder in `img/`
- Link: `https://stephanholzer12.github.io/unterricht/<ordner>/<seite>.html`
- Neue Einheit in `einheiten.json` eintragen, dann `python3 werkzeug/build_index.py` → Übersicht pro Klasse (`<klasse>-<fach>/index.html`); die Startseite listet bewusst keine Klassen
- QR-Code für die Klasse: `https://stephanholzer12.github.io/unterricht/<klasse>-<fach>/`

## Bausteine
- `vorlagen/extract.py` + `vorlagen/build_theorie.py`: Theorie aus der TH-Kadetten-PPP (Texte, Bilder, GIFs) → `theorie.html`
- `vorlagen/aufgaben_K1.2_vorlage.html`: Arbeitsblatt (Beispiel K1.2) mit Aufgabentypen text, table, sketch (Foto), strike (Durchstreichen), assign (Zuordnen), puzzle (Rätsel); Speichern im Browser (localStorage), PDF-Abgabe mit jsPDF 2.5.1 (eingebettet) und Schrift Carlito (Teilmenge in `schriften/`, Zeichenbereiche in `ranges.json`)
- `vorlagen/assemble.py` + `vorlagen/site.py`: setzen Wappen, Tarnmuster, Smiley, Schrift, QR-Code ein und schreiben die fertigen Seiten
- `vorlagen/pdf_auswertung.js`: neue PDF-Abgabe »Auswertung für die Lehrkraft« (ersetzt `buildPdf()` im Arbeitsblatt): Übersicht auf Seite 1 (bearbeitet / automatisch geprüft / Punkte, Summe, Note oder Bewertungsraster), danach jede Aufgabe als Block; Auswahl-, Zahlen- und Ampel-Antworten werden grün/rot markiert, bei Fehlern steht die richtige Lösung daneben, freie Texte »selbst bewerten«. Prüfregeln pro Aufgabe: `pts`, `key` (assign), `check`/`checks` (`all`, `ampel`, `trendAmpel`, `reason`), Präfix `pre`; global optional `RASTER`. Beispiel: `3ab-nawi/k2-3b-trendcheck/`
- `vorlagen/quiz_vorlage.html`: Quiz (Sofort-Feedback, Buchseite pro Frage, QR-Code für die Klasse)

- `quellen/<einheit>/`: Quellen und Bauskript einzelner Einheiten (z. B. `quellen/1ab-k1-2-2-koerper/bauen.py` für NAWI 1AB K1.2.2)

## Regeln
- Nur Unterrichtsmaterial: keine Noten, keine Schülernamen, keine Testlösungen, keine eingescannten Buchseiten
- Antworten der Kadetten bleiben im Browser; Abgabe als PDF in LMS
