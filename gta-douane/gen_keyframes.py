#!/usr/bin/env python3
"""Génère les 6 images de départ (keyframes) du film "GTA : La Douane" avec GPT Image 2.

Usage:
  python3 gen_keyframes.py            # tous les plans manquants
  python3 gen_keyframes.py 1 4       # seulement ces plans
"""
import base64, concurrent.futures as cf, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "keyframes")
KEY = os.environ["OPENAI_API_KEY"]

# Le personnage : stylisé "jeu vidéo", inspiré du phénomène, pas un portrait réel.
DOUANE = (
    "LA DOUANE, a fictional video-game character: a chubby, stocky 14-year-old Parisian street kid "
    "with a round face, full cheeks and a solid husky build that he carries with total swagger, "
    "short buzz cut with faded sides, big charismatic mischievous grin, white tank top stretched "
    "over his belly, black football shorts, white socks in slide sandals, a small crossbody bag "
    "worn across the chest, holding a huge fluorescent orange-and-yellow super-soaker water gun"
)

STYLE = (
    "Official GTA VI key art style: painterly-realistic AAA video game render, ultra-saturated warm "
    "colors, Miami-style sunset gradient sky from hot pink to orange to violet, crisp rim lighting, "
    "glossy summer heat haze, subtle film grain, cinematic composition. Setting: Canal Saint-Martin "
    "in Paris — the green iron footbridge, canal lock gates, plane trees, Haussmann facades, a moored "
    "barge, crowds having drinks on the stone quays. Scorching 2026 heatwave. "
)

HUD = (
    "Authentic GTA gameplay HUD overlaid on the image: a small round minimap in the bottom-left "
    "corner showing the canal as a blue line with a white player arrow, "
)

SHOTS = {
    1: STYLE + "Video game cover key art, no HUD. " + DOUANE + " poses like a GTA cover protagonist, "
       "water gun held across his chest, standing on the quay in front of the green iron footbridge, "
       "heat haze rising, pigeons flying. Bold title lettering in the exact iconic GTA VI pink-to-orange "
       "gradient neon logo style, large across the sky: \"GTA\" with below it \"LA DOUANE\". Smaller "
       "clean white subtitle text at the bottom: \"ÉDITION SPÉCIALE CANAL SAINT-MARTIN\" and beneath it "
       "\"ÉTÉ 2026 · CANICULE\". The text must be spelled exactly as given.",

    2: STYLE + HUD + "and yellow mission text at the bottom center reading exactly \"LA DOUANE DU CANAL\", "
       "and a green money counter in the top right reading \"2,00 €\". Third-person over-the-shoulder "
       "gameplay screenshot, camera behind the character: " + DOUANE + " rides a kick scooter at speed "
       "along the Quai de Valmy, a green bistro chair strapped onto the scooter deck in front of him, "
       "startled cyclists swerving away, motion blur on the ground.",

    3: STYLE + HUD + "and a green popup text \"+2 €\" near the center right. Cinematic in-game cutscene: "
       + DOUANE + " aims his water gun point-blank at a stopped middle-aged cyclist in lycra and helmet, "
       "next to a handwritten cardboard sign on a pole reading exactly \"PÉAGE 2€\", on the cobblestone "
       "quay by the canal lock, amused crowd watching from café terraces in the background.",

    4: STYLE + HUD + "and three white wanted stars glowing in the top-right corner. Action shot: "
       + DOUANE + " sprays a massive arc of water from his super-soaker at two French police officers "
       "in navy uniforms who shield themselves, backlit water droplets frozen in golden sunset light, "
       "pigeons scattering into the air, spectators laughing on the footbridge behind.",

    5: STYLE + HUD + "and small white text at the bottom reading exactly \"MISSION ACCOMPLIE\". Epic wide "
       "gameplay shot: " + DOUANE + " captured mid-air doing a backflip off the green iron footbridge "
       "into the canal, arms spread, water gun still in hand, a huge splash crown rising below him, a "
       "dense crowd on the bridge and quays filming with raised smartphones, blazing sunset reflections "
       "on the water.",

    6: STYLE + "No HUD. Outro shot: " + DOUANE + ", soaking wet and triumphant, sits like a king on the "
       "green bistro chair mounted on his kick scooter in the middle of the empty quay, water gun resting "
       "on his shoulder, dramatic backlit silhouette against the blazing pink-orange sunset over the canal, "
       "steam rising from the hot cobblestones. Clean white title text centered in the sky reading exactly "
       "\"PROCHAINEMENT\" and below it smaller \"ÉTÉ 2026 · CANICULE\".",
}


def gen(n):
    body = json.dumps({
        "model": "gpt-image-2",
        "prompt": SHOTS[n],
        "size": "1536x864",
        "quality": "high",
        "output_format": "png",
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body, method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        res = json.load(resp)
    img = base64.b64decode(res["data"][0]["b64_json"])
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"plan{n}.png")
    with open(path, "wb") as f:
        f.write(img)
    return n, path


if __name__ == "__main__":
    want = [int(x) for x in sys.argv[1:]] or sorted(SHOTS)
    todo = [n for n in want if not os.path.exists(os.path.join(OUT, f"plan{n}.png"))]
    print(f"{len(todo)} keyframes à générer: {todo}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fut in cf.as_completed([ex.submit(gen, n) for n in todo]):
            try:
                n, path = fut.result()
                print(f"✅ plan {n} -> {path}", flush=True)
            except Exception as e:
                print(f"❌ {type(e).__name__}: {e}", flush=True)
    print("Terminé.")
