"""Setzt werkzeug/pdf_hilfe.js inline in alle Handy-Seiten mit PDF-Abgabe (erkennbar an jsPDF).
Aufruf im Repository-Ordner: python3 werkzeug/pdf_hilfe_einbauen.py  – nach jeder neuen Seite und nach Änderungen an pdf_hilfe.js erneut ausführen.
Ersetzt einen schon vorhandenen Block zwischen <!-- pdf_hilfe:start --> und <!-- pdf_hilfe:end -->."""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = open(os.path.join(ROOT, "werkzeug", "pdf_hilfe.js"), encoding="utf-8").read()
BLOCK = "<!-- pdf_hilfe:start -->\n<script>\n" + JS + "</script>\n<!-- pdf_hilfe:end -->\n"
n = 0
for f in sorted(glob.glob(os.path.join(ROOT, "*", "*", "*.html"))):
    if os.sep + "werkzeug" + os.sep in f: continue
    s = open(f, encoding="utf-8").read()
    if "jsPDF" not in s: continue
    s = re.sub(r"<!-- pdf_hilfe:start -->.*?<!-- pdf_hilfe:end -->\n?", "", s, flags=re.S)
    i = s.rindex("</body>")
    s = s[:i] + BLOCK + s[i:]
    open(f, "w", encoding="utf-8").write(s); n += 1
    print("PDF-Hilfe:", os.path.relpath(f, ROOT))
print(n, "Seiten")
