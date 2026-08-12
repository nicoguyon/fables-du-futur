#!/usr/bin/env python3
"""Certification v2 — séparation-évaluation générale avec intervalles de
rotation, pour minorer aire(conv(D ∪ σ₁F₁ ∪ … ∪ σ_kF_k)) sur TOUTES les
isométries σᵢ.

Réductions exactes (démontrées à la main) :
  * Le disque D (diamètre 1, centré à l'origine) absorbe les translations
    globales ; la rotation globale permet de figer l'orientation de la
    PREMIÈRE forme non-disque (θ₁ = 0).
  * Toutes nos formes-tests sont à symétrie axiale : les copies
    réfléchies sont des copies rotées — pas de dimension de réflexion.
  * Chaque forme est à symétrie de rotation d'ordre m : θ ∈ [0, 2π/m).
  * Lemme « loin » : chaque forme contient son centre c (= t) ; donc
    conv ⊇ conv(D ∪ {t}), d'aire A(d) = r²(π − arccos(r/d)) + r√(d²−r²),
    r = 1/2, croissante en d = |t|. A(0.9) ≈ 0.914. Il suffit donc de
    certifier |t|∞ ≤ 0.9 par forme, le reste étant couvert par A.

Test de point certain, EXACT au niveau flottant (marges explicites) :
  p ∈ R_θ F + t pour tout θ ∈ [θ₁,θ₂], t ∈ boîte ?
  * F polygone (∩ demi-plans nⱼ·x ≤ bⱼ, |nⱼ| = 1) :
      max_θ,t nⱼ·R_{−θ}(p − t) = max_{coins c} |p−c| · M(ψ_{p−c} − ψ_{nⱼ})
      où M(φ) = max cos(φ − θ) sur l'intervalle (1 si φ ∈ [θ₁,θ₂] mod 2π,
      sinon max aux extrémités). Le max sur t d'une fonction convexe d'un
      rectangle est atteint en un coin.
  * F Reuleaux (∩ disques unité centrés aux sommets vᵢ) :
      max_θ,t |p − t − R_θvᵢ|² = max_{coins c} (|q|² + |vᵢ|² − 2|q||vᵢ|·m(φ)),
      q = p − c, φ = ψ_q − ψ_{vᵢ}, m(φ) = min cos(φ − θ) sur l'intervalle.

Minorant par boîte : aire de l'enveloppe convexe des points certains de
toutes les formes (celle-ci est incluse dans conv(∪σᵢFᵢ) pour TOUT
placement de la boîte), moins une marge flottante.
"""
import json
import math
import os
import sys
import time

import numpy as np
from scipy.spatial import ConvexHull

MARGE_FLOTTANTE = 1e-9
EPS_TEST = 1e-12
RAYON_DOMAINE = 0.9

TAU = 2 * math.pi


# ------------------------------------------------------------------ formes

def _poly_reg(k):
    m = k // 2
    r = 1 / (2 * math.sin(m * math.pi / k)) if k >= 4 else 1 / math.sqrt(3)
    a = np.array([math.pi / 2 + i * TAU / k for i in range(k)])
    return r * np.stack([np.cos(a), np.sin(a)], axis=1)


class Polygone:
    """Polygone convexe régulier de diamètre 1, symétrie d'ordre k."""

    def __init__(self, k):
        self.sommets = _poly_reg(k)
        self.periode = TAU / k
        v = self.sommets
        n = len(v)
        normales, offsets = [], []
        for i in range(n):
            e = v[(i + 1) % n] - v[i]
            nn = np.array([e[1], -e[0]])
            nn = nn / np.linalg.norm(nn)
            if nn @ v[i] < 0:
                nn = -nn
            normales.append(nn)
            offsets.append(nn @ v[i])
        self.normales = np.array(normales)
        self.offsets = np.array(offsets)
        self.psi_n = np.arctan2(self.normales[:, 1], self.normales[:, 0])
        # candidats témoins : sommets + points d'arêtes
        cand = [v]
        for i in range(n):
            lam = np.linspace(0, 1, 12, endpoint=False)[1:]
            cand.append(np.outer(1 - lam, v[i]) + np.outer(lam, v[(i + 1) % n]))
        self.cand0 = np.vstack(cand)

    def certains(self, boite_t, th1, th2, rho_pull):
        """Points certains pour t ∈ boite_t, θ ∈ [th1, th2]."""
        cand = self.cand0 * max(0.0, 1 - rho_pull / 0.28)  # retrait homothétique
        # (0.28 < inradius de nos polygones ; le test exact fait le tri)
        t0 = np.array([(boite_t[0] + boite_t[1]) / 2, (boite_t[2] + boite_t[3]) / 2])
        th0 = (th1 + th2) / 2
        c, s = math.cos(th0), math.sin(th0)
        cand_place = cand @ np.array([[c, s], [-s, c]])
        cand_place = cand_place + t0
        ok = self._test(cand_place, boite_t, th1, th2)
        return cand_place[ok]

    def _test(self, pts, boite_t, th1, th2):
        x1, x2, y1, y2 = boite_t
        ok = np.ones(len(pts), dtype=bool)
        for cx in (x1, x2):
            for cy in (y1, y2):
                q = pts - np.array([cx, cy])
                nq = np.linalg.norm(q, axis=1)
                psi_q = np.arctan2(q[:, 1], q[:, 0])
                phi = psi_q[:, None] - self.psi_n[None, :]
                M = _max_cos(phi, th1, th2)
                val = nq[:, None] * M
                ok &= np.all(val <= self.offsets[None, :] - EPS_TEST, axis=1)
        return ok


