#!/usr/bin/env python3
"""LUCIDE — compositing : applique l'emblème et compose des cartes de marque
(OG, affiches manifeste, prix-vérité) avec une typo et un placement maîtrisés."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
F = "/root/.fonts/"
INK=(21,24,29); PAPER=(246,243,236); AUBE=(236,183,156); VERRE=(47,163,154)

def font(name, size): return ImageFont.truetype(F+name, size)
SERIF=lambda s: font("InstrumentSerif-Regular.ttf", s)
SERIF_I=lambda s: font("InstrumentSerif-Italic.ttf", s)
MONO=lambda s: font("SpaceMono-Regular.ttf", s)
MONO_B=lambda s: font("SpaceMono-Bold.ttf", s)

def emblem(color="ink", h=240):
    f = {"ink":"lucide-emblem.png","white":"lucide-emblem-white.png","verre":"lucide-emblem-verre.png"}[color]
    im = Image.open(os.path.join(A,"logos",f)).convert("RGBA")
    return im.resize((h,h), Image.LANCZOS)

def wm(color="ink"):
    f = "lucide-wordmark.png" if color=="ink" else "lucide-wordmark-white.png"
    return Image.open(os.path.join(A,"logos",f)).convert("RGBA")

def tracked(d, xy, text, fnt, fill, track=0, anchor_center=None):
    x,y=xy
    if anchor_center is not None:
        w=sum(d.textlength(c,font=fnt)+track for c in text)-track
        x=anchor_center-w/2
    for c in text:
        d.text((x,y),c,font=fnt,fill=fill); x+=d.textlength(c,font=fnt)+track

def save(im, name, q=88):
    out=os.path.join(A,"social",name); os.makedirs(os.path.dirname(out),exist_ok=True)
    im.convert("RGB").save(out,"JPEG",quality=q,optimize=True); print("✓",name)

# 1) OG card : sur la hero og.jpg, lockup blanc + signature dans l'espace négatif gauche
def og_card():
    base=Image.open(os.path.join(A,"social","og.jpg")).convert("RGB")
    base=ImageOps.fit(base,(1200,630),Image.LANCZOS); d=ImageDraw.Draw(base)
    # voile dégradé gauche pour lisibilité
    veil=Image.new("L",(1200,630),0); vd=ImageDraw.Draw(veil)
    for x in range(700): vd.line([(x,0),(x,630)],fill=int(150*(1-x/700)))
    dark=Image.new("RGB",(1200,630),INK); base=Image.composite(dark,base,veil)
    d=ImageDraw.Draw(base)
    e=emblem("white",70); base.paste(e,(64,60),e)
    tracked(d,(150,72),"LUCIDE",SERIF(64),PAPER,track=5)
    d.text((66,210),"Voir",font=SERIF(132),fill=PAPER)
    d.text((300,210),"clair.",font=SERIF_I(132),fill=AUBE)
    tracked(d,(70,400),"LA LUNETTE À TRANSPARENCE RADICALE",MONO(20),PAPER,track=3)
    tracked(d,(70,440),"LE PRIX-VÉRITÉ GRAVÉ DANS CHAQUE PAIRE",MONO(20),AUBE,track=3)
    save(base,"og.jpg")

# 2) Chamoisine de marque : emblème tonal centré sur le tissu
def cloth():
    p=os.path.join(A,"product","a02-chamoisine.jpg")
    if not os.path.exists(p): return
    base=Image.open(p).convert("RGB"); W,H=base.size; d=ImageDraw.Draw(base,"RGBA")
    e=emblem("ink",int(W*0.16)); ex,ey=int(W*0.5-e.width/2),int(H*0.42-e.height/2)
    e2=e.copy(); e2.putalpha(e.getchannel("A").point(lambda a:int(a*0.5)))
    base.paste(e2,(ex,ey),e2)
    tracked(d,(0,ey+e.height+14),"VOIR CLAIR",MONO(int(W*0.028)),(21,24,29,150),
            track=int(W*0.012),anchor_center=W*0.5)
    save(base,"a02-chamoisine-brand.jpg")

# 3) Affiche manifeste (1:1) : fond encre, type, emblème
def poster(name, top, big_i, lines, accent=AUBE):
    im=Image.new("RGB",(1080,1080),INK); d=ImageDraw.Draw(im)
    e=emblem("white",84); im.paste(e,(80,80),e)
    tracked(d,(180,96),"LUCIDE",SERIF(60),PAPER,track=5)
    tracked(d,(80,300),top,MONO(24),accent,track=4)
    d.text((76,350),big_i[0],font=SERIF(118),fill=PAPER)
    d.text((76,470),big_i[1],font=SERIF_I(118),fill=accent)
    y=660
    for ln in lines:
        d.text((80,y),ln,font=SERIF(40),fill=PAPER); y+=58
    tracked(d,(80,1000),"LUCIDE.VISION · GDIY #544",MONO(18),(246,243,236,120) if False else (150,150,150),track=3)
    save(im,name)

# 4) Prix-vérité — graphique comparatif (pour l'Ardoise & le journal)
def prix_verite_plate():
    im=Image.new("RGB",(1080,1350),PAPER); d=ImageDraw.Draw(im)
    d.rectangle([40,40,1040,1310],outline=INK,width=3)
    tracked(d,(0,90),"LE PRIX-VÉRITÉ",MONO_B(30),VERRE,track=6,anchor_center=540)
    d.text((540,140),"L'Aube",font=SERIF(96),fill=INK,anchor="ma")
    tracked(d,(0,270),"OÙ VONT VOS 95 €",MONO(22),INK,track=4,anchor_center=540)
    rows=[("Acétate italien",14,15),("Verres anti-reflet",21,22),("Façon & atelier",18,19),
          ("Transport & étui",3,3),("Marge LUCIDE (juste)",39,41)]
    y=360
    for lbl,val,pct in rows:
        d.text((90,y),lbl,font=MONO(26),fill=INK)
        d.text((990,y),f"{val} €",font=MONO_B(26),fill=VERRE,anchor="ra")
        d.rounded_rectangle([90,y+38,990,y+54],8,fill=(220,213,200))
        d.rounded_rectangle([90,y+38,90+int(900*pct/100),y+54],8,fill=AUBE)
        y+=104
    d.line([90,y+6,990,y+6],fill=INK,width=2)
    d.text((90,y+24),"PRIX-VÉRITÉ",font=MONO_B(34),fill=INK)
    d.text((990,y+24),"95 €",font=MONO_B(34),fill=VERRE,anchor="ra")
    d.text((90,y+90),"La même paire, dans l'industrie :",font=SERIF(40),fill=INK)
    d.text((990,y+84),"240 €",font=SERIF_I(56),fill=AUBE,anchor="ra")
    tracked(d,(0,y+180),"ON A JUSTE ENLEVÉ LE MENSONGE.",MONO(22),INK,track=3,anchor_center=540)
    save(im,"prix-verite-plate.jpg")

if __name__=="__main__":
    og_card()
    cloth()
    poster("manifeste-1","DE VRAIES PROMESSES",("Pas de","label."),
           ["Pas de certification-décor.","Une charte. Des preuves.","Le reste, c'est du marketing."])
    poster("manifeste-2","LA COLLECTION",("Quatorze","pièces."),
           ["Pas une de trop.","On ne multiplie pas l'offre","pour vous vendre du flou."],accent=VERRE)
    poster("manifeste-3","RÉPARABLE À VIE",("On ne jette","pas."),
           ["Verres remplaçables.","Charnières vissées.","On ne jette pas la lumière."])
    prix_verite_plate()
    print("compositing terminé")
