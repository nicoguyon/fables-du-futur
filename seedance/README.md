# Seedance 2.0 — plan « plongée Times Square »

Anime `scene-times-square.png` (raptor + aventurier + capitaine pirate sur un
passage piéton de Times Square) en un plan vidéo.

**Mouvement caméra :** vue plongeante descendant vers les trois persos, puis
montée/poussée vers la tour (gratte-ciel illuminé) derrière eux.

## Générer

```bash
# clé fal dans FAL_KEY ou /root/.fal_key (cf. trailer/falgen.py)
python3 seedance/gen_clip.py
```

Sortie : `seedance/clips/times-square-plongee.mp4` (Seedance 2.0 image-to-video,
1080p, 8 s) + l'URL fal hébergée affichée en fin de run.

- Modèle : `bytedance/seedance-2.0/image-to-video`
- Le script uploade d'abord l'image locale vers le storage fal, puis lance le job.