class Reuleaux:
    """Polygone de Reuleaux à k côtés (k impair), largeur 1."""

    def __init__(self, k, n_arc=48):
        self.v = _poly_reg(k)
        self.periode = TAU / k
        self.nv = np.linalg.norm(self.v, axis=1)
        self.psi_v = np.arctan2(self.v[:, 1], self.v[:, 0])
        m = k // 2
        pts, centres = [], []
        for i in range(k):
            c = self.v[i]
            a = self.v[(i + m) % k] - c
            b = self.v[(i + m + 1) % k] - c
            a1, a2 = math.atan2(a[1], a[0]), math.atan2(b[1], b[0])
            while a2 < a1:
                a2 += TAU
            if a2 - a1 > math.pi:
                a1, a2 = a2, a1 + TAU
            for sarc in np.linspace(a1, a2, n_arc):
                pts.append(c + np.array([math.cos(sarc), math.sin(sarc)]))
                centres.append(c)
        self.cand0 = np.array(pts)
        self.centres0 = np.array(centres)

    def certains(self, boite_t, th1, th2, rho_pull):
        vers = self.cand0 - self.centres0
        cand = self.cand0 - vers * rho_pull  # retrait le long de la normale d'arc
        t0 = np.array([(boite_t[0] + boite_t[1]) / 2, (boite_t[2] + boite_t[3]) / 2])
        th0 = (th1 + th2) / 2
        c, s = math.cos(th0), math.sin(th0)
        rot = np.array([[c, s], [-s, c]])
        cand_place = cand @ rot + t0
        ok = self._test(cand_place, boite_t, th1, th2)
        return cand_place[ok]

    def _test(self, pts, boite_t, th1, th2):
        x1, x2, y1, y2 = boite_t
        ok = np.ones(len(pts), dtype=bool)
        for cx in (x1, x2):
            for cy in (y1, y2):
                q = pts - np.array([cx, cy])
                nq = np.linalg.norm(q, axis=1)
                psi_q = np.arctan2(q[:, 1], q[:, 0])
                phi = psi_q[:, None] - self.psi_v[None, :]
                m = _min_cos(phi, th1, th2)
                d2 = nq[:, None] ** 2 + self.nv[None, :] ** 2 \
                    - 2 * nq[:, None] * self.nv[None, :] * m
                ok &= np.all(d2 <= 1.0 - EPS_TEST, axis=1)
        return ok


def _max_cos(phi, th1, th2):
    """max cos(phi − θ), θ ∈ [th1, th2] (vectorisé)."""
    d = np.mod(phi - th1, TAU)
    largeur = th2 - th1
    dedans = d <= largeur
    m = np.maximum(np.cos(phi - th1), np.cos(phi - th2))
    return np.where(dedans, 1.0, m)


def _min_cos(phi, th1, th2):
    """min cos(phi − θ), θ ∈ [th1, th2] : cos atteint −1 si phi − π ∈ intervalle."""
    d = np.mod(phi - math.pi - th1, TAU)
    largeur = th2 - th1
    dedans = d <= largeur
    m = np.minimum(np.cos(phi - th1), np.cos(phi - th2))
    return np.where(dedans, -1.0, m)


# ---------------------------------------------------------------- moteur

