"""Compose le fond du site à partir des deux calques de la charte (toujours les mêmes fichiers,
jamais regénérés) : fond #E5E5E5, grain 5 % en mode Normal, texture 7 % en mode Produit.

Usage (depuis la racine du dépôt) :
  python3 scripts/compose_fond.py TEXTURE.png GRAIN.png SORTIE.webp [couvrant|motif] [qualité WebP, 88 par défaut]

- couvrant : le calque entier 1080 x 1440, affiché en « cover » (page d'une seule hauteur d'écran).
- motif    : un quart du calque, raccordé par miroir en 1080 x 1440, répété sans couture (pages longues).
Dépendances : Pillow et numpy (pip install pillow numpy).
"""
import pathlib
import sys

import numpy as np
from PIL import Image

tex_p, grain_p, out_p = sys.argv[1:4]
mode = sys.argv[4] if len(sys.argv) > 4 else "couvrant"
qualite = int(sys.argv[5]) if len(sys.argv) > 5 else 88
if mode not in ("couvrant", "motif"):
    sys.exit("mode inconnu : couvrant ou motif")

BASE = np.array([0xE5, 0xE5, 0xE5], dtype=np.float64) / 255.0

tex = np.asarray(Image.open(tex_p).convert("L"), dtype=np.float64) / 255.0
grain = np.asarray(Image.open(grain_p).convert("L"), dtype=np.float64) / 255.0
if tex.shape != (1440, 1080) or grain.shape != (1440, 1080):
    sys.exit(f"calques attendus en 1080 x 1440 : texture {tex.shape[::-1]}, grain {grain.shape[::-1]}")

if mode == "motif":
    tex, grain = tex[:720, :540], grain[:720, :540]

h, w = tex.shape
b = np.broadcast_to(BASE, (h, w, 3))
img = b * 0.95 + grain[..., None] * 0.05          # 1. grain, mode Normal, 5 %
img = img * (1 - 0.07 + 0.07 * tex[..., None])     # 2. texture, mode Produit, 7 %
out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)

if mode == "motif":
    top = np.concatenate([out, out[:, ::-1]], axis=1)
    out = np.concatenate([top, top[::-1, :]], axis=0)

pathlib.Path(out_p).parent.mkdir(parents=True, exist_ok=True)
Image.fromarray(out, "RGB").save(out_p, "WEBP", quality=qualite, method=6)
moy = out.reshape(-1, 3).mean(axis=0).round().astype(int)
print(f"{out_p} : {out.shape[1]} x {out.shape[0]} px, couleur moyenne #{moy[0]:02X}{moy[1]:02X}{moy[2]:02X}")
