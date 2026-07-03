#!/usr/bin/env python3
"""Montage final de « La Cérémonie des Prochaines » :
carton d'ouverture (3 s) + 6 segments lip-syncés + carton de fin (4 s),
nappe musicale discrète sous l'ensemble.

Usage: python3 assemble.py [--music-only]
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "trailer"))
from falgen import run, download

R = lambda *p: os.path.join(ROOT, *p)
OUT = R("la-ceremonie-des-prochaines.mp4")

MUSIC_PROMPT = (
    "sparse tense cinematic underscore, low sustained cello and double bass, distant felt piano "
    "notes, faint string harmonics, very restrained, slowly building gravity and quiet anger "
    "toward the end, no melody in the foreground, dark elegant award-ceremony undertone, "
    "fully instrumental"
)


def music():
    out = R("audio", "underscore.mp3")
    if os.path.exists(out):
        return print("underscore: déjà là")
    res = run("fal-ai/elevenlabs/music",
              {"prompt": MUSIC_PROMPT, "music_length_ms": 84000,
               "force_instrumental": True, "output_format": "mp3_44100_128"},
              label="underscore")
    download(res["audio"]["url"], out)
    print("✅ underscore.mp3")


def dur(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).strip())


def assemble():
    segs = [R("synced", f"seg{i}.mp4") for i in range(1, 7)]
    total = 3 + sum(dur(s) for s in segs) + 4
    inputs = ["-loop", "1", "-t", "3", "-i", R("cards", "open.png")]
    for s in segs:
        inputs += ["-i", s]
    inputs += ["-loop", "1", "-t", "4", "-i", R("cards", "end.png"),
               "-i", R("audio", "underscore.mp3")]
    n_open, n_end, n_mus = 0, 7, 8

    f = []
    # Cartons : mise au format + fondus + piste silencieuse
    f.append(f"[{n_open}:v]scale=1920:1080,setsar=1,fps=25,format=yuv420p,"
             f"fade=t=in:d=0.8,fade=t=out:st=2.4:d=0.6[vopen]")
    f.append(f"[{n_end}:v]scale=1920:1080,setsar=1,fps=25,format=yuv420p,"
             f"fade=t=in:d=0.6,fade=t=out:st=3.2:d=0.8[vend]")
    f.append("anullsrc=r=48000:cl=stereo,atrim=duration=3[aopen]")
    f.append("anullsrc=r=48000:cl=stereo,atrim=duration=4[aend]")
    for i in range(1, 7):
        f.append(f"[{i}:v]scale=1920:1080,setsar=1,fps=25,format=yuv420p[v{i}]")
        f.append(f"[{i}:a]aresample=48000,pan=stereo|c0=c0|c1=c1[a{i}]")
    chain = "[vopen][aopen]" + "".join(f"[v{i}][a{i}]" for i in range(1, 7)) + "[vend][aend]"
    f.append(f"{chain}concat=n=8:v=1:a=1[vc][voice]")
    f.append(f"[{n_mus}:a]atrim=duration={total:.2f},asetpts=PTS-STARTPTS,aresample=48000,"
             f"volume=0.16,afade=t=in:d=2,afade=t=out:st={total-4:.2f}:d=4[mus]")
    f.append("[voice][mus]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]")

    cmd = ["ffmpeg", "-y", "-loglevel", "warning", *inputs,
           "-filter_complex", ";".join(f),
           "-map", "[vc]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "224k", "-movflags", "+faststart",
           "-t", f"{total:.2f}", OUT]
    subprocess.run(cmd, check=True)
    print(f"✅ {OUT} ({total:.1f}s)")


if __name__ == "__main__":
    music()
    if "--music-only" not in sys.argv:
        assemble()
