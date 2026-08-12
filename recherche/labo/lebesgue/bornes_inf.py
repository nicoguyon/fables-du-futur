#!/usr/bin/env python3
"""Explorateur de bornes inférieures pour le problème de la couverture
universelle de Lebesgue (1914).

Principe (Brass–Sharifi 2005, Xie 2026) : toute couverture universelle
convexe U contient une copie congruente de chaque forme de diamètre 1 ;
donc aire(U) >= min sur tous les placements de l'aire de l'enveloppe
convexe de l'union des formes-tests. Ce minimum, calculé sur un ensemble
fini de formes, est une borne inférieure du problème.

État de l'art : 0.832 (Brass–Sharifi, disque + triangle de Reuleaux),
0.833 certifié (Xie, juin 2026 : disque + triangle équilatéral +
pentagone régulier, arXiv:2606.04458).

Cet outil est un EXPLORATEUR numérique : il estime le minimum pour un
jeu de formes donné (multi-départs + Nelder-Mead). La certification par
arithmétique d'intervalles viendra ensuite. Le disque est discrétisé par
un polygone inscrit (sous-estimation => prudent pour une borne inf.).
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull


def disque(n=2000):
    """Disque de diamètre 1 (polygone inscrit à n sommets)."""
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return 0.5 * np.stack([np.cos(a), np.sin(a)], axis=1)


def triangle_equilateral():
    """Triangle équilatéral de côté 1 (diamètre 1) centré au centroïde."""
    a = np.array([math.pi / 2 + k * 2 * math.pi / 3 for k in range(3)])
    r = 1 / math.sqrt(3)
    return r * np.stack([np.cos(a), np.sin(a)], axis=1)


def pentagone():
    """Pentagone régulier de diamètre (diagonale) 1."""
    r = 1 / (2 * math.sin(2 * math.pi / 5))
    a = np.array([math.pi / 2 + k * 2 * math.pi / 5 for k in range(5)])
    return r * np.stack([np.cos(a), np.sin(a)], axis=1)


def reuleaux_triangle(n_arc=240):
    """Triangle de Reuleaux de largeur 1 (arcs de rayon 1)."""
    v = triangle_equilateral()
    pts = []
    for i in range(3):
        c = v[i]
        j, k = v[(i + 1) % 3], v[(i + 2) % 3]
        a1 = math.atan2(*(j - c)[::-1])
        a2 = math.atan2(*(k - c)[::-1])
        while a2 < a1:
            a2 += 2 * math.pi
        if a2 - a1 > math.pi:  # prendre le petit arc
            a1, a2 = a2, a1 + 2 * math.pi
        a = np.linspace(a1, a2, n_arc)
        pts.append(c + np.stack([np.cos(a), np.sin(a)], axis=1))
    return np.vstack(pts)


def place(points, theta, tx, ty):
    c, s = math.cos(theta), math.sin(theta)
    rot = np.array([[c, -s], [s, c]])
    return points @ rot.T + np.array([tx, ty])


def aire_enveloppe(formes, params):
    """Aire de l'enveloppe convexe de l'union des formes placées.
    formes[0] reste fixe ; chaque forme suivante a (theta, tx, ty)."""
    nuages = [formes[0]]
    for i, f in enumerate(formes[1:]):
        th, tx, ty = params[3 * i:3 * i + 3]
        nuages.append(place(f, th, tx, ty))
    pts = np.vstack(nuages)
    return ConvexHull(pts).volume  # en 2D, .volume = aire


def minimise(formes, essais=60, graine=0):
    """Multi-départs aléatoires + Nelder-Mead. Rend (aire_min, params)."""
    rng = np.random.default_rng(graine)
    k = len(formes) - 1
    if k == 0:
        return ConvexHull(formes[0]).volume, None
    meilleur = (math.inf, None)
    for e in range(essais):
        x0 = np.concatenate([
            [rng.uniform(0, 2 * math.pi), rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25)]
            for _ in range(k)
        ]) if k else np.array([])
        res = minimize(lambda p: aire_enveloppe(formes, p), x0,
                       method="Nelder-Mead",
                       options={"maxiter": 4000, "xatol": 1e-10, "fatol": 1e-12})
        if res.fun < meilleur[0]:
            meilleur = (res.fun, res.x)
    return meilleur


JEUX = {
    "disque seul": [disque()],
    "disque + reuleaux (Brass-Sharifi)": [disque(), reuleaux_triangle()],
    "disque + triangle + pentagone (Xie 2026)": [disque(), triangle_equilateral(), pentagone()],
    "les 4 (Xie + reuleaux)": [disque(), triangle_equilateral(), pentagone(), reuleaux_triangle()],
}

if __name__ == "__main__":
    noms = sys.argv[1:] or list(JEUX)
    for nom in noms:
        formes = JEUX[nom]
        aire, params = minimise(formes)
        print(f"{nom:45s} -> min numérique de l'aire de l'enveloppe : {aire:.6f}")
        if params is not None and len(params):
            print(f"{'':45s}    placements optimaux : {np.round(params, 4).tolist()}")
