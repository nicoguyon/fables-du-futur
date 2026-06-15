#!/usr/bin/env python3
"""LUCIDE — génère les plans du film via Seedance 2.0 image-to-video (fal).
Anime les stills déjà générés (URLs hébergées dans assets/ref/_refs.json) → cohérence parfaite.
Usage: python3 film_clips.py [clip_id ...]   (sans arg: tous les manquants)"""
import os, sys, json
import concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trailer"))
from falgen import run, download

ROOT = os.path.dirname(os.path.abspath(__file__))
REFS = json.load(open(os.path.join(ROOT, "assets", "ref", "_refs.json")))
OUT = os.path.join(ROOT, "film", "clips")
os.makedirs(OUT, exist_ok=True)
MODEL = "bytedance/seedance-2.0/image-to-video"
NO = " Subtle, restrained camera move, photoreal, dawn light, calm. No text overlay, no captions, no flicker."

# id : (still_name, duration, prompt)
CLIPS = {
 "c1-oeil": ("manifeste-oeil", "5", "Extreme macro of a human eye, the eyelid lifts almost imperceptibly as a tiny "
   "sunrise glows brighter on the iris; slow push-in."+NO),
 "c2-surenchere": ("journal-surenchere", "6", "Slow lateral dolly gliding past a long wall of dozens of identical "
   "glossy designer glasses under cold light, drifting toward ONE honest rosy acetate pair glowing in warm dawn "
   "light at the end."+NO),
 "c3-acetate": ("hero-acetate", "5", "Dawn light slowly rakes across translucent rose and honey acetate blocks and a "
   "clear lens, caustic glows shifting, a hand-free still life breathing with light."+NO),
 "c4-graving": ("hero-graving", "5", "A laser engraves a tiny precise line of numbers into the inner side of an "
   "eyeglass temple, a thin wisp of smoke rising, shallow focus, slow push-in."+NO),  # déjà généré (test)
 "c5-aube": ("v01-aube", "5", "A pair of translucent rosy acetate eyeglasses on bone-white; slow parallax orbit as a "
   "soft beam of dawn light sweeps across the lenses and the long shadow shifts."+NO),
 "c6-elise": ("ref-elise", "5", "The woman in rosy acetate glasses, very still, takes a soft natural breath and lifts "
   "her eyes calmly toward the lens; honest, un-retouched, warm window light."+NO),
 "c7-marius": ("ref-marius", "5", "The man in tortoiseshell glasses calmly turns his head a few degrees and gives a "
   "small confident look toward camera; dignified, warm dawn light."+NO),
 "c8-counter": ("hero-counter", "5", "An independent optician's counter at dawn; gentle reveal push-in over a wooden "
   "tray of a few frames as morning light grows through the shopfront."+NO),
}

def gen(cid):
    name, dur, prompt = CLIPS[cid]
    out = os.path.join(OUT, f"{cid}.mp4")
    if os.path.exists(out): return cid, "skip"
    if name not in REFS: return cid, f"ERR no still {name}"
    res = run(MODEL, {"prompt": prompt, "image_url": REFS[name], "resolution": "1080p", "duration": dur},
              poll=10, timeout=900, label=cid)
    v = res.get("video", {}).get("url")
    if not v: return cid, "ERR no video"
    download(v, out)
    return cid, "ok"

if __name__ == "__main__":
    # rename existing test clip to c4 if present
    t = os.path.join(OUT, "test-graving.mp4")
    if os.path.exists(t) and not os.path.exists(os.path.join(OUT,"c4-graving.mp4")):
        os.rename(t, os.path.join(OUT, "c4-graving.mp4"))
    want = sys.argv[1:] or [c for c in CLIPS if not os.path.exists(os.path.join(OUT,f"{c}.mp4"))]
    print(f"{len(want)} clips à générer: {want}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for cid, st in ex.map(gen, want):
            print(("✅ " if st in ("ok","skip") else "❌ ")+cid+" "+st, flush=True)
