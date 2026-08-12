# Labo — nos 2 cibles (sélection finale, août 2026)

*Choisies pour : vérification 100 % automatique en arithmétique exacte (erreur impossible),
recherche faisable en CPU modeste (pas besoin des moyens d'un labo), terrain actif mais pas saturé.*

## Cible 1 — Problèmes sommes/différences (AlphaEvolve #42, #43, #44 · esprit Erdős)

Trouver un ensemble fini d'entiers A qui maximise un exposant entre |A+A| et |A-A|.
- Direction #42 : maximiser log|A+A|/log|A-A|. Baseline AlphaEvolve committée ici :
  |A|=309, |A+A|=1367, |A-A|=1163, exposant **1.02290** (`baseline_alphaevolve_p42.json`, vérifiée).
- Direction #44 : AlphaEvolve avait θ=1.1584 (mai 2025), record repris par des humains
  (arXiv:2505.16105). Statut « former_record » = frontière encore mobile.
- Vérif : `python3 sum_difference/verifier.py <fichier.json>` (secondes, entiers exacts).
- Étape 0 avant toute recherche : re-sourcer le record exact du jour (arXiv + wiki Erdős).

## Cible 2 — Factoriser N! en N facteurs (AlphaEvolve #38 · Erdős n°391, Guy–Selfridge, OEIS A034258)

Maximiser le plus petit facteur quand on écrit N! comme produit de N entiers.
- Vérité terrain : b-file OEIS committée (`factorielle/oeis_A034258.txt`, n ≤ ~10 100).
- Terrain de recherche : constructions pour de grands N au-delà de la table, et l'écart
  au terme asymptotique N/e (cf. Tao, arXiv:2503.20170).
- Vérif : `python3 factorielle/verifier.py <fichier.json>` — produit exact en bigint.
- Test de fumée fait : greedy naïf → min=7 pour N=30 (optimum connu : 8). La boucle
  de recherche doit d'abord égaler la table OEIS, puis viser au-delà.

## Protocole (rappel)
1. Baseline reproduite et vérifiée avant toute recherche.
2. Boucle de recherche évolutionnaire (Claude écrit/évolue les heuristiques, calcul local).
3. Second avis GPT-5 (biblio + constructions alternatives + tentative de réfutation) via Nico.
4. Aucun résultat annoncé sans certificat vérifié par script indépendant.
5. Si record battu : certificat + code publiés, soumission à la base concernée, mention IA.

## Piste parallèle (faible coût)
Chasse bibliographique sur des problèmes Erdős listés « ouverts » (voir
`../problemes-ouverts-ia-2026.md`, piste B1) — chaque trouvaille validée est une
contribution officielle créditée sur erdosproblems.com.
