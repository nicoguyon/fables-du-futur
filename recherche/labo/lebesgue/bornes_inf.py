#!/usr/bin/env python3
"""Explorateur de bornes inférieures pour le problème de la couverture
universelle de Lebesgue (1914). v2 — parallèle, deux étages.

Principe (Brass–Sharifi 2005, Xie 2026 arXiv:2606.04458) : toute
couverture universelle convexe contient une copie congruente de chaque
forme de diamètre 1 ; donc son aire est au moins le minimum, sur tous
les placements, de l'aire de l'enveloppe convexe de l'union d'un jeu de
formes-tests. Record certifié : 0.833 (Xie : disque + triangle
équilatéral + pentagone régulier).

Outil d'EXPLORATION : multi-départs parallèles (étage 1, grossier,
disque 512 points) puis raffinage des meilleurs candidats (étage 2,
disque 2048 points, tolérances serrées). Discrétisations inscrites
(sous-estimation => prudent). La certification viendra ensuite.

Usage : python3 bornes_inf.py [nom_de_jeu ...]   (défaut : balayage)
"""
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull


# ---------------------------------------------------------------- formes

def disque(n=512):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return 0.5 * np.stack([np.cos(a), np.sin(a)], axis=1)


def polygone_regulier(k, diametre_par_diagonale=True):
    """k-gone régulier de diamètre 1 (diamètre = plus longue diagonale)."""
    # pour k impair la plus longue diagonale sous-tend floor(k/2) pas
    m = k // 2
    r = 1 / (2 * math.sin(m * math.pi / k)) if diametre_par_diagonale else 0.5
    a = np.array([math.pi / 2 + i * 2 * math.pi / k for i in range(k)])
    return r * np.stack([np.cos(a), np.sin(a)], axis=1)


def triangle_equilateral():
    return polygone_regulier(3)


def pentagone():
    return polygone_regulier(5)


def carre():
    """Carré de diagonale 1."""
    a = np.array([math.pi / 4 + i * math.pi / 2 for i in range(4)])
    return 0.5 * np.stack([np.cos(a), np.sin(a)], axis=1)


def reuleaux(k, n_arc=180):
    """Polygone de Reuleaux à k côtés (k impair), largeur 1."""
    v = polygone_regulier(k)
    pts = []
    m = k // 2
    for i in range(k):
        c = v[i]
        j1, j2 = v[(i + m) % k], v[(i + m + 1) % k]
        a1 = math.atan2(*(j1 - c)[::-1])
        a2 = math.atan2(*(j2 - c)[::-1])
        while a2 < a1:
            a2 += 2 * math.pi
        if a2 - a1 > math.pi:
            a1, a2 = a2 - 2 * math.pi, a1
            a1, a2 = a2, a1 + 2 * math.pi - (a2 - a1)  # sécurité
        a = np.linspace(a1, a2, n_arc)
        pts.append(c + np.stack([np.cos(a), np.sin(a)], axis=1))
    p = np.vstack(pts)
    # garde-fou : diamètre ~ 1
    assert abs(_diametre(p) - 1) < 1e-6, f"reuleaux({k}) diamètre {_diametre(p)}"
    return p


def _diametre(p):
    h = p[ConvexHull(p).vertices]
    d = 0.0
    for i in range(len(h)):
        d = max(d, float(np.max(np.linalg.norm(h - h[i], axis=1))))
    return d


# ------------------------------------------------------------ optimisation

def place(points, theta, tx, ty):
    c, s = math.cos(theta), math.sin(theta)
    return points @ np.array([[c, s], [-s, c]]) + np.array([tx, ty])


def aire_enveloppe(formes, params):
    nuages = [formes[0]]
    for i, f in enumerate(formes[1:]):
        th, tx, ty = params[3 * i:3 * i + 3]
        nuages.append(place(f, th, tx, ty))
    return ConvexHull(np.vstack(nuages)).volume


def _un_depart(arg):
    formes, x0, maxiter, xatol, fatol = arg
    res = minimize(lambda p: aire_enveloppe(formes, p), x0,
                   method="Nelder-Mead",
                   options={"maxiter": maxiter, "xatol": xatol, "fatol": fatol})
    return float(res.fun), res.x


