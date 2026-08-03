# NEUROMANCIEN — faux teaser de série cyberpunk (30 s), avec la vraie tête de Nico

Réponse « en mieux » au teaser Neuromancer d'Apple TV : même codes visuels,
mais canal Saint-Martin 2087 et Nico en console cowboy. Voir `01-script.md`.

## Il manque UNE chose : ta photo
Dépose un portrait net (bonne lumière, visage bien visible) ici :

    neuromancien/ref/nico.jpg

## Ensuite, dans l'ordre
```bash
cd neuromancien
python3 gen_keyframes.py   # 6 images GPT Image 2 (plans 2-6 avec ta tête)
python3 gen_voix.py        # 3 segments de voix off ElevenLabs
python3 gen_music.py       # score Suno V5 instrumental
python3 gen_clips.py       # 6 plans Seedance 2.0, 4K, 5 s
python3 assemble.py        # montage ffmpeg → neuromancien-30s.mp4
```
Chaque étape saute les fichiers déjà présents ; on peut regénérer un seul plan :
`python3 gen_keyframes.py 4 && python3 gen_clips.py 4`.

Version verticale TikTok/Reels : préfixer les étapes keyframes/clips/assemble
de `AR=916`.

Prérequis : `OPENAI_API_KEY`, `FAL_KEY`, `SUNO_API_KEY` dans l'env, et `ffmpeg`
pour le montage (`apt-get install -y ffmpeg` si absent).
