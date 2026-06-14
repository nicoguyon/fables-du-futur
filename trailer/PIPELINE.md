# Pipeline de production — de la clé API au rendu final

Tout est automatisé en Python (génération) + Remotion (montage). La clé fal.ai est lue dans
`/root/.fal_key` (hors repo) ou via la variable d'environnement `FAL_KEY`.

```
┌─ 1. RÉFÉRENCES ─────────┐   ┌─ 2. PLANS VIDÉO ──────────┐   ┌─ 3. SON ───────────────┐
│ gen_refs.py             │   │ gen_clips.py              │   │ gen_audio.py           │
│ nano-banana-pro 21:9 2K │──▶│ Seedance 2.0 ref→video    │   │ ElevenLabs Music + TTS │
│ → references/*.jpg      │   │ 21:9 · 1080p · 5s · 12    │   │ → public/audio/*.mp3   │
│ → references/refs.json  │   │ → public/clips/shotNN.mp4 │   │                        │
└─────────────────────────┘   └───────────────────────────┘   └────────────────────────┘
                                            │
                                            ▼
                              ┌─ 4. MONTAGE (Remotion) ─────────────┐
                              │ remotion render Trailer out/trailer.mp4 │
                              │ 2560×1097 (21:9) · 30 fps · 60 s        │
                              └─────────────────────────────────────────┘
```

## Pré-requis
```bash
export FAL_KEY="xxxxxxxx:xxxxxxxx"        # ou écrire la clé dans /root/.fal_key
cd trailer/remotion && npm install         # dépendances Remotion (une fois)
```

## Étapes
```bash
cd trailer

# 1) Portraits de référence (verrouille les personnages) — ~30 s/portrait
python3 gen_refs.py

# 2) Les 12 plans Seedance 2.0 (cohérence via refs) — ~5 min/plan, 6 en parallèle
python3 gen_clips.py            # ou: python3 gen_clips.py 5 8   pour relancer des plans

# 3) Musique + voix off
python3 gen_audio.py            # ou: python3 gen_audio.py voice   (juste la VO)

# 4) Montage final 21:9
cd remotion
npx remotion render Trailer out/trailer.mp4 --concurrency=2
# Aperçu interactif : npx remotion studio
```

## Remplacer la musique par du Suno officiel
Génère le morceau sur suno.com (prompt dans `05-musique-suno.md`, mode Instrumental), puis :
```bash
cp ~/Downloads/mon_suno.mp3 trailer/remotion/public/audio/music.mp3
cd trailer/remotion && npx remotion render Trailer out/trailer.mp4
```

## Réglages utiles
- **Coût / vitesse :** remplacer `bytedance/seedance-2.0/reference-to-video` par la variante
  `bytedance/seedance-2.0/fast/reference-to-video` dans `gen_clips.py` (moins cher, plus rapide).
- **Audio natif Seedance :** mettre `generate_audio: True` dans `gen_clips.py` pour des bruitages
  diégétiques par plan (par défaut `False` pour garder le mix musique+VO propre).
- **Durée d'un plan :** changer `SHOT_FRAMES` dans `remotion/src/shots.ts` (150 = 5 s @30fps).
