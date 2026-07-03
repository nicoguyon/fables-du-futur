#!/usr/bin/env python3
"""LA CÉRÉMONIE DES PROCHAINES — pipeline complet.

Étapes (relançables indépendamment, les fichiers existants sont sautés) :
  python3 gen_all.py ref        # portrait de référence de la MC (GPT Image 2)
  python3 gen_all.py keyframes # 6 plans cohérents (GPT Image 2 edits + ref)
  python3 gen_all.py tts        # 6 segments voix (ElevenLabs via fal)
  python3 gen_all.py clips      # 6 plans Seedance 1080p (durée = audio + marge)
  python3 gen_all.py lipsync   # sync-lipsync v2 pro par segment
  python3 gen_all.py            # tout dans l'ordre
"""
import base64, json, math, os, subprocess, sys, urllib.request, uuid
import concurrent.futures as cf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "trailer"))
from falgen import run, download

OPENAI_KEY = os.environ["OPENAI_API_KEY"]

MC = ("APOLLINE, an elegant French mistress of ceremony in her mid-30s, olive skin, sleek dark "
      "chignon with a few loose strands, sculpted cheekbones, deep red lips, small gold earrings, "
      "wearing a high-neck emerald-green sequined evening gown with long sleeves")

STAGE = ("on an intimate art-deco gala stage: gold velvet curtain, black lacquered podium bearing "
         "a small stack of golden envelopes, single warm spotlight, floating dust in the beam, "
         "dark auditorium with blurred silhouettes, cinematic editorial photography, shallow depth "
         "of field, medium-format quality, moody and precise")

SEGMENTS = [
    ("Mesdames et messieurs, bonsoir. Bienvenue à la Cérémonie des Prochaines, cent-dix-septième "
     "édition. Un tonnerre d'applaudissements : cette année encore, les nominées n'ont pas démérité.",
     "Wide-to-medium shot, she stands at the podium arms open in welcome, radiant impeccable "
     "public smile, chin high, perfect poise"),
    ("Dans la catégorie « elle l'a bien cherché » : celle qui portait ce haut-là, un jour de "
     "canicule. Trente-neuf degrés à l'ombre. Le jury est formel : la météo n'excuse rien. "
     "Un décolleté reste une déclaration.",
     "Medium shot at the podium, she opens the first golden envelope with ceremonial elegance, "
     "professional smile still on but the eyes slightly harder"),
    ("Dans la catégorie « meilleure comédienne » : celle qu'on ne croit pas. Dix plaintes contre "
     "le même homme, zéro condamnation. Quel talent, tout de même : inventer dix fois, exactement, "
     "la même histoire.",
     "Medium-close shot, she reads from a golden card, one eyebrow arched, the smile thinning "
     "into something sharper, ironic applause gesture with one hand"),
    ("Dans la catégorie « révélation hystérique » : celle qui saigne une semaine par mois, et qui "
     "voudrait, en plus, qu'on la plaigne. Le jury exige de la tenue : ce qui se passe dans son "
     "ventre ne regarde pas les congés.",
     "Close shot, warmer key light on her face, the public smile now completely gone, jaw tight, "
     "eyes shining with contained anger"),
    ("Dans la catégorie « promotion canapé » : celle qui a dit oui à son patron. Enfin… « oui ». "
     "Elle n'a pas dit non assez fort. Pas assez longtemps. Pas assez poliment.",
     "Medium-close shot, she sets the golden card down flat on the podium, deliberate slow gesture, "
     "stares straight into the lens, dead calm and cutting"),
    ("Et la Prochaine est… Personne. Il n'y a pas de nominées ce soir. Il n'y a que des coupables. "
     "Et un public qui applaudit. Cette cérémonie fermera ses portes le jour où la honte changera "
     "de camp. Bonsoir.",
     "Medium shot, she tears the final golden envelope in half and lets the pieces fall, then "
     "looks straight into the camera in silence, the spotlight tightening on her face, dignity "
     "and fire"),
]

R = lambda *p: os.path.join(ROOT, *p)


