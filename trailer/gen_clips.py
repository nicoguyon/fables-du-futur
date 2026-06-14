#!/usr/bin/env python3
"""Génère les 12 plans de la bande-annonce via Seedance 2.0 reference-to-video.
Continuité personnages assurée par les portraits de référence (references/refs.json),
référencés dans le prompt par @Image1, @Image2, ... (dans l'ordre de image_urls).

Usage:
  python3 gen_clips.py            # tous les plans manquants
  python3 gen_clips.py 1 9 12     # seulement ces plans
"""
import os, sys, json, concurrent.futures as cf
from falgen import run, download

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(ROOT, "remotion", "public", "clips")
REFS = json.load(open(os.path.join(ROOT, "references", "refs.json")))

MODEL = "bytedance/seedance-2.0/reference-to-video"

CINE = ("Anamorphic 21:9 cinematic film still in motion, shot on ARRI Alexa with vintage Cooke lenses, "
        "shallow depth of field, gentle film grain, dark deadpan comedy tone in the manner of Quentin "
        "Dupieux and Yorgos Lanthimos: beautiful polished imagery, unsettling calm. ")

# Chaque plan : (refs dans l'ordre, prompt). @ImageN suit l'ordre des refs.
SHOTS = {
    1: (["julien"],
        CINE + "In a pristine white electric-car showroom with a glossy reflective floor and unreal "
        "bright showroom lighting, JULIEN (@Image1), a 40-year-old man in a navy dealership polo with a "
        "lanyard, hands a set of car keys to an off-screen customer with a magician's flourish and a "
        "too-wide salesman smile, everything gleaming. Slow smooth dolly-in, slight heroic low angle, "
        "clean advertising look."),
    2: (["linda", "axel", "julien", "lustucru"],
        CINE + "In an ultra-tidy minimalist designer kitchen in soft morning light, LINDA (@Image1) in "
        "sage activewear calmly sets down a tiny plate holding a single seed in front of each person; "
        "the teenage boy AXEL (@Image2), a beige plaster across his nose, stares at his almost-empty "
        "plate in silent despair; JULIEN (@Image3) smiles absently with one hand resting on his left "
        "thigh; the scruffy dog LUSTUCRU (@Image4) peers up hungrily from under the table. Symmetrical "
        "wide static framing, slow subtle push-in, sage and cream palette."),
    3: (["julien"],
        CINE + "In a garage under hard cold fluorescent light, JULIEN (@Image1) confidently steps up onto "
        "a stool to reach something high on a shelf, then his foot slips; extreme slow-motion fall as he "
        "tips backward toward the concrete floor, arms reaching. Dramatic slow motion, hard contrast, "
        "sudden tension."),
    4: (["julien"],
        CINE + "In a quiet hospital room at cold blue dawn, JULIEN (@Image1), in a pale hospital gown, "
        "wakes and looks down at his own left leg, staring at it with quiet horror as if it were a "
        "foreign object that is not his, his hand hovering over it with disgust and fascination. Close on "
        "his face, then a slow tilt down to the leg; clinical cold blue light with one thin ray of sun."),
    5: (["julien"],
        CINE + "At a misty forest edge at golden dawn, JULIEN (@Image1) in hunting clothes, completely "
        "alone, secretly rigs a shotgun on a log so it will 'accidentally' fall and fire toward his own "
        "left leg, glancing around with exaggerated fake innocence. Wide misty shot, beautiful hazy "
        "golden light, absurd solitary scheming."),
    6: (["julien"],
        CINE + "In a dark workshop at night, JULIEN (@Image1) plunges his left leg into a fuming tub of "
        "dry ice, thick white vapor billowing and filling the frame, gritting his teeth with an "
        "unsettling calm, a watch placed beside him like a timer. Close shot, volumetric vapor, deep blue "
        "night light cut by a single orange work lamp."),
    7: (["julien"],
        CINE + "On a deserted construction site at dusty dusk, JULIEN (@Image1) lies on the ground and "
        "pulls a rope to tip a heavy concrete block suspended directly above his left leg, eyes closed, "
        "almost serene. Low angle looking up at the slowly descending block, dusty twilight haze."),
    8: (["julien"],
        CINE + "At a railway track at nightfall, JULIEN (@Image1) lies along the tracks with his left leg "
        "laid across a steel rail, calmly checking his wristwatch; far down the line a train headlight "
        "appears and grows, rushing closer, its blinding white light flooding the frame. Wide shot along "
        "the track, deep blue night turning to blinding white."),
    9: (["michael", "julien"],
        CINE + "In a spotless operating room, the surgeon MICHAEL (@Image1) in green scrubs gently peels "
        "back a bandage to reveal an intact, neatly stitched, fully saved leg, smiling kindly and proud; "
        "reverse angle on JULIEN (@Image2) lying on the table whose eyes slowly fill with cold, pure "
        "hatred. Tight shot/reverse-shot, clinical green light, slow push-in onto Julien's eyes."),
    10: (["michael", "julien"],
        CINE + "In a bare cellar lit only by a single swinging bare bulb, MICHAEL (@Image1) is tied to a "
        "wooden chair, glasses askew, terrified and sweating; a surgical scalpel lies on a table before "
        "him; JULIEN (@Image2) steps calmly out of the shadow into the light and slowly slides the "
        "scalpel toward Michael. Chiaroscuro, the oscillating bulb swinging shadows, oppressive static "
        "shot, dread."),
    11: (["julien"],
        CINE + "In a warm sunlit recovery room, JULIEN (@Image1) wakes in a hospital bed, looks down and "
        "sees that his left leg is finally gone, amputated, the blanket flat where it should be, and his "
        "face breaks into the most beautiful, peaceful smile of pure relief, tears of joy in his eyes. "
        "Slow close-up on his face, warm golden emotional light."),
    12: (["julien", "lustucru"],
        CINE + "On a wet country road at dawn, JULIEN (@Image1), his left leg missing, walks away alone "
        "on crutches down the glistening asphalt, backlit by the rising sun; he stops, lifts his face to "
        "the light and smiles, finally free, while the scruffy dog LUSTUCRU (@Image2) trots up from "
        "behind to join him. Wide rear shot slowly craning upward, golden-hour backlight, soft lens "
        "flare, bittersweet and luminous."),
}


def one(n):
    refs, prompt = SHOTS[n]
    image_urls = [REFS[r] for r in refs]
    res = run(MODEL, {
        "prompt": prompt,
        "image_urls": image_urls,
        "aspect_ratio": "21:9",
        "resolution": "1080p",
        "duration": "5",
        "generate_audio": False,
    }, label=f"plan{n:02d}", timeout=1500)
    url = res["video"]["url"]
    out = os.path.join(CLIPS, f"shot{n:02d}.mp4")
    download(url, out)
    return n, url


if __name__ == "__main__":
    want = [int(x) for x in sys.argv[1:]] or sorted(SHOTS)
    todo = [n for n in want
            if not os.path.exists(os.path.join(CLIPS, f"shot{n:02d}.mp4"))]
    print(f"{len(todo)} plans à générer: {todo}", flush=True)
    manifest_path = os.path.join(CLIPS, "clips.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fut in cf.as_completed([ex.submit(one, n) for n in todo]):
            try:
                n, url = fut.result()
                manifest[f"shot{n:02d}"] = url
                json.dump(manifest, open(manifest_path, "w"), indent=2)
                print(f"✅ plan {n:02d} -> shot{n:02d}.mp4", flush=True)
            except Exception as e:
                print(f"❌ {e}", flush=True)
    print("Terminé. clips.json:", sorted(manifest))
