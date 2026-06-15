#!/usr/bin/env python3
"""LUCIDE — génération des visuels via fal.ai nano-banana-pro (gemini-3-pro-image).
- text-to-image : fal-ai/nano-banana-pro
- reference/edit : fal-ai/nano-banana-pro/edit (image_urls)  → cohérence des mannequins
Style de marque partagé (LOOK) pour une direction artistique homogène.

Usage:
  python3 falimg.py group:hero          # un groupe entier
  python3 falimg.py v01-aube s01-plein-sud   # des plans précis
  python3 falimg.py all                 # tout ce qui manque
Les fichiers existants sont préservés (idempotent). Sortie web ≤1600px jpg q86.
"""
import os, sys, json, io, time
import concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trailer"))
from falgen import run, KEY  # noqa
import urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
REFS_FILE = os.path.join(ASSETS, "ref", "_refs.json")

LOOK = (
 "Editorial photography for a French eyewear maison named LUCIDE. "
 "Art direction: honest and clean, un-retouched natural skin with visible pores and real texture, "
 "soft cinematic DAWN light (first light around 6am, warm peach glow meeting cool clear shadows), "
 "calm, precise, quietly confident. Palette: bone-white (#F6F3EC), dawn-peach (#ECB79C), "
 "clear teal accent (#2FA39A), warm slightly desaturated tones, generous negative space. "
 "Medium-format look, 80mm, gentle honest depth of field, fine natural grain, no HDR. "
 "No on-image text, no captions, no watermark, no brand logos on the frames (plain clean temples). "
)
PACK = (
 "Premium studio PACKSHOT, one hero object only, centered, seamless bone-white (#F6F3EC) sweep, "
 "soft dawn light from camera-left casting one long soft shadow, subtle warm reflection on the surface, "
 "ultra-sharp catalogue grade, no text, no logos, no props unless described. " + ""
)

def P(scene, pack=False):
    return (PACK if pack else "") + LOOK + "Scene: " + scene

