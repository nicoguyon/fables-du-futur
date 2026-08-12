#!/usr/bin/env python3
"""Vérificateur EXACT pour « Factoriser N! en N facteurs » (AlphaEvolve #38,
lié au problème d'Erdős n°391 / conjecture de Guy–Selfridge, OEIS A034258).

Objet vérifié : une liste de N entiers >= 1 dont le produit vaut exactement N!.
Score = min(facteurs). C(N) est le meilleur score possible.
Tout est en entiers Python (précision arbitraire) : aucune erreur possible.

Usage :
  python3 verifier.py fichier.json   # {"N": 100, "facteurs": [entiers...]}

La vérité terrain pour N <= ~10100 est dans oeis_A034258.txt (b-file OEIS) :
toute construction doit d'abord ÉGALER ces valeurs (baseline), l'objectif
de recherche est au-delà de la table (grands N) ou sur les variantes du
problème (bornes asymptotiques, second ordre — cf. Tao, arXiv:2503.20170).
"""
import json
import math
import sys


def verifie(n, facteurs):
    assert len(facteurs) == n, f"Il faut exactement N={n} facteurs (reçu {len(facteurs)})"
    assert all(isinstance(f, int) and f >= 1 for f in facteurs), "Facteurs entiers >= 1 requis"
    produit = 1
    for f in facteurs:
        produit *= f
    assert produit == math.factorial(n), "Le produit ne vaut PAS N! — construction invalide"
    return min(facteurs)


def oeis_valeur(n, chemin="oeis_A034258.txt"):
    try:
        for ligne in open(chemin):
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            k, v = ligne.split()
            if int(k) == n:
                return int(v)
    except FileNotFoundError:
        pass
    return None


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    n, facteurs = data["N"], data["facteurs"]
    score = verifie(n, facteurs)
    print(f"Construction VALIDE : {n}! = produit de {n} facteurs, min = {score}")
    ref = oeis_valeur(n)
    if ref is not None:
        etat = "ÉGALE" if score == ref else ("BAT (?! à revérifier)" if score > ref else "sous")
        print(f"OEIS A034258({n}) = {ref} -> notre construction {etat} la référence")
    else:
        print(f"N={n} hors table OEIS : terrain de recherche (comparer à la borne N/e ≈ {n/math.e:.1f})")
