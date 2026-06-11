#!/usr/bin/env python3
"""Fusionne les drafts (lot_*.json) en data/fables.json avec timestamps horaires rétroactifs.
La fable la plus récente reçoit l'heure pile (H:00) la plus récemment passée."""
import json, glob, os, sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS = os.path.join(ROOT, "data", "drafts")
OUT = os.path.join(ROOT, "data", "fables.json")

# Ordre éditorial du recueil initial (I → XII)
ORDER = [
    "corbeau-algorithme", "cigale-serveur", "datacenter-luciole", "androide-forgeron",
    "trois-lois", "ver-cartographe", "souris-labyrinthe", "replicant-papillon",
    "sonde-ocean", "clone-miroir", "vaisseau-jardinier", "enfant-modele",
]

merged = {}
for f in sorted(glob.glob(os.path.join(DRAFTS, "lot_*.json"))):
    data = json.load(open(f, encoding="utf-8"))
    for fa in data["fables"]:
        cur = merged.setdefault(fa["id"], {"id": fa["id"]})
        for k, v in fa.items():
            if k == "id":
                continue
            if v:
                cur[k] = v

missing = [i for i in ORDER if i not in merged]
if missing:
    sys.exit(f"Fables manquantes: {missing}")
for i in ORDER:
    fa = merged[i]
    for lang in ("fr", "en"):
        assert fa.get(lang, {}).get("verses"), f"{i}: {lang} vide"
    assert fa.get("image_prompt"), f"{i}: image_prompt manquant"

now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
fables = []
for idx, fid in enumerate(ORDER):
    fa = merged[fid]
    fa["num"] = idx + 1
    fa["ts"] = (now - timedelta(hours=len(ORDER) - 1 - idx)).strftime("%Y-%m-%dT%H:%M:%SZ")
    fa["image"] = f"img/{fid}.jpg" if os.path.exists(os.path.join(ROOT, "img", f"{fid}.jpg")) else None
    fables.append(fa)

json.dump({"fables": fables}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"OK {len(fables)} fables -> {OUT}")
