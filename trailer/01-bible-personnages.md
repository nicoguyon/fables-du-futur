# Bible de personnages — images de référence

> **But :** verrouiller l'apparence de chaque personnage AVANT de générer la moindre vidéo.
> On produit d'abord **une image de référence par personnage** (Nano Banana Pro / gemini-3-pro-image),
> puis on injecte ces images comme *reference images* dans Seedance 2.0 pour chaque plan.
> Résultat : le **même visage, la même silhouette, les mêmes vêtements** d'un plan à l'autre.

**Charte visuelle commune à toutes les références** (à coller en tête de chaque prompt) :
> *Photorealistic cinematic film still, anamorphic 21:9 framing, shot on ARRI Alexa with vintage
> Cooke lenses, soft cinematic skin tones, slightly desaturated pastel palette with one saturated
> accent colour, gentle film grain, naturalistic but flattering lighting. Neutral grey studio
> background for the reference portrait. Single subject, full body and face clearly visible,
> consistent identity sheet.*

---

## 1. JULIEN — le protagoniste · 40 ans
**Rôle :** vendeur de voitures électriques, « Monsieur-je-sais-tout ». Mari modèle qui bascule.
**Arc visuel :** propre et souriant au début → fébrile, cerné, déterminé à mesure qu'il veut
perdre sa jambe → apaisé, lumineux, libre à la fin.

**Signalétique (à garder identique) :**
- Homme blanc, 40 ans, 1m80, carrure moyenne.
- Cheveux châtains coupe nette poivre-et-sel naissant, légère barbe de trois jours.
- Yeux noisette, sourire commercial un peu trop large.
- **Tenue 1 (vendeur) :** polo bleu marine de concession avec petit logo brodé, badge/lanyard,
  chino beige, baskets blanches propres.
- **Marqueur clé :** il porte de plus en plus son attention/regard sur sa **jambe gauche**
  (qu'il finit par traiter comme un objet étranger).

**Prompt image de référence :**
```
[CHARTE COMMUNE] Reference identity sheet of JULIEN, a 40-year-old white man, 1m80, athletic-average
build, neat chestnut hair turning slightly salt-and-pepper, three-day stubble, hazel eyes, a slightly
too-wide salesman smile. Wearing a navy-blue car-dealership polo shirt with a small embroidered logo,
a lanyard badge, beige chinos and clean white sneakers. Confident, friendly posture. Neutral grey
studio background, full body visible, face sharp and well-lit. Photorealistic cinematic film still.
```

---

## 2. LINDA — l'épouse · 40 ans
**Rôle :** « Madame Santé ». Fan de bien-être, bougies, jiu-jitsu brésilien, mobilité, diète.
Met toute la famille au régime. Énergie solaire, contrôle bienveillant.

**Signalétique :**
- Femme, 40 ans, silhouette athlétique et tonique (BJJ).
- Cheveux bruns tirés en chignon haut serré, peau éclatante sans maquillage, boucles d'oreilles minimalistes.
- **Tenue 1 (lifestyle) :** brassière et legging de sport beige/sauge, tapis de yoga roulé sous le bras,
  bouteille d'eau en inox, parfois une **bougie artisanale** à la main.
- **Tenue 2 (BJJ) :** kimono (gi) blanc, ceinture violette nouée.
- **Accessoires récurrents :** bougies, kombucha, fruits verts, assiettes minuscules.

**Prompt image de référence :**
```
[CHARTE COMMUNE] Reference identity sheet of LINDA, a fit toned 40-year-old woman, brown hair pulled
into a tight high bun, glowing bare-faced skin, minimalist earrings. Wearing a sage-beige sports bra
and matching leggings, holding a rolled yoga mat and a steel water bottle, an artisanal scented candle
nearby. Serene, radiant, gently controlling expression. Neutral grey studio background, full body
visible. Photorealistic cinematic film still.
```

---

## 3. AXEL — le fils · jeune ado
**Rôle :** l'ado type. Un petit bouton sur le nez **caché derrière un gros sparadrap** (gag récurrent
et marqueur d'identification immédiat).

**Signalétique :**
- Garçon ~14 ans, dégingandé, cheveux mi-longs dans les yeux.
- **MARQUEUR CLÉ NON NÉGOCIABLE :** un **grand sparadrap beige bien visible en travers du nez**.
- **Tenue :** hoodie oversize gris, casque audio autour du cou, téléphone à la main, regard fuyant.

**Prompt image de référence :**
```
[CHARTE COMMUNE] Reference identity sheet of AXEL, a lanky ~14-year-old teenage boy, medium-length hair
falling over his eyes, slightly slouched. IMPORTANT distinctive feature: a large beige adhesive bandage
(sticking plaster) prominently placed across the bridge of his nose, hiding a pimple. Wearing an oversized
grey hoodie, headphones around his neck, holding a smartphone, avoidant teenage gaze. Neutral grey studio
background, full body visible. Photorealistic cinematic film still.
```

---

## 4. LUSTUCRU — le chien
**Rôle :** le chien de la famille. Témoin muet, comique, attachant.

**Signalétique :**
- Chien de taille moyenne, type bâtard adorable / griffon à poil dur beige-roux ébouriffé.
- Truffe noire, regard expressif, une oreille qui tombe, collier rouge avec médaille « LUSTUCRU ».

**Prompt image de référence :**
```
[CHARTE COMMUNE] Reference identity sheet of LUSTUCRU, an adorable medium-sized scruffy mixed-breed dog,
wiry sandy-ginger fur, black nose, very expressive eyes, one floppy ear, wearing a red collar with a tag.
Sitting, head tilted, endearing. Neutral grey studio background, full body visible. Photorealistic
cinematic film still.
```

---

## 5. MICHAËL — le chirurgien
**Rôle :** le chirurgien qui « remet la jambe en place ». Calme, droit, attaché au serment d'Hippocrate.
Julien finit par le détester puis le kidnapper. Arc : autorité sereine → terreur du kidnappé → dilemme moral.

**Signalétique :**
- Homme, ~45-50 ans, élégant, lunettes fines, tempes grisonnantes, mains soignées.
- **Tenue 1 (bloc) :** blouse/scrubs vert chirurgical, charlotte, masque baissé sous le menton.
- **Tenue 2 (kidnappé) :** chemise froissée, ligoté sur une chaise, transpirant, lunettes de travers.

**Prompt image de référence :**
```
[CHARTE COMMUNE] Reference identity sheet of MICHAËL, an elegant 45-50-year-old surgeon, thin glasses,
greying temples, well-groomed hands. Wearing green surgical scrubs and a scrub cap, surgical mask pulled
down under the chin. Calm, authoritative, reassuring expression. Neutral grey studio background, full body
visible. Photorealistic cinematic film still.
```

---

## Ordre de génération recommandé
1. Générer les **5 portraits de référence** ci-dessus → `trailer/references/julien.jpg`, `linda.jpg`,
   `axel.jpg`, `lustucru.jpg`, `michael.jpg`.
2. (Optionnel mais conseillé) générer **1 image-clé par plan** (keyframe) à partir des portraits, pour
   donner à Seedance un point de départ visuel fort sur chaque plan.
3. Lancer Seedance 2.0 en **image→vidéo** avec les portraits comme *reference images* (voir `03-prompts-seedance.md`).
