# 🎬 SIMPLE COMME UNE AMPUTATION — bande-annonce

Bande-annonce 60 s (format **Immersive Cinéma 21:9**) du long-métrage d'Alexandre, générée de
bout en bout par IA : **images de référence (Nano Banana Pro)** → **plans vidéo (Seedance 2.0)** →
**musique + voix off (ElevenLabs)** → **montage (Remotion)**.

## Le dossier
| Fichier | Contenu |
|---|---|
| `00-NOTE-INTENTION.md` | Pitch, ton, parti pris visuel, format |
| `01-bible-personnages.md` | Fiches + prompts des **images de référence** (cohérence des persos) |
| `02-decoupage.md` | Le **découpage** en 12 plans de 5 s |
| `03-prompts-seedance.md` | Les **prompts Seedance 2.0**, plan par plan |
| `04-voix-off.md` | Le **script de la voix off** |
| `05-musique-suno.md` | Le **prompt musique** (Suno / ElevenLabs Music) |
| `PIPELINE.md` | La marche à suivre, de la clé API au rendu |
| `falgen.py` `gen_refs.py` `gen_clips.py` `gen_audio.py` | Le code de génération (fal.ai) |
| `references/` | Les 5 portraits de référence générés |
| `remotion/` | Le projet de montage (rendu `out/trailer.mp4`) |

## Rendu rapide
```bash
cd trailer/remotion && npm install
npx remotion render Trailer out/trailer.mp4 --concurrency=2
```
(génération préalable des médias : voir `PIPELINE.md`)
