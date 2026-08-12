# DOSSIER POUR CRITIQUE ADVERSARIALE — Labo Lebesgue (Nicolas Guyon + Claude)
# 12 août 2026. Tout est copiable-collable ; le code complet est en annexe.

## Ta mission (destinataire : GPT-5)
Critique impitoyablement tout ce qui suit : erreurs mathématiques, failles de
rigueur dans les tests de « points certains », biais du protocole numérique,
faiblesses de la stratégie, affirmations trop fortes, pistes manquées.
Classe tes critiques par gravité (bloquant / sérieux / mineur) et propose
des corrections concrètes. Ne sois pas poli, sois exact.

## 1. Contexte et objectif
Problème de Lebesgue (1914) : α = inf des aires des convexes U de R² tels que
toute partie de diamètre <= 1 admette une copie congruente (réflexions
comprises) incluse dans U. Encadrement actuel : 0.833 (Xie, arXiv:2606.04458,
certifié, juin 2026) <= α <= 0.8440935944 (Gibbs, arXiv:1810.10089, 2018).
Notre objectif : améliorer la borne INFÉRIEURE via la méthode des formes-tests.

## 2. Le lemme (fondation, trivial mais central)
Si F1..Fk sont de diamètre <= 1, alors α >= min sur les isométries σi de
aire(conv(σ1F1 ∪ … ∪ σkFk)). Preuve : U contient une copie de chaque Fi ;
convexité ; aire. La méthode est asymptotiquement complète (toutes les formes
=> le min vaut α). Xie l'applique avec {disque, triangle équilatéral,
pentagone régulier} (tous de diamètre 1) et certifie 0.833 par arithmétique
d'intervalles sur l'espace des placements (5 dims après quotient).

