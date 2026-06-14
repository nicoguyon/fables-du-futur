#!/usr/bin/env python3
"""Helper fal.ai (queue API) — image (nano-banana-pro), vidéo (Seedance 2.0),
voix off (ElevenLabs TTS) et musique (ElevenLabs Music).

La clé est lue dans /root/.fal_key (hors repo, jamais committée).
Usage librairie : from falgen import run, download
"""
import json, os, sys, time, urllib.request, urllib.error

KEY = (os.environ.get("FAL_KEY") or open("/root/.fal_key").read()).strip()
QUEUE = "https://queue.fal.run"


def _req(url, method="GET", body=None, timeout=180):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} sur {url}: {e.read().decode()[:500]}")


def run(model, inp, poll=6, timeout=1200, label=None):
    """Soumet un job en file d'attente, attend la fin, renvoie le JSON résultat."""
    label = label or model
    sub = _req(f"{QUEUE}/{model}", "POST", inp)
    status_url = sub.get("status_url")
    response_url = sub.get("response_url")
    rid = sub.get("request_id")
    if not status_url:
        return sub  # réponse synchrone
    t0 = time.time()
    last = None
    while True:
        st = _req(status_url)
        s = st.get("status")
        if s != last:
            print(f"  [{label}] {s} ({int(time.time()-t0)}s)", flush=True)
            last = s
        if s == "COMPLETED":
            return _req(response_url)
        if s in ("FAILED", "ERROR"):
            raise RuntimeError(f"[{label}] échec: {json.dumps(st)[:600]}")
        if time.time() - t0 > timeout:
            raise TimeoutError(f"[{label}] timeout (rid={rid})")
        time.sleep(poll)


def download(url, path, timeout=600):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers={"Authorization": f"Key {KEY}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(path, "wb") as f:
        f.write(resp.read())
    return path


if __name__ == "__main__":
    # Smoke test rapide : génère un portrait de référence de Julien.
    ROOT = os.path.dirname(os.path.abspath(__file__))
    prompt = (
        "Photorealistic cinematic film still, anamorphic 21:9 framing, shot on ARRI Alexa with "
        "vintage Cooke lenses, soft cinematic skin tones, slightly desaturated pastel palette, "
        "gentle film grain. Reference identity portrait of JULIEN, a 40-year-old white man, 1m80, "
        "athletic-average build, neat chestnut hair turning slightly salt-and-pepper, three-day "
        "stubble, hazel eyes, a slightly too-wide salesman smile. Wearing a navy-blue car-dealership "
        "polo shirt with a small embroidered logo, a lanyard badge, beige chinos, clean white "
        "sneakers. Confident friendly posture, full body visible, neutral grey studio background."
    )
    res = run("fal-ai/nano-banana-pro",
              {"prompt": prompt, "aspect_ratio": "21:9", "resolution": "2K", "output_format": "jpeg"},
              label="smoke-julien")
    url = res["images"][0]["url"]
    out = download(url, os.path.join(ROOT, "references", "julien.jpg"))
    print("OK ->", out)
    print("URL hébergée:", url)
