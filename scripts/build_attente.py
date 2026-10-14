"""Construit la page d'attente themixfr.com : docs/index.html autonome (polices, logo et fond
intégrés en base64 ; aucun appel externe, aucun cookie) + docs/CNAME.

Usage (depuis n'importe où) : python3 scripts/build_attente.py
Sources : sources/fonts, sources/logo, et le fond composé par scripts/compose_fond.py
(sources/fond/fond_attente.webp ; s'il manque, la page sort en gris uni #E5E5E5).
"""
import base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "sources" / "fonts"
LOGO = ROOT / "sources" / "logo" / "logo_the_mix_noir.png"
FOND = ROOT / "sources" / "fond" / "fond_attente.webp"
OUT = ROOT / "docs"

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

font_faces = ""
for fam, prefix, weights in [
    ("Big Shoulders Display", "big-shoulders-display", (800, 900)),
    ("Figtree", "figtree", (400, 600)),
]:
    for w in weights:
        data = b64(FONTS / f"{prefix}-latin-{w}-normal.woff2")
        font_faces += (
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}\n" % (fam, w, data)
        )

logo = b64(LOGO)
bg_image = ""
if FOND.exists():
    bg_image = (f"background-image:url(data:image/webp;base64,{b64(FOND)});"
                "background-size:cover;background-position:center top;background-repeat:no-repeat;")

links = [
    ("Instagram", "https://www.instagram.com/themixfr/"),
    ("TikTok", "https://www.tiktok.com/@themixfr"),
    ("YouTube", "https://www.youtube.com/@themixfr"),
]
items = "\n".join(
    f'      <li><a href="{url}" rel="noopener" aria-label="The Mix sur {name} : @themixfr">'
    f'<span class="net">{name}</span><span class="handle">@themixfr</span></a></li>'
    for name, url in links
)

html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Mix</title>
<meta name="description" content="Le site arrive mi-novembre.">
<meta name="robots" content="noindex">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#E5E5E5">
<meta property="og:title" content="The Mix">
<meta property="og:description" content="Le site arrive mi-novembre.">
<meta property="og:locale" content="fr_FR">
<link rel="icon" type="image/png" href="data:image/png;base64,{logo}">
<style>
{font_faces}
:root{{
  --bg:#E5E5E5; --ink:#0D0D0D; --text:#262626;
  --violet:#6B35D4; --pill:#7B3FE4; --hover:rgba(107,53,212,.08);
}}
*{{box-sizing:border-box}}
html{{background-color:var(--bg)}}
body{{margin:0;color:var(--ink);background-color:var(--bg);min-height:100vh;min-height:100svh;{bg_image}}}
body{{font-family:'Figtree',system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
main{{max-width:560px;margin:0 auto;min-height:100vh;min-height:100svh;
  padding:48px 16px 28px;display:flex;flex-direction:column}}
.logo{{display:block;width:min(200px,50vw);height:auto}}
h1{{font-family:'Big Shoulders Display',sans-serif;font-weight:900;text-transform:uppercase;
  font-size:clamp(44px,14vw,84px);line-height:1.16;letter-spacing:.005em;margin:56px 0 48px}}
h1 .nw{{white-space:nowrap}}
.pill{{background:var(--pill);color:#fff;border-radius:16px;padding:.08em .07em .01em;
  white-space:nowrap;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
ul{{list-style:none;margin:0;padding:0;display:grid;gap:14px}}
a{{color:inherit}}
li a{{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:64px;
  padding:12px 24px;border:3px solid var(--violet);border-radius:32px;text-decoration:none;
  transition:background-color .15s ease}}
li a:hover{{background:var(--hover)}}
li a:focus-visible,footer a:focus-visible{{outline:3px solid var(--ink);outline-offset:3px}}
.net{{font-family:'Big Shoulders Display',sans-serif;font-weight:800;text-transform:uppercase;
  font-size:28px;letter-spacing:.06em;line-height:1}}
.handle{{font-weight:600;font-size:16px;color:var(--violet)}}
footer{{margin-top:auto;padding-top:56px;font-size:13px;line-height:1.5;color:var(--text)}}
footer a{{text-decoration:underline;text-underline-offset:2px}}
@media (prefers-reduced-motion:reduce){{li a{{transition:none}}}}
</style>
</head>
<body>
<main>
  <img class="logo" src="data:image/png;base64,{logo}" alt="The Mix" width="669" height="455">
  <h1>Le site arrive <span class="nw"><span class="pill">mi-novembre</span>.</span></h1>
  <nav aria-label="Réseaux sociaux">
    <ul>
{items}
    </ul>
  </nav>
  <footer>Vinsaki SAS · <a href="mailto:contact@themixfr.com">contact@themixfr.com</a></footer>
</main>
</body>
</html>
"""
(OUT / "index.html").write_text(html, encoding="utf-8")
(OUT / "CNAME").write_text("themixfr.com\n", encoding="utf-8")
print("index.html", len(html.encode()) // 1024, "Ko")
