# MÉGA-POST X — à publier le 14 août 2026 au matin
# (thread principal en français + 2 tweets compagnons EN + règles d'envoi)

## THREAD PRINCIPAL 🇫🇷

**1/12**
Qu'est-ce qui vous plaît le plus pour les vacances : générer des images de vous en pape sur la plage… ou essayer de faire avancer un théorème de mathématiques vieux de 112 ans, sans être mathématicien, avec l'IA ?
Moi j'ai choisi. Voilà l'expérience que je lance publiquement. 🧵

**2/12**
Le déclic : il y a 4 jours, un ingénieur d'Anthropic (pas matheux du tout) a demandé à Claude, en joggant, de « tenter l'hypothèse de Riemann ». Échec sur Riemann — mais en chemin l'IA a relevé une borne vieille de 35 ans (41.6 % → 67.2 % des zéros sur la droite critique), preuve vérifiée en Lean, relue par Conrey et Goldston.

**3/12**
Alors je me suis dit : et si un amateur français faisait pareil, en public, sur un problème français ?
Mon choix, expliqué comme à un enfant : tu as plein de biscuits de formes différentes — ronds, triangles, étoiles — mais tous tiennent dans ta main. Quelle est la PLUS PETITE boîte qui peut ranger n'importe lequel d'entre eux ?
C'est la question posée par Henri Lebesgue en 1914. Personne n'a la réponse depuis 112 ans.

**4/12**
La méthode de l'expérience :
— je choisis le problème et je pilote ;
— Claude (Anthropic) conçoit les algorithmes et calcule, nuit et jour, avec checkpoints ;
— GPT-5 joue le rapporteur hostile et attaque tout ;
— et VOUS, mathématiciens, vous tranchez.
Tout est public, tout se reproduit en minutes.

**5/12**
Où on en est après 48 h, en toute transparence (règle de la maison : on explique tout simplement, et on ne prétend JAMAIS plus que ce qu'on a) :
✅ méthode du record reproduite (0.8336 ≈ le 0.833 certifié de Xie, juin 2026)
✅ un candidat : ajouter un pentagone de Reuleaux pousse le plancher potentiel à 0.8346
⏳ certification en cours (des milliards de configurations à écarter)
❌ rien de « prouvé » encore — et on ne dira jamais le contraire

**6/12**
Le croisement d'IA a déjà payé : GPT-5 a attrapé une vraie erreur d'énoncé chez nous (une valeur atteignable présentée comme une borne), on a corrigé publiquement. Et nous, on a vérifié ses références sur pièces : deux confirmées, une introuvable — écartée. Les IA se surveillent mutuellement, les humains arbitrent.

**7/12**
Et ce matin, l'expérience a produit sa première vraie CONJECTURE.
Version enfant : quand tu écartes deux jouets posés sur une nappe, la nappe qu'il faut pour les couvrir tous les deux grandit toujours « en accélérant », jamais par à-coups vers le bas.
Version matheux : l'aire de l'enveloppe convexe semble CONVEXE en les translations, localement (0 violation sur 300 tests dans le régime critique).
Si ce lemme tient → le coût de la preuve s'effondre d'un facteur ~10 000.

**8/12**
C'est une question de géométrie convexe à la française (aires mixtes, Brunn–Minkowski). Et c'est exactement le genre de point où on a besoin de vous : une preuve, une référence, ou un contre-exemple.

**9/12**
Le contrat de l'expérience, publiquement :
— chaque semaine, une hypothèse falsifiable + le code pour la tester ;
— chaque affirmation étiquetée : candidat / durci / certifié ;
— toute invalidation est un CADEAU : on remercie, on corrige en public, c'est déjà documenté dans notre journal de bord.

**10/12**
Appel aux mathématiciens français (et aux autres) : venez casser ça.
La note de recherche (avec schémas), le code (~500 lignes de Python), le journal complet :
→ [LIEN NOTE FR]
→ [LIEN REPO GITHUB]
→ [LIEN NOTE EN]

**11/12**
Je mentionne quelques personnes dont le regard serait précieux — pas pour le buzz, pour l'arbitrage. En France : @gro_tsen (le lemme de convexité, c'est pour vous), @micmaths, @VillaniCedric, @roger_mansuy, @ElJj. Standard de preuve et IA : @wtgowers. Le gardien historique du problème : @johncarlosbaez. Cassez, validez, orientez.

**12/12**
Objectif final assumé : une vraie avancée certifiée sur le plancher de Lebesgue — un théorème, pas un tweet.
Si ça marche : la recette sera publique et réutilisable sur d'autres problèmes du patrimoine mathématique français.
Si ça casse : vous aurez le rapport d'autopsie complet.
Rendez-vous chaque semaine. Allez, on y va. 🇫🇷📐

## TWEET COMPAGNON EN (à poster en réponse au 10/12)
For English-speaking mathematicians: an amateur + adversarial AIs, publicly attacking the lower bound of Lebesgue's universal covering problem (state of the art: 0.833 certified, Xie 2026). Our candidate 4-shape family targets 0.834+, certification running, and a fresh local-convexity conjecture that would collapse the proof cost. Break it: [LIEN EN]

## TWEET BONUS ÉNIGME (à poster le lendemain, relance naturelle)
Énigme pour les geeks de géométrie : Gibbs (2014) rapportait 0.83699 pour l'embouteillage minimal de {cercle + Reuleaux 3,5,7,9}. Notre optimiseur, sur SA famille, reconverge obstinément vers 0.83754 (800 départs). Bassin étroit ? Convention différente ? Valeur perfectible ? Le premier qui tranche gagne notre gratitude éternelle + son nom au journal de bord.

## IMAGES (dans le même dossier du repo)
- img1_configuration.png -> joindre au tweet 3/12 (ou 1/12 en héros)
- img2_bornes.png -> joindre au tweet 3/12 ou 5/12
- img3_convexite.png -> joindre au tweet 7/12 (la conjecture)

## RÈGLES D'ENVOI
1. Handles VÉRIFIÉS le 13/08 : @gro_tsen, @micmaths, @johncarlosbaez, @wtgowers, @VillaniCedric (officiel — attention aux comptes fans), @roger_mansuy (avec underscore). Reste à confirmer d'un clic dans la recherche X : @ElJj (sinon le retirer).
2. Remplacer les [LIENS] : note FR + note EN (activer le partage dans le menu de chaque page artifact) + repo github.com/nicoguyon/fables-du-futur/tree/claude/math-problems-research-npnrg2/recherche/labo/lebesgue
3. Poster le thread d'un bloc le matin (9h-10h, bon créneau), le tweet EN en réponse, l'énigme le lendemain.
4. Ne JAMAIS éditer vers plus de certitude que le texte — il est calibré au millimètre épistémique.
