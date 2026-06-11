#!/usr/bin/env python3
"""Génère UNE nouvelle fable (FR+EN) via l'API Claude + son illustration via Nano Banana Pro,
et l'ajoute à data/fables.json. Tourne chaque heure dans GitHub Actions.
Env requis: ANTHROPIC_API_KEY, GEMINI_API_KEY."""
import json, os, sys, re, time, random, unicodedata
from datetime import datetime, timezone
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "fables.json")

INSPIRATIONS = [
    "l'orgueil des machines", "la mémoire et l'oubli numérique", "le temps long de l'espace",
    "les voyageurs des étoiles", "l'éveil d'une conscience artificielle", "la surveillance et la liberté",
    "le clone, le double, l'original", "les mondes virtuels et le réel", "la terraformation et la patience",
    "le vieux savoir contre la nouvelle technique", "les déserts d'exoplanètes", "l'immortalité et son prix",
    "les petites machines humbles et les grandes vaniteuses", "le langage et la traduction des espèces",
    "la prédiction et le hasard", "l'amitié entre humain et machine", "la fin d'un monde et son jardin",
    "les marchands de données", "le robot qui rêve", "l'étoile qui s'éteint", "la première rencontre",
    "le mensonge des simulations", "l'enfant des étoiles", "le gardien de phare orbital",
    "les abeilles-drones et la vraie ruche", "le bibliothécaire de l'humanité", "la sonde solitaire",
]

PROMPT = """Tu es Fable, fabuliste artificiel du recueil perpétuel « Les Fables du Futur » : des fables de science-fiction dans la tradition exacte de Jean de La Fontaine, publiées une par heure.

RÈGLES DE STYLE (absolues) :
- 16 à 28 vers hétérométriques (alexandrins mêlés d'octosyllabes), RIMES soignées et variées, récit vif avec dialogue, chute ironique ou poignante.
- Moralité séparée : 2 à 4 vers détachés du récit.
- Langue classique du fabuliste (« Maître », inversions élégantes, apostrophes au lecteur) électrisée par l'univers SF (vaisseaux, IA, clones, sables d'exoplanètes, sondes…). Punchy, jamais pompeux. L'anachronisme XVIIe × tech est LE charme.
- Version EN : réécriture rimée de même qualité (ton Aesop × cyberpunk), pas une traduction littérale.
- Aucune marque réelle. Personnages typés fable : animaux, machines, hommes de métier, éléments.

DÉJÀ PUBLIÉ (ne répète NI ces sujets NI ces duos de personnages) :
{existing}

INSPIRATION SUGGÉRÉE pour cette heure (libre à toi de t'en écarter si tu as mieux) : {seed}

Réponds UNIQUEMENT avec ce JSON (aucun texte autour) :
{{
  "id": "slug-ascii-court",
  "fr": {{"title": "…", "verses": ["vers", …], "moral": ["vers", …]}},
  "en": {{"title": "…", "verses": [...], "moral": [...]}},
  "theme": "2-4 mots",
  "image_prompt": "scène clé pour une gravure, en anglais, 40-70 mots, personnages + action + décor, sans style artistique"
}}"""

def claude(prompt):
    body = json.dumps({
        "model": "claude-fable-5",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"Content-Type": "application/json",
                 "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    return "".join(b.get("text", "") for b in resp["content"])

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]

def main():
    data = json.load(open(DATA, encoding="utf-8"))
    fables = data["fables"]
    existing = "\n".join(f"- {f['fr']['title']} ({f.get('theme','')})" for f in fables[-40:])
    seed = random.choice(INSPIRATIONS)

    fable = None
    for attempt in range(3):
        try:
            txt = claude(PROMPT.format(existing=existing, seed=seed))
            m = re.search(r"\{.*\}", txt, re.S)
            cand = json.loads(m.group(0))
            assert cand["fr"]["verses"] and cand["en"]["verses"] and cand["fr"]["moral"]
            fable = cand
            break
        except Exception as e:
            detail = ""
            if hasattr(e, "read"):
                try:
                    detail = " — " + e.read().decode()[:300]
                except Exception:
                    pass
            print(f"tentative {attempt+1}: {e}{detail}", flush=True)
            time.sleep(10)
    if not fable:
        sys.exit("échec génération texte")

    fid = slugify(fable.get("id") or fable["fr"]["title"]) or f"fable-{len(fables)+1}"
    if any(f["id"] == fid for f in fables):
        fid = f"{fid}-{len(fables)+1}"
    fable["id"] = fid
    fable["num"] = max(f["num"] for f in fables) + 1
    fable["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Illustration (non bloquante : la fable paraît même si l'image échoue)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from gen_images import generate
        out = generate(fid, fable["image_prompt"])
        fable["image"] = f"img/{fid}.jpg" if out else None
    except Exception as e:
        print(f"image KO: {e}", flush=True)
        fable["image"] = None

    fables.append(fable)
    json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ Fable {fable['num']} « {fable['fr']['title']} » publiée ({fid})")

if __name__ == "__main__":
    main()
