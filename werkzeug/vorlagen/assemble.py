import base64, json, sys
src=open("ab_src.html").read()
rd=lambda p: open(p).read().strip()
qr = sys.argv[1] if len(sys.argv)>1 else None
rep={"__CAMO__":rd("/home/claude/w2/camo.b64"),"__LOGO__":rd("/home/claude/w2/logo.b64"),"__SMILEY__":rd("/home/claude/w2/smiley.b64"),
     "__FONTR__":base64.b64encode(open("carlito-Regular.ttf","rb").read()).decode(),"__FONTB__":base64.b64encode(open("carlito-Bold.ttf","rb").read()).decode(),
     "__RANGES__":open("ranges.json").read(),
     "__QR__":base64.b64encode(open(qr,"rb").read()).decode() if qr else "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=",
     "__QRHIDE__":"" if qr else "hidden"}
for k,v in rep.items(): src=src.replace(k,v)
assert "__" not in src.replace("__proto__",""), [l[:80] for l in src.split("\n") if "__" in l][:3]
art="/home/claude/ab/26-27-2AB-K1.2-Bindungen-TH-Handy.html"
open(art,"w").write(src)
# eigenständige Datei (z. B. für LMS/OneDrive): mit vollständigem Dokumentrahmen
title_end=src.index("</title>")+8
std='<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'+src[:title_end]+"\n"
rest=src[title_end:]; body_start=rest.index("<header")
std+=rest[:body_start]+"</head>\n<body>\n"+rest[body_start:]+"\n</body>\n</html>\n"
open("/home/claude/out/26-27-2AB-K1.2-Bindungen-TH-Handy.html","w").write(std)
print(len(src)//1024,"KB")