A_DISQUE = 256
_a = np.linspace(0, TAU, A_DISQUE, endpoint=False)
PTS_DISQUE = 0.5 * (1 - 1e-12) * np.stack([np.cos(_a), np.sin(_a)], axis=1)


def borne_loin_A(d):
    r = 0.5
    if d <= r:
        return 0.0
    d = d * (1 - 1e-12)
    return r * r * (math.pi - math.acos(r / d)) + r * math.sqrt(d * d - r * r)


class Probleme:
    """formes : liste de (objet, tourne) — tourne=False fige θ=0 (quotient)."""

    def __init__(self, formes, L):
        self.formes = formes
        self.L = L
        # paramètres : pour chaque forme, [θ?] + tx + ty
        self.dims = []
        for i, (f, tourne) in enumerate(formes):
            if tourne:
                self.dims.append(("th", i, 0.0, f.periode))
            self.dims.append(("tx", i, -RAYON_DOMAINE, RAYON_DOMAINE))
            self.dims.append(("ty", i, -RAYON_DOMAINE, RAYON_DOMAINE))
        self.n_ok = 0
        self.n_split = 0
        self.echecs = []

    def _decoupe(self, boite):
        # largeur effective : rotations pondérées par le circonrayon (~0.58)
        larg = []
        for (typ, i, _, _), (lo, hi) in zip(self.dims, boite):
            w = (hi - lo) * (0.58 if typ == "th" else 1.0)
            larg.append(w)
        j = int(np.argmax(larg))
        lo, hi = boite[j]
        mid = (lo + hi) / 2
        b1 = list(boite)
        b2 = list(boite)
        b1[j] = (lo, mid)
        b2[j] = (mid, hi)
        return tuple(b1), tuple(b2), max(larg)

    def _borne(self, boite):
        # 1. borne « loin » par forme
        meilleurs = 0.0
        par_forme = {}
        for (typ, i, _, _), (lo, hi) in zip(self.dims, boite):
            par_forme.setdefault(i, {})[typ] = (lo, hi)
        for i, (f, tourne) in enumerate(self.formes):
            tx = par_forme[i]["tx"]
            ty = par_forme[i]["ty"]
            dx = max(tx[0], 0.0, -tx[1])
            dy = max(ty[0], 0.0, -ty[1])
            meilleurs = max(meilleurs, borne_loin_A(math.hypot(dx, dy)))
        if meilleurs >= self.L:
            return meilleurs
        # 2. borne témoin
        nuages = [PTS_DISQUE]
        for i, (f, tourne) in enumerate(self.formes):
            tx = par_forme[i]["tx"]
            ty = par_forme[i]["ty"]
            th1, th2 = par_forme[i].get("th", (0.0, 0.0))
            rho_t = 0.5 * math.hypot(tx[1] - tx[0], ty[1] - ty[0])
            rho_th = 0.58 * (th2 - th1) / 2
            rho_pull = 1.05 * (rho_t + rho_th) + 1e-9
            pts = f.certains((tx[0], tx[1], ty[0], ty[1]), th1, th2, rho_pull)
            if len(pts):
                nuages.append(pts)
        pts = np.vstack(nuages)
        if len(pts) < 3:
            return meilleurs
        return max(meilleurs, ConvexHull(pts).volume - MARGE_FLOTTANTE)

    def certifie(self, taille_min=2e-5, budget_s=None, rapport=200000, pile_init=None,
                 chemin_ckpt=None):
        boite0 = tuple((lo, hi) for (_, _, lo, hi) in self.dims)
        pile = list(pile_init) if pile_init is not None else [boite0]
        t0 = time.time()
        dernier_ckpt = t0
        pire = math.inf
        while pile:
            maintenant = time.time()
            if chemin_ckpt and maintenant - dernier_ckpt > 60:
                json.dump({"L": self.L, "pile": pile, "boites_faites": self.n_ok},
                          open(chemin_ckpt, "w"))
                dernier_ckpt = maintenant
            if budget_s and maintenant - t0 > budget_s:
                if chemin_ckpt:
                    json.dump({"L": self.L, "pile": pile, "boites_faites": self.n_ok},
                              open(chemin_ckpt, "w"))
                return {"succes": False, "raison": "budget temps", "restantes": len(pile),
                        "boites": self.n_ok, "ckpt": chemin_ckpt,
                        "secondes": round(maintenant - t0, 1)}
            boite = pile.pop()
            lb = self._borne(boite)
            if lb >= self.L:
                self.n_ok += 1
                pire = min(pire, lb)
                if self.n_ok % rapport == 0:
                    print(f"  … {self.n_ok} boîtes ok, pile {len(pile)}, "
                          f"{round(time.time() - t0)} s", flush=True)
                continue
            b1, b2, wmax = self._decoupe(boite)
            if wmax < taille_min:
                return {"succes": False, "raison": "boîte bloquante", "boite": boite,
                        "borne": lb, "boites": self.n_ok,
                        "secondes": round(time.time() - t0, 1)}
            self.n_split += 1
            pile.append(b1)
            pile.append(b2)
        if chemin_ckpt and os.path.exists(chemin_ckpt):
            os.remove(chemin_ckpt)
        return {"succes": True, "L": self.L, "boites": self.n_ok,
                "decoupes": self.n_split, "pire_borne": pire,
                "secondes": round(time.time() - t0, 1)}


