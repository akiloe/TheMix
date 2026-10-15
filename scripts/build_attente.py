"""Construit la page d'attente themixfr.com : docs/index.html autonome (polices, logo et fond
intégrés en base64 ; aucun appel externe, aucun cookie, aucun stockage) + docs/CNAME.

La page contient le pop-up newsletter (élément <dialog> natif) : il renvoie vers la page
d'inscription Systeme.io (NEWSLETTER_URL) et ne charge aucun script externe.
Le script copie aussi dans docs/assets/ les polices (avec leurs licences) et le fond, que les
pages Systeme.io (app.themixfr.com) chargent depuis themixfr.com.

Usage (depuis n'importe où) : python3 scripts/build_attente.py
Sources : sources/fonts, sources/logo, et le fond composé par scripts/compose_fond.py
(sources/fond/fond_attente.webp ; s'il manque, la page sort en gris uni #E5E5E5).
"""
import base64, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "sources" / "fonts"
LOGO = ROOT / "sources" / "logo" / "logo_the_mix_noir.png"
FOND = ROOT / "sources" / "fond" / "fond_attente.webp"
OUT = ROOT / "docs"
NEWSLETTER_URL = "https://app.themixfr.com/newsletter"
POPUP_DELAY_S = 10  # ouverture automatique, une fois par chargement de page (rien n'est mémorisé)

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

# Fichiers servis à app.themixfr.com (pages Systeme.io) : polices + licences SIL OFL, fond.
ASSETS = OUT / "assets"
(ASSETS / "fonts").mkdir(parents=True, exist_ok=True)
for name in ("figtree-latin-400-normal.woff2", "figtree-latin-600-normal.woff2",
             "big-shoulders-display-latin-900-normal.woff2",
             "OFL-Figtree.txt", "OFL-BigShouldersDisplay.txt"):
    shutil.copyfile(FONTS / name, ASSETS / "fonts" / name)
if FOND.exists():
    shutil.copyfile(FOND, ASSETS / "fond.webp")

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
fond_var = "none"
if FOND.exists():
    fond_var = f"url(data:image/webp;base64,{b64(FOND)})"
