# NEUROMANCIEN — teaser 30 s
### Fausse série prestige cyberpunk · « Une série originale Comptoir IA » · Janvier 2027

## Note d'intention
Réponse au teaser de *Neuromancer* (Apple TV) tourné à Tokyo : eux ont Tokyo,
nous on a **le canal Saint-Martin en 2087**. Même grammaire visuelle que les
teasers de séries prestige — nuit, pluie, néons, anamorphique, teal & magenta,
braam final — mais un décor que personne n'a jamais cyberpunkisé : passerelles
vertes en fer gréées de câbles holographiques, écluses qui fuient de la lumière,
façades haussmanniennes couvertes d'enseignes néon **en français**, péniche
reconvertie en repaire de hacker.

Le héros : **Nico** (vraie tête, transfert d'identité depuis `ref/nico.jpg`),
alias **le Neuromancien**, console cowboy en trench techwear, implant lumineux
à la tempe.

La punchline littéraire (voix off, phrase d'ouverture du roman de Gibson,
détournée) :

> « Le ciel au-dessus du canal était couleur de télé, calée sur un canal mort. »

— double sens canal TV / canal Saint-Martin. C'est ça qui fait « plus stylé » :
pas juste de la belle image, une vraie idée.

## Découpage — 6 plans × 5 s = 30 s

| # | Plan | Description | Texte / VO |
|---|------|-------------|-----------|
| 1 | **Cold open** | Large : le canal la nuit sous la pluie, ciel = statique télé « canal mort », passerelle verte holo-câblée, koïs holographiques sur l'eau noire | VO 1 : « Le ciel au-dessus du canal… » |
| 2 | **Le visage** | Très gros plan : Nico dans la péniche-repaire, visage éclairé par des écrans holo de code français, implant qui pulse | — |
| 3 | **La rue** | Plan pied : Nico marche quai de Valmy sous la pluie néon, passants augmentés, drone-projecteur qui balaie | — |
| 4 | **La plongée** | Il enclenche le jack : la moitié de son visage se dissout en wireframe teal — Paris vectoriel à l'infini derrière son œil | VO 2 : « Ils ont branché la ville sur une intelligence… » |
| 5 | **L'entité** | Très large : silhouette de Nico sur la passerelle face à un visage holographique doré colossal dressé au-dessus du canal | …« Personne n'a demandé ce qu'elle rêvait. » |
| 6 | **Titre** | Plan poitrine : Nico regarde caméra, léger sourire ; titre chrome-glitch « NEUROMANCIEN », « UNE SÉRIE ORIGINALE COMPTOIR IA », « JANVIER 2027 » | Braam + VO 3 : « Neuromancien. Janvier 2027. » |

## Bande-son
- **Musique** (Suno V5, instrumental) : score dark synthwave façon Blade Runner
  2049, cuivres CS-80, sub-bass, montée lente, braam final.
- **Voix off** (ElevenLabs, voix grave FR) : 3 segments ci-dessus.
- **Son diégétique** Seedance (pluie, drones) en fond à 15 %.

## Pipeline
1. `ref/nico.jpg` — **photo de Nico requise** (portrait net, lumière franche)
2. `python3 gen_keyframes.py` — 6 images GPT Image 2 (plan 1 sans ref, 2–6 en
   edit avec transfert d'identité)
3. `python3 gen_voix.py` + `python3 gen_music.py`
4. `python3 gen_clips.py` — Seedance 2.0 image-to-video 4K, 5 s/plan
5. `python3 assemble.py` — montage ffmpeg 3840×2160

Variante verticale TikTok/Reels : préfixer chaque étape image/vidéo/montage de
`AR=916`.
