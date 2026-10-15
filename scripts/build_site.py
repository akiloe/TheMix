"""Construit le site complet de The Mix (aperçu) : lit data/site.json, écrit docs/apercu/.

Pages : index.html (accueil), articles/index.html (tous les articles),
articles/<slug>/index.html (un article), plus site.css, site.js et img/logo.webp.
Polices et fond : servis depuis /assets/ (copiés par build_attente.py ; ce script n'y touche pas).
Vignettes des podcasts : docs/apercu/img/<id>-640.webp (et <id>-1280.webp si disponible),
téléchargées une fois depuis YouTube et gardées dans le dépôt ; ce script ne les télécharge pas.
Aucun appel externe au chargement : le lecteur YouTube (youtube-nocookie.com) n'est créé qu'au clic.

Usage : python3 scripts/build_site.py [--data data/site.json] [--out docs/apercu]
(--data et --out servent aux essais : données de test, sortie hors du dépôt.)
"""
import argparse, datetime, html, json, math, pathlib, re, shutil

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=str(ROOT / "data" / "site.json"))
ap.add_argument("--out", default=str(ROOT / "docs" / "apercu"))
args = ap.parse_args()
D = json.loads(pathlib.Path(args.data).read_text(encoding="utf-8"))
OUT = pathlib.Path(args.out)
IMG = OUT / "img"
SITE = D["site"]
BASE = SITE["url_base"]  # « /apercu/ »
NL_URL = SITE["newsletter_url"]
POPUP_DELAY_S = 10

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


# ---------- texte ----------
def t(s):
    """Échappe et applique l'espace insécable de la typographie française avant : ; ? !"""
    return re.sub(r" ([:;?!»])", r"&nbsp;\1", html.escape(s, quote=True)).replace("« ", "«&nbsp;")


def a(s):
    """Valeur d'attribut."""
    return html.escape(s, quote=True)


def pill_title(text, word=None):
    """Titre avec `word` en pill (dernière occurrence), lié au mot qui précède par une espace insécable."""
    if not word or word.lower() not in text.lower():
        return t(text)
    i = text.lower().rfind(word.lower())
    before, w, after = text[:i], text[i:i + len(word)], text[i + len(word):]
    before = re.sub(r" ([:;?!])", " \\1", before)
    head, _, last = before.rstrip().rpartition(" ")
    if len(last) > 5:  # mot long : pas lié à la pill (sinon le groupe insécable déborde sur téléphone)
        head, last = before.rstrip(), ""
    lead = (t(head) + " ") if head else ""
    joint = "&nbsp;" if last and before.endswith(" ") else ""
    return f'{lead}<span class="nw">{t(last)}{joint}<span class="pill" data-sweep>{t(w)}</span>{t(after)}</span>'


def date_fr(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f"{d.day}{'er' if d.day == 1 else ''} {MOIS[d.month - 1]} {d.year}"


def duree_txt(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h} h {m:02d}" if h and m else (f"{h} h" if h else f"{m} min")


def hms(d):
    h, m, s = (int(x) for x in d.split(":"))
    return h, m, s


def mots(*textes):
    return sum(len(re.findall(r"\w+", x)) for x in textes)


# ---------- images ----------
def img_size(name):
    with Image.open(IMG / name) as im:
        return im.size


def thumb(ep, sizes, lazy=True):
    i = ep["id"]
    small, big = f"{i}-640.webp", f"{i}-1280.webp"
    if not (IMG / small).exists():
        return None
    w, h = img_size(small)
    srcset = f"{BASE}img/{small} {w}w"
    if (IMG / big).exists():
        srcset += f", {BASE}img/{big} {img_size(big)[0]}w"
    return (f'<img src="{BASE}img/{small}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt=""'
            f'{" loading=\"lazy\"" if lazy else ""} decoding="async">')


def player(ep, sizes, lazy=True):
    im = thumb(ep, sizes, lazy)
    inner = im or '<span class="ph-in">Vignette indisponible</span>'
    return f'''<div class="player" data-yt="{a(ep["id"])}" data-title="{a(ep["titre"])}">
      <button type="button" class="play" aria-label="Lire sur YouTube : {a(ep["titre"])}">{inner}<span class="play-ic" aria-hidden="true"><svg viewBox="0 0 24 24" width="24" height="24"><path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/></svg></span></button>
    </div>'''


def placeholder(label, ratio_class, initial=None):
    if initial:
        return f'<div class="ph {ratio_class} ph-initiale" role="img" aria-label="{a(label)}"><span aria-hidden="true">{t(initial)}</span></div>'
    return f'<div class="ph {ratio_class}" role="img" aria-label="{a(label)}"><span class="ph-in" aria-hidden="true">{t(label)}</span></div>'


# ---------- gabarit commun ----------
def nav_items(home, current=""):
    pre = "" if home else BASE
    items = [("formations", "Formations", f"{pre}#formations", bool(D["formations"]["liste"])),
             ("articles", "Articles", f"{BASE}articles/", True),
             ("podcasts", "Podcasts", f"{pre}#podcasts", bool(D["podcasts"]["episodes"])),
             ("equipe", "Équipe", f"{pre}#equipe", bool(D["equipe"]["membres"]))]
    return "".join(f'<li><a href="{a(h)}"{" aria-current=\"page\"" if k == current else ""}>{t(lbl)}</a></li>'
                   for k, lbl, h, ok in items if ok)


def page(title, desc, body, home=False, current=""):
    logo_href = BASE
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t(title)}</title>
<meta name="description" content="{a(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#E5E5E5">
<link rel="icon" type="image/webp" href="{BASE}img/logo.webp">
<link rel="preload" href="/assets/fonts/big-shoulders-display-latin-900-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/figtree-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{BASE}site.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body{' data-home' if home else ''}>
<a class="skip" href="#contenu">Aller au contenu</a>
<p class="apercu">{t(SITE["bandeau_apercu"])}</p>
<header class="hd wrap">
  <a class="logo" href="{logo_href}"{' aria-current="page"' if home else ''}><img src="{BASE}img/logo.webp" width="164" height="112" alt="The Mix, accueil"></a>
  <nav class="nav" aria-label="Navigation principale">
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <ul class="menu" id="menu">{nav_items(home, current)}</ul>
  </nav>
  <a class="btn-nl" href="{a(NL_URL)}" data-nl aria-haspopup="dialog">Newsletter</a>
