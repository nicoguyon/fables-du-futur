#!/usr/bin/env python3
"""Génère la musique (ElevenLabs Music) et la voix off française (ElevenLabs TTS)
dans remotion/public/audio/. La musique est swappable par un MP3 Suno officiel.

La voix off est générée en 6 segments calés au plan près (offsets en ms), puis
remixée sur 60 s avec ffmpeg pour que la narration colle au montage."""
import os, subprocess, tempfile
from falgen import run, download

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ROOT, "remotion", "public", "audio")

MUSIC_PROMPT = (
    "dark whimsical cinematic trailer score, off-kilter waltz, playful pizzicato strings, ticking "
    "clock percussion, glockenspiel, deep cello, a single melancholic piano, building from a naive "
    "quirky opening to a bittersweet emotional climax, in the style of Jon Brion and Yann Tiersen, "
    "fully instrumental, 60 seconds, cinematic mix"
)

# Segments calés sur le montage : (offset_ms depuis le début, texte). 30fps → 1 plan = 5000 ms.
VOICE_SEGMENTS = [
    (0,     "Julien avait tout. Une belle vie. Une belle famille. Un métier où il vendait du rêve électrique."),
    (9500,  "Et puis un jour... une chute. Une simple chute. À son réveil, son cerveau ne reconnaissait plus sa jambe gauche. Cette jambe-là... n'était plus la sienne."),
    (21000, "Alors Julien a décidé de s'en débarrasser. Par tous les moyens. Absolument tous les moyens."),
    (38000, "Mais un homme s'obstinait à le réparer. Il ne lui restait plus qu'une seule solution."),
    (47500, "Et le jour où il l'a enfin perdue, il a tout perdu. Sa femme, ses enfants. Mais il a gagné sa liberté."),
    (55000, "Parce que le bonheur... c'est simple comme une amputation."),
]


def music():
    res = run("fal-ai/elevenlabs/music",
              {"prompt": MUSIC_PROMPT, "music_length_ms": 60000,
               "force_instrumental": True, "output_format": "mp3_44100_128"},
              label="music")
    download(res["audio"]["url"], os.path.join(AUDIO, "music.mp3"))
    print("✅ music.mp3")


def voice():
    tmp = tempfile.mkdtemp()
    seg_files = []
    for i, (off, text) in enumerate(VOICE_SEGMENTS):
        res = run("fal-ai/elevenlabs/tts/multilingual-v2",
                  {"text": text, "voice": "Brian", "language_code": "fr",
                   "stability": 0.45, "similarity_boost": 0.75, "speed": 0.95},
                  label=f"voix{i}")
        p = os.path.join(tmp, f"seg{i}.mp3")
        download(res["audio"]["url"], p)
        seg_files.append((off, p))
    # Mixe les segments à leurs offsets sur un fond de 60 s avec ffmpeg.
    inputs = []
    filters = []
    for i, (off, p) in enumerate(seg_files):
        inputs += ["-i", p]
        filters.append(f"[{i}]adelay={off}|{off}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(seg_files)))
    filters.append(f"{mix}amix=inputs={len(seg_files)}:normalize=0[out]")
    out = os.path.join(AUDIO, "voix.mp3")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs,
           "-filter_complex", ";".join(filters),
           "-map", "[out]", "-t", "60", "-ar", "44100", out]
    subprocess.run(cmd, check=True)
    print("✅ voix.mp3 (6 segments calés sur 60 s)")


if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["music", "voice"]
    if "music" in which:
        music()
    if "voice" in which:
        voice()
