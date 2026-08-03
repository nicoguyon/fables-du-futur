#!/usr/bin/env python3
"""Montage final : 6 plans Seedance (5 s) + score Suno + 3 segments de voix off.
Le son diégétique Seedance (pluie, drones) reste en fond léger sous le score.

Usage: python3 assemble.py [suno1|suno2]   # choix de la piste (défaut: suno1)
       AR=916 python3 assemble.py          # version verticale
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VERTICAL = os.environ.get("AR") == "916"
CLIPS = [os.path.join(ROOT, "clips-916" if VERTICAL else "clips", f"plan{n}.mp4") for n in range(1, 7)]
MUSIC = os.path.join(ROOT, "audio", (sys.argv[1] if len(sys.argv) > 1 else "suno1") + ".mp3")
VO = [os.path.join(ROOT, "audio", f"vo{i}.mp3") for i in (1, 2, 3)]
VO_AT = [1.0, 15.5, 25.6]          # secondes de départ des 3 segments de voix off
OUT = os.path.join(ROOT, "neuromancien-30s-916.mp4" if VERTICAL else "neuromancien-30s.mp4")
W, H = (2160, 3840) if VERTICAL else (3840, 2160)

DUR = 5.0
TOTAL = DUR * len(CLIPS)

inputs = []
for c in CLIPS:
    inputs += ["-i", c]
mi = len(CLIPS)                     # index musique
inputs += ["-i", MUSIC]
vi = mi + 1                         # index premier segment VO
for v in VO:
    inputs += ["-i", v]

filters = []
for i in range(len(CLIPS)):
    filters.append(f"[{i}:v]trim=duration={DUR},setpts=PTS-STARTPTS,"
                   f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                   f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p[v{i}]")
    filters.append(f"[{i}:a]atrim=duration={DUR},asetpts=PTS-STARTPTS,"
                   f"aresample=48000,pan=stereo|c0=c0|c1=c1[a{i}]")
vcat = "".join(f"[v{i}][a{i}]" for i in range(len(CLIPS)))
filters.append(f"{vcat}concat=n={len(CLIPS)}:v=1:a=1[vc][diegetic]")
filters.append("[diegetic]volume=0.15[amb]")
filters.append(f"[{mi}:a]atrim=duration={TOTAL},asetpts=PTS-STARTPTS,aresample=48000,"
               f"afade=t=in:d=0.4,afade=t=out:st={TOTAL-1.5}:d=1.5,volume=0.9[mus]")
vo_labels = []
for k, at in enumerate(VO_AT):
    filters.append(f"[{vi+k}:a]aresample=48000,adelay={int(at*1000)}|{int(at*1000)},"
                   f"volume=1.6[vo{k}]")
    vo_labels.append(f"[vo{k}]")
filters.append(f"[amb][mus]{''.join(vo_labels)}amix=inputs={2+len(VO_AT)}:normalize=0,"
               f"alimiter=limit=0.95[aout]")
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