fond_css = ("background-image:var(--fond);background-size:cover;background-position:center top;"
            "background-repeat:no-repeat;")

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
  --fond:{fond_var};
}}
*{{box-sizing:border-box}}
html{{background-color:var(--bg)}}
body{{margin:0;color:var(--ink);background-color:var(--bg);min-height:100vh;min-height:100svh;{fond_css}}}
body{{font-family:'Figtree',system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
main{{max-width:560px;margin:0 auto;min-height:100vh;min-height:100svh;
  padding:48px 16px 28px;display:flex;flex-direction:column}}
.logo{{display:block;width:min(200px,50vw);height:auto}}
h1{{font-family:'Big Shoulders Display',sans-serif;font-weight:900;text-transform:uppercase;
  font-size:clamp(44px,14vw,84px);line-height:calc(1.16em + 10px);letter-spacing:.005em;margin:56px 0 48px}}
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
.cta{{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:64px;
  margin:0 0 14px;padding:12px 24px;border-radius:32px;background:var(--pill);color:#fff;
  text-decoration:none;transition:background-color .15s ease}}
.cta:hover{{background:var(--violet)}}
.cta .net{{color:#fff}}
.cta .handle{{color:#fff}}
.cta:focus-visible,dialog a:focus-visible,dialog button:focus-visible{{outline:3px solid var(--ink);outline-offset:3px}}
dialog{{padding:0;border:0;background:transparent;max-width:none;max-height:none;
  width:min(480px,calc(100vw - 32px))}}
dialog::backdrop{{background:rgba(13,13,13,.55)}}
.box:focus{{outline:none}}
.nw{{white-space:nowrap}}
.box{{position:relative;background-color:var(--bg);{fond_css}border:3px solid var(--violet);
  border-radius:32px;padding:40px 24px 24px;color:var(--text);
  max-height:calc(100vh - 32px);max-height:calc(100svh - 32px);overflow:auto}}
.box h2{{font-family:'Big Shoulders Display',sans-serif;font-weight:900;text-transform:uppercase;
  color:var(--ink);font-size:clamp(40px,11vw,56px);line-height:calc(1.16em + 10px);
  letter-spacing:.005em;margin:0 0 16px}}
.box p{{font-size:17px;line-height:1.5;margin:0 0 24px}}
.box .go{{display:flex;align-items:center;justify-content:center;min-height:56px;padding:12px 24px;
  border-radius:32px;background:var(--pill);color:#fff;text-decoration:none;font-weight:600;font-size:17px}}
.box .go:hover{{background:var(--violet)}}
.box .later{{display:block;margin:12px auto 0;padding:10px 16px;border:0;background:none;
  font:600 15px 'Figtree',system-ui,sans-serif;color:var(--text);text-decoration:underline;
  text-underline-offset:2px;cursor:pointer}}
.box .x{{position:absolute;top:12px;right:12px;width:44px;height:44px;border:0;border-radius:22px;
  background:none;color:var(--ink);font:600 28px/1 'Figtree',system-ui,sans-serif;cursor:pointer}}
.box .x:hover,.box .later:hover{{background:var(--hover)}}
.box small{{display:block;margin-top:16px;font-size:13px;line-height:1.5;color:var(--text)}}
@media (prefers-reduced-motion:reduce){{li a,.cta{{transition:none}}}}
</style>
</head>
<body>
<main>
  <img class="logo" src="data:image/png;base64,{logo}" alt="The Mix" width="669" height="455">
  <h1>Le site arrive <span class="nw"><span class="pill">mi-novembre</span>.</span></h1>
  <a class="cta" href="{NEWSLETTER_URL}" aria-haspopup="dialog">
    <span class="net">Newsletter</span><span class="handle">Je m'inscris</span></a>
  <nav aria-label="Réseaux sociaux">
    <ul>
{items}
    </ul>
  </nav>
  <footer>Vinsaki SAS · <a href="mailto:contact@themixfr.com">contact@themixfr.com</a></footer>
</main>
<dialog id="nl" aria-labelledby="nl-titre">
  <div class="box" tabindex="-1" autofocus>
    <button class="x" type="button" data-close aria-label="Fermer">×</button>
    <h2 id="nl-titre">La newsletter <span class="nw"><span class="pill">The Mix</span></span></h2>
    <p>Les guides gratuits, l'annonce des prochains événements et une sélection de nos contenus, directement dans ta boîte mail.</p>
    <a class="go" href="{NEWSLETTER_URL}">Recevoir la newsletter</a>
    <button class="later" type="button" data-close>Plus tard</button>
    <small>L'inscription se fait sur app.themixfr.com, avec une confirmation par <span class="nw">e-mail</span>. Tu peux te désinscrire à tout moment.</small>
  </div>
</dialog>
<script>
(function(){{
  var d=document.getElementById('nl'), cta=document.querySelector('.cta'), vu=false;
  if(!d||typeof d.showModal!=='function') return; /* sans <dialog> : le lien mène à la page d'inscription */
  function ouvrir(){{ if(!d.open){{ vu=true; d.showModal(); }} }}
  cta.addEventListener('click', function(e){{ e.preventDefault(); ouvrir(); }});
  d.addEventListener('click', function(e){{ if(e.target===d) d.close(); }});
  Array.prototype.forEach.call(d.querySelectorAll('[data-close]'), function(b){{
    b.addEventListener('click', function(){{ d.close(); }});
  }});
  setTimeout(function(){{ if(!vu) ouvrir(); }}, {POPUP_DELAY_S * 1000});
}})();
</script>
</body>
</html>
"""
(OUT / "index.html").write_text(html, encoding="utf-8")
(OUT / "CNAME").write_text("themixfr.com\n", encoding="utf-8")
print("index.html", len(html.encode()) // 1024, "Ko")
