#!/usr/bin/env python3
"""Anime les 6 keyframes en plans vidéo via Seedance 2.0 image-to-video (fal.ai), 4K, 5 s.

Usage:
  python3 gen_clips.py            # tous les plans manquants
  python3 gen_clips.py 2 5       # seulement ces plans
"""
import base64, concurrent.futures as cf, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "trailer"))
from falgen import run, download, KEY

KEYFRAMES = os.path.join(ROOT, "keyframes")
CLIPS = os.path.join(ROOT, "clips")
MODEL = "bytedance/seedance-2.0/image-to-video"

HUD_LOCK = (" The video-game HUD overlay (minimap, on-screen texts, money counter, wanted stars) stays "
            "perfectly static, fixed to the screen, unchanged for the whole shot. Photorealistic AAA "
            "video-game render, GTA VI look, saturated sunset colors, heat haze.")

MOTION = {
    1: "Cinematic game title screen coming alive: the big title lettering stays perfectly fixed while the "
       "scene breathes behind it — the chubby kid slowly raises his water gun and smirks at the camera, "
       "pigeons fly across the pink sky, heat haze shimmers, crowds move gently on the quays, slow subtle "
       "push-in." + HUD_LOCK,
    2: "Third-person video-game gameplay: the chubby kid rides his kick scooter with the green bistro chair "
       "mounted on it, rolling forward fast along the canal quay, the game camera tracking smoothly behind "
       "him, cyclists swerve out of his way, he looks back over his shoulder grinning at the camera, "
       "sunlight flickering through the plane trees." + HUD_LOCK,
    3: "In-game cutscene: the chubby kid fires a powerful continuous jet of water from his super-soaker "
       "point-blank into the cyclist's face, the cyclist flinches and nearly falls off his bike, water "
       "spraying everywhere in golden light, the café crowd bursts out laughing, the green '+2 €' popup "
       "gently pulses." + HUD_LOCK,
    4: "Epic action shot: the chubby kid sweeps his massive water jet across the two French police officers "
       "who recoil and shield their faces, water droplets sparkling in slow motion in the golden sunset "
       "light, pigeons scattering into the sky, the crowd on the footbridge cheers and films with phones."
       + HUD_LOCK,
    5: "The chubby kid drops from the footbridge into the canal in slow motion, arms spread wide holding "
       "his water gun, and lands in a giant cannonball splash that soaks the quay, the huge crowd cheers "
       "and films with raised smartphones, water spray catching the sunset light, slight camera shake on "
       "impact." + HUD_LOCK,
    6: "Cinematic outro: slow dolly-out from the soaked chubby kid lounging like a king on the bistro chair "
       "mounted on his scooter, he gives a satisfied nod to the camera, steam rises from the hot "
       "cobblestones, the sunset glows and shimmers on the canal. The title text stays perfectly fixed and "
       "unchanged. Strictly NO video-game HUD, no minimap, no menus, no interface elements, no extra text "
       "of any kind appears at any moment — clean cinematic image with only the existing title. "
       "Photorealistic AAA video-game render, GTA VI look, saturated sunset colors, heat haze.",
}


def data_uri(path):
    """Encode la keyframe en data URI JPEG (rest.fal.run bloqué par le proxy réseau)."""
    jpg = path.replace(".png", ".jpg")
    if not os.path.exists(jpg):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-q:v", "2", jpg], check=True)
    with open(jpg, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def one(n):
    img_url = data_uri(os.path.join(KEYFRAMES, f"plan{n}.png"))
    res = run(MODEL, {
        "prompt": MOTION[n],
        "image_url": img_url,
        "aspect_ratio": "16:9",
        "resolution": "4k",
        "duration": "5",
        "bitrate_mode": "high",
        "generate_audio": True,
    }, label=f"plan{n}", timeout=2400, poll=10)
    url = res["video"]["url"]
    out = os.path.join(CLIPS, f"plan{n}.mp4")
    download(url, out)
    return n, url


if __name__ == "__main__":
    want = [int(x) for x in sys.argv[1:]] or sorted(MOTION)
    todo = [n for n in want if not os.path.exists(os.path.join(CLIPS, f"plan{n}.mp4"))]
    print(f"{len(todo)} plans à générer: {todo}", flush=True)
    os.makedirs(CLIPS, exist_ok=True)
    manifest_path = os.path.join(CLIPS, "clips.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fut in cf.as_completed([ex.submit(one, n) for n in todo]):
            try:
                n, url = fut.result()
                manifest[f"plan{n}"] = url
                json.dump(manifest, open(manifest_path, "w"), indent=2)
                print(f"✅ plan {n} -> clips/plan{n}.mp4", flush=True)
            except Exception as e:
                print(f"❌ {e}", flush=True)
    print("Terminé:", sorted(manifest))
