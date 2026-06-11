#!/usr/bin/env python3
"""Génère les gravures d'illustration des fables via Nano Banana Pro (gemini-3-pro-image, REST direct).
Usage: python3 gen_images.py [id ...]   (sans arg: toutes les fables sans image)"""
import json, os, sys, base64, io, time
import concurrent.futures as cf
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_key():
    for line in open(os.path.expanduser("~/.brand_factory/keys.env")):
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("GEMINI_API_KEY introuvable")

KEY = os.environ.get("GEMINI_API_KEY") or load_key()
MODEL = "gemini-3-pro-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

STYLE = ("Antique fable-book engraving in the manner of Gustave Doré and J.J. Grandville, "
         "fine copperplate etching, dense crosshatching, warm sepia-black ink on aged ivory paper, "
         "dramatic chiaroscuro, ornate vignette composition whose edges fade softly into blank paper, "
         "19th-century illustrated book plate aesthetic with a subtle retro-futuristic twist. "
         "Scene: {scene}. "
         "Single illustration, no text, no caption, no letters, no decorative border frame.")

def generate(fid, scene, retries=3):
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE.format(scene=scene)}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "4:5", "imageSize": "2K"},
        },
    }).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                resp = json.load(r)
            for part in resp["candidates"][0]["content"]["parts"]:
                if "inlineData" in part:
                    raw = base64.b64decode(part["inlineData"]["data"])
                    return save_web(fid, raw)
            raise RuntimeError("pas d'image dans la réponse")
        except Exception as e:
            print(f"  {fid}: tentative {attempt+1} échouée: {e}", flush=True)
            time.sleep(8 * (attempt + 1))
    return None

def save_web(fid, raw):
    """Downscale web (max 1400px) + jpg q82 — jamais de 4K lourd sur Vercel."""
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.width > 1400:
        im = im.resize((1400, int(im.height * 1400 / im.width)), Image.LANCZOS)
    out = os.path.join(ROOT, "img", f"{fid}.jpg")
    im.save(out, "JPEG", quality=82, optimize=True)
    return out

if __name__ == "__main__":
    data = json.load(open(os.path.join(ROOT, "data", "fables.json"), encoding="utf-8"))
    want = sys.argv[1:]
    todo = [f for f in data["fables"]
            if (not want and not os.path.exists(os.path.join(ROOT, "img", f["id"] + ".jpg")))
            or f["id"] in want]
    print(f"{len(todo)} images à générer…", flush=True)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(generate, f["id"], f["image_prompt"]): f["id"] for f in todo}
        for fut in cf.as_completed(futs):
            fid = futs[fut]
            res = fut.result()
            print(("✅ " if res else "❌ ") + fid, flush=True)
    # met à jour le champ image
    for f in data["fables"]:
        p = os.path.join(ROOT, "img", f["id"] + ".jpg")
        f["image"] = f"img/{f['id']}.jpg" if os.path.exists(p) else None
    json.dump(data, open(os.path.join(ROOT, "data", "fables.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("fables.json mis à jour")
