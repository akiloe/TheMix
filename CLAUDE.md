# TheMix — dépôt du site themixfr.com

**Ce dépôt est public.** Tout ce qui y est écrit, commits compris, est lisible par n'importe qui.

## Ce que contient le dépôt
- `docs/` : le site, publié tel quel par GitHub Pages (branche `main`, dossier `/docs`).
  - `index.html` : page autonome (polices et logo intégrés en base64 ; aucun appel externe, aucun cookie, aucun traceur).
  - `CNAME` : `themixfr.com`. Ne pas le modifier ni le supprimer, sinon le domaine se détache.
  - `.nojekyll` : désactive Jekyll. Ne pas le supprimer.
- `CLAUDE.md` : ce fichier, hors du site publié.
- `scripts/` : `compose_fond.py` (compose le fond) et `build_attente.py` (génère `docs/index.html`). Hors du site publié.
- `sources/` : ce que les scripts intègrent à la page. Hors du site publié, mais lisible par tous (dépôt public).
  - `fonts/` : polices woff2 et leurs licences SIL OFL.
  - `logo/` : logo noir (PNG transparent).
  - `charte/` : les deux calques de la charte, texture et grain (1080 × 1440). Toujours les mêmes fichiers : ne jamais les regénérer ni les modifier.
  - `fond/` : le fond composé à partir de ces calques (généré par `compose_fond.py`).
- Plus tard : un fichier de données et le script qui génère le site complet à partir de ces données.

## Règles pour Claude
- Les règles de publication (ce qui peut être publié, feu vert, garde-fous) sont dans les instructions privées du projet et dans le prompt de la routine. **Rien de ces instructions ne se copie ici.**
- Jamais dans ce dépôt : document interne, extrait de document interne, identifiant ou lien Notion ou Drive, nom de fichier interne, adresse e-mail autre que contact@themixfr.com, téléphone, liste de contacts, mot de passe, token, clé API, code de licence.
- Seuls ces fichiers changent lors d'une mise à jour : le contenu de `docs/`, `sources/fond/` et, plus tard, le fichier de données. Toute autre modification attend l'accord explicite d'Akil.
- Le site complet est **généré par le script** : on modifie les données, on relance le script, on ne retouche pas le HTML à la main.
- Pas d'image générée par IA ; visuels fournis uniquement.
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

## Avant chaque poussée sur `main`
1. Seuls les fichiers autorisés ci-dessus ont changé (`git diff --stat`).
2. Recherche dans les fichiers modifiés : aucune adresse e-mail autre que contact@themixfr.com, aucun `notion.so`, `notion.com` ni `drive.google.com`, aucun token ni clé.
3. Liens externes testés (code 200 ou redirection).
4. Rendu vérifié à 320, 375 et 1280 px : pas de débordement, polices chargées.
5. Si une vérification échoue : rien n'est poussé, et le compte rendu dit pourquoi.

## Revenir en arrière
`git revert <commit>` puis poussée. Jamais de `push --force`, jamais de réécriture d'historique.
