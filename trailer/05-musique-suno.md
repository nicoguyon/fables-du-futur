# Musique de bande-annonce

## Le brief musical
Une **comédie noire** : la musique doit être *jolie et inquiétante à la fois*. On vise le décalage
entre la douceur mélodique et la noirceur du sujet — l'école **Jon Brion / Yann Tiersen (Amélie) /
Yorgos Lanthimos**. Une valse bancale, un tic-tac d'horloge, des pizzicati malicieux, qui montent
vers un climax doux-amer et lumineux sur la fin (plans 11-12).

**Structure (60 s) :**
- 0:00–0:15 — pizzicati légers + glockenspiel, naïf, presque publicitaire (installation).
- 0:15–0:40 — tic-tac, valse bancale, tension comique qui s'emballe (la chute + les tentatives).
- 0:40–0:50 — cordes graves, suspense (le réparateur / le kidnapping).
- 0:50–1:00 — piano + cordes amples, climax émotionnel doux-amer, résolution lumineuse (la liberté).

---

## Option A — Suno officiel *(préféré par le brief)*
Je n'ai **pas** de clé API Suno officielle dans cette session. Pour utiliser Suno :
1. Va sur suno.com, crée le morceau avec le prompt ci-dessous (mode *Instrumental*).
2. Dépose le MP3 dans `trailer/remotion/public/audio/music.mp3` (écrase le placeholder).

**Prompt Suno (style) :**
```
dark whimsical cinematic trailer score, off-kilter waltz, playful pizzicato strings, ticking clock
percussion, glockenspiel, deep cello, a single melancholic piano, building from naive and quirky to
a bittersweet emotional climax, in the style of Jon Brion and Yann Tiersen, instrumental, 60 seconds
```
**Titre / tags :** `cinematic, dark comedy, waltz, instrumental, bittersweet`

## Option B — généré automatiquement (déjà câblé) *(fallback dispo maintenant)*
À défaut de Suno, le script `gen_audio.py` génère la musique via **ElevenLabs Music** sur fal
(`fal-ai/elevenlabs/music`, `force_instrumental: true`, `music_length_ms: 60000`) avec le même prompt.
Résultat → `trailer/remotion/public/audio/music.mp3`. Swappable à tout moment par un MP3 Suno.