# ─────────────────────────────── SHOT LIST ───────────────────────────────
# name : (group, aspect_ratio, prompt, [optional ref names for edit mode])
SHOTS = {
 # ---- HERO / IDENTITÉ ----
 "hero-aube-01": ("hero","21:9", P("A person photographed from behind at a large window at first light, "
   "wearing thin translucent acetate eyeglasses (just visible in profile), looking out at a city slowly "
   "waking under a peach dawn sky. Vast calm, hopeful, 'looking the future in the eye'. Cinematic wide.")),
 "hero-atelier": ("hero","16:9", P("Close on a craftsman's hands at a wooden workbench at dawn assembling "
   "translucent rosy acetate eyeglass frames with small steel tools and brass screws, warm task light, "
   "shavings of acetate, an honest artisanal optical atelier.")),
 "hero-graving": ("hero","16:9", P("Extreme macro of the inner side of an eyeglass temple arm being laser-"
   "engraved with a tiny precise breakdown of numbers (a cost/price ledger), thin engraved lines, "
   "a wisp of smoke, shallow focus, clinical yet warm dawn light.")),
 "hero-acetate": ("hero","4:5", P("Macro still life of translucent rose and honey acetate blocks and a single "
   "clear optical lens on bone-white, dawn light passing THROUGH the material, caustic glows, pure clarity.")),
 "hero-counter": ("hero","16:9", P("An independent optician's counter at dawn, a clean minimalist wooden tray "
   "presenting a few eyeglass frames, a brass measuring rule, soft morning light through a shopfront, "
   "trust and craft, no signage text.")),
 "manifeste-oeil": ("hero","1:1", P("Extreme close-up of a single human eye, calm, in which a tiny sunrise over a "
   "horizon line is reflected on the iris — the brand emblem made real. Hyper detailed, honest, no makeup.")),

 # ---- PACKSHOTS PRODUITS (14) ----
 "v01-aube": ("product","1:1", P("A pair of eyeglasses with thin TRANSLUCENT ROSY acetate frame, round-soft "
   "rectangular shape, clear lenses, plain temples, three-quarter view, slightly open.", pack=True)),
 "v02-meridien": ("product","1:1", P("A pair of ROUND thin brushed-titanium eyeglasses, very light, minimal, "
   "adjustable nose pads, clear lenses, plain temples, three-quarter view.", pack=True)),
 "v03-comptoir": ("product","1:1", P("A pair of PANTO-shape tortoiseshell acetate eyeglasses (real honey-brown "
   "tortoise, not printed), classic timeless, clear lenses, plain temples, three-quarter view.", pack=True)),
 "v04-demi-lune": ("product","1:1", P("A pair of HALF-MOON reading glasses, slim black-and-honey acetate, "
   "half-rim lower lenses, very light, folded flat, top-down hero on bone-white.", pack=True)),
 "v05-ecran": ("product","1:1", P("A pair of CRYSTAL-CLEAR transparent acetate eyeglasses with a faint warm "
   "blue-light-filter tint on the lenses, modern unisex, plain temples, three-quarter view.", pack=True)),
 "s01-plein-sud": ("product","1:1", P("A pair of SUNGLASSES, large soft mask shape, translucent honey acetate, "
   "gradient amber 'dawn' tinted lenses, plain temples, three-quarter view.", pack=True)),
 "s02-lucide-noir": ("product","1:1", P("A pair of deep BLACK acetate wayfarer SUNGLASSES, clean strong line, "
   "dark lenses, plain temples, no visible logo, three-quarter view.", pack=True)),
 "s03-mirage": ("product","1:1", P("A pair of SUNGLASSES with rose-gold MIRROR flash lenses (dew-colored), "
   "thin titanium + clear acetate, three-quarter view, reflective.", pack=True)),
 "s04-pilote-vrai": ("product","1:1", P("A pair of AVIATOR SUNGLASSES, champagne-gold thin titanium, teardrop "
   "polarized lenses, adjustable nose pads, three-quarter view.", pack=True)),
 "a01-boite-noire": ("product","1:1", P("A rigid recycled-aluminium eyeglass CASE, matte dark, open, revealing "
   "recycled foam interior; the inner lid has a tiny engraved numeric ledger. Hero on bone-white.", pack=True)),
 "a02-chamoisine": ("product","1:1", P("A folded microfiber lens CLOTH in dawn-peach, soft fabric texture, "
   "flat top-down on bone-white, minimal.", pack=True)),
 "a03-lien": ("product","1:1", P("An eyeglass CORD-CHAIN made of waxed cotton and small recycled-steel links "
   "with silicone end-loops, coiled elegantly on bone-white, top-down.", pack=True)),
 "a04-ordonnance": ("product","1:1", P("A small care KIT laid out neatly: a refillable 30ml spray bottle, a tiny "
   "watchmaker screwdriver, spare screws and nose pads, a folded cloth, top-down on bone-white.", pack=True)),
 "a05-ardoise": ("product","4:5", P("An enamelled steel apothecary-style PLAQUE (30x40cm) leaning on a wall, "
   "blank surface ready for engraving, vintage pharmacy aesthetic, dawn light, no text yet.", pack=True)),

 # ---- CASTING / VISAGES (références mannequins) ----
 "ref-elise": ("ref","4:5", P("Honest studio reference portrait of ELISE, a 32-year-old white French woman, "
   "natural light-brown hair, freckles, no makeup, calm direct gaze, wearing thin translucent rosy acetate "
   "eyeglasses, plain bone-white background, shoulders up, real skin texture.")),
 "ref-sasha": ("ref","4:5", P("Honest studio reference portrait of SASHA, a 26-year-old androgynous mixed-race "
   "person, short dark curly hair, clear skin, neutral expression, wearing round thin titanium eyeglasses, "
   "plain bone-white background, shoulders up.")),
 "ref-marius": ("ref","4:5", P("Honest studio reference portrait of MARIUS, a 47-year-old Black French man, "
   "short greying hair, light stubble, kind serious face, wearing panto tortoiseshell eyeglasses, "
   "plain bone-white background, shoulders up, real skin.")),
 "ref-aya": ("ref","4:5", P("Honest studio reference portrait of AYA, an elegant 63-year-old Asian-French woman, "
   "silver bob, fine wrinkles kept natural, serene, wearing crystal-clear acetate eyeglasses, "
   "plain bone-white background, shoulders up.")),

 # ---- SOCIAL / CAMPAGNE ----
 "og": ("social","16:9", P("Wide campaign hero: a single pair of translucent rosy acetate eyeglasses resting "
   "on a bone-white surface in a beam of peach dawn light, vast clean negative space on the left for a logo, "
   "minimal, premium, iconic.")),
 "social-prix-verite": ("social","1:1", P("Flat lay top-down: a pair of clear acetate eyeglasses beside a small "
   "printed paper card showing a simple hand-drawn cost bar-chart (no readable text), a brass coin, dawn light "
   "on bone-white, the idea of an honest price breakdown.")),
 "social-charte": ("social","1:1", P("Flat lay top-down on bone-white: a folded dawn-peach microfiber cloth, a "
   "rigid aluminium eyeglass case, a tiny screwdriver and spare screws, two frames, arranged with calm precision, "
   "an apothecary-clinical mood.")),
 "social-aube-frame": ("social","1:1", P("A pair of honey-acetate sunglasses held up against a peach dawn sky, "
   "fingertips just visible, the amber gradient lenses glowing with first light, minimal poetic campaign image.")),
 "social-atelier-hands": ("social","1:1", P("Close top-down on a craftsman's hands setting a clear lens into a "
   "rosy acetate frame on a wooden bench, brass tools around, warm dawn task light, artisanal honesty.")),

 # ---- JOURNAL (éditorial) ----
 "journal-surenchere": ("journal","16:9", P("Conceptual editorial: a long wall of dozens of near-identical glossy "
   "designer eyeglasses under cold retail light on the left, and ONE honest rosy acetate pair alone in warm dawn "
   "light on the right — the surenchère versus the truth. Cinematic, quietly critical.")),
 "journal-acetate": ("journal","16:9", P("Editorial macro of raw Italian acetate sheets in honey and rose tones "
   "stacked in an atelier, dawn light raking across the translucent material, craft documentary feel.")),
 "journal-opticien": ("journal","16:9", P("An independent optician in a clean warm workshop measuring a client's "
   "pupillary distance with a small ruler held to translucent eyeglasses, focused care, dawn light, documentary.")),
 "journal-rechargeable": ("journal","16:9", P("Close editorial shot of hands using a tiny screwdriver to replace a "
   "lens in a tortoiseshell acetate frame on a workbench, spare parts in a tray, the idea of repair-for-life.")),
}

