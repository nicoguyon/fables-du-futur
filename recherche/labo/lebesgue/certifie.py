#!/usr/bin/env python3
"""Certification v1 — preuve par séparation-évaluation d'une minoration
pour aire(conv(disque ∪ σ·Reuleaux₃)), σ parcourant les isométries.

Théorème visé (démo de la machinerie sur le cas 2D) :
    pour toute isométrie σ du plan,
    aire(conv(D ∪ σR)) >= L = 0.825
où D est le disque de diamètre 1 centré à l'origine et R le triangle de
Reuleaux de largeur 1.

Réductions exactes (démontrées à la main, pas numériques) :
  1. Rotation globale : aire(θ, t) = aire(0, rot(-θ)·t). Il suffit donc
     de certifier θ = 0, t ∈ R².
  2. Réflexions : R est à symétrie axiale — les copies réfléchies sont
     des copies rotées, couvertes par (1).
  3. |t| >= 0.9 : conv(D ∪ σR) contient conv(D ∪ {t}) (le centre de R
     appartient à R) dont l'aire vaut
        A(d) = r²·(π − arccos(r/d)) + r·sqrt(d² − r²),  r = 1/2, d = |t|,
     fonction croissante de d, avec A(0.9) ≈ 0.874 >= L.  [lemme_loin]
  4. |t| <= 0.9 : séparation-évaluation sur des boîtes de translations.
     Pour une boîte B, un point p est CERTAIN (∈ R + t pour tout t ∈ B)
     ssi max_{c ∈ coins(B)} |p − c − v_i| <= 1 pour les 3 sommets v_i
     (R est l'intersection des 3 disques unité centrés aux v_i ; le max
     sur un rectangle d'une fonction convexe de t est atteint en un
     coin). L'enveloppe des points certains (des deux formes) est
     incluse dans conv(D ∪ (R+t)) pour TOUT t de B : son aire, moins une
     marge flottante, minore l'aire sur toute la boîte.

Arithmétique : flottants IEEE avec marges de sécurité explicites
(MARGE_FLOTTANTE soustraite de chaque aire, rayons contractés). Une
version en rationnels exacts est prévue pour la publication.
"""
import math
import time

import numpy as np
from scipy.spatial import ConvexHull

L_CIBLE = 0.825
MARGE_FLOTTANTE = 1e-9
RAYON_DOMAINE = 0.9
TAILLE_MIN = 1e-5

# Reuleaux3 : sommets du triangle équilatéral de côté 1 (circonrayon 1/√3)
V = [(0.0, 1 / math.sqrt(3)),
     (-0.5, -0.5 / math.sqrt(3)),
     (0.5, -0.5 / math.sqrt(3))]


def certain_reuleaux(p, boite):
    """p ∈ R + t pour tout t de la boîte (x1,x2,y1,y2) ? Test exact."""
    x1, x2, y1, y2 = boite
    for vx, vy in V:
        m = 0.0
        for cx in (x1, x2):
            for cy in (y1, y2):
                dx, dy = p[0] - cx - vx, p[1] - cy - vy
                d2 = dx * dx + dy * dy
                if d2 > m:
                    m = d2
        if m > 1.0:  # rayon 1 exact ; toute marge est déjà dans les candidats
            return False
    return True


def bord_reuleaux(n=180):
    """Points du bord de R et centre d'arc de chacun (forme à l'origine)."""
    pts = []
    centres = []
    for i in range(3):
        c = np.array(V[i])
        a = np.array(V[(i + 1) % 3]) - c
        b = np.array(V[(i + 2) % 3]) - c
        a1, a2 = math.atan2(a[1], a[0]), math.atan2(b[1], b[0])
        while a2 < a1:
            a2 += 2 * math.pi
        if a2 - a1 > math.pi:
            a1, a2 = a2, a1 + 2 * math.pi
        for s in np.linspace(a1, a2, n):
            pts.append((c[0] + math.cos(s), c[1] + math.sin(s)))
            centres.append(c)
    return np.array(pts), np.array(centres)


