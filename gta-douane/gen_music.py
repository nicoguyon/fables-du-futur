#!/usr/bin/env python3
"""Génère le morceau du film via l'API Suno (api.sunoapi.org) → audio/music.mp3

Usage:
  python3 gen_music.py           # lance la génération + attend + télécharge
  python3 gen_music.py <taskId> # reprend le polling d'une tâche existante
"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ROOT, "audio")
KEY = os.environ["SUNO_API_KEY"]
BASE = "https://api.sunoapi.org"

TITLE = "La Douane du Canal (GTA Édition Spéciale)"

STYLE = ("french rap banger, heavy 808 bass, dark drill synths mixed with 80s Miami synthwave pads, "
         "summer heatwave anthem, energetic teenage hype ad-libs, water splash sound effects, "
         "aggressive but playful, 140 BPM, radio GTA vibe")

LYRICS = """[Intro]
Eh, eh — La Douane !
Canal Saint-Martin (splash), ça paye ou ça nage

[Refrain]
Deux euros tu passes (passe !)
Sinon je t'arrose (splash !)
Pistolet à eau, j'suis le patron du canal
La chaise sur la trott', défilé royal
Canicule à Paris, quarante à l'ombre (eh)
Les keufs sont trempés, y'a plus personne qui gronde
GTA La Douane, édition spéciale
Canal Saint-Martin, c'est mon capital

[Couplet]
Quatorze ans, déjà la légende du dixième
Le péage est ouvert, même les vélos m'aiment
Je saute de la passerelle, triple salto arrière
Tout le quai me filme, je fais monter la fièvre
Mission accomplie, trois étoiles au compteur
La Douane du canal, gros, c'est moi le doseur

[Outro]
Splash... La Douane... été 2026... canicule
"""


def req(path, body=None, method=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method or ("POST" if data else "GET"),
                               headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                                        "User-Agent": "curl/8.5.0"})
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.load(resp)


def main():
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        res = req("/api/v1/generate", {
            "customMode": True, "instrumental": False, "model": "V5",
            "title": TITLE, "style": STYLE, "prompt": LYRICS,
            "callBackUrl": "https://example.com/noop",
        })
        print("submit:", json.dumps(res)[:300], flush=True)
        task = res["data"]["taskId"]
        print("taskId:", task, flush=True)
    t0 = time.time()
    while True:
        info = req(f"/api/v1/generate/record-info?taskId={task}")
        status = (info.get("data") or {}).get("status")
        print(f"  [suno] {status} ({int(time.time()-t0)}s)", flush=True)
        if status == "SUCCESS":
            tracks = info["data"]["response"]["sunoData"]
            os.makedirs(AUDIO, exist_ok=True)
            for i, tr in enumerate(tracks, 1):
                url = tr.get("audioUrl") or tr.get("streamAudioUrl")
                out = os.path.join(AUDIO, f"suno{i}.mp3")
                dl = urllib.request.Request(url, headers={"User-Agent": "curl/8.5.0"})
                with urllib.request.urlopen(dl, timeout=600) as resp, open(out, "wb") as f:
                    f.write(resp.read())
                print(f"✅ {out} ({tr.get('duration')}s) — {tr.get('title')}", flush=True)
            json.dump(info, open(os.path.join(AUDIO, "suno.json"), "w"), indent=2)
            return
        if status in ("CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED", "CALLBACK_EXCEPTION", "SENSITIVE_WORD_ERROR"):
            raise SystemExit(f"échec Suno: {json.dumps(info)[:800]}")
        if time.time() - t0 > 900:
            raise SystemExit(f"timeout Suno (taskId={task})")
        time.sleep(15)


if __name__ == "__main__":
    main()
