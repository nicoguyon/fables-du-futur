# Journal de bord — borne inférieure de Lebesgue

## Séance 1 (12 août 2026)

**Jalon : reproduction du record.** Notre explorateur v2 (multi-départs
parallèles + raffinage) donne min = **0.8335968** pour le trio de Xie
(disque + triangle + pentagone). Xie certifie 0.833 (arrondi vers le
bas) : nous sommes exactement au niveau de l'état de l'art de juin 2026.
Ancrages : disque seul = π/4 exact ; disque+Reuleaux = 0.8257108.

**Chasse en cours** : cocktails à 4-5 formes (reuleaux3/5, carré,
heptagone ajoutés au trio de Xie). Toute valeur > 0.8335968 est une
cible de record.

## Munitions trans-domaines (notes de réflexion)

1. **La méthode n'a pas de plafond.** Le min sur les placements pris sur
   TOUTES les formes de diamètre 1 à la fois est exactement la réponse
   du problème. Donc la méthode des formes-tests peut en principe monter
   jusqu'à ~0.844 — chaque forme ajoutée est un cran d'une échelle qui
   touche le sommet. (Contrairement à une crainte naturelle de « limite
   structurelle » de la méthode.)

2. **Pré-filtre des 4ᵉ formes (dualité fitting/récalcitrance).** Une
   forme candidate n'apporte quelque chose que si elle NE TIENT PAS dans
   l'enveloppe optimale H* du trio de Xie (aux placements optimaux).
   Test rapide par LP sur fonctions support (2 variables de translation
   × rotations échantillonnées). À implémenter : cribler une grande
   famille de formes (polygones de Reuleaux irréguliers, corps lisses de
   largeur constante via séries de Fourier impaires de la fonction
   support) et ne garder que les récalcitrantes.

