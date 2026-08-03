#!/usr/bin/env python3
"""Génère les 6 keyframes du teaser NEUROMANCIEN avec GPT Image 2.

Plan 1 : génération pure (pas de personnage).
Plans 2-6 : edit avec transfert d'identité depuis ref/nico.jpg (la vraie tête de Nico).

Usage:
  python3 gen_keyframes.py            # tous les plans manquants
  python3 gen_keyframes.py 2 5        # seulement ces plans
  AR=916 python3 gen_keyframes.py     # version verticale 9:16
"""
import base64, concurrent.futures as cf, json, os, sys, urllib.request, uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
VERTICAL = os.environ.get("AR") == "916"
OUT = os.path.join(ROOT, "keyframes-916" if VERTICAL else "keyframes")
SIZE = "864x1536" if VERTICAL else "1536x864"
KEY = os.environ["OPENAI_API_KEY"]

REF = next((os.path.join(ROOT, "ref", f) for f in ("nico.jpg", "nico.jpeg", "nico.png")
            if os.path.exists(os.path.join(ROOT, "ref", f))), None)

# Le héros : la vraie tête de Nico (ref photo), restylée console cowboy.
NICO = (
    "the exact man from the reference photo — keep his real face, identical facial features, "
    "same hairstyle, clearly recognizable — restyled as LE NEUROMANCIEN, a legendary console "
    "cowboy: long matte-black techwear trench with a high collar over a charcoal turtleneck, "
    "a thin glowing data-implant line at his right temple, a discreet chrome jack behind the "
    "ear, teal and magenta neon reflections playing on his skin, calm intense gaze"
)

STYLE = (
    ("Vertical 9:16 smartphone-format composition, subject centered, key elements kept well "
     "inside the frame. " if VERTICAL else "") +
    "Teaser still for a prestige cyberpunk TV series, cinematic anamorphic look, Blade Runner "
    "2049 meets Neuromancer: night, heavy rain, teal-and-magenta palette with amber accents, "
    "volumetric haze, wet mirror-like reflections, strong backlight, fine film grain, shallow "
    "depth of field. Setting: Canal Saint-Martin, Paris, year 2087 — the green iron footbridge "
    "rigged with glowing holographic cables, canal lock gates leaking shafts of light, "
    "Haussmann facades stacked with French neon signs reading «CRÉDITS NEURONAUX», «RAMEN 24/7», "
    "«COMPTOIR», holographic koi fish drifting above the black water, a moored barge converted "
    "into a hacker den, police drones sweeping searchlights in the far distance. "
)

SHOTS = {
    1: STYLE + "Cold-open establishing shot, no prominent characters: wide view down the canal "
       "at night in the rain, the sky above the canal glowing like an old television tuned to a "
       "dead channel — flickering grey-white static clouds — the green iron footbridge silhouetted "
       "against it, neon signs mirrored in the rippling black water, holographic koi gliding over "
       "the surface, a single police drone searchlight far away. No text anywhere.",

    2: STYLE + "Extreme close-up portrait inside the barge hacker den: " + NICO + ", his face lit "
       "only by floating holographic screens filled with French code and neural-network diagrams, "
       "the temple implant pulsing softly, rain streaking the porthole behind him, shallow focus "
       "on his eyes. No text anywhere.",

    3: STYLE + "Full-length shot: " + NICO + " walking straight toward camera along the Quai de "
       "Valmy at night in the rain, trench flowing, augmented passers-by with luminous umbrellas "
       "blurred around him, a drone searchlight sweeping the wet cobblestones, dense French neon "
       "signage above. No text anywhere.",

    4: STYLE + "Surreal cyberspace-dive shot: " + NICO + " in profile as he slots a cable into "
       "the jack behind his ear — the half of his face nearest camera dissolving into glowing "
       "teal wireframe, and behind his eye an infinite neon vector-grid Paris stretching to the "
       "horizon, data streams rising like rain in reverse. No text anywhere.",

    5: STYLE + "Vast wide shot: the small silhouette of " + NICO + " standing on the green iron "
       "footbridge, facing a colossal benevolent-yet-terrifying golden holographic human face "
       "rising above the canal between the Haussmann facades, its light freezing the falling "
       "rain into sparkling suspension, the crowd on the quays tiny and motionless. No text "
       "anywhere.",

    6: STYLE + "Series title outro: chest-up shot of " + NICO + " looking straight into the "
       "camera with a faint knowing smirk, neon rain behind him over the canal. Above him, huge "
       "chrome letters with subtle glitch distortion spelling exactly «NEUROMANCIEN». Below, "
       "small clean white text reading exactly «UNE SÉRIE ORIGINALE COMPTOIR IA» and beneath it "
       "«JANVIER 2027». The text must be spelled exactly as given, elegant prestige-TV title "
       "design.",
}

NEEDS_REF = {2, 3, 4, 5, 6}


def _openai_json(url, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.load(resp)


def _openai_edit(prompt, size, ref_path):
    mime = "image/png" if ref_path.endswith(".png") else "image/jpeg"
    ref_bytes = open(ref_path, "rb").read()
    b = uuid.uuid4().hex
    parts = b""
    for k, v in {"model": "gpt-image-2", "prompt": prompt, "size": size, "quality": "high"}.items():
        parts += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    parts += (f"--{b}\r\nContent-Disposition: form-data; name=\"image[]\"; "
              f"filename=\"ref\"\r\nContent-Type: {mime}\r\n\r\n").encode() + ref_bytes + b"\r\n"
    parts += f"--{b}--\r\n".encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/edits", data=parts, method="POST",
        headers={"Authorization": f"Bearer {KEY}",
                 "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.load(resp)


def one(n):
    out = os.path.join(OUT, f"plan{n}.png")
    if os.path.exists(out):
        return f"plan{n}: déjà là"
    if n in NEEDS_REF:
        if not REF:
            return f"plan{n}: ⏸️  photo manquante — dépose ref/nico.jpg d'abord"
        res = _openai_edit(SHOTS[n], SIZE, REF)
    else:
        res = _openai_json("https://api.openai.com/v1/images/generations",
                           {"model": "gpt-image-2", "prompt": SHOTS[n], "size": SIZE,
                            "quality": "high", "output_format": "png"})
    open(out, "wb").write(base64.b64decode(res["data"][0]["b64_json"]))
    return f"✅ plan{n}.png"


if __name__ == "__main__":
    want = [int(x) for x in sys.argv[1:]] or sorted(SHOTS)
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(one, want):
            print(r, flush=True)
