#!/usr/bin/env python3
"""Génère les portraits de référence des personnages (nano-banana-pro, 21:9, 2K)
et sauvegarde les URLs hébergées fal dans references/refs.json (pour Seedance)."""
import os, json, concurrent.futures as cf
from falgen import run, download

ROOT = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(ROOT, "references")

CHARTE = (
    "Photorealistic cinematic film still, anamorphic 21:9 framing, shot on ARRI Alexa with vintage "
    "Cooke lenses, soft cinematic skin tones, slightly desaturated pastel palette, gentle film grain, "
    "naturalistic flattering lighting, neutral grey studio background, single subject, full body and "
    "face clearly visible, consistent identity sheet. "
)

CHARS = {
    "julien": "Reference identity portrait of JULIEN, a 40-year-old white man, 1m80, athletic-average build, "
        "neat chestnut hair turning slightly salt-and-pepper, three-day stubble, hazel eyes, a slightly "
        "too-wide salesman smile. Wearing a navy-blue car-dealership polo shirt with a small embroidered "
        "logo, a lanyard badge, beige chinos, clean white sneakers. Confident friendly posture.",
    "linda": "Reference identity portrait of LINDA, a fit toned 40-year-old woman, brown hair pulled into a "
        "tight high bun, glowing bare-faced skin, minimalist earrings. Wearing a sage-beige sports bra and "
        "matching leggings, holding a rolled yoga mat and a steel water bottle, an artisanal scented candle "
        "nearby. Serene, radiant, gently controlling expression.",
    "axel": "Reference identity portrait of AXEL, a lanky 14-year-old teenage boy, medium-length hair falling "
        "over his eyes, slightly slouched. Distinctive feature: a large beige adhesive bandage (sticking "
        "plaster) prominently placed across the bridge of his nose, hiding a pimple. Wearing an oversized grey "
        "hoodie, headphones around his neck, holding a smartphone, avoidant teenage gaze.",
    "lustucru": "Reference identity portrait of LUSTUCRU, an adorable medium-sized scruffy mixed-breed dog, wiry "
        "sandy-ginger fur, black nose, very expressive eyes, one floppy ear, wearing a red collar with a tag. "
        "Sitting, head tilted, endearing.",
    "michael": "Reference identity portrait of MICHAEL, an elegant 47-year-old surgeon, thin glasses, greying "
        "temples, well-groomed hands. Wearing green surgical scrubs and a scrub cap, surgical mask pulled down "
        "under the chin. Calm, authoritative, reassuring expression.",
}


def one(name, desc):
    res = run("fal-ai/nano-banana-pro",
              {"prompt": CHARTE + desc, "aspect_ratio": "21:9", "resolution": "2K", "output_format": "jpeg"},
              label=name)
    url = res["images"][0]["url"]
    download(url, os.path.join(REF, f"{name}.jpg"))
    return name, url


if __name__ == "__main__":
    todo = list(CHARS.items())  # tous (régénère julien aussi pour cohérence du set)
    refs = {}
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for fut in cf.as_completed([ex.submit(one, n, d) for n, d in todo]):
            name, url = fut.result()
            refs[name] = url
            print(f"✅ {name} -> {url}", flush=True)
    json.dump(refs, open(os.path.join(REF, "refs.json"), "w"), indent=2)
    print("refs.json écrit:", refs)