</header>
<main id="contenu">
{body}
</main>
{footer()}
{dialog()}
<script src="{BASE}site.js" defer></script>
</body>
</html>
'''


def footer():
    res = "".join(f'<li><a class="lien" href="{a(r["url"])}" rel="noopener" aria-label="The Mix sur {a(r["nom"])} : {a(r["handle"])}">{t(r["nom"])}</a></li>'
                  for r in SITE["reseaux"])
    return f'''<footer class="ft wrap">
  <a class="ft-logo" href="{BASE}"><img src="{BASE}img/logo.webp" width="164" height="112" alt="The Mix, accueil" loading="lazy"></a>
  <div class="ft-cols">
    <p>{t(SITE["editeur"])} · <a class="lien" href="mailto:{a(SITE["contact"])}">{t(SITE["contact"])}</a></p>
    <ul class="ft-res" aria-label="Réseaux sociaux : @themixfr">{res}</ul>
    <p><a class="lien" href="/mentions-legales/">Mentions légales</a> · <a class="lien" href="/confidentialite/">Confidentialité</a></p>
  </div>
</footer>'''


def dialog():
    N = D["newsletter"]
    return f'''<dialog id="nl" aria-labelledby="nl-titre">
  <div class="box" tabindex="-1" autofocus>
    <button class="x" type="button" data-close aria-label="Fermer">×</button>
    <h2 class="t" id="nl-titre">{pill_title(N["titre"] + " " + N["titre_pill"], N["titre_pill"])}</h2>
    <p>{t(N["texte"])}</p>
    <a class="go" href="{a(NL_URL)}">{t(N["bouton"])}</a>
    <small>{t(N["mention"])}</small>
  </div>
</dialog>'''


def sec_title(id_, text, pill=True):
    inner = f'<span class="pill" data-sweep>{t(text)}</span>' if pill else t(text)
    return f'<h2 class="t sec-t" id="{id_}" data-in>{inner}</h2>'


def cta(label, url):
    href = f' href="{a(url)}"' if url else ""
    return f'<a class="cta"{href}>{t(label)}</a>'


# ---------- sections de l'accueil ----------
def hero():
    H = D["entete"]
    return f'''<section class="hero wrap" aria-labelledby="h-titre">
  <h1 class="t" id="h-titre" data-in>{pill_title(H["accroche"], H.get("accroche_pill"))}</h1>
  <p class="lead" data-in>{t(H["phrase"])}</p>
</section>'''


def evenement():
    E = D["evenement"]
    f = E.get("fiche") if E.get("afficher_exemple", True) else None
    if f and f.get("debut"):
        if datetime.datetime.fromisoformat(f["debut"]) < datetime.datetime.now() and not f.get("exemple"):
            f = None
    head = sec_title("e-titre", "Prochain événement", pill=False)
    if not f:
        return f'''<section class="sec wrap ev-sec" id="evenement" aria-labelledby="e-titre">
  {head}
  <div class="ev-vide" data-in>
    <p>{t(E["vide"])}</p>
    <a class="cta" href="{a(NL_URL)}" data-nl aria-haspopup="dialog">Newsletter</a>
  </div>
</section>'''
    dt = datetime.datetime.fromisoformat(f["debut"])
    jour = f'{JOURS[dt.weekday()]} {date_fr(f["debut"])}'
    heure = f'{dt.hour} h {dt.minute:02d}'
    prix = "Gratuit" if not f.get("prix") else f'{f["prix"]} €'
    inter = "".join(f'<li><b>{t(p["nom"])}</b> ({t(p["credits"])})</li>' for p in f.get("intervenants", []))
    tag = '<p class="tag">Exemple</p>' if f.get("exemple") else ""
    visu = (f'<img src="{BASE}img/{a(f["visuel"])}" alt="" width="{img_size(f["visuel"])[0]}" height="{img_size(f["visuel"])[1]}" loading="lazy">'
            if f.get("visuel") else placeholder("Visuel à venir", "r-43"))
    return f'''<section class="sec wrap ev-sec" id="evenement" aria-labelledby="e-titre">
  {head}
  <article class="ev" data-in>
    <div class="ev-visu">{visu}</div>
    <div class="ev-txt">
      {tag}
      <h3 class="t">{t(f["titre"])}</h3>
      <dl class="ev-dl">
        <div><dt>Type</dt><dd>{t(f["type"])}</dd></div>
        <div><dt>Date</dt><dd><time datetime="{a(f["debut"][:10])}">{t(jour)}</time></dd></div>
        <div><dt>Heure</dt><dd><time datetime="{a(f["debut"])}">{t(heure)}</time></dd></div>
        <div><dt>Lieu</dt><dd>{t(f["lieu"])}</dd></div>
        <div><dt>Durée</dt><dd>{t(duree_txt(f["duree_min"]))}</dd></div>
        <div><dt>Prix</dt><dd>{t(prix)}</dd></div>
      </dl>
      <p class="ev-res">{t(f["resume"])}</p>
      <h4 class="mini">Avec</h4>
      <ul class="ev-int">{inter}</ul>
      {cta("Je m'inscris", f.get("inscription_url"))}
    </div>
  </article>
