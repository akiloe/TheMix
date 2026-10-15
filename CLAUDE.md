# TheMix — dépôt du site themixfr.com

**Ce dépôt est public.** Tout ce qui y est écrit, commits compris, est lisible par n'importe qui.

## Ce que contient le dépôt
- `docs/` : le site, publié tel quel par GitHub Pages (branche `main`, dossier `/docs`).
  - `index.html` : page autonome (polices et logo intégrés en base64). Seule exception aux appels externes : le formulaire d'inscription à la newsletter et son pop-up, fournis par Systeme.io (script collé tel quel), ajoutés ou modifiés uniquement avec l'accord explicite d'Akil. Aucun autre appel externe, aucun traceur. Si ce script dépose un cookie soumis à consentement, il ne se charge qu'après acceptation, via un bandeau validé par Akil.
    Pop-up newsletter actuel (choix d'Akil du 15/10/2026) : fenêtre maison (`<dialog>`), sans script externe ni stockage, qui renvoie vers la page d'inscription `https://app.themixfr.com/newsletter` ; ouverture une fois par chargement de page après 10 s, et au clic sur le bouton « Newsletter ».
  - `assets/` : polices (avec leurs licences SIL OFL) et fond, copiés par `build_attente.py`. Les pages Systeme.io d'`app.themixfr.com` chargent désormais leurs polices et leur fond depuis les fichiers Systeme.io ; garder ces copies (ne pas les supprimer ni les renommer sans accord d'Akil).
  - `mentions-legales/` et `confidentialite/` : pages légales générées par `scripts/build_legal.py` (polices et fond chargés depuis `/assets/`, aucun appel externe). Les informations manquantes sont écrites `[[…]]` dans le script ; on ne pousse pas sur `main` tant que le script signale des points à compléter.
  - `apercu/` : aperçu du site complet (https://themixfr.com/apercu/, `noindex, nofollow`), généré par `scripts/build_site.py` à partir de `data/site.json` : accueil, page Articles, pages d'article, `site.css`, `site.js`, `img/`. Polices et fond chargés depuis `/assets/`. Aucun appel externe au chargement ; seule exception, le lecteur YouTube (`youtube-nocookie.com`), créé quand le visiteur clique sur lecture. Les vignettes des podcasts sont dans `apercu/img/` (téléchargées une fois depuis YouTube, gardées dans le dépôt) ; le script ne les télécharge pas.
  - `CNAME` : `themixfr.com`. Ne pas le modifier ni le supprimer, sinon le domaine se détache.
  - `.nojekyll` : désactive Jekyll. Ne pas le supprimer.
- `CLAUDE.md` : ce fichier, hors du site publié.
- `scripts/` : `compose_fond.py` (compose le fond), `build_attente.py` (génère `docs/index.html` et `docs/assets/`), `build_legal.py` (génère les pages légales) et `build_site.py` (génère `docs/apercu/`). Hors du site publié.
- `data/site.json` : les données du site complet (textes, formations, podcasts, articles, équipe). Hors du site publié, mais lisible par tous. Un texte provisoire porte `"a_valider": true`, une information trouvée en ligne `"a_verifier": true` avec sa source, un contenu factice `"exemple": true`.
- `sources/` : ce que les scripts intègrent à la page. Hors du site publié, mais lisible par tous (dépôt public).
  - `fonts/` : polices woff2 et leurs licences SIL OFL.
  - `logo/` : logo noir (PNG transparent).
  - `charte/` : les deux calques de la charte, texture et grain (1080 × 1440). Toujours les mêmes fichiers : ne jamais les regénérer ni les modifier.
  - `fond/` : le fond composé à partir de ces calques (généré par `compose_fond.py`).

## Règles pour Claude
- Les règles de publication (ce qui peut être publié, feu vert, garde-fous) sont dans les instructions privées du projet et dans le prompt de la routine. **Rien de ces instructions ne se copie ici.**
- Jamais dans ce dépôt : document interne, extrait de document interne, identifiant ou lien Notion ou Drive, nom de fichier interne, adresse e-mail autre que contact@themixfr.com, téléphone (sauf ceux que la loi impose dans les mentions légales : éditeur et hébergeurs), liste de contacts, mot de passe, token, clé API, code de licence.
- Seuls ces fichiers changent lors d'une mise à jour : le contenu de `docs/` (dont `docs/apercu/`), `sources/fond/` et `data/site.json`. Toute autre modification attend l'accord explicite d'Akil.
- `build_attente.py` doit toujours produire un `docs/index.html` identique octet pour octet tant que la page d'attente reste en ligne : le site complet ne la modifie pas.
- Le site complet est **généré par le script** : on modifie `data/site.json`, on relance `python3 scripts/build_site.py`, on ne retouche jamais `docs/apercu/` à la main.
- Pas d'image générée par IA ; visuels fournis uniquement. **Exception provisoire** (décision d'Akil du 15/10/2026, sous sa responsabilité) : les photos de l'équipe peuvent être des photos trouvées en ligne, de préférence publiées par la personne elle-même, avec leur URL d'origine notée dans `data/site.json` ; elles sont remplacées avant le lancement par des photos dont The Mix a les droits. Sans photo, l'emplacement montre l'initiale.
- Polices : Big Shoulders Display (800, 900) et Figtree (400, 600), licence SIL OFL, intégrées en base64.
- Fond (décision d'Akil du 14/10/2026) : gris `#E5E5E5` avec grain 5 % (mode Normal) et texture 7 % (mode Produit), composés par `scripts/compose_fond.py` à partir de `sources/charte/`. Le rendu moyen est un peu plus foncé que `#E5E5E5`, comme sur les posts.
- Couleurs : texte `#0D0D0D` et `#262626` (jamais `#6B6B6B` pour du texte sur ce fond : contraste insuffisant), violet `#6B35D4` (cadres, liens) et `#7B3FE4` (pill, texte blanc). Pas de vert.
- Pill : `border-radius: 16px`, padding `0.08em 0.07em 0.01em` ; au moins 12 px entre le haut de la pill et la ligne au-dessus, obtenus en augmentant l'interligne. Cadre outline : 3 px `#6B35D4`, `border-radius: 32px`. Pas de filet horizontal.
- Mobile d'abord : aucune barre de défilement horizontale de 320 à 1280 px de large.
- Page en `noindex` jusqu'au lancement de mi-novembre 2026 ; à retirer seulement sur instruction d'Akil.

## Construire la page d'attente
```
pip install pillow numpy          # si besoin
python3 scripts/compose_fond.py sources/charte/TEXTURE_THE_MIX_Metal051C_1080x1440.png sources/charte/GRAIN_THE_MIX_1080x1440.png sources/fond/fond_attente.webp couvrant
python3 scripts/build_attente.py
```
On ne retouche jamais `docs/index.html` à la main : on modifie le script, puis on le relance.

## Construire l'aperçu du site complet
```
python3 scripts/build_site.py     # lit data/site.json, écrit docs/apercu/, liste ce qui reste provisoire
```

## Avant chaque poussée sur `main`
1. Seuls les fichiers autorisés ci-dessus ont changé (`git diff --stat`).
2. Recherche dans les fichiers modifiés : aucune adresse e-mail autre que contact@themixfr.com, aucun `notion.so`, `notion.com` ni `drive.google.com`, aucun token ni clé.
3. Liens externes testés (code 200 ou redirection).
4. Rendu vérifié à 320, 375 et 1280 px (et 768 px pour `docs/apercu/`) : pas de débordement, polices chargées, aucune requête externe au chargement ; `docs/index.html` inchangé.
5. Si une vérification échoue : rien n'est poussé, et le compte rendu dit pourquoi.

## Revenir en arrière
`git revert <commit>` puis poussée. Jamais de `push --force`, jamais de réécriture d'historique.
