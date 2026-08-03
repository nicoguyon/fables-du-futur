#!/usr/bin/env python3
"""Voix off du teaser (ElevenLabs via fal) → audio/vo1.mp3, vo2.mp3, vo3.mp3."""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "trailer"))
from falgen import run, download

SEGMENTS = [
    "Le ciel au-dessus du canal… était couleur de télé, calée sur un canal mort.",
    "Ils ont branché la ville sur une intelligence. Personne n'a demandé ce qu'elle rêvait.",
    "Neuromancien. Janvier deux mille vingt-sept.",
]

if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
    for i, text in enumerate(SEGMENTS, 1):
        out = os.path.join(ROOT, "audio", f"vo{i}.mp3")
        if os.path.exists(out):
            print(f"vo{i}.mp3: déjà là"); continue
        res = run("fal-ai/elevenlabs/tts/multilingual-v2",
                  {"text": text, "voice": "Daniel", "language_code": "fr",
                   "stability": 0.4, "similarity_boost": 0.8, "style": 0.55, "speed": 0.9},
                  label=f"vo{i}")
        download(res["audio"]["url"], out)
        print(f"✅ vo{i}.mp3", flush=True)