PROBLEMES = {
    # validation : disque + Reuleaux3 avec rotation LIBRE (3 dims).
    # Doit redonner >= 0.825 comme certifie.py (qui fige θ par quotient).
    "valide3d": (lambda: Probleme([(Reuleaux(3, 128), True)], float(os.environ.get("L", "0.8245")))),
    # trio de Xie : triangle figé (quotient rotation globale), pentagone
    # libre -> 5 dims. Objectif : certification indépendante de >= L.
    "xie3": (lambda: Probleme([(Polygone(3), False), (Polygone(5), True)],
                              float(os.environ.get("L", "0.833")))),
    # le jeu à 4 formes (record visé) : 8 dims.
    "record4": (lambda: Probleme([(Polygone(3), False), (Polygone(5), True),
                                  (Reuleaux(5, 40), True)],
                                 float(os.environ.get("L", "0.834")))),
}

def _travailleur(args):
    nom, boites, budget, graine = args
    pb = PROBLEMES[nom]()
    ckpt = f"ckpt_{nom}_{graine}.json"
    return pb.certifie(budget_s=budget, pile_init=boites, rapport=10**9,
                       chemin_ckpt=ckpt)


def certifie_parallele(nom, procs=4, budget_s=None):
    """Découpe la racine en lots et distribue sur `procs` processus.
    Succès ssi TOUS les lots certifient (l'union des lots couvre la racine)."""
    from multiprocessing import Pool
    pb = PROBLEMES[nom]()
    lots = None
    if os.environ.get("RESUME") == "1":
        piles = []
        for i in range(procs):
            ck = f"ckpt_{nom}_{i}.json"
            if os.path.exists(ck):
                piles.append([tuple(tuple(iv) for iv in b)
                              for b in json.load(open(ck))["pile"]])
            else:
                piles.append([])
        if any(piles):
            lots = [(nom, piles[i], budget_s, i) for i in range(procs) if piles[i]]
            print(f"[reprise] {sum(len(p) for p in piles)} boîtes restantes "
                  f"depuis les checkpoints", flush=True)
    if lots is None:
        boites = [tuple((lo, hi) for (_, _, lo, hi) in pb.dims)]
        while len(boites) < procs * 16:
            b = boites.pop(0)
            b1, b2, _ = pb._decoupe(b)
            boites.extend([b1, b2])
        lots = [(nom, boites[i::procs], budget_s, i) for i in range(procs)]
    t0 = time.time()
    with Pool(procs) as pool:
        resultats = pool.map(_travailleur, lots)
    total = sum(r.get("boites", 0) for r in resultats)
    echecs = [r for r in resultats if not r.get("succes")]
    if not echecs:
        return {"succes": True, "L": pb.L, "boites": total, "procs": procs,
                "secondes": round(time.time() - t0, 1)}
    return {"succes": False, "boites": total, "echecs": echecs,
            "secondes": round(time.time() - t0, 1)}


if __name__ == "__main__":
    nom = sys.argv[1] if len(sys.argv) > 1 else "valide3d"
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else None
    procs = int(os.environ.get("PROCS", "1"))
    pb = PROBLEMES[nom]()
    print(f"[{nom}] L = {pb.L}, dims = {len(pb.dims)}, procs = {procs}", flush=True)
    if procs > 1:
        res = certifie_parallele(nom, procs=procs, budget_s=budget)
    else:
        res = pb.certifie(budget_s=budget)
    print(res)
