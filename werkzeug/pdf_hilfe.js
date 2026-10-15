/* PDF-Hilfe für die Handy-Seiten (Arbeitsblatt, Versuche, Gruppe …).
   Problem: Manche Handys laden die PDF nicht herunter – v. a. in App-Browsern (Instagram, Teams, Snapchat,
   WebView) und auf manchen iPhones. Diese Datei hängt sich an jeden Download-Link einer PDF (blob:) und zeigt
   danach ein kleines Feld mit zwei Ersatzwegen: »Teilen / Speichern« (Teilen-Menü des Handys) und »PDF öffnen«.
   Zusätzlich ein Hinweis, wenn die Seite in einem App-Browser geöffnet wurde.
   Einbau: python3 werkzeug/pdf_hilfe_einbauen.py (setzt diese Datei inline in alle Seiten mit PDF-Abgabe). */
(function () {
  if (window.__pdfHilfe) return; window.__pdfHilfe = true;
  var ua = navigator.userAgent || "";
  var inApp = /Instagram|FBAN|FBAV|FB_IAB|Snapchat|musical_ly|BytedanceWebview|TikTok|Line\/|MicroMessenger|Teams\/|; wv\)/i.test(ua) ||
              (/(iPhone|iPad|iPod)/.test(ua) && /AppleWebKit/.test(ua) && !/Safari/.test(ua));
  var css = ".ph-box{position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;max-width:560px;margin:0 auto;background:#fff;" +
    "border:2px solid #4E5B31;border-radius:14px;box-shadow:0 6px 24px rgba(0,0,0,.18);padding:14px 14px 12px;font:16px/1.4 system-ui,sans-serif;color:#2C3424}" +
    ".ph-box b{display:block;font-size:17px;margin-bottom:4px;color:#4E5B31}.ph-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}" +
    ".ph-btn{flex:1 1 140px;min-height:44px;border-radius:10px;border:0;background:#4E5B31;color:#fff;font:600 16px system-ui,sans-serif;cursor:pointer}" +
    ".ph-btn.alt{background:#E6F0D3;color:#2C3424}.ph-x{position:absolute;right:8px;top:4px;border:0;background:none;font-size:24px;color:#6B6B6B;cursor:pointer}" +
    ".ph-warn{position:relative;z-index:9998;background:#FFF4CC;border-bottom:2px solid #C9A227;padding:10px 14px;font:15px/1.4 system-ui,sans-serif;color:#2C3424}";
  function addCss() { if (document.getElementById("ph-css")) return; var s = document.createElement("style"); s.id = "ph-css"; s.textContent = css; document.head.appendChild(s); }
  function mk(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt) e.textContent = txt; return e; }

  function panel(blob, name) {
    addCss();
    var old = document.getElementById("ph-box"); if (old) old.remove();
    var box = mk("div", "ph-box"); box.id = "ph-box"; box.setAttribute("role", "dialog"); box.setAttribute("aria-label", "PDF speichern");
    var x = mk("button", "ph-x", "×"); x.type = "button"; x.setAttribute("aria-label", "Schließen"); x.onclick = function () { box.remove(); };
    box.appendChild(x);
    box.appendChild(mk("b", "", "PDF fertig: " + name));
    box.appendChild(mk("div", "", inApp
      ? "Du bist in einem App-Browser – hier klappt der Download oft nicht. Nimm einen der Knöpfe:"
      : "Keine PDF bei den Downloads? Dann nimm einen der Knöpfe:"));
    var row = mk("div", "ph-row");
    var file = null; try { file = new File([blob], name, { type: "application/pdf" }); } catch (e) {}
    if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
      var sh = mk("button", "ph-btn", "Teilen / Speichern"); sh.type = "button";
      sh.onclick = function () { navigator.share({ files: [file], title: name }).catch(function () {}); };
      row.appendChild(sh);
    }
    var op = mk("button", row.firstChild ? "ph-btn alt" : "ph-btn", "PDF öffnen"); op.type = "button";
    op.onclick = function () {
      var u = URL.createObjectURL(blob);
      var w = window.open(u, "_blank");
      if (!w) location.href = u;
      setTimeout(function () { URL.revokeObjectURL(u); }, 120000);
    };
    row.appendChild(op);
    box.appendChild(row);
    box.appendChild(mk("div", "", "Danach die PDF in LMS hochladen. Beim Öffnen: im Teilen-Menü »In Dateien sichern« bzw. »Herunterladen«."));
    box.lastChild.style.cssText = "font-size:14px;color:#6B6B6B;margin-top:8px";
    document.body.appendChild(box);
  }

  var orig = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    var a = this, name = a.getAttribute("download") || "", href = a.href || "";
    var res = orig.apply(a, arguments);
    if (/\.pdf$/i.test(name) && href.indexOf("blob:") === 0) {
      fetch(href).then(function (r) { return r.blob(); }).then(function (b) { panel(b, name); }).catch(function () {});
    }
    return res;
  };

  if (inApp) {
    var warn = function () {
      addCss();
      var w = mk("div", "ph-warn");
      w.innerHTML = "<strong>Tipp:</strong> Öffne diese Seite im normalen Browser (oben ⋮ oder ··· → <em>Im Browser öffnen</em>). Sonst klappen Speichern und PDF oft nicht.";
      document.body.insertBefore(w, document.body.firstChild);
    };
    if (document.body) warn(); else document.addEventListener("DOMContentLoaded", warn);
  }
})();
