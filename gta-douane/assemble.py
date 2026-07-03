#!/usr/bin/env python3
"""Montage final : concatène les 6 plans Seedance (5 s chacun) + musique Suno.
Le son diégétique Seedance (foule, eau) reste en fond sous le rap.

Usage: python3 assemble.py [suno1|suno2]   # choix de la piste (défaut: suno1)
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VERTICAL = os.environ.get("AR") == "916"   # AR=916 → version 9:16 (TikTok/Reels)
CLIPS = [os.path.join(ROOT, "clips-916" if VERTICAL else "clips", f"plan{n}.mp4") for n in range(1, 7)]
MUSIC = os.path.join(ROOT, "audio", (sys.argv[1] if len(sys.argv) > 1 else "suno1") + ".mp3")
OUT = os.path.join(ROOT, "gta-la-douane-30s-916.mp4" if VERTICAL else "gta-la-douane-30s.mp4")
W, H = (2160, 3840) if VERTICAL else (3840, 2160)

DUR = 5.0
TOTAL = DUR * len(CLIPS)

inputs = []
for c in CLIPS:
    inputs += ["-i", c]
inputs += ["-i", MUSIC]
mi = len(CLIPS)  # index de la musique

filters = []
# Vidéo : uniformise 3840x2160 @30fps, coupe à 5 s exactes
for i in range(len(CLIPS)):
    filters.append(f"[{i}:v]trim=duration={DUR},setpts=PTS-STARTPTS,"
                   f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                   f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p[v{i}]")
    filters.append(f"[{i}:a]atrim=duration={DUR},asetpts=PTS-STARTPTS,"
                   f"aresample=48000,pan=stereo|c0=c0|c1=c1[a{i}]")
vcat = "".join(f"[v{i}][a{i}]" for i in range(len(CLIPS)))
filters.append(f"{vcat}concat=n={len(CLIPS)}:v=1:a=1[vc][diegetic]")
# Mix : ambiance Seedance à 20 %, rap Suno à 100 %, fondu de fin
filters.append(f"[diegetic]volume=0.2[amb]")
filters.append(f"[{mi}:a]atrim=duration={TOTAL},asetpts=PTS-STARTPTS,aresample=48000,"
               f"afade=t=in:d=0.3,afade=t=out:st={TOTAL-2}:d=2,volume=1.0[mus]")
filters.append("[amb][mus]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]")
# Fondu vidéo de fin
filters.append(f"[vc]fade=t=out:st={TOTAL-0.8}:d=0.8[vout]")

cmd = ["ffmpeg", "-y", "-loglevel", "warning", *inputs,
       "-filter_complex", ";".join(filters),
       "-map", "[vout]", "-map", "[aout]",
       "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
       "-t", str(TOTAL), OUT]
print(" ".join(cmd))
subprocess.run(cmd, check=True)
print("✅", OUT)