# ---------- OpenAI images ----------
def _openai_multipart(fields, file_field, file_name, file_bytes):
    b = uuid.uuid4().hex
    parts = b""
    for k, v in fields.items():
        parts += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    parts += (f"--{b}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
              f"filename=\"{file_name}\"\r\nContent-Type: image/png\r\n\r\n").encode() + file_bytes + b"\r\n"
    parts += f"--{b}--\r\n".encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/edits", data=parts, method="POST",
        headers={"Authorization": f"Bearer {OPENAI_KEY}",
                 "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.load(resp)


def _openai_gen(prompt, size, out):
    body = json.dumps({"model": "gpt-image-2", "prompt": prompt, "size": size,
                       "quality": "high", "output_format": "png"}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body, method="POST",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        res = json.load(resp)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(base64.b64decode(res["data"][0]["b64_json"]))
    return out


def step_ref():
    out = R("keyframes", "ref.png")
    if os.path.exists(out):
        return print("ref: déjà là")
    _openai_gen("Reference identity portrait, three-quarter view, waist-up: " + MC +
                ", standing " + STAGE, "1024x1536", out)
    print("✅ ref.png")


def step_keyframes():
    ref = open(R("keyframes", "ref.png"), "rb").read()
    def one(i):
        out = R("keyframes", f"seg{i+1}.png")
        if os.path.exists(out):
            return f"seg{i+1}: déjà là"
        _, shot = SEGMENTS[i]
        prompt = ("Keep this exact woman — same face, same hair, same emerald sequined gown — " +
                  shot + ", " + STAGE + " Cinematic 16:9 frame.")
        res = _openai_multipart({"model": "gpt-image-2", "prompt": prompt,
                                 "size": "1536x864", "quality": "high"},
                                "image[]", "ref.png", ref)
        open(out, "wb").write(base64.b64decode(res["data"][0]["b64_json"]))
        return f"✅ seg{i+1}.png"
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(one, range(6)):
            print(r, flush=True)


# ---------- ElevenLabs TTS via fal ----------
def step_tts():
    os.makedirs(R("audio"), exist_ok=True)
    for i, (text, _) in enumerate(SEGMENTS, 1):
        out = R("audio", f"seg{i}.mp3")
        if os.path.exists(out):
            print(f"seg{i}.mp3: déjà là"); continue
        res = run("fal-ai/elevenlabs/tts/multilingual-v2",
                  {"text": text, "voice": "Charlotte", "language_code": "fr",
                   "stability": 0.35, "similarity_boost": 0.8, "style": 0.6, "speed": 0.96},
                  label=f"tts{i}")
        download(res["audio"]["url"], out)
        print(f"✅ seg{i}.mp3", flush=True)


def _dur(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path]).strip())


def _data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


# ---------- Seedance clips ----------
def step_clips():
    os.makedirs(R("clips"), exist_ok=True)
    def one(i):
        out = R("clips", f"seg{i}.mp4")
        if os.path.exists(out):
            return f"seg{i}: déjà là"
        dur = min(15, max(5, math.ceil(_dur(R("audio", f"seg{i}.mp3")) + 1)))
        _, shot = SEGMENTS[i - 1]
        jpg = R("keyframes", f"seg{i}.jpg")
        if not os.path.exists(jpg):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i",
                            R("keyframes", f"seg{i}.png"), "-q:v", "2", jpg], check=True)
        res = run("bytedance/seedance-2.0/image-to-video", {
            "prompt": ("She speaks continuously and passionately to the audience, natural expressive "
                       "mouth movements and micro-expressions, subtle hand gestures matching a live "
                       "award-show speech. " + shot + ". Slow, elegant push-in, cinematic lighting, "
                       "no cuts, no text overlays."),
            "image_url": _data_uri(jpg, "image/jpeg"),
            "aspect_ratio": "16:9", "resolution": "1080p",
            "duration": str(dur), "generate_audio": False,
        }, label=f"clip{i}", timeout=1800, poll=8)
        download(res["video"]["url"], out)
        return f"✅ seg{i}.mp4 ({dur}s)"
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(one, range(1, 7)):
            print(r, flush=True)


# ---------- Lipsync ----------
def _r2_presigned(path, key):
    """Upload sur R2 et renvoie une URL présignée (1 h) — les data URI vidéo sont trop
    lourdes pour queue.fal.run et le bucket n'expose pas d'accès public."""
    import boto3
    from botocore.config import Config
    s3 = boto3.client(
        "s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        config=Config(signature_version="s3v4"), region_name="auto")
    bucket = os.environ["R2_BUCKET"]
    s3.upload_file(path, bucket, key)
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key},
                                     ExpiresIn=3600)


def step_lipsync():
    os.makedirs(R("synced"), exist_ok=True)
    def one(i):
        out = R("synced", f"seg{i}.mp4")
        if os.path.exists(out):
            return f"seg{i}: déjà là"
        video_url = _r2_presigned(R("clips", f"seg{i}.mp4"), f"ceremonie/seg{i}.mp4")
        audio_url = _r2_presigned(R("audio", f"seg{i}.mp3"), f"ceremonie/seg{i}.mp3")
        res = run("fal-ai/sync-lipsync/v2", {
            "video_url": video_url,
            "audio_url": audio_url,
            "model": "lipsync-2-pro",
            "sync_mode": "cut_off",
        }, label=f"lipsync{i}", timeout=1800, poll=8)
        download(res["video"]["url"], out)
        return f"✅ synced/seg{i}.mp4"
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(one, range(1, 7)):
            print(r, flush=True)


STEPS = {"ref": step_ref, "keyframes": step_keyframes, "tts": step_tts,
         "clips": step_clips, "lipsync": step_lipsync}

if __name__ == "__main__":
    for s in (sys.argv[1:] or ["ref", "keyframes", "tts", "clips", "lipsync"]):
        print(f"—— étape {s} ——", flush=True)
        STEPS[s]()
    print("Terminé.")
