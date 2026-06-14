# Prompts Seedance 2.0 — plan par plan

**Modèle :** `bytedance/seedance-2.0/reference-to-video` (fal.ai)
**Réglages communs :** `aspect_ratio: "21:9"` · `resolution: "1080p"` · `duration: "5"` · `generate_audio: false`
**Continuité personnages :** on passe les portraits de `references/` dans `image_urls`, et le prompt
les appelle par `@Image1`, `@Image2`… **dans l'ordre de la liste**.

> Tous ces prompts sont implémentés tels quels dans `gen_clips.py` (source de vérité exécutable).
> Préfixe de style commun (« CINE ») appliqué à chaque plan :
> *Anamorphic 21:9 cinematic film still in motion, ARRI Alexa + vintage Cooke lenses, shallow DoF,
> film grain, dark deadpan comedy à la Dupieux/Lanthimos: beautiful polished imagery, unsettling calm.*

| Plan | Réfs (ordre = @Image1…) | Action clé |
|---|---|---|
| 01 | julien | Showroom : remise des clés, sourire commercial, dolly-in héroïque |
| 02 | linda, axel, julien, lustucru | Cuisine : la diète, assiettes minuscules, cadrage symétrique |
| 03 | julien | Garage : la chute au ralenti |
| 04 | julien | Hôpital : il fixe sa jambe gauche étrangère |
| 05 | julien | Forêt : faux accident de chasse |
| 06 | julien | Atelier : jambe dans la neige carbonique |
| 07 | julien | Chantier : le bloc de béton qui descend |
| 08 | julien | Voie ferrée : jambe sur le rail, phare du train |
| 09 | michael, julien | Bloc op : Michaël « répare » / la haine dans les yeux de Julien |
| 10 | michael, julien | Cave : Michaël ligoté, le scalpel glissé |
| 11 | julien | Réveil : la jambe enfin disparue, sourire de soulagement |
| 12 | julien, lustucru | Route à l'aube : liberté en béquilles, Lustucru le rejoint |

**Pourquoi `reference-to-video` et pas `image-to-video` ?** La variante *reference* accepte jusqu'à
**9 images** et permet de combiner plusieurs personnages dans un même plan (ex. plan 02 : Linda + Axel +
Julien + Lustucru) en gardant chaque identité — impossible avec une seule image de départ.

**Relancer un plan** (ex. si un rendu ne plaît pas) :
```bash
cd trailer && python3 gen_clips.py 9       # régénère le plan 9
```
(supprime d'abord `remotion/public/clips/shot09.mp4` pour forcer la régénération.)