## 3. Nos résultats numériques (explorateur, NON certifiés)
Optimisation : Nelder-Mead multi-départs (120 à 2000), deux étages
(grossier/raffiné), formes discrétisées par polygones INSCRITS (=>
sous-estimation, sens prudent). Bruit calibré ~1e-5 par test de monotonie
(un jeu de 5 formes est sorti 1e-5 SOUS son sous-ensemble de 4 — impossible
mathématiquement, donc c'est l'erreur d'optimisation).

| jeu de formes-tests | min numérique |
|---|---|
| disque seul | 0.785397 (= π/4, contrôle exact) |
| disque + triangle de Reuleaux | 0.825711 |
| disque + triangle + pentagone (jeu de Xie) | 0.8335968 (cohérent avec son 0.833) |
| jeu de Xie + carré (diagonale 1) | 0.8336021 (gain nul) |
| jeu de Xie + Reuleaux-triangle | 0.8338548 |
| jeu de Xie + heptagone régulier | 0.8343338 (après attaque à 500 départs ; un run à 120 départs donnait 0.8351916, tombé — leçon d'honnêteté) |
| jeu de Xie + hendécagone régulier | 0.8345968 (300 départs seulement) |
| jeu de Xie + PENTAGONE DE REULEAUX | 0.8345744, stable à 2000 départs (nos runs : 0.8345678 / 0.8345744, écart 7e-6 = bruit) |

Affirmation centrale à critiquer : le jeu {disque, triangle, pentagone,
pentagone de Reuleaux} a un minimum ~0.83457, soit +0.0010 au-dessus du jeu
de Xie ; si certifié >= 0.834, cela améliorerait le record.

## 4. Le moteur de certification (l'objet principal à critiquer)
Schéma de preuve par séparation-évaluation sur l'espace des placements.

Réductions (à vérifier) :
(a) disque fixé à l'origine (absorbe les translations globales) ;
(b) rotation globale : on fige l'orientation de la première forme non-disque
    (θ_triangle = 0) — argument : toute config est équivalente par rotation
    globale, le disque étant invariant ;
(c) réflexions : toutes nos formes-tests sont à symétrie axiale, donc les
    copies réfléchies sont des copies rotées — pas de dimension en plus ;
(d) symétrie de rotation d'ordre m de chaque forme : θ ∈ [0, 2π/m) ;
(e) lemme « loin » : chaque forme contient son centre t, donc l'enveloppe
    contient conv(D ∪ {t}) d'aire A(d) = r²(π − arccos(r/d)) + r·sqrt(d²−r²),
    r = 1/2, d = |t|, croissante ; A(0.9) ≈ 0.914 > toutes nos cibles. On ne
    certifie donc que |t|∞ <= 0.9 par forme.

Minorant par boîte de paramètres (à vérifier ligne à ligne) :
Un point p est CERTAIN pour la forme F, la boîte de translations T et
l'intervalle de rotations [θ1,θ2] ssi p ∈ R_θ F + t pour TOUT (θ,t).
- F polygone (∩ demi-plans n_j·x <= b_j, |n_j| = 1) :
  condition : max sur les 4 coins c de T de |p−c|·M(ψ_{p−c} − ψ_{n_j}) <= b_j
  pour tout j, où M(φ) = max_{θ∈[θ1,θ2]} cos(φ−θ) (= 1 si φ dans
  l'intervalle mod 2π, sinon max aux extrémités). Justification : n_j·R_{−θ}q
  = (R_θ n_j)·q = |q| cos(ψ_q − ψ_{n_j} − θ), et le max sur t d'une fonction
  convexe de t sur un rectangle est atteint en un coin.
- F Reuleaux d'ordre k (∩ des k disques unité centrés aux sommets v_i) :
  condition : max sur coins c de |q|² + |v_i|² − 2|q||v_i|·m(ψ_q − ψ_{v_i})
  <= 1 pour tout i, q = p − c, m(φ) = min cos(φ−θ) sur l'intervalle
  (= −1 si φ−π est dans l'intervalle mod 2π).
L'enveloppe convexe des points certains de toutes les formes est incluse dans
conv(∪ σ_iF_i) pour TOUT placement de la boîte ; son aire (shoelace via
scipy ConvexHull, moins marge 1e-9) minore donc l'aire sur la boîte.
Candidats témoins : bords discrétisés, rétractés de ρ = 1.05·(rayon boîte
translation + 0.58·demi-largeur rotation) — le long de la normale d'arc pour
les Reuleaux, homothétiquement pour les polygones — puis TESTÉS exactement
(le retrait n'a pas besoin d'être théoriquement suffisant : le test tranche).

Points faibles connus (déjà identifiés par nous, à compléter) :
- arithmétique flottante IEEE avec marges (1e-9 aire, 1e-12 tests), PAS
  d'arrondi dirigé ni de rationnels — durcissement prévu ;
- ConvexHull (qhull) en flottant : l'aire calculée peut-elle surestimer de
  plus que la marge ? à analyser ;
- le test « max en un coin » exige la convexité en t à θ FIXÉ puis le max sur
  θ — nous prenons max sur coins de (max sur θ) : l'échange max-max est-il
  licite ? (nous pensons oui : sup sup = sup sup) ;
- la fonction q ↦ |q|·M(ψ_q − ψ_n) est-elle bien convexe en q pour que le max
  sur le rectangle soit en un coin ? M dépend de q via ψ_q — NOUS AVONS UN
  DOUTE ICI : critique ce point en priorité. (Notre défense : pour chaque θ
  fixé la fonction est linéaire en q donc le sup sur le rectangle est au
  coin ; et sup_θ sup_t = sup_t sup_θ ; le test implémente sup_coins sup_θ,
  qui majore-t-il sup_t sup_θ ? sup sur les coins <= sup sur T ; il faut
  l'ÉGALITÉ sup_T = sup_coins : vraie car t ↦ sup_θ(linéaire en t) est un
  sup de fonctions linéaires donc convexe => max au bord, et sur un rectangle
  au coin. Vérifie ce raisonnement.)

Résultats du moteur :
- v1 (2 dims, sans rotation, disque + Reuleaux-triangle) : PROUVÉ
  aire >= 0.825 pour toute isométrie (1822 boîtes, 9.7 s ; min numérique
  0.82571). Deux bugs trouvés en route, tous deux « sûrs » (perte de
  puissance, jamais fausse preuve) : direction de rétraction des témoins ;
  convention de rotation (transposée en trop).
- v2 (rotations par intervalles) : validation 3D en cours (400k+ boîtes sans
  blocage) ; assaut du jeu de Xie (5 dims) lancé à L = 0.832.

## 5. Questions stratégiques (critique aussi ça)
1. Le passage à 8 dims (jeu à 4 formes, cible 0.834) est-il computationnellement
   réaliste avec ce schéma ? Xie a utilisé ~357k domaines en 5 dims.
2. Existe-t-il des minorations par boîte plus fortes que nos témoins
   (aires mixtes, support functions par intervalles) ?
3. Le choix du pentagone de Reuleaux comme 4e forme est-il optimal ? Comment
   caractériser les formes qui « débordent » nécessairement ?
4. Que penses-tu du choix borne inférieure vs déformation de Gibbs (majorant) ?

## ANNEXE : code complet (3 fichiers)

### bornes_inf.py
```python
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
}

if __name__ == "__main__":
    noms = sys.argv[1:] or ["xie3", "xie3+reuleaux3", "xie3+carre",
                            "xie3+reuleaux5", "xie3+heptagone"]
    for nom in noms:
        aire, params = minimise(JEUX[nom])
        print(f"{nom:28s} -> min numérique : {aire:.7f}", flush=True)
        if params is not None:
            print(f"{'':28s}    params : {np.round(params, 5).tolist()}", flush=True)

```

### certifie.py
```python
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

```

### certifie2.py
```python
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

    def certifie(self, taille_min=2e-5, budget_s=None, rapport=200000):
        boite0 = tuple((lo, hi) for (_, _, lo, hi) in self.dims)
        pile = [boite0]
        t0 = time.time()
        pire = math.inf
        while pile:
            if budget_s and time.time() - t0 > budget_s:
                return {"succes": False, "raison": "budget temps", "restantes": len(pile),
                        "boites": self.n_ok, "secondes": round(time.time() - t0, 1)}
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

if __name__ == "__main__":
    nom = sys.argv[1] if len(sys.argv) > 1 else "valide3d"
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else None
    pb = PROBLEMES[nom]()
    print(f"[{nom}] L = {pb.L}, dims = {len(pb.dims)}", flush=True)
    res = pb.certifie(budget_s=budget)
    print(res)

```
