#!/usr/bin/env python3
"""Anime scene-times-square.png en vidéo via Seedance 2.0 image-to-video (fal).

Mouvement caméra : vue plongeante vers les trois persos, puis montée/poussée
vers la tour (gratte-ciel) derrière eux.

Clé fal lue dans FAL_KEY ou /root/.fal_key (cf. trailer/falgen.py).
Usage : python3 seedance/gen_clip.py
"""
import os, sys, json, mimetypes, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "trailer"))
from falgen import run, download, KEY  # noqa: E402

MODEL = "bytedance/seedance-2.0/image-to-video"
STILL = os.path.join(ROOT, "scene-times-square.png")
OUT = os.path.join(ROOT, "clips", "times-square-plongee.mp4")

PROMPT = (
    "High-angle aerial shot looking straight down on a busy Times Square crosswalk at dusk. "
    "The camera slowly cranes down toward the three central characters who hold their dynamic "
    "action poses: a battle-scarred metallic velociraptor, a rugged adventurer in a red cap and "
    "dark-red jacket, and a weathered pirate captain shouldering a large brass spyglass-cannon. "
    "Then the camera tilts up and pushes forward past them, rising toward the towering illuminated "
    "skyscraper directly behind, its giant glowing billboards and antenna-topped roof filling the "
    "frame. Cinematic photoreal, golden-blue dusk light, neon reflections on wet asphalt, crowds "
    "and yellow cabs drifting. One smooth continuous camera move. "
    "No text overlay, no captions, no flicker, characters stay consistent, no morphing."
)


def upload(path):
    """Upload un fichier local vers le storage fal, renvoie l'URL hébergée."""
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    init = urllib.request.Request(
        "https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
        data=json.dumps({"content_type": ctype, "file_name": os.path.basename(path)}).encode(),
        method="POST",
        headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(init, timeout=60) as r:
        info = json.load(r)
    with open(path, "rb") as f:
        put = urllib.request.Request(info["upload_url"], data=f.read(), method="PUT",
                                     headers={"Content-Type": ctype})
        urllib.request.urlopen(put, timeout=300)
    return info["file_url"]


if __name__ == "__main__":
    if os.path.exists(OUT):
        print("déjà généré:", OUT)
        sys.exit(0)
    print("upload de l'image…", flush=True)
    image_url = upload(STILL)
    print("image_url:", image_url, flush=True)
    res = run(MODEL, {
        "prompt": PROMPT,
        "image_url": image_url,
        "resolution": "1080p",
        "duration": "8",
    }, poll=10, timeout=1200, label="times-square-plongee")
    url = res.get("video", {}).get("url")
    if not url:
        raise SystemExit("pas de vidéo: " + json.dumps(res)[:500])
    download(url, OUT)
    print("✅", OUT)
    print("URL hébergée:", url)