# Lifestyle (edit mode, référence un visage) — ajoutés après génération des refs
LIFESTYLE = {
 "look-elise-cafe": ("look","4:5","ref-elise", "the same woman, wearing translucent rosy acetate eyeglasses, "
   "sitting at a parisian café at dawn with a coffee, reading a paper, soft first light, candid editorial."),
 "look-sasha-rooftop": ("look","4:5","ref-sasha", "the same person, wearing round titanium eyeglasses, on a "
   "rooftop at dawn looking at the city, wind in hair, calm confident, editorial."),
 "look-marius-atelier": ("look","4:5","ref-marius", "the same man, wearing tortoiseshell eyeglasses, in a warm "
   "optical atelier holding a frame up to dawn light to inspect it, focused, editorial."),
 "look-aya-window": ("look","4:5","ref-aya", "the same woman, wearing crystal acetate eyeglasses, by a window "
   "at first light reading a letter, serene, fine art editorial portrait."),
 "look-sun-elise": ("look","4:5","ref-elise", "the same woman, now wearing honey-acetate sunglasses with amber "
   "dawn-gradient lenses, on a sunlit terrace, golden first light, summer editorial."),
 "look-sun-marius": ("look","4:5","ref-marius", "the same man, wearing champagne-gold aviator sunglasses, "
   "outdoors at dawn looking to the horizon, cinematic, editorial."),
 "look-duo": ("look","16:9","ref-elise", "this woman and another person together at a sunlit window at dawn, "
   "both wearing elegant LUCIDE eyeglasses, warm candid editorial campaign image."),
}

