#!/usr/bin/env python3
"""Moteur de recherche pour t(N) = A034258 : factoriser N! en N facteurs
en maximisant le plus petit facteur.

v5 — best-fit multi-éléments + finition lisse :
  pour un seuil candidat t :
  1. les premiers >= t forment chacun un facteur seul ;
  2. chaque nouveau facteur démarre avec le plus grand premier « moyen »
     restant (5 <= p < t), puis :
       - tant qu'on peut, on GRANDIT avec le plus grand moyen <= t/f
         (aucun gaspillage) ;
       - sinon on FINIT avec le moins cher entre : plus petit moyen >= t/f
         et plus petit 2^a·3^b >= t/f réalisable avec le stock de 2 et 3 ;
  3. moyens épuisés : facteurs purs 2^a·3^b >= t au plus juste ;
  4. restes versés dans le premier facteur. Balayage descendant de t.

Guidage heuristique ; le résultat est revérifié en exact (produit == N!)
inline et par verifier.py (script indépendant).
"""
import bisect
import math
import sys
from collections import Counter


def primes_de_factorielle(n):
    """Multiset exact des facteurs premiers de n! (crible + formule de Legendre)."""
    crible = list(range(n + 1))
    for i in range(2, int(math.isqrt(n)) + 1):
        if crible[i] == i:
            for j in range(i * i, n + 1, i):
                if crible[j] == j:
                    crible[j] = i
    premiers = [p for p in range(2, n + 1) if crible[p] == p]
    exp = Counter()
    for p in premiers:
        pk = p
        while pk <= n:
            exp[p] += n // pk
            pk *= p
    return exp


def plus_petit_23(cible, deux, trois):
    """Plus petit 2^a·3^b >= cible avec a <= deux, b <= trois. None si impossible."""
    meilleur = None
    puiss3 = 1
    b = 0
    while b <= trois:
        reste = (cible + puiss3 - 1) // puiss3
        a = max(0, (reste - 1).bit_length())
        if a <= deux:
            val = (1 << a) * puiss3
            if meilleur is None or val < meilleur[0]:
                meilleur = (val, a, b)
        if puiss3 >= cible:
            break
        puiss3 *= 3
        b += 1
    return meilleur


