"""Orakel-Tests (anderer Rechenweg als die Demo, ORACLE-PLAYBOOK §5/§6): die Mindestzahl Stapel gegen Brute Force über alle Mengenpartitionen, gegen
Dilworth (kleinste Kettenüberdeckung = n minus maximales Matching, gerechnet mit scipy) und gegen ein numpy-Programm mit O(n²); die Verteilung der
Stapelzahl gegen die Summe der Quadrate der Standard-Young-Tableaux (Hakenformel, nur Ganzzahlen); „sofort“ gegen das Nachspielen aller Zuordnungen.
Aufzählungen bis n = 7 oder 8 laufen im Normalbetrieb, bis n = 9 mit `pytest -m slow`."""

import math
from itertools import permutations

import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

import pat_patience as P
import pat_sofort as S
import pat_tables as T


# --- unabhängige Rechenwege ---------------------------------------------------------------------------------------------------------------
def min_bloecke_brute(a, richtung):
    """Kleinste Zahl Blöcke einer Mengenpartition, jeder Block entlang der Ankunft streng fallend ('fallend') bzw. wachsend ('wachsend')."""
    n = len(a)
    best = [n]
    letzter: list = []

    def rek(i):
        if len(letzter) >= best[0]:
            return
        if i == n:
            best[0] = len(letzter)
            return
        for b in range(len(letzter)):
            alt = letzter[b]
            if (a[i] < alt) if richtung == "fallend" else (a[i] > alt):
                letzter[b] = a[i]
                rek(i + 1)
                letzter[b] = alt
        letzter.append(a[i])
        rek(i + 1)
        letzter.pop()

    rek(0)
    return best[0]


def kettenzahl(a, rel):
    """Dilworth: kleinste Überdeckung durch Ketten (i vor j, rel(a_i, a_j)) = n minus maximales Matching im zweiteiligen Graphen (scipy)."""
    n = len(a)
    if n == 0:
        return 0
    m = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in range(i + 1, n):
            if rel(a[i], a[j]):
                m[i, j] = 1
    treffer = maximum_bipartite_matching(csr_matrix(m), perm_type="column")
    return n - int((treffer >= 0).sum())


def lnds_dp(a):
    best = np.ones(len(a), dtype=int)
    for i in range(len(a)):
        for j in range(i):
            if a[j] <= a[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
    return int(best.max()) if len(a) else 0


def lis_dp(a):
    best = np.ones(len(a), dtype=int)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
    return int(best.max()) if len(a) else 0


def partitionen(n, maxteil=None):
    maxteil = n if maxteil is None else maxteil
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxteil), 0, -1):
        for rest in partitionen(n - k, k):
            yield (k,) + rest


def f_haken(lam):
    """Zahl der Standard-Young-Tableaux der Form lam (Hakenformel, nur Ganzzahlen)."""
    n = sum(lam)
    spalten = [sum(1 for x in lam if x > j) for j in range(lam[0])]
    produkt = 1
    for i, zeile in enumerate(lam):
        for j in range(zeile):
            produkt *= (zeile - j - 1) + (spalten[j] - i - 1) + 1
    return math.factorial(n) // produkt


def summe_f2(n, k):
    return sum(f_haken(lam) ** 2 for lam in partitionen(n) if lam[0] == k)


def spiele_nach(a, zuordnung, k):
    """Eigene Simulation: jeder Container auf den zugeordneten Stapel; nach jedem Einlagern wird ausgegeben, was an der Reihe ist. True, wenn 1..n herauskommt."""
    stapel = [[] for _ in range(k)]
    dran = 1
    for x, s in zip(a, zuordnung):
        stapel[s].append(x)
        while True:
            for st in stapel:
                if st and st[-1] == dran:
                    st.pop()
                    dran += 1
                    break
            else:
                break
    return dran == len(a) + 1


def zuordnungen(n, hoechstens_k):
    """Alle Zuordnungen der n Container zu Stapeln bis auf die Benennung der Stapel (Restricted Growth Strings) mit höchstens k Stapeln."""
    def rek(pre, benutzt):
        if len(pre) == n:
            yield tuple(pre)
            return
        for s in range(min(benutzt + 1, hoechstens_k)):
            pre.append(s)
            yield from rek(pre, max(benutzt, s + 1))
            pre.pop()
    yield from rek([], 0)


def sofort_brute(a):
    for k in range(1, len(a) + 2):
        if any(spiele_nach(a, z, k) for z in zuordnungen(len(a), k)):
            return max(k, 1) if a else 0
    raise AssertionError


# --- Mindestzahl Stapel = LIS ----------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("n", range(1, 7))
def test_stapelzahl_gleich_brute_force_ueber_alle_mengenpartitionen(n):
    for p in permutations(range(1, n + 1)):
        assert min_bloecke_brute(p, "fallend") == P.lis_laenge(p) == len(P.stapel_legen(p, "erster")), p
        assert min_bloecke_brute(p, "wachsend") == P.lds_laenge(p), p


def test_brute_force_n_7():
    for p in permutations(range(1, 8)):
        assert min_bloecke_brute(p, "fallend") == P.lis_laenge(p), p


@pytest.mark.parametrize("n", range(1, 8))
def test_stapelzahl_gleich_dilworth_matching(n):
    for p in permutations(range(1, n + 1)):
        assert kettenzahl(p, lambda x, y: x > y) == P.lis_laenge(p), p     # fallende Stapel = Ketten „später und kleiner“
        assert kettenzahl(p, lambda x, y: x < y) == P.lds_laenge(p), p     # wachsende Stapel