def fetch_ref_urls(names):
    refs = json.load(open(REFS_FILE)) if os.path.exists(REFS_FILE) else {}
    return [refs[n] for n in names if n in refs]

def save_web(name, group, raw, maxpx=1600):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if max(im.size) > maxpx:
        s = maxpx/max(im.size); im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)
    out = os.path.join(ASSETS, group, f"{name}.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "JPEG", quality=86, optimize=True)
    return out

def gen_t2i(name, group, ar, prompt):
    res = run("fal-ai/nano-banana-pro",
              {"prompt": prompt, "aspect_ratio": ar, "resolution": "2K", "output_format": "jpeg"},
              label=name, timeout=600)
    url = res["images"][0]["url"]
    raw = urllib.request.urlopen(urllib.request.Request(url), timeout=300).read()
    # mémorise l'URL hébergée (utile comme référence)
    refs = json.load(open(REFS_FILE)) if os.path.exists(REFS_FILE) else {}
    refs[name] = url; os.makedirs(os.path.dirname(REFS_FILE), exist_ok=True)
    json.dump(refs, open(REFS_FILE,"w"), indent=1)
    return save_web(name, group, raw)

def gen_edit(name, group, ar, ref_name, prompt):
    urls = fetch_ref_urls([ref_name])
    if not urls:
        print(f"  {name}: référence {ref_name} absente — génère-la d'abord"); return None
    res = run("fal-ai/nano-banana-pro/edit",
              {"prompt": LOOK + "Scene: " + prompt, "image_urls": urls,
               "aspect_ratio": ar, "resolution": "2K", "output_format": "jpeg"},
              label=name, timeout=600)
    url = res["images"][0]["url"]
    raw = urllib.request.urlopen(urllib.request.Request(url), timeout=300).read()
    return save_web(name, group, raw)

def exists(name, group):
    return os.path.exists(os.path.join(ASSETS, group, f"{name}.jpg"))

def main():
    args = sys.argv[1:] or ["all"]
    todo = []  # (name, kind, group, ar, prompt, ref)
    want_groups = {a.split(":")[1] for a in args if a.startswith("group:")}
    want_all = "all" in args
    want_names = {a for a in args if not a.startswith("group:") and a != "all"}
    for name,(g,ar,pr) in SHOTS.items():
        if want_all or g in want_groups or name in want_names:
            if not exists(name,g): todo.append((name,"t2i",g,ar,pr,None))
    for name,(g,ar,ref,pr) in LIFESTYLE.items():
        if want_all or g in want_groups or name in want_names:
            if not exists(name,g): todo.append((name,"edit",g,ar,pr,ref))
    print(f"{len(todo)} visuels à générer", flush=True)
    def work(t):
        name,kind,g,ar,pr,ref = t
        try:
            return name, (gen_edit(name,g,ar,ref,pr) if kind=="edit" else gen_t2i(name,g,ar,pr))
        except Exception as e:
            return name, f"ERR {e}"
    # t2i en parallèle ; edits après (dépendent des refs)
    t2i = [t for t in todo if t[1]=="t2i"]; edits=[t for t in todo if t[1]=="edit"]
    for batch in (t2i, edits):
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            for name,res in ex.map(work, batch):
                print(("✅ " if res and "ERR" not in str(res) else "❌ ")+name+(" "+str(res) if res and "ERR" in str(res) else ""), flush=True)

if __name__ == "__main__":
    main()
