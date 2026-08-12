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
