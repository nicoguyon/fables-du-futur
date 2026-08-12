# Journal de bord — t(N) : factoriser N! en N facteurs

## Séance 1 (12 août 2026)

**Records du jour (étape 0)** : Tao et al. (arXiv:2503.20170) ont réglé
l'asymptotique t(N)/N = 1/e − c₀/log N + O(log^−(1+c) N) et prouvé
t(N) ≥ N/3 pour N ≥ 43632 (conjecture Guy–Selfridge). Les valeurs EXACTES
de t(N) = A034258 ne sont connues que jusqu'à N ≈ 10 100 (b-file OEIS,
committée ici). Terrain visé : constructions au-delà de la table.

**Échelle des heuristiques testées** (t trouvé vs optimum connu) :

| N | optimum | v1 glouton | v2 best-fit | v3 LPT+répar. | v4 cofacteur | v5 multi | v4+v5 |
|------|------|-----|-----|-----|-----|-----|-----|
| 30 | 8 | 7 | 8 | 7 | 8 | 8 | **8 ✅** |
| 100 | 29 | 23 | 25 | 28 | 28 | 27 | **28 (−1)** |
| 300 | 90 | 63 | 77 | 71 | 85 | 77 | **85 (−5)** |
| 1000 | 312 | 226 | 247 | 233 | échec colle | 243 | **243 (−69)** |
| 3000 | 960 | 626 | 729 | — | échec colle | 723 | **723 (−237)** |

**Diagnostic** (instrumenté à N=1000, t=312) : le goulot est l'allocation
globale de la « colle » 2^a·3^b. La v4 (chaque premier moyen reçoit un
cofacteur au plus juste) est quasi optimale tant que le stock de 2/3
suffit (−1 à N=100, −5 à N=300) puis s'effondre par pénurie : à N=1000
elle épuise 994 deux et 498 trois avant d'avoir servi les petits premiers
(5, 7, 11...), qui devraient être groupés entre eux (5·7·11 = 385 ≥ 312,
zéro colle). La v5 groupe mais gaspille les gros moyens comme remplisseurs.

**Prochaine itération (v6)** : allocation globale de la colle — décider
QUELS premiers moyens reçoivent de la colle et lesquels se groupent,
p.ex. DP exacte sur la partie lisse / programmation en nombres entiers
locale, ou l'algorithme de la partie computationnelle de Tao et al.
(à lire : leur section calcul + code public éventuel).

**Question posée à GPT-5 (croisement)** : « Quel est l'algorithme de
construction de l'état de l'art pour les bornes inférieures de
OEIS A034258 (t(N), Guy–Selfridge, arXiv:2503.20170) ? Existe-t-il du
code public ? Comment l'allocation des facteurs 2 et 3 y est-elle
optimisée ? »

**v6 (réparation par dons)** : partir de la meilleure construction et
tenter t+1 en déplaçant des premiers des bacs excédentaires vers les
déficitaires. Résultat : aucun gain — la solution gloutonne n'a pas de
mou (à N=1000, presque tous les bacs sont exactement à t, les donneurs
manquent). Confirme que l'écart est STRUCTUREL : le glouton gaspille la
colle 2/3 en dépassements, il faut une allocation globale exacte (v7 :
matching/DP à coût minimal, ou l'algorithme du papier de Tao et al.).

**Règle inchangée** : toute construction est revérifiée en exact
(produit == N!, bigint) inline ET par `verifier.py` avant toute annonce.