</section>'''


def formations():
    F = D["formations"]
    if not F["liste"]:
        return ""
    cards = ""
    for f in F["liste"]:
        visu = placeholder("Visuel à venir", "r-43") if not f.get("visuel") else \
            f'<img src="{BASE}img/{a(f["visuel"])}" alt="" width="{img_size(f["visuel"])[0]}" height="{img_size(f["visuel"])[1]}" loading="lazy">'
        cards += f'''<article class="f-card" data-in>
    {visu}
    <h3 class="t">{pill_title(f["titre"], f.get("logiciel"))}</h3>
    <ul class="facts"><li><b>{f["modules"]}</b> modules</li><li><b>{t(f["duree"])}</b></li><li>avec {t(" et ".join(f["avec"]))}</li></ul>
    {cta(F["bouton"], f.get("url"))}
    <p class="mention">{t(F["mention"])}</p>
  </article>'''
    return f'''<section class="sec wrap" id="formations" aria-labelledby="f-titre">
  {sec_title("f-titre", F["titre_section"])}
  <p class="stmt" data-in>{t(F["promesse"])}</p>
  <p class="pq" data-in>{t(F["pour_qui"]["texte"])}</p>
  <div class="f-grid">{cards}</div>
</section>'''


def newsletter():
    N = D["newsletter"]
    return f'''<section class="sec wrap" id="newsletter" aria-labelledby="n-titre">
  <div class="nl-bloc" data-in>
    <h2 class="t sec-t" id="n-titre">{pill_title(N["titre"] + " " + N["titre_pill"], N["titre_pill"])}</h2>
    <div class="nl-txt">
      <p>{t(N["texte"])}</p>
      <a class="btn" href="{a(NL_URL)}">{t(N["bouton"])}</a>
      <small>{t(N["mention"])}</small>
    </div>
  </div>
</section>'''


def articles_tries():
    return sorted(D["articles"]["liste"], key=lambda x: x["date"], reverse=True)


def art_card(x, lazy=True, level="h3"):
    href = f'{BASE}articles/{a(x["slug"])}/'
    visu = (f'<img src="{BASE}img/{a(x["image"])}" alt="" width="{img_size(x["image"])[0]}" height="{img_size(x["image"])[1]}"{" loading=\"lazy\"" if lazy else ""}>'
            if x.get("image") else placeholder("Image à fournir", "r-32"))
    return f'''<li class="a-card" data-in>
    <a href="{href}">
      {visu}
      <p class="a-meta"><span class="rub">{t(x["rubrique"])}</span> · <time datetime="{a(x["date"])}">{t(date_fr(x["date"]))}</time></p>
      <{level} class="a-titre">{t(x["titre"])}</{level}>
    </a>
  </li>'''


def articles_home():
    L = articles_tries()[:3]
    if not L:
        return ""
    cards = "".join(art_card(x) for x in L)
    return f'''<section class="sec wrap" id="articles" aria-labelledby="a-titre">
  {sec_title("a-titre", D["articles"]["titre_section"])}
  <ul class="a-grid n{len(L)}">{cards}</ul>
  <p class="more" data-in><a class="lien" href="{BASE}articles/">Tous les articles</a></p>
</section>'''


def dur_iso(d):
    h, m, s = hms(d)
    return f"PT{h}H{m}M{s}S"


def dur_txt(d):
    h, m, _ = hms(d)
    return f"{h} h {m:02d}" if h else f"{m} min"


def podcasts():
    P = D["podcasts"]
    E = P["episodes"]
    if not E:
        return ""
    f = E[0]
    rest = "".join(f'''<li data-in>{player(x, "(min-width: 700px) 33vw, 100vw")}<h3>{t(x["titre"])}</h3><time class="dur" datetime="{dur_iso(x["duree"])}">{dur_txt(x["duree"])}</time></li>'''
                   for x in E[1:])
    grid = f'<ul class="pod-grid">{rest}</ul>' if rest else ""
    return f'''<section class="sec wrap" id="podcasts" aria-labelledby="p-titre">
  {sec_title("p-titre", P["titre_section"])}
  <div class="pod-feat" data-in>{player(f, "(min-width: 1024px) 66vw, 100vw")}<div><h3>{t(f["titre"])}</h3><time class="dur" datetime="{dur_iso(f["duree"])}">{dur_txt(f["duree"])}</time></div></div>
  {grid}
  <div class="pod-foot" data-in><p class="cookies">{t(P["mention_cookies"])}</p>
    <a class="lien" href="{a(P["playlist_url"])}">Toute la playlist</a></div>
</section>'''


def equipe():
    Q = D["equipe"]
    if not Q["membres"]:
        return ""
    cards = ""
    for m in Q["membres"]:
        ph = m.get("photo")
        visu = (f'<img src="{BASE}img/{a(ph)}" alt="{a(m["prenom"])}" width="{img_size(ph)[0]}" height="{img_size(ph)[1]}" loading="lazy">'
                if ph and (IMG / ph).exists() else placeholder(f"Photo de {m['prenom']} à venir", "r-45", m["prenom"][0]))
        if m.get("credits"):
            cr = "".join(f'<li>{t(c["artiste"])}{(" " + t(c["instagram"])) if c.get("instagram") else ""}{(" : " + t(c["projet"])) if c.get("projet") else ""}</li>'
                         for c in m["credits"])
            cr = f'<ul class="cr">{cr}</ul>'
        else:
            cr = f'<p class="cr">{t(m.get("credits_note") or "[crédits à fournir]")}</p>'
        cards += f'''<li class="q-card" data-in>
    {visu}
    <h3 class="t">{t(m["prenom"])}</h3>
    <p class="role">{t(m["role"]["texte"])}</p>
    {cr}
  </li>'''
    return f'''<section class="sec wrap" id="equipe" aria-labelledby="q-titre">
  {sec_title("q-titre", Q["titre_section"])}
  <ul class="q-grid">{cards}</ul>
