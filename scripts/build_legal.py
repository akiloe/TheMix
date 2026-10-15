"""Construit les pages légales de themixfr.com :
docs/mentions-legales/index.html et docs/confidentialite/index.html.

Polices et fond : chargés depuis /assets/ (même domaine, copiés par build_attente.py).
Aucun appel externe, aucun cookie, aucun stockage. Pages en noindex jusqu'au lancement.

Les informations manquantes sont écrites entre [[ ]] : elles s'affichent encadrées et le
script les compte. On ne fusionne pas sur main tant qu'il en reste.

Usage : python3 scripts/build_legal.py   (après scripts/build_attente.py)
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
MAJ = "15 octobre 2026"

# ---------------------------------------------------------------- société
SOCIETE = "Vinsaki SAS"
SIEGE = "[[adresse complète du siège (numéro et rue)]], 75008 Paris"
CONTACT = '<a href="mailto:contact@themixfr.com">contact@themixfr.com</a>'

CSS = """
@font-face{font-family:'Figtree';font-weight:400;font-display:swap;src:url(/assets/fonts/figtree-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Figtree';font-weight:600;font-display:swap;src:url(/assets/fonts/figtree-latin-600-normal.woff2) format('woff2')}
@font-face{font-family:'Big Shoulders Display';font-weight:900;font-display:swap;src:url(/assets/fonts/big-shoulders-display-latin-900-normal.woff2) format('woff2')}
:root{--bg:#E5E5E5;--ink:#0D0D0D;--text:#262626;--violet:#6B35D4;--pill:#7B3FE4}
*{box-sizing:border-box}
html{background-color:var(--bg)}
body{margin:0;color:var(--text);background:var(--bg) url(/assets/fond.webp) center top/cover no-repeat fixed;
  font:400 17px/1.6 'Figtree',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
main{max-width:720px;margin:0 auto;padding:40px 16px 56px}
.home{display:inline-block;font:900 28px/1 'Big Shoulders Display',sans-serif;text-transform:uppercase;
  color:var(--ink);text-decoration:none;letter-spacing:.02em}
h1{font:900 clamp(40px,11vw,64px)/calc(1.16em + 10px) 'Big Shoulders Display',sans-serif;text-transform:uppercase;
  color:var(--ink);margin:40px 0 8px;letter-spacing:.005em;overflow-wrap:anywhere}
.maj{margin:0 0 32px;font-size:14px}
h2{font:900 28px/1.2 'Big Shoulders Display',sans-serif;text-transform:uppercase;color:var(--ink);
  margin:40px 0 12px;letter-spacing:.01em}
p,li{margin:0 0 12px}
ul{padding-left:20px;margin:0 0 12px}
a{color:var(--violet);font-weight:600;text-underline-offset:2px;overflow-wrap:anywhere}
a:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
strong{color:var(--ink);font-weight:600}
.carte{border:3px solid var(--violet);border-radius:32px;padding:20px 24px;margin:0 0 16px}
.carte h3{margin:0 0 8px;font:600 18px/1.4 'Figtree',sans-serif;color:var(--ink)}
.carte p{margin:0 0 6px;font-size:16px}
.todo{outline:2px dashed var(--violet);outline-offset:2px;border-radius:4px;color:var(--ink);font-weight:600}
footer{margin-top:56px;font-size:14px}
"""

def page(slug, titre, corps):
    corps_html, n = re.subn(r"\[\[(.+?)\]\]", r'<span class="todo">[à compléter : \1]</span>', corps)
    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre} | The Mix</title>
<meta name="robots" content="noindex">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#E5E5E5">
<style>{CSS}</style>
</head>
<body>
<main>
  <a class="home" href="/">The Mix</a>
  <h1>{titre}</h1>
  <p class="maj">Mise à jour : {MAJ}</p>
{corps_html}
  <footer><a href="/mentions-legales/">Mentions légales</a> · <a href="/confidentialite/">Politique de confidentialité</a> · {CONTACT}</footer>
</main>
</body>
</html>
"""
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(html, encoding="utf-8")
    return n

# ---------------------------------------------------------------- mentions légales
MENTIONS = f"""
  <h2>Éditeur</h2>
  <p>Le site themixfr.com et les pages app.themixfr.com sont édités par <strong>{SOCIETE}</strong>, société par actions simplifiée au capital de 1 000 €, immatriculée au RCS de Paris sous le numéro 106 584 808, dont le siège social est situé {SIEGE}.</p>
  <p>The Mix est une marque exploitée par {SOCIETE}.</p>
  <p>E-mail : {CONTACT}<br>Téléphone : [[numéro de téléphone de l'éditeur]]<br>TVA intracommunautaire : [[numéro de TVA, si la société en a un]]</p>

  <h2>Directeur de la publication</h2>
  <p>Vincent Audou, président de {SOCIETE}.</p>

  <h2>Hébergement</h2>
  <div class="carte">
    <h3>Site themixfr.com</h3>
    <p>GitHub Pages, service de GitHub, Inc.<br>88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis<br>Téléphone : [[téléphone de GitHub, Inc.]]</p>
  </div>
  <div class="carte">
    <h3>Pages app.themixfr.com (inscription, formations)</h3>
    <p>Systeme.io, service d'ITACWT Limited<br>2 Cruise Park Rise, Tyrrelstown, Dublin 15, Irlande<br>Serveurs Amazon Web Services situés en Irlande<br>Téléphone : [[téléphone d'ITACWT Limited]]</p>
  </div>

  <h2>Propriété intellectuelle</h2>
  <p>Les textes, visuels, vidéos, logos et la marque The Mix sont la propriété de {SOCIETE} ou de leurs auteurs. Toute reproduction ou réutilisation sans autorisation écrite est interdite. Les crédits des photos de tiers sont indiqués avec chaque contenu.</p>
  <p>Les polices Big Shoulders Display et Figtree sont utilisées sous licence SIL Open Font License.</p>

  <h2>Données personnelles</h2>
  <p>Voir la <a href="/confidentialite/">politique de confidentialité</a>.</p>
"""

# ---------------------------------------------------------------- confidentialité
CONFIDENTIALITE = f"""
  <p>Cette page explique quelles données The Mix collecte, pourquoi, combien de temps elles sont gardées et comment exercer tes droits.</p>

  <h2>Qui est responsable</h2>
  <p><strong>{SOCIETE}</strong>, éditrice de The Mix, siège social {SIEGE}. Pour toute question sur tes données : {CONTACT}.</p>

  <h2>Ce que nous collectons et pourquoi</h2>
  <div class="carte">
    <h3>Newsletter</h3>
    <p><strong>Données :</strong> ton adresse e-mail, la date de ton inscription et de ta confirmation.</p>
    <p><strong>Pourquoi :</strong> t'envoyer la newsletter (guides gratuits, annonce des événements, sélection de contenus).</p>
    <p><strong>Base légale :</strong> ton consentement, confirmé par le lien reçu par e-mail (double opt-in). Tu peux le retirer à tout moment avec le lien de désinscription présent dans chaque e-mail.</p>
    <p><strong>Durée :</strong> jusqu'à ta désinscription. Si tu n'as interagi avec aucun e-mail pendant 3 ans, nous te demandons si tu veux rester inscrit, puis nous supprimons ton adresse sans réponse de ta part.</p>
  </div>
  <div class="carte">
    <h3>Guides gratuits demandés sur Instagram</h3>
    <p><strong>Données :</strong> ton nom et ton identifiant Instagram, le mot-clé que tu as commenté et les messages échangés.</p>
    <p><strong>Pourquoi :</strong> t'envoyer en message privé le lien du guide que tu as demandé.</p>
    <p><strong>Base légale :</strong> ta demande.</p>
    <p><strong>Durée :</strong> 3 ans après ton dernier message.</p>
  </div>
  <div class="carte">
    <h3>Achat d'une formation</h3>
    <p><strong>Données :</strong> tes nom, prénom et adresse e-mail, ta commande et ton accès à la formation. Les données de paiement sont traitées directement par le prestataire de paiement, [[prestataire de paiement]] ; nous n'avons pas accès à ton numéro de carte.</p>
    <p><strong>Pourquoi :</strong> traiter ta commande, te donner accès à la formation, établir la facture.</p>
    <p><strong>Base légale :</strong> le contrat de vente, et nos obligations comptables pour les factures.</p>
    <p><strong>Durée :</strong> le temps de ton accès à la formation, puis 3 ans ; 10 ans pour les factures.</p>
  </div>
  <div class="carte">
    <h3>Messages envoyés à contact@themixfr.com</h3>
    <p><strong>Pourquoi :</strong> te répondre. <strong>Base légale :</strong> notre intérêt légitime à répondre aux demandes. <strong>Durée :</strong> le temps de traiter ta demande, puis 3 ans au plus.</p>
  </div>

  <h2>Qui reçoit tes données</h2>
  <p>Tes données ne sont ni vendues ni louées. Seuls l'équipe de The Mix et les prestataires techniques suivants y ont accès, pour notre compte :</p>
  <ul>
    <li><strong>Systeme.io</strong> (ITACWT Limited, Irlande ; serveurs en Irlande) : inscriptions, envoi des e-mails et de la newsletter, formations.</li>
    <li><strong>ManyChat</strong> (ManyChat, Inc., États-Unis) : messages privés Instagram.</li>
    <li><strong>IONOS</strong> (IONOS SE, Allemagne) : messagerie contact@themixfr.com.</li>
    <li><strong>GitHub</strong> (GitHub, Inc., États-Unis) : hébergement du site themixfr.com.</li>
  </ul>
  <p>Instagram (Meta) traite aussi les données de ton compte pour son propre compte, selon sa propre politique.</p>

  <h2>Transferts hors de l'Union européenne</h2>
  <p>ManyChat et GitHub sont établis aux États-Unis. Ces transferts sont encadrés par [[base légale des transferts : Data Privacy Framework ou clauses contractuelles types, à vérifier pour chaque prestataire]].</p>

  <h2>Cookies</h2>
  <p><strong>Sur themixfr.com :</strong> aucun cookie, aucun traceur, aucune mesure d'audience. Le pop-up de la newsletter ne mémorise rien.</p>
  <p><strong>Sur app.themixfr.com</strong> (pages Systeme.io) : Systeme.io dépose un cookie nommé « v », d'une durée de 10 ans, dont la finalité est [[finalité du cookie « v » à obtenir auprès de Systeme.io]].</p>

  <h2>Tes droits</h2>
  <p>Tu peux demander l'accès à tes données, leur rectification, leur effacement, leur portabilité ou la limitation de leur traitement, t'opposer à leur traitement, retirer ton consentement à tout moment et définir des directives sur leur sort après ton décès. Écris-nous à {CONTACT} : nous répondons dans un délai d'un mois.</p>
  <p>Si tu estimes que tes droits ne sont pas respectés, tu peux adresser une réclamation à la CNIL (<a href="https://www.cnil.fr">cnil.fr</a>).</p>

  <h2>Modifications</h2>
  <p>Cette politique peut évoluer. La date de mise à jour figure en haut de la page.</p>
"""

total = page("mentions-legales", "Mentions légales", MENTIONS)
total += page("confidentialite", "Politique de confidentialité", CONFIDENTIALITE)
print("mentions-legales/ et confidentialite/ générées")
print(f"À COMPLÉTER : {total} point(s)" if total else "Aucun point à compléter.")