def minimise(noms_formes, essais=None, graine=0, procs=4):
    if essais is None:
        essais = int(os.environ.get("ESSAIS", "120"))
    """Deux étages. noms_formes : liste de fabriques (nom, kwargs grossier/fin)."""
    rng = np.random.default_rng(graine)
    formes_g = [FABRIQUES[n](fin=False) for n in noms_formes]
    formes_f = [FABRIQUES[n](fin=True) for n in noms_formes]
    k = len(formes_g) - 1
    if k == 0:
        return ConvexHull(formes_f[0]).volume, None
    departs = []
    for _ in range(essais):
        x0 = np.concatenate([[rng.uniform(0, 2 * math.pi),
                              rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3)]
                             for _ in range(k)])
        departs.append((formes_g, x0, 1200, 1e-6, 1e-9))
    with Pool(procs) as pool:
        gros = pool.map(_un_depart, departs)
    gros.sort(key=lambda r: r[0])
    # étage 2 : raffine les 6 meilleurs + petites perturbations
    candidats = []
    for val, x in gros[:6]:
        candidats.append((formes_f, x, 6000, 1e-10, 1e-13))
        for _ in range(2):
            candidats.append((formes_f, x + rng.normal(0, 0.02, size=x.shape),
                              6000, 1e-10, 1e-13))
    with Pool(procs) as pool:
        fins = pool.map(_un_depart, candidats)
    fins.sort(key=lambda r: r[0])
    return fins[0]


FABRIQUES = {
    "disque": lambda fin: disque(2048 if fin else 512),
    "triangle": lambda fin: triangle_equilateral(),
    "pentagone": lambda fin: pentagone(),
    "carre": lambda fin: carre(),
    "heptagone": lambda fin: polygone_regulier(7),
    "nonagone": lambda fin: polygone_regulier(9),
    "hendecagone": lambda fin: polygone_regulier(11),
    "reuleaux3": lambda fin: reuleaux(3, 360 if fin else 120),
    "reuleaux5": lambda fin: reuleaux(5, 220 if fin else 80),
    "reuleaux7": lambda fin: reuleaux(7, 160 if fin else 60),
    "reuleaux9": lambda fin: reuleaux(9, 140 if fin else 50),
}

JEUX = {
    "xie3": ["disque", "triangle", "pentagone"],
    "xie3+reuleaux3": ["disque", "triangle", "pentagone", "reuleaux3"],
    "xie3+carre": ["disque", "triangle", "pentagone", "carre"],
    "xie3+reuleaux5": ["disque", "triangle", "pentagone", "reuleaux5"],
    "xie3+heptagone": ["disque", "triangle", "pentagone", "heptagone"],
    "brass-sharifi": ["disque", "reuleaux3"],
    "xie3+reuleaux3+carre": ["disque", "triangle", "pentagone", "reuleaux3", "carre"],
    "xie3+nonagone": ["disque", "triangle", "pentagone", "nonagone"],
    "xie3+hendecagone": ["disque", "triangle", "pentagone", "hendecagone"],
    "xie3+heptagone+reuleaux5": ["disque", "triangle", "pentagone", "heptagone", "reuleaux5"],
    "sans-disque": ["heptagone", "triangle", "pentagone"],
    "gibbs5": ["disque", "reuleaux3", "reuleaux5", "reuleaux7", "reuleaux9"],
    "gibbs5+pentagone": ["disque", "reuleaux3", "reuleaux5", "reuleaux7", "reuleaux9", "pentagone"],
    "disque+triangle": ["disque", "triangle"],
}

if __name__ == "__main__":
    noms = sys.argv[1:] or ["xie3", "xie3+reuleaux3", "xie3+carre",
                            "xie3+reuleaux5", "xie3+heptagone"]
    for nom in noms:
        aire, params = minimise(JEUX[nom])
        print(f"{nom:28s} -> min numérique : {aire:.7f}", flush=True)
        if params is not None:
            print(f"{'':28s}    params : {np.round(params, 5).tolist()}", flush=True)