</section>'''


# ---------- pages ----------
def build_home():
    body = hero() + evenement() + formations() + newsletter() + articles_home() + podcasts() + equipe()
    return page("The Mix : le média du son (aperçu)", D["entete"]["phrase"], body, home=True)


def build_articles_index():
    L = articles_tries()
    if L:
        inner = f'<ul class="a-grid all">{"".join(art_card(x, lazy=k >= 3, level="h2") for k, x in enumerate(L))}</ul>'
    else:
        inner = f'<p class="stmt" data-in>{t(D["articles"]["vide"]["texte"])}</p>'
    body = f'''<section class="sec wrap page-top" aria-labelledby="a-titre">
  <h1 class="t sec-t" id="a-titre" data-in><span class="pill" data-sweep>{t(D["articles"]["titre_section"])}</span></h1>
  {inner}
</section>'''
    return page("Articles : The Mix (aperçu)", "Tous les articles de The Mix.", body, current="articles")


def bloc(b):
    if b["type"] == "p":
        return f'<p>{t(b["texte"])}</p>'
    if b["type"] == "h2":
        return f'<h2 class="t">{t(b["texte"])}</h2>'
    if b["type"] == "citation":
        aut = f'<figcaption>{t(b["auteur"])}</figcaption>' if b.get("auteur") else ""
        return f'<figure class="quote"><blockquote><p>{t(b["texte"])}</p></blockquote>{aut}</figure>'
    raise ValueError(f"bloc inconnu : {b['type']}")


def build_article(x):
    n = mots(x["titre"], x["chapo"], *[b["texte"] for b in x["corps"]])
    lecture = max(1, math.ceil(n / 230))
    visu = (f'<img src="{BASE}img/{a(x["image"])}" alt="{a(x.get("image_alt", ""))}" width="{img_size(x["image"])[0]}" height="{img_size(x["image"])[1]}">'
            if x.get("image") else placeholder("Image à fournir", "r-169"))
    credits = ""
    if x.get("credits"):
        credits = '<section class="credits" aria-labelledby="c-titre"><h2 class="mini" id="c-titre">Crédits</h2><ul>' + \
                  "".join(f"<li>{t(c)}</li>" for c in x["credits"]) + "</ul></section>"
    body = f'''<article class="art wrap page-top">
  <p class="back"><a class="lien" href="{BASE}articles/">Tous les articles</a></p>
  <header class="art-hd">
    <p class="a-meta" data-in><span class="rub">{t(x["rubrique"])}</span></p>
    <h1 class="t{' long' if len(x["titre"]) > 60 else ''}" data-in>{pill_title(x["titre"], x.get("titre_pill"))}</h1>
    <p class="a-by" data-in>Par {t(x["auteur"])} · <time datetime="{a(x["date"])}">{t(date_fr(x["date"]))}</time> · {lecture} min de lecture</p>
    <p class="chapo" data-in>{t(x["chapo"])}</p>
  </header>
  <div class="art-img" data-in>{visu}</div>
  <div class="art-body">
    {"".join(bloc(b) for b in x["corps"])}
    {credits}
  </div>
  <p class="back end"><a class="lien" href="{BASE}articles/">Tous les articles</a></p>
