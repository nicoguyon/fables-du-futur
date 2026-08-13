#!/usr/bin/env python3
"""Chasse au bassin de Gibbs (0.83699098) par basin-hopping depuis notre
meilleur point (0.8374805). Méthode de Gibbs 2014 : recuit/sauts."""
import math, os
import numpy as np
from scipy.optimize import basinhopping
import bornes_inf as B

formes = [B.FABRIQUES[n](fin=False) for n in B.JEUX["gibbs5"]]
formes_fin = [B.FABRIQUES[n](fin=True) for n in B.JEUX["gibbs5"]]

def f(p, fs=formes):
    return B.aire_enveloppe(fs, p)

x0 = np.array([0.20278, 0.0024, 0.00162, 7.33771, -0.02034, -0.01513,
               11.0641, -0.00957, 0.00842, 5.43883, 0.00078, 0.00029])
rng = np.random.default_rng(int(os.environ.get("GRAINE", "7")))

class Pas:
    def __init__(self): self.s = 0.08
    def __call__(self, x):
        x = np.array(x, copy=True)
        # perturbe rotations ET translations à des échelles adaptées
        for i in range(0, len(x), 3):
            x[i] += rng.normal(0, self.s * 4)      # rotation
            x[i+1] += rng.normal(0, self.s)        # tx
            x[i+2] += rng.normal(0, self.s)        # ty
        return x

res = basinhopping(f, x0, niter=int(os.environ.get("HOPS", "1500")),
                   take_step=Pas(),
                   minimizer_kwargs={"method": "Nelder-Mead",
                                     "options": {"maxiter": 2000, "xatol": 1e-8, "fatol": 1e-11}},
                   seed=int(os.environ.get("GRAINE", "7")))
# raffinage fin
from scipy.optimize import minimize
fin = minimize(lambda p: B.aire_enveloppe(formes_fin, p), res.x, method="Nelder-Mead",
               options={"maxiter": 8000, "xatol": 1e-10, "fatol": 1e-13})
print(f"basin-hopping : {res.fun:.7f} -> raffiné : {fin.fun:.7f}")
print("params :", np.round(fin.x, 5).tolist())
print("[rappel : notre plancher actuel 0.8374805 ; cible de Gibbs 0.83699098]")
