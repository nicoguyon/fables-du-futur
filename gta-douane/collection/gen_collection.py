#!/usr/bin/env python3
"""Collection capsule LA DOUANE × LUDOVIC ROTH — réimagine 6 pièces du designer
dans l'univers GTA canal Saint-Martin via GPT Image 2 (endpoint edits, haute fidélité).

Usage:
  python3 gen_collection.py           # toutes les pièces manquantes
  python3 gen_collection.py apollo   # une pièce précise
"""
import base64, concurrent.futures as cf, json, os, sys, urllib.request, uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(ROOT, "refs")
OUT = os.path.join(ROOT, "art")
KEY = os.environ["OPENAI_API_KEY"]

UNIVERS = (
    "Reimagine this exact designer piece — keep its design, proportions, materials and finishes "
    "perfectly faithful — as the hero of a luxury advertising campaign set in the GTA VI key art "
    "universe of 'LA DOUANE': Canal Saint-Martin in Paris during the scorching 2026 heatwave, "
    "ultra-saturated Miami sunset gradient sky from hot pink to orange, green iron footbridge, "
    "lock gates, plane trees, Haussmann facades, painterly-realistic AAA video game render, "
    "crisp rim light, heat haze, subtle film grain, cinematic editorial composition. "
)

PIECES = {
    "apollo": UNIVERS + "The Apollo table (clear acrylic top with copper cylinder crossbars, full-size "
        "dining table version) stands in majesty in the middle of the cobbled quay at golden hour, "
        "dressed for a chic canal apéritif: two glasses of bright orange spritz, a carafe, and a "
        "fluorescent orange-and-yellow super-soaker water gun casually resting on the acrylic top. "
        "Pigeons strut around its legs, the footbridge glows behind, tiny water droplets sparkle in "
        "the air, apéro crowd blurred in the background.",

    "colorplane": UNIVERS + "The iridescent green-blue tubular steel chair with its curved oak seat is "
        "mounted like a throne on a battered black kick scooter, replacing a bistro chair — the "
        "legendary chair-scooter of the canal — parked on the cobblestones next to a handwritten "
        "cardboard sign reading exactly \"PÉAGE 2€\", a huge orange-and-yellow water gun leaning "
        "against it, sunset blazing on its iridescent frame, crowd on café terraces watching with awe.",

    "cosse": UNIVERS + "The Cosse pendant light (folded cognac leather pods with white stitching, "
        "suspended on thin cables) hangs from the green iron footbridge above the canal lock at dusk, "
        "glowing warmly like a lantern over the dark green water, its light reflecting in long ripples, "
        "silhouettes of people having drinks along the quays below, pink neon sky.",

    "eclipse": UNIVERS + "The Éclipse chandelier — three vertically chained black rings, each holding a "
        "hammered gold disc glowing with warm light — floats suspended above the middle of the canal at "
        "blue hour like three golden moons aligned, their hammered gold reflections shimmering on the "
        "still water, the footbridge and Haussmann facades in silhouette, people on the quays looking up "
        "in wonder, fireflies of light in the heat haze.",

    "iko": UNIVERS + "Several IKO pendant lights (white pleated paper fans radiating around a black stem, "
        "glowing softly from within) hang from the branches of the plane trees above a summer guinguette "
        "on the quay: string of tables, spritz glasses, a pétanque game paused, everyone bathed in the "
        "soft paper glow mixing with the hot pink sunset, water of the canal glittering behind.",

    "s5": UNIVERS + "The S5 hi-fi amplifier (perforated aluminum cube with brushed aluminum top plate and "
        "curved handle) sits on the hot cobblestones of the quay like the legendary boombox of the canal, "
        "surrounded by sitting teenagers in tank tops and slides nodding to the music, a small water "
        "splash frozen mid-air catching the sunset light next to it, pigeons grooving, the footbridge "
        "and pink sky behind, bass vibrations subtly rippling a puddle.",
}


def edit(name):
    boundary = uuid.uuid4().hex
    img = open(os.path.join(REFS, f"{name}.jpg"), "rb").read()
    parts = b""
    def field(k, v):
        return (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    parts += field("model", "gpt-image-2")
    parts += field("prompt", PIECES[name])
    parts += field("size", "1536x1024")
    parts += field("quality", "high")
    parts += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image[]\"; "
              f"filename=\"{name}.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode() + img + b"\r\n"
    parts += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/edits", data=parts, method="POST",
        headers={"Authorization": f"Bearer {KEY}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        res = json.load(resp)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{name}.png")
    with open(path, "wb") as f:
        f.write(base64.b64decode(res["data"][0]["b64_json"]))
    return name, path


if __name__ == "__main__":
    want = sys.argv[1:] or sorted(PIECES)
    todo = [n for n in want if not os.path.exists(os.path.join(OUT, f"{n}.png"))]
    print(f"{len(todo)} pièces à générer: {todo}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fut in cf.as_completed([ex.submit(edit, n) for n in todo]):
            try:
                n, path = fut.result()
                print(f"✅ {n} -> {path}", flush=True)
            except Exception as e:
                print(f"❌ {type(e).__name__}: {e}", flush=True)
    print("Terminé.")
