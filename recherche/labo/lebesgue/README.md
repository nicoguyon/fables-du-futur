# Labo Lebesgue 🇫🇷 — la couverture universelle (1914)

**Le problème** (Henri Lebesgue, lettre à Pál, 1914) : quelle est la plus
petite surface convexe capable de recouvrir n'importe quelle forme de
diamètre 1 ?

**Frontière actuelle (vérifiée août 2026)** :
- Borne supérieure : **0.8440935944** — Gibbs 2018 (arXiv:1810.10089),
  hexagone régulier de largeur 1 raboté coin après coin. Gibbs est un
  physicien indépendant, pas un académique.
- Borne inférieure : **0.833** certifiée — Xie, juin 2026
  (arXiv:2606.04458), améliorant les 0.832 de Brass–Sharifi (2005).
  Méthode : toute couverture convexe U contient une copie congruente de
  chaque forme de diamètre 1, donc aire(U) >= min sur les placements de
  l'aire de l'enveloppe convexe de l'union de formes-tests choisies
  (Xie : disque + triangle équilatéral + pentagone régulier).

**Notre angle d'attaque : la borne INFÉRIEURE.** C'est le côté purement
computationnel du problème : une optimisation en dimension ~6-9
(rotations + translations des formes-tests), certifiable par
arithmétique d'intervalles, où le record vient d'être bougé il y a deux
mois — la preuve que le terrain est actif et accessible. Idées à tester :
meilleur jeu de formes-tests (4ᵉ forme ? polygones de Reuleaux ?),
meilleure optimisation, puis certification.

## Outils

- `bornes_inf.py` — explorateur numérique : minimise l'aire de
  l'enveloppe convexe d'un jeu de formes placées librement
  (multi-départs + Nelder-Mead). Le disque est discrétisé par un
  polygone inscrit : sous-estimation, donc prudent pour une borne inf.

## Ancrages validés

| Jeu de formes | min numérique | référence |
|---|---|---|
| disque seul | 0.785397 | π/4 = 0.785398 ✅ |
| disque + Reuleaux | 0.825711 | (l'argument Brass–Sharifi 0.832 utilise plus que l'enveloppe seule) |
| disque + triangle + pentagone | **0.8335968** | reproduit le record de Xie (0.833 certifié, juin 2026) ✅ |
| + pentagone de Reuleaux | **0.8345744** | notre cible de record (stable à 2000 départs) 🎯 |

## Garde-fous

1. Un minimum numérique n'est PAS une borne : c'est une cible. La borne
   exige de certifier que TOUT placement donne une aire >= la valeur
   annoncée (balayage certifié du domaine des paramètres, comme Xie).
2. Discrétisations toujours inscrites (jamais circonscrites).
3. Toute annonce passe par une revérification indépendante (second
   script, autre méthode) et le croisement GPT-5.