@pytest.mark.parametrize("n", range(1, 9))
def test_lis_gleich_numpy_dp(n):
    for p in permutations(range(1, n + 1)):
        assert P.lis_laenge(p) == lis_dp(p) and P.lds_laenge(p) == lis_dp([-x for x in p]), p


@pytest.mark.slow
def test_aufzaehlung_bis_n_9_alle_rechenwege():
    for n in (8, 9):
        for p in permutations(range(1, n + 1)):
            assert P.lis_laenge(p) == lis_dp(p), p
            assert P.stapel_legen(p, "erster") == P.stapel_legen(p, "engste")
            assert len(P.stapel_legen(p, "erster")) == P.lis_laenge(p)
    for p in permutations(range(1, 9)):
        assert kettenzahl(p, lambda x, y: x > y) == P.lis_laenge(p), p


def test_erster_passender_gleich_engste_passung_in_allen_folgen_bis_n_7():
    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            assert P.stapel_legen(p, "erster") == P.stapel_legen(p, "engste"), p


# --- Verteilung der Stapelzahl = Summe f^2 -------------------------------------------------------------------------------------------------------
def test_hakenformel_an_bekannten_formen():
    assert f_haken((2, 1)) == 2 and f_haken((3, 2)) == 5 and f_haken((2, 2, 1)) == 5 and f_haken((4, 3, 2, 1)) == 768
    assert sum(f_haken(lam) ** 2 for lam in partitionen(6)) == math.factorial(6)


@pytest.mark.parametrize("n", range(1, 9))
def test_verteilung_gleich_summe_f_quadrat_gegen_aufzaehlung(n):
    zeile = [0] * n
    for p in permutations(range(1, n + 1)):
        zeile[P.lis_laenge(p) - 1] += 1
    assert zeile == [summe_f2(n, k) for k in range(1, n + 1)]


def test_eingefrorene_verteilung_gleich_summe_f_quadrat_bis_n_10():
    for n in range(1, 11):
        z = T.zeile(n)
        assert z["verteilung"] == [summe_f2(n, k) for k in range(1, n + 1)], n
        assert sum(z["verteilung"]) == math.factorial(n) == z["folgen"]


def test_zeile_n_7_gleich_oeis_a047874_laut_quellenbericht():
    assert T.zeile(7)["verteilung"] == [1, 428, 2332, 1821, 421, 36, 1]


# --- sofort ------------------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("n", range(1, 6))
def test_sofort_gleich_nachspielen_aller_zuordnungen(n):
    for p in permutations(range(1, n + 1)):
        assert S.sofort_min(p) == sofort_brute(p), p


def test_sofort_gleich_nachspielen_n_6():
    for p in permutations(range(1, 7)):
        assert S.sofort_min(p) == sofort_brute(p), p


def test_sofort_hoechstens_zwei_gegen_zaehlfolge_a216040():
    erwartet = {1: 1, 2: 2, 3: 6, 4: 23, 5: 103, 6: 513, 7: 2760, 8: 15741}     # n <= 7 laut Quellenbericht (A216040), n = 8 eigene Zählung
    for n, zahl in erwartet.items():
        assert sum(1 for p in permutations(range(1, n + 1)) if S.sofort_min(p) <= 2) == zahl, n


def test_sofort_nie_ueber_lis_und_ein_stapel_genau_catalan():
    for n in range(1, 8):
        ein = 0
        for p in permutations(range(1, n + 1)):
            s = S.sofort_min(p)
            assert s <= P.lis_laenge(p), p
            ein += s == 1
        assert ein == math.comb(2 * n, n) // (n + 1)


# --- Gleichstände ------------------------------------------------------------------------------------------------------------------------------
def test_gleichstaende_gleich_dilworth_in_allen_woertern_2_2_2_2():
    basis = [1, 1, 2, 2, 3, 3, 4, 4]
    worte = sorted(set(permutations(basis)))
    assert len(worte) == 2520
    for w in worte:
        assert kettenzahl(w, lambda x, y: x >= y) == P.min_stapel_gleichstaende(w, True) == lis_dp(w), w          # nicht steigende Stapel
        assert kettenzahl(w, lambda x, y: x > y) == P.min_stapel_gleichstaende(w, False) == lnds_dp(w), w          # streng fallende Stapel


def test_gleichstaende_gruppe_4_4_und_3_3_2():
    for basis in ([1] * 4 + [2] * 4, [1] * 3 + [2] * 3 + [3] * 2):
        for w in sorted(set(permutations(basis)))[::7]:
            assert kettenzahl(w, lambda x, y: x >= y) == P.min_stapel_gleichstaende(w, True), w
            assert kettenzahl(w, lambda x, y: x > y) == P.min_stapel_gleichstaende(w, False), w


def test_gierige_stapelzahl_bei_gleichstaenden_gleich_der_formel():
    basis = [1, 1, 2, 2, 3, 3]
    for w in sorted(set(permutations(basis))):
        assert len(P.stapel_legen(w, "erster", gleiche_teilen=True)) == P.min_stapel_gleichstaende(w, True), w
        assert len(P.stapel_legen(w, "erster", gleiche_teilen=False)) == P.min_stapel_gleichstaende(w, False), w
