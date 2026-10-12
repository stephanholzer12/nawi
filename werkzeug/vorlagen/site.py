import base64, re, subprocess, qrcode, os, io
BASE="https://stephanholzer12.github.io/unterricht/"
SITE="/home/claude/unterricht/"
def qr_b64(url):
    q=qrcode.QRCode(border=2,box_size=12,error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data(url); q.make()
    b=io.BytesIO(); q.make_image(fill_color="#2C3424",back_color="white").save(b,format="PNG"); return base64.b64encode(b.getvalue()).decode(), b.getvalue()
def wrap(src):
    te=src.index("</title>")+8; rest=src[te:]; bs=rest.index("<header")
    return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            + src[:te] + "\n" + rest[:bs] + "</head>\n<body>\n" + rest[bs:] + "\n</body>\n</html>\n")
unit="2ab-nawi/k1-2-bindungen/"; os.makedirs(SITE+unit, exist_ok=True)
# Arbeitsblatt
url_ab=BASE+unit+"aufgaben.html"; b64,png=qr_b64(url_ab); open("qr_site_ab.png","wb").write(png)
subprocess.run(["python3","assemble.py","qr_site_ab.png"],check=True)
src=open("26-27-2AB-K1.2-Bindungen-TH-Handy.html").read()
js=open("node_modules/jspdf/dist/jspdf.umd.min.js").read()
src=src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>', "<script>/* jsPDF 2.5.1 (MIT) */\n"+js+"\n</script>")
assert "jspdf/2.5.1/jspdf.umd.min.js\"></script>" not in src
open(SITE+unit+"aufgaben.html","w").write(wrap(src))
# Quiz
url_q=BASE+unit+"quiz.html"; qb64,qpng=qr_b64(url_q); open("qr_site_quiz.png","wb").write(qpng)
q=open("/home/claude/out/26-27-2AB-K1.2-Bindungen-Quiz.html").read()
q,n=re.subn(r'(alt="QR-Code zum Bindungs-Check" src="data:image/png;base64,)[A-Za-z0-9+/=]+', lambda m: m.group(1)+qb64, q); assert n==1
if "[hidden]" not in q: q=q.replace("<style>","<style>\n[hidden] { display: none !important; }",1)
open(SITE+unit+"quiz.html","w").write(wrap(q))
open(SITE+".nojekyll","w").write("")
print(url_ab); print(url_q)
