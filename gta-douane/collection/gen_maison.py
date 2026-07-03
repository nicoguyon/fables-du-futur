#!/usr/bin/env python3
"""LA DOUANE MAISON — deux séries à partir des photos originales (refs/) :
  - interieur : les pièces dans des intérieurs parisiens crédibles, reflets travaillés
  - variante  : déclinaisons "Édition Canicule" des meubles (colorways audacieux)

Usage:
  python3 gen_maison.py                 # tout ce qui manque
  python3 gen_maison.py int_apollo var_eclipse ...
"""
import base64, concurrent.futures as cf, json, os, sys, urllib.request, uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(ROOT, "refs")
OUT = os.path.join(ROOT, "maison", "art")
KEY = os.environ["OPENAI_API_KEY"]

INT = (
    "Keep this exact designer piece perfectly faithful — same design, proportions, materials, finishes — "
    "and stage it in a breathtaking but completely believable high-end Parisian interior, photographed "
    "like an Architectural Digest editorial: ultra-realistic interior photography, physically accurate "
    "reflections and materials, tall Haussmann windows with a view over the Canal Saint-Martin at hot "
    "pink summer dusk (2026 heatwave), warm golden light raking across the room, subtle heat haze "
    "outside, medium-format photo quality, rich micro-contrast, no cartoon, no video-game look. "
)

VAR = (
    "Create a bold new colorway variant of this exact designer piece — same design language, same "
    "proportions and construction, but a daring new material/finish edition — presented as a luxury "
    "product hero shot in a minimal seamless studio with soft gradient backdrop, ultra-realistic "
    "materials, physically accurate reflections, dust-free perfection, medium-format photo quality. "
)

PIECES = {
    # ——— Série intérieurs ———
    "int_eclipse": ("eclipse", INT + "The Éclipse chandelier hangs in a double-height Haussmann stairwell "
        "entry: dark herringbone parquet polished like a mirror reflecting the three hammered-gold discs, "
        "a tall antique mirror doubling the piece, curved staircase with wrought-iron railing, the warm "
        "disc light and pink dusk mixing on the ceiling mouldings."),
    "int_colorplane": ("colorplane", INT + "The iridescent chair sits in a sun-drenched corner on waxed "
        "oak herringbone parquet that catches its green-blue reflection like a shallow pool, linen "
        "curtain breathing in the hot breeze, the canal footbridge visible through the open window, a "
        "small stack of art books and an espresso cup on the floor beside it."),
    "int_apollo": ("apollo", INT + "The Apollo table, full-size dining version (clear acrylic top, copper "
        "cylinder crossbars), stands in a dining room with polished waxed concrete floor: the acrylic is "
        "almost invisible except for its edges catching the dusk, the copper bars glow and cast warm "
        "caustic light patterns through the acrylic onto the floor, six sculptural chairs around it, the "
        "pink sky and canal reflected in the tabletop."),
    "int_cosse": ("cosse", INT + "The Cosse leather pendant glows over a reading corner: cognac leather "
        "sofa, travertine side table with a small pile of novels, the pendant's warm light grazing the "
        "leather pods and reflecting softly in a black lacquered wall panel, dusk light through sheer "
        "curtains, a sleeping cat."),
    "int_iko": ("iko", INT + "Several IKO pleated-paper pendants at different heights above a long oak "
        "atelier table near the window: the pleats cast soft fan-shaped shadows on the white wall, paper "
        "glowing like lanterns, ceramics and sketchbooks on the table, the canal and its footbridge in "
        "the pink dusk outside."),
    "int_s5": ("s5", INT + "The S5 perforated aluminum amplifier sits on a black-lacquered sideboard in a "
        "listening room: its reflection perfect in the lacquer, walnut shelves of vinyl records behind, "
        "two floor-standing speakers, a record spinning on a turntable beside it, the hot pink dusk from "
        "the window raking across the perforated aluminum grid."),
    # ——— Série déclinaisons "Édition Canicule" ———
    "var_eclipse": ("eclipse", VAR + "ÉCLIPSE — ÉDITION CANICULE: the three hammered discs in anodized "
        "sunset gradient — hot pink melting into orange like the 2026 heatwave sky — on black rings, "
        "their glow tinting the studio backdrop pink and gold."),
    "var_colorplane": ("colorplane", VAR + "COLORPLANE — ÉDITION CANICULE: the tubular frame in anodized "
        "sunset gradient shifting from hot pink to orange to violet depending on the angle, seat in "
        "smoked charred oak, sitting in a shallow mirror of water that reflects it perfectly."),
    "var_apollo": ("apollo", VAR + "APOLLO — ÉDITION PISCINE: the tabletop in pool-water blue tinted "
        "acrylic with subtle ripple texture casting swimming-pool caustics on the floor, crossbars in "
        "mirror-polished chrome instead of copper."),
    "var_cosse": ("cosse", VAR + "COSSE — ÉDITION SUPER SOAKER: the leather pods in glossy fluorescent "
        "orange and yellow leather with white stitching — a knowing wink to a water gun — hanging in a "
        "row of three sizes, playful and impeccably crafted."),
    "var_iko": ("iko", VAR + "IKO — ÉDITION FLAMANT: the pleated paper in a delicate gradient from white "
        "at the stem to intense flamingo pink at the tips, glowing from within, three of them like "
        "exotic birds at different heights."),
    "var_s5": ("s5", VAR + "S5 — ÉDITION OR MARTELÉ: the perforated cube in hammered brushed gold with a "
        "mirror-polished copper top plate and handle, standing on a black granite plinth, its warm "
        "reflection stretching across the polished stone."),
}


def edit(name):
    ref, prompt = PIECES[name]
    boundary = uuid.uuid4().hex
    img = open(os.path.join(REFS, f"{ref}.jpg"), "rb").read()
    parts = b""
    def field(k, v):
        return (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    parts += field("model", "gpt-image-2")
    parts += field("prompt", prompt)
    parts += field("size", "1536x1024")
    parts += field("quality", "high")
    parts += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image[]\"; "
              f"filename=\"{ref}.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode() + img + b"\r\n"
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
    print(f"{len(todo)} images à générer: {todo}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fut in cf.as_completed([ex.submit(edit, n) for n in todo]):
            try:
                n, path = fut.result()
                print(f"✅ {n} -> {path}", flush=True)
            except Exception as e:
                print(f"❌ {n if isinstance(n, str) else ''} {type(e).__name__}: {e}", flush=True)
    print("Terminé.")
