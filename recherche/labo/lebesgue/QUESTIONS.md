# Registre des questions ouvertes — boucle communauté

*Principe : chaque question posée à un expert (humain ou IA) est tracée ici.
Une réponse reçue = intégrée dans la machine (moteur, notes, stratégie)
puis marquée. Rien ne se perd.*

| # | Question | Posée à | Statut | Intégration |
|---|---|---|---|---|
| Q1 | Faille dans l'argument « max aux coins » (sup_θ puis sup d'une fonction convexe de t) ? | GPT-5 (round 2) ; à poser à D. Madore | ouverte | verrou de soundness du certificateur |
| Q2 | Obstruction connue qui a laissé la borne inférieure dormante depuis 2005 ? | à poser à J. Baez | ouverte | choix stratégique borne inf vs sup |
| Q3 | Standard de vérification pour qu'un certificat d'amateur soit cru (fractions exactes vs intervalles dirigés) ? | GPT-5 (round 2) ; à poser à T. Gowers | ouverte | durcissement arithmétique |
| Q4 | Attaque hiérarchique 5D→8D : héritage des bornes des boîtes 3-formes ? | GPT-5 (round 2) | ouverte | performance du B&B record4 |
| Q5 | Famille de Gibbs (11 dims, candidat 0.83699) vs 4-formes (8 dims, 0.834574) : laquelle certifier en premier ? | GPT-5 (round 2) | ouverte | allocation du calcul |
| Q6 | Minorations par boîte plus fortes que les témoins (aires mixtes, Brunn–Minkowski) ? | note §7 ; expert géométrie convexe (M. Fradelizi ?) | ouverte | accélération du B&B |
| — | « Gonzalez 2026 » : identifiant arXiv exact ? | GPT-5 (round 2) | ouverte | référence à valider ou écarter |
| Q7 | Famille de Gibbs 2014 : nous convergeons vers 0.83754 (800 départs), pas son 0.83699 — bassin étroit, convention différente, ou valeur perfectible ? | à poser à J. Baez / P. Gibbs | ouverte | vraie valeur du candidat gibbs5 |

| Q8 | L'aire de conv(A ∪ (B+t) ∪ (C+u)) est-elle convexe en (t,u) sur un voisinage (rotations fixées) ? Référence ou preuve ? Nos tests : convexe à amplitude 0.15 (0/300 violations), violée à 0.30 (1/200). Si oui localement : le B&B se réduit aux rotations. | GPT-5 round 2 ; D. Madore ; M. Fradelizi (aires mixtes !) | ouverte | RÉDUCTION STRUCTURELLE du coût de certification (facteur ~10^4) |

## Réponses intégrées
- GPT-5 (round 1, 13/08) : requalification candidat/minoration, carré ⊂ disque,
  précédents Gibbs 2014 + Elekes vérifiés, cible 0.834 — tout intégré (notes v2,
  journal séance 4).
