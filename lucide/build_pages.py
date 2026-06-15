#!/usr/bin/env python3
"""Génère les pages produit LUCIDE (produit/<slug>.html) à partir de catalog.js.
Le catalogue est extrait via Node (source unique = catalog.js)."""
import json, subprocess, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_catalog():
    js = ('global.window={};require("%s/catalog.js");'
          'process.stdout.write(JSON.stringify(window.LUCIDE_CATALOG))' % ROOT)
    out = subprocess.check_output(["node","-e",js]).decode()
    return json.loads(out)

HEAD = """<!DOCTYPE html><html lang="fr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — LUCIDE · {tagline}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://lucide.vision/produit/{slug}.html">
<meta property="og:type" content="product"><meta property="og:title" content="{name} — LUCIDE">
<meta property="og:description" content="{tagline}"><meta property="og:image" content="https://lucide.vision/lucide/assets/product/{slug}.jpg">
<link rel="icon" href="../assets/logos/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/tokens.css">
<script type="application/ld+json">{jsonld}</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:var(--font-body);color:var(--text);background:var(--bg)}}
a{{color:inherit;text-decoration:none}}img{{display:block;max-width:100%}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 28px}}
.serif{{font-family:var(--font-display)}}.mono{{font-family:var(--font-mono)}}
header{{position:sticky;top:0;z-index:60;background:rgba(246,243,236,.86);backdrop-filter:blur(14px);border-bottom:1px solid rgba(21,24,29,.14)}}
.nav{{display:flex;align-items:center;gap:18px;height:70px;max-width:1240px;margin:0 auto;padding:0 28px}}
.brand{{display:flex;align-items:center;gap:11px}}.brand img{{height:32px}}.brand .wm{{font-family:var(--font-display);font-size:28px;letter-spacing:.14em}}
.nav .back{{margin-left:auto;font-size:14px;color:var(--text-soft)}}
.crumbs{{font-family:var(--font-mono);font-size:12px;color:var(--text-soft);padding:22px 0;letter-spacing:.04em}}
.crumbs a:hover{{color:var(--verre)}}
.product{{display:grid;grid-template-columns:1fr 1fr;gap:clamp(28px,5vw,60px);align-items:start;padding-bottom:60px}}
@media(max-width:840px){{.product{{grid-template-columns:1fr}}}}
.gallery img{{width:100%;border-radius:var(--radius-lg);background:var(--paper-2);aspect-ratio:1/1;object-fit:cover;box-shadow:var(--shadow-sm)}}
.line{{font-family:var(--font-mono);font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--verre)}}
h1{{font-family:var(--font-display);font-size:clamp(38px,6vw,60px);line-height:1;margin:8px 0 6px;font-weight:400}}
.tagline{{font-size:19px;color:var(--text-soft);font-weight:300}}
.price{{font-family:var(--font-mono);font-size:26px;font-weight:700;margin:22px 0 6px}}
.price small{{font-size:13px;color:var(--text-soft);font-weight:400}}
.desc{{font-size:16px;line-height:1.65;color:var(--text-soft);margin:16px 0;font-weight:300}}
.add{{background:var(--ink);color:var(--paper);border:none;border-radius:40px;padding:16px 34px;font-weight:600;font-size:15px;cursor:pointer;transition:.2s;margin-top:8px}}
.add:hover{{background:var(--verre)}}
.specs{{list-style:none;margin:26px 0;border-top:1px solid rgba(21,24,29,.14)}}
.specs li{{padding:13px 0;border-bottom:1px solid rgba(21,24,29,.14);font-size:14.5px;display:flex;gap:10px}}
.specs li::before{{content:"—";color:var(--verre)}}
.verite{{background:var(--ink);color:var(--paper);border-radius:var(--radius-lg);padding:26px 28px;margin-top:8px}}
.verite h3{{font-family:var(--font-display);font-size:24px;font-weight:400;margin-bottom:4px}}
.verite .sub{{font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--aube);margin-bottom:16px}}
.lrow{{display:flex;align-items:center;gap:12px;margin:9px 0;font-family:var(--font-mono);font-size:13px}}
.lrow .lbl{{flex:1}}.lrow .val{{color:var(--aube)}}
.lbar{{height:7px;border-radius:6px;background:rgba(246,243,236,.12);overflow:hidden;flex:1.4}}
.lbar i{{display:block;height:100%;background:var(--aube)}}
.ltot{{border-top:1px solid rgba(246,243,236,.2);margin-top:14px;padding-top:14px;display:flex;justify-content:space-between;font-family:var(--font-mono);font-weight:700}}
.ltot .val{{color:var(--verre)}}
.vfoot{{font-size:12.5px;color:rgba(246,243,236,.6);margin-top:14px;line-height:1.55;font-weight:300}}
footer{{background:var(--ink);color:rgba(246,243,236,.6);padding:40px 0;margin-top:40px;font-family:var(--font-mono);font-size:12px;text-align:center}}
</style></head><body>
<header><div class="nav"><a href="../index.html" class="brand"><img src="../assets/logos/lucide-emblem.svg" alt="LUCIDE"><span class="wm">LUCIDE</span></a><a class="back" href="../index.html#collection">← Toute la collection</a></div></header>
<div class="wrap">
<div class="crumbs"><a href="../index.html">Accueil</a> / <a href="../index.html#collection">{line}</a> / {name}</div>
<div class="product">
  <div class="gallery"><img src="../assets/product/{slug}.jpg" alt="{name} — LUCIDE"></div>
  <div class="info">
    <div class="line">{line}</div><h1>{name}</h1><p class="tagline">{tagline}</p>
    <div class="price">{price} €&nbsp; <small>· prix-vérité, verres inclus</small></div>
    <p class="desc">{desc}</p>
    <button class="add" onclick='go()'>Ajouter au panier</button>
    <ul class="specs">{specs}</ul>
    <div class="verite"><div class="sub">Le prix-vérité, gravé à l'intérieur</div><h3>Où vont vos {price} €</h3>
      {ledger}
      <div class="ltot"><span>Prix-vérité</span><span class="val">{price} €</span></div>
      <p class="vfoot">Aucune ligne cachée. Notre marge couvre l'atelier, l'opticien, le service et la garantie à vie — pas une campagne d'affichage. La même paire, ailleurs, coûterait {industry} €.</p>
    </div>
  </div>
</div></div>
<footer>© 2026 LUCIDE — « Voir clair. » · Marque fictive, exercice créatif inspiré de GDIY #544 (Coline Bertrand).</footer>
<script src="../catalog.js"></script>
<script>
function go(){{const c=JSON.parse(localStorage.getItem('lucide_cart')||'[]');c.push('{slug}');localStorage.setItem('lucide_cart',JSON.stringify(c));location.href='../index.html'}}
</script></body></html>"""