def construit(n, t, exp):
    """Essaie de former n facteurs >= t. Rend la liste ou None."""
    deux, trois = exp.get(2, 0), exp.get(3, 0)
    mids = []
    facteurs = []
    for p in sorted(exp):
        if p in (2, 3):
            continue
        if p >= t:
            facteurs.extend([p] * exp[p])
        else:
            mids.extend([p] * exp[p])
    while len(facteurs) < n and (mids or (deux + trois)):
        if mids:
            f = mids.pop()
        else:
            res = plus_petit_23(t, deux, trois)
            if res is None:
                return None
            val, a, b = res
            deux -= a
            trois -= b
            facteurs.append(val)
            continue
        while f < t:
            besoin = (t + f - 1) // f
            # grandir sans gaspiller : plus grand moyen <= t // f
            i = bisect.bisect_right(mids, t // f) - 1
            if i >= 0 and mids[i] * f < t:
                f *= mids.pop(i)
                continue
            # finir au plus juste : moyen ou lisse
            j = bisect.bisect_left(mids, besoin)
            fin_mid = mids[j] if j < len(mids) else None
            fin_23 = plus_petit_23(besoin, deux, trois)
            if fin_mid is not None and (fin_23 is None or fin_mid <= fin_23[0]):
                f *= mids.pop(j)
            elif fin_23 is not None:
                val, a, b = fin_23
                deux -= a
                trois -= b
                f *= val
            elif i >= 0:
                f *= mids.pop(i)  # dernier recours : le grand moyen dispo
            else:
                return None
        facteurs.append(f)
    if len(facteurs) < n:
        return None
    # excédents et restes : fusionnés dans le premier facteur (jamais nuisible)
    extra = facteurs[n:]
    facteurs = facteurs[:n]
    for x in extra:
        facteurs[0] *= x
    for p in mids:
        facteurs[0] *= p
    facteurs[0] *= (1 << deux) * (3 ** trois)
    return facteurs


def construit_cofacteur(n, t, exp):
    """Stratégie alternative (v4) : chaque premier moyen, du plus grand au
    plus petit, reçoit UN cofacteur au plus juste (un moyen restant ou un
    2^a·3^b). Meilleure quand le stock de 2/3 suffit ; échoue par pénurie
    de « colle » quand les petits moyens sont trop nombreux."""
    deux, trois = exp.get(2, 0), exp.get(3, 0)
    mids = []
    facteurs = []
    for p in sorted(exp):
        if p in (2, 3):
            continue
        if p >= t:
            facteurs.extend([p] * exp[p])
        else:
            mids.extend([p] * exp[p])
    if len(facteurs) > n:
        return None
    while mids:
        p = mids.pop()
        besoin = (t + p - 1) // p
        i = bisect.bisect_left(mids, besoin)
        opt_a = mids[i] if i < len(mids) else None
        opt_b = plus_petit_23(besoin, deux, trois)
        if opt_a is not None and (opt_b is None or opt_a <= opt_b[0]):
            mids.pop(i)
            facteurs.append(p * opt_a)
        elif opt_b is not None:
            val, a, b = opt_b
            deux -= a
            trois -= b
            facteurs.append(p * val)
        else:
            return None
    while len(facteurs) < n:
        res = plus_petit_23(t, deux, trois)
        if res is None:
            return None
        val, a, b = res
        deux -= a
        trois -= b
        facteurs.append(val)
    extra = facteurs[n:]
    facteurs = facteurs[:n]
    for x in extra:
        facteurs[0] *= x
    facteurs[0] *= (1 << deux) * (3 ** trois)
    return facteurs


STRATEGIES = (construit, construit_cofacteur)


def factorise_petit(x):
    """Factorise un entier en petits premiers (les facteurs sont <= N)."""
    fs = []
    d = 2
    while d * d <= x:
        while x % d == 0:
            fs.append(d)
            x //= d
        d += 1
    if x > 1:
        fs.append(x)
    return fs


def repare_vers(n, t, facteurs, rondes_max=None):
    """Tente de rendre tous les facteurs >= t en déplaçant des premiers
    des bacs excédentaires (qui restent >= t après don) vers les bacs
    déficitaires. Rend la nouvelle liste de facteurs ou None si blocage."""
    bacs = [sorted(factorise_petit(f)) for f in facteurs]
    vals = [f for f in facteurs]
    if rondes_max is None:
        rondes_max = 20 * n
    for _ in range(rondes_max):
        i_min = min(range(n), key=lambda i: vals[i])
        if vals[i_min] >= t:
            return vals
        deficit = (t + vals[i_min] - 1) // vals[i_min]
        # candidats : (p, j) retirables (bac j reste >= t sans p)
        juste = None   # plus petit p >= deficit
        gros = None    # plus gros p toutes catégories (si aucun ne suffit)
        for j in range(n):
            if j == i_min:
                continue
            vj = vals[j]
            for p in bacs[j]:
                if vj // p < t:
                    break  # bacs triés croissants : les suivants sont plus gros
                if p >= deficit:
                    if juste is None or p < juste[0]:
                        juste = (p, j)
                    break  # inutile de regarder plus gros dans ce bac
                if gros is None or p > gros[0]:
                    gros = (p, j)
        choix = juste or gros
        if choix is None:
            return None
        p, j = choix
        bacs[j].remove(p)
        vals[j] //= p
        bisect.insort(bacs[i_min], p)
        vals[i_min] *= p
    return None


def meilleur_t(n, exp=None, t_max=None):
    """Balayage descendant + phase de réparation pour grappiller au-delà."""
    if exp is None:
        exp = primes_de_factorielle(n)
    if t_max is None:
        t_max = int(n / math.e) + 2
    base = None
    for t in range(t_max, 0, -1):
        for strat in STRATEGIES:
            f = strat(n, t, exp)
            if f is not None:
                base = (t, f)
                break
        if base:
            break
    if base is None:
        return 1, None
    t, f = base
    # réparation : tente t+1, t+2... tant que ça passe
    while True:
        f2 = repare_vers(n, t + 1, f)
        if f2 is None:
            return t, f
        t += 1
        f = f2


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [30, 100, 300, 1000, 3000]
    ref = {}
    try:
        for ligne in open("oeis_A034258.txt"):
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#"):
                k, v = ligne.split()
                ref[int(k)] = int(v)
    except FileNotFoundError:
        pass
    for n in ns:
        t, f = meilleur_t(n)
        produit = 1
        for x in f:
            produit *= x
        assert produit == math.factorial(n) and len(f) == n and min(f) >= t
        cible = ref.get(n)
        etat = "?" if cible is None else ("OK ===" if t == cible else f"écart {t - cible:+d}")
        print(f"N={n:6d}  t_trouvé={t:5d}  optimum_connu={cible}  [{etat}]  (N/e={n/math.e:.1f})")
