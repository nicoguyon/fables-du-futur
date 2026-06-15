#!/usr/bin/env python3
"""LUCIDE — montage final du film avec ffmpeg : cartes + 8 plans Seedance,
fondus enchaînés (xfade), sous-titres gravés, mix musique + voix off.
Sortie: film/lucide-voir-clair.mp4 (1080p, 24fps)."""
import os, subprocess, json

ROOT = os.path.dirname(os.path.abspath(__file__))
CL = os.path.join(ROOT, "film", "clips"); CARDS = os.path.join(ROOT, "film", "cards")
AUD = os.path.join(ROOT, "film", "audio"); OUT = os.path.join(ROOT, "film", "lucide-voir-clair.mp4")
FONT = "/root/.fonts/SpaceMono-Regular.ttf"
W, H, FPS, XF = 1920, 1080, 24, 0.5

# ordre : (source, durée forcée s, sous-titre ou None)
SEQ = [
 ("card:title.jpg", 3.0, None),
 ("clip:c1-oeil",   5.0, "Le matin, tout est clair."),
 ("clip:c2-surenchere", 6.0, "La lunette : l'industrie de la surenchère."),
 ("clip:c3-acetate",5.0, "La matière, honnête."),
 ("clip:c4-graving",5.0, "Le prix — le vrai — gravé dedans."),
 ("clip:c5-aube",   5.0, "Le bon verre. Le juste prix."),
 ("clip:c6-elise",  5.0, "De vrais visages."),
 ("clip:c7-marius", 5.0, "Aucune retouche. Aucune promesse creuse."),
 ("clip:c8-counter",5.0, "Chez votre opticien de confiance."),
 ("card:end.jpg",   5.0, None),
]

def esc(t):
    return t.replace("\\","\\\\").replace(":","\\:").replace("'","’").replace(",","\\,")

def build():
    inputs, filt, labels = [], [], []
    for i,(src,dur,sub) in enumerate(SEQ):
        kind,name = src.split(":")
        if kind=="card":
            inputs += ["-loop","1","-t",f"{dur}","-i",os.path.join(CARDS,name)]
        else:
            inputs += ["-i",os.path.join(CL,name+".mp4")]
        v=(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
           f"setsar=1,fps={FPS},format=yuv420p,trim=duration={dur},setpts=PTS-STARTPTS")
        if sub:
            v+=(f",drawtext=fontfile={FONT}:text='{esc(sub)}':fontcolor=white:fontsize=34:"
                f"box=1:boxcolor=0x15181d@0.55:boxborderw=18:x=(w-text_w)/2:y=h-130:"
                f"alpha='if(lt(t,0.4),t/0.4,if(lt(t,{dur-0.5}),1,({dur}-t)/0.5))'")
        filt.append(v+f"[v{i}]"); labels.append(f"[v{i}]")
    # chaîne xfade
    durs=[d for _,d,_ in SEQ]; prev="[v0]"; off=durs[0]-XF
    for i in range(1,len(SEQ)):
        out=f"[x{i}]" if i<len(SEQ)-1 else "[vout]"
        filt.append(f"{prev}{labels[i]}xfade=transition=fade:duration={XF}:offset={off:.3f}{out}")
        prev=out; off+=durs[i]-XF
    total=sum(durs)-XF*(len(SEQ)-1)
    # audio : musique douce + voix
    ai=len(SEQ)
    inputs += ["-i",os.path.join(AUD,"music.mp3"),"-i",os.path.join(AUD,"voix.mp3")]
    filt.append(f"[{ai}:a]volume=0.32,afade=t=in:st=0:d=1.5,afade=t=out:st={total-2:.2f}:d=2[mus]")
    filt.append(f"[{ai+1}:a]volume=1.35[vo]")
    filt.append(f"[mus][vo]amix=inputs=2:normalize=0:duration=first,atrim=duration={total:.2f}[aout]")
    cmd=["ffmpeg","-y","-loglevel","error",*inputs,"-filter_complex",";".join(filt),
         "-map","[vout]","-map","[aout]","-c:v","libx264","-crf","18","-preset","slow",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",OUT]
    print(f"montage… durée ≈ {total:.1f}s")
    subprocess.run(cmd,check=True)
    d=json.loads(subprocess.check_output(["ffprobe","-v","quiet","-print_format","json",
        "-show_format","-show_streams",OUT]))
    print("✅",OUT, f'{float(d["format"]["duration"]):.1f}s', f'{int(d["format"]["size"])//1024} Ko')

if __name__=="__main__": build()