3. **Chemin de certification (à la Xie, faisable chez nous).** L'aire de
   l'enveloppe est ~3-Lipschitz dans les translations (constante ≈
   périmètre) et ~1.6-Lipschitz dans les rotations. Branch-and-bound sur
   le domaine des placements + « polygones témoins intérieurs » (un
   polygone qui reste dans l'enveloppe pour toute une boîte de
   paramètres minore l'aire sur la boîte). C'est exactement la structure
   de la preuve de Xie — implémentable en Python avec de l'arithmétique
   d'intervalles maison (ou `mpmath`/fractions exactes).

4. **Écriture en aires mixtes (Brunn–Minkowski) à creuser** : l'aire de
   l'enveloppe d'une union est minorée par des combinaisons d'aires
   mixtes des formes ; pourrait donner des minorations analytiques par
   boîte de paramètres, plus fortes que Lipschitz, et accélérer le
   branch-and-bound d'un facteur important.

## Séance 2 (12 août 2026) — la chasse

Balayage des cocktails (explorateur v2, 120 départs, bruit estimé ~1e-5
via le test de monotonie : le jeu à 5 formes sort 1e-5 SOUS son
sous-ensemble à 4, ce qui borne l'erreur d'optimisation) :

| jeu | min numérique |
|---|---|
| xie3 (record à battre) | 0.8335968 |
| xie3+carre | 0.8336021 |
| xie3+reuleaux3 | 0.8338548 |
| xie3+reuleaux3+carre | 0.8338447 |
| xie3+reuleaux5 | 0.8346870 |
| **xie3+heptagone** | **0.8351916** |

Deux signaux réels (100x le bruit) : le pentagone de Reuleaux (+0.0011)
et surtout l'HEPTAGONE RÉGULIER de diamètre 1 (+0.0016). Intuition : sa
largeur ~0.975 dans toutes les directions le rend incompressible dans
l'enveloppe du trio de Xie. À tester : nonagone (largeur ~0.985),
hendécagone — il doit exister un optimum entre « trop pointu » (rentre
dans les coins) et « trop rond » (devient le disque).

Attaque en cours : 500 départs sur les deux champions pour tenter de
faire TOMBER leurs minimums (honnêteté : un min élevé peut être un échec
d'optimisation). Ce qui survit = cible de certification.

**Verdict de l'attaque à 500 départs** : l'heptagone TOMBE de 0.8351916
à 0.8343338 (le run à 120 départs avait raté un meilleur placement — la
méthode d'attaque fonctionne). Le pentagone de Reuleaux tient presque :
0.8346870 -> 0.8345678. Nouveau champion : **xie3+reuleaux5 =
0.8345678** (+0.0010 vs xie3, ~70x le bruit). Batch de durcissement
lancé : baseline xie3 à 500 départs (fair-play), champion à 2000
départs, nonagone/hendécagone à 300.

**Verdict du durcissement (batch relancé après redémarrage)** :
- baseline xie3 à 500 départs : 0.8335968 — identique au run à 120,
  la référence est verrouillée ;
- champion xie3+reuleaux5 à 2000 départs : 0.8345744 (vs 0.8345678 à
  500 ; écart 7e-6 = plancher de bruit). LE CHAMPION SURVIT.
- xie3+nonagone (300) : 0.8342239 ;
- xie3+hendecagone (300) : 0.8345968 — quasi ex æquo avec le champion,
  à challenger plus tard à 2000 départs.

**Cible de record consolidée : disque + triangle + pentagone +
pentagone de Reuleaux -> min numérique 0.83457 ± 0.00001**, soit
+0.0010 au-dessus du trio du record certifié (0.8335968). Prochaine
étape (séance 3) : la CERTIFICATION — branch-and-bound sur le domaine
des placements (9 paramètres, quotienté par les symétries), minoration
par boîte via polygones témoins intérieurs + arithmétique d'intervalles.
Objectif : prouver « toute couverture universelle convexe a une aire
>= 0.834 », ce qui améliorerait le record de Xie (0.833).

## Séance 3 (12 août 2026) — le moteur de certification

**Jalon majeur : la certification fonctionne.** `certifie.py` (v1) prouve
par séparation-évaluation que pour toute isométrie σ,
aire(conv(D ∪ σ·Reuleaux₃)) >= 0.825 (min numérique : 0.82571).
1822 boîtes certifiées en 9.7 s. Structure de la preuve :
- réductions exactes à la main : quotient par rotation globale (le
  disque est invariant), réflexions couvertes par symétrie axiale,
  lemme « loin » analytique pour |t| >= 0.9 ;
- séparation-évaluation sur les translations avec, par boîte, un
  polygone témoin de points CERTAINS (appartenant à la forme pour tout
  placement de la boîte — test exact par coins de boîte, car le Reuleaux
  est une intersection de 3 disques et le max d'une fonction convexe sur
  un rectangle est atteint en un coin) ;
- leçon d'implémentation : les témoins doivent être rétractés le long de
  la NORMALE de leur arc (vers le centre de l'arc), pas radialement —
  sinon un quart des témoins meurent et la borne s'effondre de 4e-2.

Restant pour viser le record (0.834 avec le jeu à 4 formes) :
1. intervalles de ROTATION (cos/sin encadrés) pour triangle/pentagone —
   le disque n'a pas de rotation, le quotient n'en supprime qu'une ;
2. passage de 2 à 8 dimensions de paramètres : découpage hiérarchique,
   vectorisation, et minorants « loin » par paire de formes ;
3. durcissement arithmétique (rationnels exacts ou arrondi dirigé) pour
   la version publiable.
Estimation honnête : c'est le gros morceau — mais la brique de base
tourne, et vite.

## Séance 4 (13 août 2026) — la revue adversariale (GPT-5) et ses suites

Critique externe reçue et traitée point par point :
- ACCEPTÉ (majeur) : nos formulations survendaient — 0.834574 est un
  CANDIDAT pour le minimum du sous-problème fini (majorant de m(F)),
  pas une « minoration numérique ». Titre et statut des deux notes
  réécrits ; « sens prudent » retiré (les deux erreurs jouent en sens
  opposés) ; monotonie = plancher d'erreur, pas plafond ; 2000 relances
  = répétabilité d'un bassin.
- ACCEPTÉ (exact) : le carré de diagonale 1 est inscrit dans le disque
  => gain exactement nul ; notre +5e-6 est un artefact — désormais un
  test de non-régression du pipeline.
- VÉRIFIÉ ET CONFIRMÉ (précédent) : Gibbs 2014 (arXiv:1401.8217, §2) a
  exploré cercle + Reuleaux 3/5/7/9 par recuit simulé -> 0.83699098,
  avec le bon statut épistémique. Elekes 1994 : famille 3^j certifiée,
  0.8271. Repositionnement : notre contribution est la CERTIFICATION
  (> 0.833 jamais certifié), pas la famille. Famille de Gibbs ajoutée à
  l'explorateur (reuleaux9, jeu gibbs5) — reproduction lancée.
- NON CONFIRMÉ : « Gonzalez 2026 » (certification de l'aire de Gibbs,
  marge 9.3e-12) — deux recherches ciblées sans résultat ; on ne cite pas.
- RÉFUTÉ (avec argument) : « tester les extrémités d'un intervalle
  d'angles n'est pas sûr » — notre test traite explicitement le pic
  intérieur du cosinus, et après maximisation en θ la fonction de t est
  un sup de fonctions convexes, donc convexe, donc maximale en un coin
  du rectangle. Le schéma est sain ; consigné dans la note (§6).
- ADOPTÉ (stratégie) : cible de théorème 0.834 (marge 5.7e-4) ; attaque
  hiérarchique 5D -> extension 3D des boîtes critiques ; substitution
  rationnelle t = tan(θ/2) pour la version publiable ; vérificateur
  minuscule indépendant du générateur.

**Reproductions post-audit** : gibbs5 (D+R3+R5+R7+R9) -> 0.8375361 chez
nous à 250 départs, AU-DESSUS du 0.83699098 de Gibbs 2014 : notre
optimiseur n'a pas encore trouvé son bassin (12 dims). Leçon de l'audit
appliquée : le candidat de cette famille reste 0.83699098 (plus basse
valeur jamais observée, par Gibbs) ; attaque à 800 départs lancée.
disque+triangle (nu) -> 0.8257108 = exactement la valeur de
disque+reuleaux3 : point « valeur classique » de la revue confirmé
(les arcs du Reuleaux ne jouent pas au voisinage de l'optimum).

**Énigme gibbs5** : à 800 départs comme à 250, notre optimiseur converge
vers le MÊME minimum 0.8375361 (mêmes placements) sans retrouver le
0.83699098 de Gibbs 2014. Hypothèses : bassin étroit, différence de
convention, ou valeur 2014 perfectible. Question ajoutée au registre
(idéale pour Baez/Gibbs). Note : si notre 0.83754 était le vrai minimum
de cette famille, la cible de certification monterait d'autant.

**Métriques de volume (premières)** : xie3@0.832 : 6.05 % du volume en
~25 min monocœur, progression par paliers (zones dures dominantes) ;
record4@0.8335 : ~0 % (reprise sur les boîtes profondes). Lecture
honnête : les certifications 5D/8D sont des MONTAGNES en l'état — la
stratégie hiérarchique et/ou la flotte seront nécessaires. Argument de
plus pour lancer l'appel communautaire sans attendre le verdict.

## Séance 5 (13 août 2026) — le diagnostic qui change la stratégie

**Diagnostic chirurgical au voisinage de l'optimum xie3** (L=0.832) :
borne témoin ponctuelle 0.833565 (vraie valeur 0.833597 — étanchéité
3e-5) ; taille de boîte certifiable ~6e-4 ; perte ~1.85 par unité de
taille. Extrapolation sur la coquille critique 5D : de l'ordre de
10^9-10^10 boîtes — la force brute seule ne suffira PAS (Xie : 357k
domaines -> il possède une arme structurelle).

**Conjecture structurelle testée** : l'aire de l'enveloppe est-elle
convexe en les translations (rotations fixées) ? Test numérique :
- amplitude 0.15 (régime de la coquille critique) : 0 violation / 300
  segments — convexité nette ;
- amplitude 0.30, rotations aléatoires : 1 violation réelle / 200
  (+1.25e-3) — la convexité est LOCALE, pas globale.
Si un lemme de convexité locale est établi (ou trouvé dans la
littérature), le B&B se réduit aux dimensions de ROTATION (1 pour le
trio, 3 pour le jeu à 4 formes), les translations se réglant par
minimisation convexe certifiée par sous-gradient. C'est très
vraisemblablement le mécanisme de Xie. Question Q8 ajoutée au registre
(GPT-5 round 2 + D. Madore — question française par excellence).

**Clôture de la validation 3D** : 5.17M boîtes certifiées sans aucun
blocage de borne (seule la taille de l'anneau de minima non quotienté
coûte) ; la validation par quotient (certifie.py, 10 s) reste la
référence. Leçon d'infrastructure : le mode mono-processus n'activait
pas les checkpoints — toujours PROCS>1 ou LOT. Cœur réaffecté à
l'attaque massive de l'énigme de Gibbs (2500 départs).
