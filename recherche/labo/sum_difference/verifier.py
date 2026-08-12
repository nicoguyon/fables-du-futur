#!/usr/bin/env python3
"""Vérificateur EXACT pour les problèmes sommes/différences (AlphaEvolve #42/#43/#44).

Objet vérifié : un ensemble fini A d'entiers distincts.
On calcule |A+A| et |A-A| en arithmétique entière exacte (aucun flottant
dans le calcul des ensembles), puis les deux exposants :

  - direction #42 : C >= log|A+A| / log|A-A|   (|A+A| grand, |A-A| petit)
  - direction #43/#44 : theta >= log|A-A| / log|A+A|   (|A-A| grand, |A+A| petit)

Usage :
  python3 verifier.py fichier.json        # {"set": [entiers...]}
  python3 verifier.py --list 0 2 3 4 7 11 12 14

Repères (à re-sourcer précisément avant toute annonce) :
  - baseline_alphaevolve_p42.json : |A|=309, |A+A|=1367, |A-A|=1163,
    exposant #42 = 1.02290 (dépôt AlphaEvolve, notebook sums_differences_problems).
  - direction #44 : AlphaEvolve theta=1.1584 (mai 2025), battu ensuite par
    des humains (arXiv:2505.16105). Vérifier le record courant avant de viser.
"""
import json
import math
import sys


def analyse(a):
    a = sorted(set(int(x) for x in a))
    n = len(a)
    if n < 2:
        raise SystemExit("Ensemble trivial (moins de 2 éléments)")
    sums = {x + y for x in a for y in a}
    diffs = {x - y for x in a for y in a}
    s, d = len(sums), len(diffs)
    return {
        "taille": n,
        "|A+A|": s,
        "|A-A|": d,
        "exposant_42 (log s / log d)": math.log(s) / math.log(d),
        "exposant_43_44 (log d / log s)": math.log(d) / math.log(s),
    }


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--list":
        data = [int(x) for x in sys.argv[2:]]
    else:
        data = json.load(open(sys.argv[1]))["set"]
    for k, v in analyse(data).items():
        print(f"{k}: {v}")
