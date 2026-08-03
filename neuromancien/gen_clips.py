#!/usr/bin/env python3
"""Anime les 6 keyframes en plans vidéo via Seedance 2.0 image-to-video (fal.ai), 4K, 5 s.

Usage:
  python3 gen_clips.py            # tous les plans manquants
  python3 gen_clips.py 2 5        # seulement ces plans
  AR=916 python3 gen_clips.py     # version verticale 9:16
"""
import base64, concurrent.futures as cf, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "trailer"))
from falgen import run, download

VERTICAL = os.environ.get("AR") == "916"
KEYFRAMES = os.path.join(ROOT, "keyframes-916" if VERTICAL else "keyframes")
CLIPS = os.path.join(ROOT, "clips-916" if VERTICAL else "clips")
ASPECT = "9:16" if VERTICAL else "16:9"
MODEL = "bytedance/seedance-2.0/image-to-video"

LOOK = (" Prestige cyberpunk TV-series teaser look, Blade Runner 2049 lighting, heavy rain, "
        "teal-and-magenta neon palette, volumetric haze, film grain, cinematic and slow. "
        "No text appears or changes at any moment.")

MOTION = {
    1: "Cold open coming alive: the TV-static sky flickers like a dead channel, rain falls "
       "steadily, holographic koi glide over the black water, neon reflections ripple, a distant "
       "drone searchlight sweeps slowly, very slow cinematic push-in toward the green footbridge."
       + LOOK,
    2: "Extreme close-up: the man's eyes track lines of holographic code, the screens' glow "
       "shifts across his face, the temple implant pulses gently, he exhales slowly, rain streaks "
       "the porthole behind him, micro push-in on his eyes." + LOOK,
    3: "The man walks steadily straight toward the camera in the rain, trench flowing, the camera "
       "dollying backward at his pace, luminous umbrellas of passers-by drifting past in bokeh, a "
       "drone searchlight sweeping across the wet cobblestones behind him." + LOOK,
    4: "Surreal dive: he slots the cable into the jack behind his ear, the wireframe half of his "
       "face shimmers and spreads slightly, data streams rise like reverse rain, the neon vector "
       "grid behind his eye rushes toward the horizon, slow rotating camera move." + LOOK,
    5: "Epic scale: the colossal golden holographic face slowly opens its eyes and tilts down "
       "toward the tiny silhouette on the footbridge, suspended raindrops sparkling in its light, "
       "the silhouette stands perfectly still, slow majestic crane-down." + LOOK,
    6: "Title outro: the man holds the camera's gaze and lets a faint smirk grow, rain and neon "
       "shimmering behind him, a slow subtle push-in. The title lettering «NEUROMANCIEN» and the "
       "small credit texts stay perfectly fixed, static, unchanged for the whole shot."
       + LOOK,
}


def data_uri(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def one(n):
    res = run(MODEL, {
        "prompt": MOTION[n],
        "image_url": data_uri(os.path.join(KEYFRAMES, f"plan{n}.png")),
        "aspect_ratio": ASPECT,
        "resolution": "4k",
        "duration": "5",
        "bitrate_mode": "high",
        "generate_audio": True,
    }, label=f"plan{n}", timeout=2400, poll=10)
    download(res["video"]["url"], os.path.join(CLIPS, f"plan{n}.mp4"))
    return f"✅ plan{n}.mp4"


if __name__ == "__main__":
    want = [int(x) for x in sys.argv[1:]] or sorted(MOTION)
    todo = [n for n in want if not os.path.exists(os.path.join(CLIPS, f"plan{n}.mp4"))]
    print(f"{len(todo)} plans à générer: {todo}", flush=True)
    os.makedirs(CLIPS, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(one, todo):
            print(r, flush=True)