</article>'''
    return page(f'{x["titre"]} : The Mix (aperçu)', x["chapo"], body, current="articles")


# ---------- sortie ----------
OUT.mkdir(parents=True, exist_ok=True)
IMG.mkdir(exist_ok=True)
with Image.open(ROOT / "sources" / "logo" / "logo_the_mix_noir.png") as lg:
    lg.resize((164, round(164 * lg.size[1] / lg.size[0])), Image.LANCZOS).save(IMG / "logo.webp", lossless=True)


# ---------- styles (site.css) ----------
FONT_FACES = "".join(
    f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;"
    f"src:url(/assets/fonts/{pre}-latin-{w}-normal.woff2) format('woff2')}}\n"
    for fam, pre, w in [("Big Shoulders Display", "big-shoulders-display", 900),
                        ("Figtree", "figtree", 400), ("Figtree", "figtree", 600)])

CSS = FONT_FACES + """
/* Charte : fond #E5E5E5 texturé, texte #0D0D0D / #262626, violet #6B35D4 (cadres, liens), #7B3FE4 (pill). */
:root{--bg:#E5E5E5;--ink:#0D0D0D;--text:#262626;--violet:#6B35D4;--pill:#7B3FE4;
  --tone:rgba(13,13,13,.055);--tone2:rgba(13,13,13,.1);--hover:rgba(107,53,212,.08);
  --ease:cubic-bezier(.16,1,.3,1);--g:clamp(16px,4.2vw,56px);--max:1360px}
*{box-sizing:border-box}
html{background:var(--bg);-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;overflow-wrap:break-word;font:400 17px/1.55 'Figtree',system-ui,sans-serif;color:var(--text);-webkit-font-smoothing:antialiased;overflow-x:clip}
body::before{content:"";position:fixed;inset:0;z-index:-1;background:url(/assets/fond.webp) center top/cover no-repeat;pointer-events:none}
img{max-width:100%;height:auto;display:block}
a{color:var(--violet)}
h1,h2,h3,h4{text-wrap:balance}
p{text-wrap:pretty}
:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
.skip{position:absolute;left:8px;top:-80px;z-index:50;background:var(--ink);color:#fff;padding:10px 14px;border-radius:12px}
.skip:focus{top:8px}
.apercu{margin:0;padding:6px var(--g);font-size:13px;line-height:1.4;color:var(--text);background:var(--tone)}
.wrap{max-width:var(--max);margin:0 auto;padding-left:var(--g);padding-right:var(--g)}
/* Titres : interligne unique. Écart mesuré entre le haut d'une pill et l'encre de la ligne du dessus =
   interligne - 1,06 em, soit 16 px à toutes les tailles (règle des 12 px). */
.t{font-family:'Big Shoulders Display',sans-serif;font-weight:900;text-transform:uppercase;color:var(--ink);
  letter-spacing:.005em;line-height:calc(1.06em + 16px);margin:0}
.nw{white-space:nowrap}
.pill{border-radius:16px;padding:.08em .07em .01em;color:#fff;-webkit-box-decoration-break:clone;box-decoration-break:clone;
  background:linear-gradient(var(--pill),var(--pill)) 0 0/100% 100% no-repeat}
.mini{font:600 15px/1.4 'Figtree',sans-serif;color:var(--ink);margin:0}
/* en-tête */
.hd{position:relative;display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;padding-top:14px;padding-bottom:14px}
.logo{border-radius:8px}
.logo img{width:72px}
.nav{margin-left:auto;display:flex;align-items:center}
.menu-btn,.btn-nl,.btn{font:600 15px/1 'Figtree',system-ui,sans-serif;min-height:44px;padding:0 18px;border-radius:999px;border:0;cursor:pointer;
  display:inline-flex;align-items:center;justify-content:center;text-decoration:none;transition:background-color .12s ease,transform .12s ease}
.menu-btn{background:var(--tone);color:var(--ink)}
.btn-nl,.btn{background:var(--pill);color:#fff}
.menu-btn:active,.btn-nl:active,.btn:active,a.cta[href]:active,.play:active,.go:active{transform:scale(.97)}
.menu{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px}
.menu a{display:flex;align-items:center;min-height:44px;padding:0 12px;border-radius:22px;text-decoration:none;color:var(--ink);font-weight:600;font-size:16px}
.menu a[aria-current]{color:var(--violet)}
html:not(.js) .menu-btn{display:none}
@media (max-width:899px){
  html.js .menu{position:absolute;left:var(--g);right:var(--g);top:100%;z-index:20;display:grid;gap:2px;padding:8px;background:var(--bg);
    border:3px solid var(--violet);border-radius:32px;box-shadow:0 12px 32px rgba(13,13,13,.18)}
  html.js .menu[hidden]{display:none}
  html.js .menu a{min-height:56px;padding:0 20px;border-radius:24px;font:900 32px/1 'Big Shoulders Display',sans-serif;text-transform:uppercase}
  html.js .menu.anim{animation:menu-in .2s var(--ease)}
  html:not(.js) .nav{order:3;margin-left:0;width:100%}
}
@keyframes menu-in{from{opacity:0;transform:translateY(-8px)}}
@media (min-width:900px){.menu-btn{display:none}.logo img{width:88px}.nav{margin-right:8px}}
@media (hover:hover) and (pointer:fine){
  .menu a:hover{background:var(--tone)} .menu-btn:hover{background:var(--tone2)} .btn-nl:hover,.btn:hover{background:var(--violet)}
}
/* liens : soulignement qui se trace au survol */
.lien{color:var(--violet);font-weight:600;text-decoration:none;background:linear-gradient(currentColor,currentColor) 0 100%/100% 2px no-repeat;padding-bottom:2px}
@media (hover:hover) and (pointer:fine){.lien{background-size:0 2px;transition:background-size .15s var(--ease)}.lien:hover{background-size:100% 2px}}
/* emplacements d'image (visuel à venir) */
.ph{position:relative;display:grid;place-items:end start;padding:14px 16px;background:var(--tone2);border-radius:20px;color:var(--text);font-size:14px;width:100%}
.r-43{aspect-ratio:4/3}.r-32{aspect-ratio:3/2}.r-169{aspect-ratio:16/9}.r-45{aspect-ratio:4/5}
.ph-initiale{place-items:center}
.ph-initiale span{font:900 clamp(96px,14vw,180px)/1 'Big Shoulders Display',sans-serif;color:var(--ink);opacity:.82}
/* bouton cadre (CTA) */
.cta{display:inline-flex;align-items:center;justify-content:center;min-height:56px;padding:4px 28px 0;border:3px solid var(--violet);border-radius:32px;
  color:var(--ink);text-decoration:none;font:900 22px/1 'Big Shoulders Display',sans-serif;text-transform:uppercase;letter-spacing:.02em;
  transition:background-color .12s ease,transform .12s ease}
a.cta:not([href]){cursor:default}
@media (hover:hover) and (pointer:fine){a.cta[href]:hover{background:var(--hover)}}
.mention{font-size:15px;font-weight:600;color:var(--ink);margin:12px 0 0}
/* sections */
.sec{padding-top:clamp(56px,9vw,128px);padding-bottom:clamp(8px,2vw,16px)}
.sec-t{font-size:clamp(52px,9vw,128px)}
.stmt{font-size:clamp(20px,2.2vw,28px);line-height:1.35;color:var(--ink);max-width:32ch;margin:20px 0 0;font-weight:600}
.pq{max-width:36em;margin:16px 0 0}
.hero{padding-top:clamp(40px,9vw,120px);padding-bottom:clamp(24px,4vw,48px)}
.hero h1{font-size:clamp(64px,14.6vw,200px)}
.hero .lead{font-size:clamp(20px,2.4vw,30px);line-height:1.35;color:var(--ink);max-width:24ch;margin:clamp(20px,3vw,40px) 0 0;font-weight:600}
/* événement */
.ev-sec .sec-t{font-size:clamp(40px,6vw,80px)}
.ev{display:grid;gap:24px;margin-top:clamp(24px,3vw,40px)}
@media (min-width:860px){.ev{grid-template-columns:5fr 7fr;gap:48px;align-items:start}}
.ev-visu img{border-radius:20px}
.tag{display:inline-block;margin:0 0 12px;padding:3px 12px 2px;border:2px solid var(--violet);border-radius:999px;color:var(--violet);font-weight:600;font-size:14px}
.ev h3{font-size:clamp(36px,4.6vw,64px)}
.ev-dl{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:14px 24px;margin:20px 0 0}
.ev-dl div{display:flex;flex-direction:column-reverse}
.ev-dl dt{font-size:14px}
.ev-dl dd{margin:0;font-weight:600;color:var(--ink);font-size:17px}
.ev-res{max-width:36em;margin:20px 0 0;color:var(--ink)}
.ev-txt .mini{margin-top:20px}
.ev-int{list-style:none;margin:6px 0 24px;padding:0;display:grid;gap:4px}
.ev-int b{color:var(--ink);font-weight:600}
.ev-vide{margin-top:24px;padding:clamp(24px,4vw,40px);background:var(--tone);border-radius:32px;display:flex;flex-wrap:wrap;align-items:center;gap:20px 32px}
.ev-vide p{margin:0;font-size:clamp(20px,2.2vw,28px);line-height:1.35;font-weight:600;color:var(--ink);max-width:34ch;flex:1 1 20ch}
/* formations */
.f-grid{display:grid;gap:clamp(48px,4vw,56px);margin-top:clamp(36px,5vw,64px)}
@media (min-width:860px){.f-grid{grid-template-columns:1fr 1fr}}
.f-card h3{font-size:clamp(34px,4.2vw,56px);margin-top:20px}
.facts{list-style:none;margin:14px 0 0;padding:0;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 22px;color:var(--ink);font-size:17px}
.facts b{font:900 30px/1 'Big Shoulders Display',sans-serif;margin-right:4px}
.f-card .cta{margin-top:24px}
/* newsletter */
.nl-bloc{display:grid;min-width:0;gap:20px;padding:clamp(28px,5vw,64px);background:var(--tone);border-radius:32px}
@media (min-width:960px){.nl-bloc{grid-template-columns:7fr 5fr;gap:48px;align-items:end}}
.nl-bloc .sec-t{font-size:clamp(48px,7vw,104px)}
.nl-txt p{margin:0 0 20px;font-size:clamp(18px,1.6vw,21px);line-height:1.45;color:var(--ink)}
.nl-txt .btn{min-height:56px;padding:0 28px;font-size:17px}
.nl-txt small{display:block;margin-top:14px;font-size:14px;line-height:1.5}
/* articles */
.a-grid{list-style:none;margin:clamp(32px,4vw,56px) 0 0;padding:0;display:grid;gap:40px 24px}
@media (min-width:700px){.a-grid.n2,.a-grid.n3,.a-grid.all{grid-template-columns:1fr 1fr}}
@media (min-width:1024px){.a-grid.n3,.a-grid.all{grid-template-columns:repeat(3,1fr)}
  .a-grid.n1 .a-card a{display:grid;grid-template-columns:7fr 5fr;grid-template-rows:1fr auto;gap:0 40px}
  .a-grid.n1 .a-meta{align-self:end}
  .a-grid.n1 .a-card .ph,.a-grid.n1 .a-card img{grid-row:span 2}}
.a-card a{display:block;text-decoration:none;color:var(--ink);border-radius:20px}
.a-card img{border-radius:20px}
.a-meta{margin:14px 0 6px;font-size:14px;color:var(--text)}
.rub{color:var(--violet);font-weight:600}
.a-titre{font:600 clamp(19px,1.7vw,22px)/1.3 'Figtree',sans-serif;margin:0;transition:color .12s ease}
@media (hover:hover) and (pointer:fine){.a-card a:hover .a-titre{color:var(--violet)}}
.more{margin:32px 0 0}
/* podcasts */
.player{position:relative;aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:var(--ink)}
.player iframe,.play{position:absolute;inset:0;width:100%;height:100%;border:0}
.play{padding:0;cursor:pointer;background:var(--ink);color:#fff;transition:transform .12s ease}
.play img{width:100%;height:100%;object-fit:cover}
.play .ph-in{position:absolute;left:16px;top:14px;font-size:14px}
.play-ic{position:absolute;left:16px;bottom:16px;width:56px;height:56px;border-radius:50%;background:var(--pill);color:#fff;display:grid;place-items:center;transition:transform .12s ease}
@media (hover:hover) and (pointer:fine){.play:hover .play-ic{transform:scale(1.08)}}
.pod-feat{display:grid;gap:18px;margin-top:clamp(36px,5vw,64px)}
@media (min-width:1024px){.pod-feat{grid-template-columns:8fr 4fr;align-items:end;gap:32px}}
.pod-feat h3{font:600 clamp(20px,2vw,26px)/1.3 'Figtree',sans-serif;color:var(--ink);margin:0}
.dur{display:block;margin-top:6px;font-variant-numeric:tabular-nums;font-size:15px}
.pod-grid{list-style:none;margin:clamp(40px,5vw,64px) 0 0;padding:0;display:grid;gap:32px}
@media (min-width:700px){.pod-grid{grid-template-columns:repeat(3,1fr);gap:24px}}
.pod-grid h3{font:600 16px/1.4 'Figtree',sans-serif;color:var(--ink);margin:12px 0 0}
.pod-foot{display:flex;flex-wrap:wrap;gap:8px 24px;align-items:baseline;justify-content:space-between;margin-top:28px}
.cookies{font-size:15px;line-height:1.5;margin:0}
/* équipe */
.q-grid{list-style:none;margin:clamp(32px,4vw,56px) 0 0;padding:0;display:grid;gap:32px}
@media (max-width:699px){.q-card{display:grid;grid-template-columns:112px minmax(0,1fr);gap:0 16px;align-items:start}
  .q-card .ph,.q-card img{grid-row:span 3}.q-card .ph-initiale span{font-size:72px}.q-card h3{margin-top:0!important}}
@media (min-width:700px){.q-grid{grid-template-columns:repeat(3,1fr);gap:24px}}
.q-card img{border-radius:20px;aspect-ratio:4/5;object-fit:cover}
.q-card h3{font-size:clamp(40px,4vw,56px);margin-top:16px}
.role{margin:4px 0 0;color:var(--ink);font-weight:600}
.cr{margin:8px 0 0;padding:0;list-style:none;font-size:15px;overflow-wrap:anywhere}
/* page article */
.page-top{padding-top:clamp(24px,5vw,64px)}
.back{margin:0 0 24px}.back.end{margin:56px 0 0}
.art-hd{max-width:980px}
.art-hd .a-meta{margin:0 0 8px;font-size:15px}
.art-hd h1{font-size:clamp(40px,6.4vw,92px)}
.art-hd h1.long{font-size:clamp(34px,4.2vw,60px)}
.a-by{margin:16px 0 0;font-size:15px}
.chapo{margin:20px 0 0;font-size:clamp(20px,2.1vw,26px);line-height:1.4;font-weight:600;color:var(--ink);max-width:40ch}
.art-img{margin:clamp(28px,4vw,48px) 0 0}
.art-img img{border-radius:20px}
.art-body{max-width:38em;margin-top:clamp(28px,4vw,48px)}
.art-body p{font-size:18px;line-height:1.65;margin:0 0 20px}
.art-body h2.t{font-size:clamp(32px,3.6vw,48px);margin:40px 0 12px}
.quote{margin:32px 0;padding:0 0 0 clamp(40px,6vw,64px);position:relative}
.quote::before{content:"«";position:absolute;left:0;top:-.18em;font:900 clamp(64px,8vw,96px)/1 'Big Shoulders Display',sans-serif;color:var(--violet)}
.quote blockquote{margin:0}
.quote blockquote p{font-size:clamp(20px,2.2vw,26px);line-height:1.42;font-weight:600;color:var(--ink);margin:0}
.quote figcaption{margin-top:10px;font-size:15px}
.credits{margin-top:40px;padding:20px 24px;background:var(--tone);border-radius:20px}
.credits ul{margin:8px 0 0;padding-left:18px;font-size:15px}
/* pied */
.ft{margin-top:clamp(80px,10vw,144px);padding-top:32px;padding-bottom:40px;display:grid;gap:24px;font-size:15px;color:var(--text)}
@media (min-width:860px){.ft{grid-template-columns:auto 1fr;align-items:end;gap:48px}}
.ft-logo{justify-self:start;border-radius:8px}.ft-logo img{width:120px}
.ft-cols{display:grid;gap:10px}
@media (min-width:860px){.ft-cols{justify-items:end;text-align:right}}
.ft p{margin:0}
.ft a{display:inline-block;padding:8px 0}
.ft-res{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px 20px}
/* pop-up newsletter (même composant que la page d'attente) */
dialog{padding:0;border:0;background:transparent;max-width:none;max-height:none;width:min(480px,calc(100vw - 32px))}
dialog::backdrop{background:rgba(13,13,13,.55)}
.box{position:relative;background:var(--bg) url(/assets/fond.webp) center top/cover no-repeat;border:3px solid var(--violet);border-radius:32px;
  padding:40px 24px 24px;color:var(--text);max-height:calc(100vh - 32px);max-height:calc(100svh - 32px);overflow:auto}
.box:focus{outline:none}
.box h2{font-size:clamp(40px,11vw,56px);margin:0 0 16px}
.box p{font-size:17px;line-height:1.5;margin:0 0 24px}
.box .go{display:flex;align-items:center;justify-content:center;min-height:56px;padding:12px 24px;border-radius:32px;background:var(--pill);color:#fff;
  text-decoration:none;font-weight:600;font-size:17px;transition:background-color .12s ease,transform .12s ease}
.box .x{position:absolute;top:12px;right:12px;width:44px;height:44px;border:0;border-radius:22px;background:none;color:var(--ink);
  font:600 28px/1 'Figtree',system-ui,sans-serif;cursor:pointer}
@media (hover:hover) and (pointer:fine){.box .go:hover{background:var(--violet)}.box .x:hover{background:var(--hover)}}
.box small{display:block;margin-top:16px;font-size:13px;line-height:1.5}
@media (prefers-reduced-motion:no-preference){
  html.js dialog[open] .box{animation:dlg-in .22s var(--ease)}
  html.js dialog[open]::backdrop{animation:fade-in .22s var(--ease)}
}
@keyframes dlg-in{from{opacity:0;transform:translateY(12px)}}
@keyframes fade-in{from{opacity:0}}
/* entrées à l'écran : une fois, 280 ms, 12 px, décalage de 40 ms ; contenu visible sans JS */
@media (prefers-reduced-motion:no-preference){
  html.js [data-in]:not(.in){opacity:0;transform:translateY(12px)}
  html.js [data-in]{transition:opacity .28s var(--ease),transform .28s var(--ease)}
  html.js .pill[data-sweep]:not(.on){background-size:0% 100%;color:var(--ink)}
  html.js .pill[data-sweep]{transition:background-size .24s var(--ease),color .12s linear .1s}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
"""

JS = r"""(function(){
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* menu mobile : s'ouvre en 200 ms, se ferme avec Échap, un lien ou un clic ailleurs */
  var mb = document.querySelector('.menu-btn'), menu = document.getElementById('menu'), small = matchMedia('(max-width: 899px)');
  function setMenu(open){
    mb.setAttribute('aria-expanded', String(open));
    menu.hidden = small.matches && !open;
    if(open && !reduce){ menu.classList.remove('anim'); void menu.offsetWidth; menu.classList.add('anim'); }
  }
  if(mb && menu){
    setMenu(false);
    small.addEventListener('change', function(){ setMenu(false); });
    mb.addEventListener('click', function(){ setMenu(mb.getAttribute('aria-expanded') !== 'true'); });
    menu.addEventListener('click', function(e){ if(e.target.closest('a') && small.matches) setMenu(false); });
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && mb.getAttribute('aria-expanded') === 'true'){ setMenu(false); mb.focus(); }
    });
    document.addEventListener('click', function(e){
      if(mb.getAttribute('aria-expanded') === 'true' && !e.target.closest('.nav')) setMenu(false);
    });
  }

  /* pop-up newsletter : au clic sur « Newsletter » ; sur l'accueil, aussi après 10 s. Rien n'est mémorisé. */
  var d = document.getElementById('nl'), vu = false;
  if(d && typeof d.showModal === 'function'){
    var ouvrir = function(){ if(!d.open){ vu = true; setMenu && mb && setMenu(false); d.showModal(); } };
    document.querySelectorAll('[data-nl]').forEach(function(b){
      b.addEventListener('click', function(e){ e.preventDefault(); ouvrir(); });
    });
    d.addEventListener('click', function(e){ if(e.target === d) d.close(); });
    d.querySelectorAll('[data-close]').forEach(function(b){ b.addEventListener('click', function(){ d.close(); }); });
    if(document.body.hasAttribute('data-home')) setTimeout(function(){ if(!vu) ouvrir(); }, POPUP_MS);
  }

  /* lecteur YouTube : créé seulement au clic, à la place exacte de la vignette (pas de saut de mise en page) */
  document.addEventListener('click', function(e){
    var b = e.target.closest('.play'); if(!b) return;
    var box = b.parentNode, f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(box.dataset.yt) + '?autoplay=1';
    f.title = 'Lecteur YouTube : ' + box.dataset.title;
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    box.replaceChild(f, b);
    f.focus();
  });

  /* entrées à l'écran, une fois par élément ; balayage de la pill quand son titre entre */
  var els = [].slice.call(document.querySelectorAll('[data-in], .pill[data-sweep]'));
  function show(x){ x.classList.add(x.matches('.pill') ? 'on' : 'in'); }
  if(reduce || !('IntersectionObserver' in window)){ els.forEach(show); return; }
  var io = new IntersectionObserver(function(list){
    var batch = list.filter(function(en){ return en.isIntersecting; }).map(function(en){ return en.target; });
    batch.forEach(function(x, k){
      io.unobserve(x);
      x.style.transitionDelay = x.matches('.pill') ? '120ms' : (Math.min(k, 6) * 40) + 'ms';
      show(x);
      x.addEventListener('transitionend', function(){ x.style.transitionDelay = ''; }, { once: true });
    });
  }, { rootMargin: '0px 0px -6% 0px' });
  els.forEach(function(x){ io.observe(x); });
})();
""".replace("POPUP_MS", str(POPUP_DELAY_S * 1000))

(OUT / "site.css").write_text(CSS.lstrip(), encoding="utf-8")
(OUT / "site.js").write_text(JS, encoding="utf-8")

# Articles : le dossier est entièrement regénéré (un article retiré des données disparaît).
ART = OUT / "articles"
if ART.exists():
    shutil.rmtree(ART)
ART.mkdir()
(OUT / "index.html").write_text(build_home(), encoding="utf-8")
(ART / "index.html").write_text(build_articles_index(), encoding="utf-8")
slugs = set()
for x in D["articles"]["liste"]:
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", x["slug"]) or x["slug"] in slugs:
        raise SystemExit(f"slug invalide ou en double : {x['slug']!r}")
    slugs.add(x["slug"])
    (ART / x["slug"]).mkdir()
    (ART / x["slug"] / "index.html").write_text(build_article(x), encoding="utf-8")

# Ce qui reste provisoire (affiché à chaque construction).
prov = []
def walk(o, path):
    if isinstance(o, dict):
        if o.get("a_valider"): prov.append(f"à valider : {path}")
        if o.get("a_verifier"): prov.append(f"à vérifier : {path}")
        if o.get("exemple"): prov.append(f"exemple factice : {path}")
        for k, v in o.items(): walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, f"{path}[{i}]")
walk(D, "")
total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
print(f"{OUT} : {len(slugs)} article(s), {total // 1024} Ko au total")
print("\n".join(prov) if prov else "Rien de provisoire.")
