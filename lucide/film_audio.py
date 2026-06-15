#!/usr/bin/env python3
"""LUCIDE — musique (ElevenLabs Music) + voix off FR (ElevenLabs TTS) pour le film.
Sortie dans film/audio/. VO en segments calés sur le montage (offsets ms)."""
import os, sys, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trailer"))
from falgen import run, download

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ROOT, "film", "audio")
os.makedirs(AUDIO, exist_ok=True)
TOTAL_MS = 49000

MUSIC_PROMPT = (
    "warm hopeful instrumental piano score, gentle sunrise mood, minimal solo piano with soft "
    "sustained strings and a warm ambient pad, calm and luminous, building softly to a serene "
    "resolution, modern cinematic neoclassical, fully instrumental, "
    "around 50 seconds"
)

VOICE = "Charlotte"  # voix féminine chaleureuse, multilingue
SEGMENTS = [
    (3000,  "Le matin, tout est clair. C'est plus tard qu'on se met à mentir."),
    (8800,  "La lunette est devenue une industrie de la surenchère. On vous fait payer un nom. Jamais un verre."),
    (15200, "Nous, on a tout gravé : la matière, la façon, et le prix. Le vrai. À l'intérieur de chaque branche."),
    (24800, "Pas de promesse magique. Pas de label qui rassure. De vrais visages, de vrais verres, un juste prix."),
    (41000, "LUCIDE. Voir clair."),
]

def music():
    res = run("fal-ai/elevenlabs/music",
              {"prompt": MUSIC_PROMPT, "music_length_ms": TOTAL_MS,
               "force_instrumental": True, "output_format": "mp3_44100_128"}, label="music", timeout=600)
    download(res["audio"]["url"], os.path.join(AUDIO, "music.mp3")); print("✅ music.mp3")

def voice():
    tmp = tempfile.mkdtemp(); segs = []
    for i,(off,text) in enumerate(SEGMENTS):
        res = run("fal-ai/elevenlabs/tts/multilingual-v2",
                  {"text": text, "voice": VOICE, "language_code": "fr",
                   "stability": 0.5, "similarity_boost": 0.75, "speed": 0.96}, label=f"vo{i}", timeout=300)
        p = os.path.join(tmp, f"s{i}.mp3"); download(res["audio"]["url"], p); segs.append((off,p))
    inp=[]; filt=[]
    for i,(off,p) in enumerate(segs):
        inp += ["-i", p]; filt.append(f"[{i}]adelay={off}|{off}[a{i}]")
    mix="".join(f"[a{i}]" for i in range(len(segs)))
    filt.append(f"{mix}amix=inputs={len(segs)}:normalize=0[out]")
    out=os.path.join(AUDIO,"voix.mp3")
    subprocess.run(["ffmpeg","-y","-loglevel","error",*inp,"-filter_complex",";".join(filt),
                    "-map","[out]","-t",str(TOTAL_MS/1000),"-ar","44100",out],check=True)
    print("✅ voix.mp3")

if __name__=="__main__":
    which=sys.argv[1:] or ["music","voice"]
    if "music" in which: music()
    if "voice" in which: voice()
