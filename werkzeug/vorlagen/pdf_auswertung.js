// PDF-Abgabe »Auswertung für die Lehrkraft« – ersetzt die alte Funktion buildPdf() im Arbeitsblatt.
// Platzhalter: __PDFKOPF__ (Zeile über dem Titel), __PDFTITEL__, __PDFFUSS__ (Fußzeile vor dem Namen).
// Optional pro Aufgabe in T:
//   pts: Punkte (Punktekasten neben der Aufgabe und in der Übersicht)
//   key: bei "assign" die richtige Option pro Zeile (Alternativen mit |)
//   check (bei "text") bzw. checks (bei "fields", eine pro Feld, null = selbst bewerten):
//     { all: ["90", "150|150,0"], exp: "90–150 g" }  → alle Begriffe (mit | Alternativen) müssen vorkommen
//     { ampel: "G" } bzw. "OR"                         → erste Farbe im Text (grün/gelb/rot) muss passen
//     { trendAmpel: {"1":"O",...}, from: ["g0","f0"] } → Ampel abhängig vom gewählten Trend (Nummer am Anfang)
//   keyTrend: bei "assign" – richtige Option je Zeile wie key
// Optional global: RASTER = [["Kriterium", "Was zählt?", Punkte], …] → Übersicht als Bewertungsraster statt Punkte pro Aufgabe.
async function buildPdf() {
  const RAS = typeof RASTER !== "undefined" ? RASTER : null;
  const { jsPDF } = window.jspdf;
  const d = new jsPDF({ unit: "mm", format: "a4" });
  d.addFileToVFS("C-R.ttf", FONT_R); d.addFont("C-R.ttf", "C", "normal");
  d.addFileToVFS("C-B.ttf", FONT_B); d.addFont("C-B.ttf", "C", "bold");
  const W = 210, M = 15, CW = W - 2 * M, BOT = 281; let y = 12;
  const C = { olive: [59, 74, 47], teal: [46, 125, 140], theory: [110, 127, 78], muted: [94, 102, 82], ink: [31, 42, 28],
              red: [178, 58, 46], redSoft: [246, 227, 223], green: [80, 140, 40], greenSoft: [230, 240, 211], tint: [238, 243, 228],
              line: [211, 220, 194], amber: [176, 136, 20], amberSoft: [251, 242, 214], white: [255, 255, 255] };
  const AMP = { G: "grün", O: "gelb", R: "rot" };
  const font = (sz, st, col) => { d.setFont("C", st); d.setFontSize(sz); d.setTextColor(...col); };
  const LH = (sz) => sz * 0.3528 * 1.28;
  const split = (s, sz, st, w) => { font(sz, st, C.ink); return d.splitTextToSize(clean(s), w); };
  const newPage = () => { d.addPage(); y = 14; };
  const need = (h) => { if (y + h > BOT) { newPage(); return true; } return false; };
  const norm = (s) => String(s || "").toLowerCase().replace(/\s+/g, " ").replace(/(\d)\.(\d)/g, "$1,$2");
  const ampelOf = (s) => { const m = norm(s).match(/gr(ü|ue)n|gelb|rot/); return m ? (m[0].startsWith("gr") ? "G" : m[0] === "gelb" ? "O" : "R") : null; };

  // ---------- Auswertung ----------
  function check(c, val) {
    if (!filled(val)) return { st: "empty" };
    if (!c) return { st: "man" };
    if (c.ampel || c.trendAmpel) {
      let want = c.ampel;
      if (c.trendAmpel) {
        const src = String(((S.a[c.from[0]] || {})[c.from[1]]) || "");
        const nr = (src.match(/\d/) || [""])[0];
        want = c.trendAmpel[nr];
        if (!want) return { st: "man", note: "Trend nicht erkannt" };
      }
      const a = ampelOf(val);
      if (!a) return { st: "bad", exp: "Ampelfarbe fehlt – erwartet " + want.split("").map(x => AMP[x]).join(" oder ") };
      return want.includes(a) ? { st: "ok", note: c.reason ? "Ampel stimmt – Begründung selbst bewerten" : "" } : { st: "bad", exp: "erwartet " + want.split("").map(x => AMP[x]).join(" oder ") };
    }
    if (c.all) {
      const v = norm(val);
      const ok = c.all.every(alt => alt.split("|").some(x => v.includes(norm(x))));
      return ok ? { st: "ok", note: c.reason ? "Urteil stimmt – Begründung selbst bewerten" : "" } : { st: "bad", exp: "erwartet: " + c.exp };
    }
    return { st: "man" };
  }
  function evaluate(t) {
    const a = S.a[t.id] || {}, out = [];
    if (t.type === "text") out.push({ label: "Antwort", val: a.t, ...check(t.check, a.t) });
    else if (t.type === "fields") t.fields.forEach((f, i) => out.push({ label: f, val: a["f" + i], ...check((t.checks || [])[i], a["f" + i]) }));
    else if (t.type === "assign") t.items.forEach(([, abb], i) => {
      const v = a["s" + i], k = (t.key || [])[i];
      let r = { st: "empty" };
      if (filled(v)) r = !k ? { st: "man" } : k.split("|").includes(v) ? { st: "ok" } : { st: "bad", exp: "richtig: " + k.split("|").join(" oder ") };
      out.push({ label: abb, val: v, assign: true, ...r });
    });
    else answerLines(t).forEach(l => out.push({ label: "", val: l, st: "man" }));
    if (t.type === "sketch") out.foto = (a.foto || null);
    return out;
  }
  const R = T.map(t => ({ t, it: evaluate(t) }));

  // ---------- Bausteine ----------
  function icon(kind, x, yc) {
    if (kind === "man") { d.setDrawColor(...C.muted); d.setLineWidth(0.35); d.circle(x, yc, 1.7, "S"); return; }
    const col = kind === "ok" ? C.green : C.red;
    d.setFillColor(...col); d.circle(x, yc, 1.9, "F");
    d.setDrawColor(255, 255, 255); d.setLineWidth(0.55);
    if (kind === "ok") { d.line(x - 0.95, yc + 0.05, x - 0.25, yc + 0.8); d.line(x - 0.25, yc + 0.8, x + 1.0, yc - 0.75); }
    else if (kind === "bad") { d.line(x - 0.75, yc - 0.75, x + 0.75, yc + 0.75); d.line(x - 0.75, yc + 0.75, x + 0.75, yc - 0.75); }
    else { d.line(x - 0.9, yc, x + 0.9, yc); }
  }
  function chip(text, x, yy, fg, bg, align = "left") {
    font(8.5, "bold", fg);
    const w = d.getTextWidth(clean(text)) + 4;
    const x0 = align === "right" ? x - w : x;
    d.setFillColor(...bg); d.roundedRect(x0, yy - 3.4, w, 4.6, 1.2, 1.2, "F");
    d.text(clean(text), x0 + 2, yy);
    return w;
  }
  function lines(arr, sz, st, col, x) { font(sz, st, col); const h = LH(sz); arr.forEach(l => { d.text(l, x, y + h * 0.8); y += h; }); }
  function stats(it) {
    const n = it.length, empty = it.filter(i => i.st === "empty").length;
    const auto = it.filter(i => i.st === "ok" || i.st === "bad"), ok = auto.filter(i => i.st === "ok").length;
    return { n, empty, auto: auto.length, ok, bad: auto.length - ok, man: it.filter(i => i.st === "man").length };
  }

  // ---------- Kopf ----------
  d.addImage(LOGO, "PNG", M, y, 10, 11.5);
  font(8.5, "bold", C.teal); d.text(clean("__PDFKOPF__"), M + 14, y + 4);
  font(17, "bold", C.olive); d.text(clean("__PDFTITEL__"), M + 14, y + 10.5);
  font(8.5, "bold", C.muted); d.text("ABGABE", W - M, y + 4, { align: "right" });
  y += 15;
  d.setFillColor(...C.tint); d.roundedRect(M, y, CW, 9, 1.5, 1.5, "F");
  font(8, "normal", C.muted); d.text("NAME", M + 3, y + 3.6); d.text("KLASSE", M + 112, y + 3.6); d.text("DATUM", M + 140, y + 3.6);
  font(12, "bold", C.ink); d.text(clean(S.name || "—"), M + 3, y + 7.6);
  d.text(clean(S.klasse || "—"), M + 112, y + 7.6); d.text(new Date().toLocaleDateString("de-AT"), M + 140, y + 7.6);
  y += 13;

  // ---------- Übersicht ----------
  font(11.5, "bold", C.olive); d.text("Auf einen Blick", M, y + 3.5); y += 6;
  const cols = [M + 2, M + 88, M + 122, M + CW - 2];
  d.setFillColor(...C.olive); d.rect(M, y, CW, 6, "F");
  font(8.5, "bold", C.white); d.text("Aufgabe", cols[0], y + 4.1); d.text("Bearbeitet", cols[1], y + 4.1); d.text("Automatisch geprüft", cols[2], y + 4.1);
  if (!RAS) d.text("Punkte", cols[3], y + 4.1, { align: "right" });
  y += 6;
  let sumPts = 0;
  R.forEach(({ t, it }, k) => {
    const s = stats(it);
    if (k % 2) { d.setFillColor(...C.tint); d.rect(M, y, CW, 6.4, "F"); }
    font(9.5, "bold", C.ink);
    const ttl = d.splitTextToSize(clean((t.nr ? (t.pre || "A") + t.nr + "  " : "") + t.title + (t.tag ? " (" + t.tag + ")" : "")), 84)[0];
    d.text(ttl, cols[0], y + 4.4);
    const done = s.n - s.empty;
    if (s.empty === 0) chip("vollständig", cols[1], y + 4.4, C.green, C.greenSoft);
    else if (done === 0) chip("leer", cols[1], y + 4.4, C.red, C.redSoft);
    else chip(done + " von " + s.n, cols[1], y + 4.4, C.amber, C.amberSoft);
    let x = cols[2];
    if (s.auto) {
      x += chip(s.ok + " richtig", x, y + 4.4, C.green, C.greenSoft) + 1.5;
      if (s.bad) chip(s.bad + " falsch", x, y + 4.4, C.red, C.redSoft);
    } else { font(8.5, "normal", C.muted); d.text(s.n - s.empty ? "selbst bewerten" : "–", x, y + 4.4); }
    if (!RAS && t.pts) { font(9.5, "normal", C.muted); d.text("____ / " + t.pts, cols[3], y + 4.4, { align: "right" }); sumPts += t.pts; }
    y += 6.4;
  });
  d.setDrawColor(...C.olive); d.setLineWidth(0.4); d.line(M, y, M + CW, y); y += 1;
  if (RAS) {
    y += 4; font(11.5, "bold", C.olive); d.text("Bewertung", M, y + 3.5); y += 6;
    let tot = 0;
    RAS.forEach(([k, was, p], i) => {
      if (i % 2) { d.setFillColor(...C.tint); d.rect(M, y, CW, 6.2, "F"); }
      font(9.5, "bold", C.ink); d.text(clean(k), cols[0], y + 4.2);
      font(8.5, "normal", C.muted); d.text(clean(was), M + 45, y + 4.2);
      font(9.5, "normal", C.muted); d.text("____ / " + p, cols[3], y + 4.2, { align: "right" });
      tot += p; y += 6.2;
    });
    sumPts = tot; d.line(M, y, M + CW, y); y += 1;
  }
  y += 2;
  d.setFillColor(...C.olive); d.roundedRect(M + CW - 92, y, 92, 10, 1.5, 1.5, "F");
  font(10, "bold", C.white); d.text("Summe ____ / " + sumPts, M + CW - 88, y + 6.6); d.text("Note ______", M + CW - 4, y + 6.6, { align: "right" });
  font(8, "normal", C.muted);
  icon("ok", M + 2, y + 2.3); d.text("automatisch richtig*", M + 5.5, y + 3.2);
  icon("bad", M + 37, y + 2.3); d.text("falsch – richtige Lösung daneben", M + 40.5, y + 3.2);
  icon("man", M + 2, y + 7.4); d.text("selbst bewerten (freier Text)", M + 5.5, y + 8.3);
  icon("empty", M + 46, y + 7.4); d.text("keine Antwort", M + 49.5, y + 8.3);
  font(7, "normal", C.muted); d.text(clean("* bei Begründungen ist nur das Urteil bzw. die Ampel geprüft – den Text selbst lesen"), M, y + 12.6);
  y += 17;

  // ---------- Aufgaben ----------
  for (const { t, it } of R) {
    need(24);
    d.setFillColor(...C.tint); d.roundedRect(M, y, CW, 8.5, 1.5, 1.5, "F");
    font(11.5, "bold", C.olive);
    d.text(d.splitTextToSize(clean((t.nr ? (t.pre ? t.pre + t.nr : "Aufgabe " + t.nr) + " · " : "") + t.title), CW - 75)[0], M + 3, y + 5.8);
    let rx = M + CW - 2;
    if (!RAS && t.pts) {
      d.setFillColor(...C.white); d.setDrawColor(...C.olive); d.setLineWidth(0.35); d.roundedRect(rx - 24, y + 1.4, 24, 5.8, 1, 1, "FD");
      font(9, "bold", C.olive); d.text("____ / " + t.pts + " P", rx - 12, y + 5.3, { align: "center" }); rx -= 27;
    }
    font(8, "bold", t.own ? C.theory : C.teal); d.text(clean(t.src + (t.tag ? " · " + t.tag : "")), rx, y + 5.5, { align: "right" });
    y += 10.5;
    const q = split(t.q, 8.5, "normal", CW - 6);
    lines(q.slice(0, 3), 8.5, "normal", C.muted, M + 3); y += 1;

    for (const i of it) {
      const X = M + 10, TW = CW - 12;
      if (i.assign) {
        const left = split(i.label, 9.5, "normal", 92), val = filled(i.val) ? String(i.val) : "— keine Auswahl —";
        const right = split(val, 10, "bold", TW - 98);
        const ex = i.exp ? split(i.exp, 8.5, "bold", TW - 98) : [];
        const h = Math.max(left.length * LH(9.5), right.length * LH(10) + ex.length * LH(8.5)) + 2;
        need(h);
        if (i.st === "bad" || i.st === "empty") { d.setFillColor(...C.redSoft); d.rect(M + 4, y - 0.4, CW - 4, h, "F"); }
        icon(i.st, M + 6, y + LH(9.5) * 0.55);
        const y0 = y;
        lines(left, 9.5, "normal", C.ink, X + 1);
        const yl = y; y = y0;
        lines(right, 10, "bold", filled(i.val) ? (i.st === "bad" ? C.red : C.ink) : C.red, X + 98);
        if (ex.length) lines(ex, 8.5, "bold", C.green, X + 98);
        y = Math.max(yl, y) + 2;
        d.setDrawColor(...C.line); d.setLineWidth(0.2); d.line(M + 4, y - 0.8, M + CW, y - 0.8);
      } else {
        const lab = i.label ? split(i.label, 8.5, "bold", TW) : [];
        const val = filled(i.val) ? split(String(i.val).trim(), 10.5, "normal", TW) : split("— keine Antwort —", 10.5, "bold", TW);
        const ex = i.exp ? split(i.exp, 8.5, "bold", TW) : [];
        const note = i.note ? split(i.note, 8, "bold", TW) : [];
        const h = lab.length * LH(8.5) + val.length * LH(10.5) + (ex.length ? ex.length * LH(8.5) + 0.8 : 0) + (note.length ? note.length * LH(8) + 0.6 : 0) + 3;
        if (h < BOT - 20) need(h);
        const bg = i.st === "bad" || i.st === "empty" ? C.redSoft : i.st === "ok" ? C.greenSoft : null;
        if (bg && y + h <= BOT) { d.setFillColor(...bg); d.rect(M + 4, y - 0.4, CW - 4, h - 1, "F"); }
        icon(i.st, M + 6, y + (lab.length ? LH(8.5) : LH(10.5)) * 0.55);
        if (lab.length) lines(lab, 8.5, "bold", C.muted, X);
        font(10.5, filled(i.val) ? "normal" : "bold", filled(i.val) ? C.ink : C.red);
        const h2 = LH(10.5);
        for (const l of val) { if (need(h2)) {} d.text(l, X, y + h2 * 0.8); y += h2; }
        if (ex.length) { y += 0.8; lines(ex, 8.5, "bold", C.red, X); }
        if (note.length) { y += 0.6; lines(note, 8, "bold", i.st === "ok" ? C.green : C.muted, X); }
        y += 2.6;
      }
    }
    if (it.foto) {
      const [iw, ih] = await imgSize(it.foto);
      let w = 100, h = w * ih / iw; if (h > 110) { h = 110; w = h * iw / ih; }
      need(h + 3); d.addImage(it.foto, "JPEG", M + 8, y, w, h); y += h + 3;
    }
    y += 3;
  }
  const n = d.getNumberOfPages();
  for (let p = 1; p <= n; p++) {
    d.setPage(p); font(7.5, "normal", C.muted);
    d.text(clean("__PDFFUSS__ · " + (S.name || "") + " · " + (S.klasse || "")), M, 291);
    d.text("Seite " + p + " von " + n, W - M, 291, { align: "right" });
  }
  return d.output("blob");
}