LABELS={"matiere":"Matière (acétate / titane)","verres":"Verres & traitements","facon":"Façon & assemblage",
        "transport":"Transport & étui","marge":"Marge LUCIDE (juste)"}

def build():
    cat=load_catalog(); os.makedirs(os.path.join(ROOT,"produit"),exist_ok=True)
    for p in cat:
        v=p["verite"]; tot=p["price"]; industry=int(round(tot*2.4/5)*5)
        rows=""
        for k in ["matiere","verres","facon","transport","marge"]:
            if v.get(k,0)<=0: continue
            pct=round(v[k]/tot*100)
            rows+=f'<div class="lrow"><span class="lbl">{LABELS[k]}</span><span class="lbar"><i style="width:{pct}%"></i></span><span class="val">{v[k]} €</span></div>'
        specs="".join(f"<li>{html.escape(s)}</li>" for s in p.get("specs",[]))
        jsonld=json.dumps({"@context":"https://schema.org","@type":"Product","name":p["name"],
            "brand":{"@type":"Brand","name":"LUCIDE"},"description":p["desc"],
            "image":f"https://lucide.vision/lucide/assets/product/{p['slug']}.jpg",
            "category":p["line"],
            "offers":{"@type":"Offer","price":p["price"],"priceCurrency":"EUR","availability":"https://schema.org/InStock"},
            "aggregateRating":{"@type":"AggregateRating","ratingValue":"4.8","reviewCount":"127"}},ensure_ascii=False)
        page=HEAD.format(name=html.escape(p["name"]),tagline=html.escape(p["tagline"]),
            desc=html.escape(p["desc"]),slug=p["slug"],line=html.escape(p["line"]),
            price=p["price"],specs=specs,ledger=rows,industry=industry,jsonld=jsonld)
        open(os.path.join(ROOT,"produit",p["slug"]+".html"),"w",encoding="utf-8").write(page)
    print(f"{len(cat)} pages produit générées")

if __name__=="__main__": build()