BORD_R, CENTRES_ARCS = bord_reuleaux()
DIRS_DISQUE = np.stack([np.cos(np.linspace(0, 2 * math.pi, 256, endpoint=False)),
                        np.sin(np.linspace(0, 2 * math.pi, 256, endpoint=False))], axis=1)
PTS_DISQUE = 0.5 * (1 - 1e-12) * DIRS_DISQUE  # |p| < 1/2 : certains, exact


def borne_temoin(boite):
    """Minorant de l'aire sur la boîte via l'enveloppe des points certains."""
    x1, x2, y1, y2 = boite
    t0 = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
    rho = 0.5 * math.hypot(x2 - x1, y2 - y1)
    # candidats : chaque point du bord tiré vers le centre de SON arc
    # (le long de la normale : la contrainte de son propre disque devient
    # sûre par inégalité triangulaire ; les deux autres sont testées)
    retrait = rho + 1e-9
    cand = BORD_R + t0
    vers_arc = cand - (CENTRES_ARCS + t0)
    normes = np.linalg.norm(vers_arc, axis=1, keepdims=True)
    cand = cand - vers_arc / normes * retrait
    certains = [p for p in cand if certain_reuleaux(p, boite)]
    pts = np.vstack([PTS_DISQUE] + ([np.array(certains)] if certains else []))
    if len(pts) < 3:
        return 0.0
    return ConvexHull(pts).volume - MARGE_FLOTTANTE


def borne_loin(boite):
    """Minorant via conv(D ∪ {t}) avec d = distance min de la boîte à 0."""
    x1, x2, y1, y2 = boite
    dx = max(x1, 0.0, -x2)
    dy = max(y1, 0.0, -y2)
    d = math.hypot(dx, dy)
    r = 0.5
    if d <= r:
        return math.pi * r * r - MARGE_FLOTTANTE
    d = d * (1 - 1e-12)
    if d <= r:
        return math.pi * r * r - MARGE_FLOTTANTE
    return r * r * (math.pi - math.acos(r / d)) + r * math.sqrt(d * d - r * r) - MARGE_FLOTTANTE


def certifie(L=L_CIBLE):
    """Certifie aire >= L sur |t|∞ <= RAYON_DOMAINE. Rend les statistiques."""
    pile = [(-RAYON_DOMAINE, RAYON_DOMAINE, -RAYON_DOMAINE, RAYON_DOMAINE)]
    n_ok = 0
    n_split = 0
    pire = math.inf
    t_debut = time.time()
    while pile:
        boite = pile.pop()
        lb = borne_loin(boite)
        if lb < L:
            lb = max(lb, borne_temoin(boite))
        if lb >= L:
            n_ok += 1
            pire = min(pire, lb)
            continue
        x1, x2, y1, y2 = boite
        if max(x2 - x1, y2 - y1) < TAILLE_MIN:
            return {"succes": False, "boite_bloquante": boite, "borne": lb,
                    "boites_certifiees": n_ok, "decoupes": n_split}
        n_split += 1
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        pile.extend([(x1, xm, y1, ym), (xm, x2, y1, ym),
                     (x1, xm, ym, y2), (xm, x2, ym, y2)])
    return {"succes": True, "L": L, "boites_certifiees": n_ok,
            "decoupes": n_split, "pire_borne_certifiee": pire,
            "secondes": round(time.time() - t_debut, 1)}


if __name__ == "__main__":
    # lemme_loin : A est croissante et A(RAYON_DOMAINE) >= L ?
    a_bord = borne_loin((RAYON_DOMAINE, RAYON_DOMAINE + 1, 0, 1))
    print(f"[lemme_loin] aire >= {a_bord:.6f} pour |t| >= {RAYON_DOMAINE} "
          f"(>= {L_CIBLE} : {'OK' if a_bord >= L_CIBLE else 'ÉCHEC'})")
    res = certifie()
    print(res)
    if res.get("succes"):
        print(f"\nTHÉORÈME (modulo arithmétique flottante à marges) :\n"
              f"  pour toute isométrie σ, aire(conv(D ∪ σR)) >= {L_CIBLE}\n"
              f"  [{res['boites_certifiees']} boîtes certifiées, "
              f"{res['secondes']} s ; rappel : min numérique = 0.82571]")
