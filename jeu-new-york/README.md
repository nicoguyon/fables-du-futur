# 🗽 NEW YORK — le jeu vidéo · teaser 15 s

Teaser de 15 secondes (1920×1080, 30 fps) du jeu **NEW YORK** (Manhattan, 2027).
Personnages : **Yosh** (pond un champignon), **Mara** (comme Mario, plus grand & très
rapide), **Pirates** (bras-canon). Le HUD met en scène les règles de vie du jeu.

## Le dossier
| Fichier | Contenu |
|---|---|
| `00-note-intention.md` | Pitch, ton, format, règles de jeu |
| `01-bible-personnages.md` | Yosh, Mara, Pirates |
| `02-decoupage.md` | Le découpage en 5 plans |
| `new-york-teaser.mp4` | **La vidéo finale (15 s)** |

## Comment c'est fait
Contrairement à la bande-annonce `../trailer/` (qui passe par fal.ai → Seedance), ce
teaser est **rendu 100 % par code** avec Remotion (React + SVG) : aucune clé API
nécessaire. Le code de la composition vit dans `../trailer/remotion/src/JeuNewYork.tsx`.

## Re-rendre / éditer
```bash
cd ../trailer/remotion
npm install                 # une fois
npx remotion studio         # aperçu interactif (composition « JeuNewYork »)
npx remotion render JeuNewYork out/new-york-teaser.mp4 --concurrency=2
```

## Le découpage en 5 plans
1. **0–3,5 s — La ville** : skyline de gratte-ciel, grand soleil, taxis, vélos, piétons, magasins. Cartons « NEW YORK / 2027 ».
2. **3,5–7 s — Les héros** : Mara fonce, Yosh pond un champignon, Pirates lève son bras-canon.
3. **7–10 s — Les dangers** : un taxi te roule dessus (−2 ❤), un boulet de canon te fonce dedans (−3 ❤).
4. **10–13 s — Chaos & boost** : tornade, gratte-ciel qui s'effondre (« évite les effondrements »), puis un bateau (+7 km).
5. **13–15 s — Logo** : « NEW YORK — le jeu vidéo · 2027 · bientôt ».
