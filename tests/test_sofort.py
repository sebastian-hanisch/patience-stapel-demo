"""pat_sofort an Handbeispielen: Konfliktkanten (Muster 231), Färbung, Nachspielen, Grenzen."""

import time
from itertools import permutations

import pat_sofort as S
from pat_model import modell_folge
from pat_patience import lis_laenge
from pat_rng import SplitMix64


def test_konfliktkante_des_handbeispiels(handbeispiel):
    # (3, 5, 2) ist das Muster 231; alle anderen Paare i < j mit kleinerem a_i haben keinen späteren, noch kleineren Container
    assert S.konfliktkanten(handbeispiel) == {(3, 5)}


def test_sofort_ein_stapel_reicht_nicht_zwei_reichen(handbeispiel):
    k, zuordnung = S.sofort_zuordnung(handbeispiel)
    assert k == 2 and S.sofort_min(handbeispiel) == 2
    assert S.sim_parallel(handbeispiel, zuordnung, k) == [1, 2, 3, 4, 5]
    assert S.sim_parallel(handbeispiel, (0, 0, 0, 0, 0), 1) != [1, 2, 3, 4, 5]     # ein Stapel sortiert (1, 3, 5, 2, 4) nicht
    assert S.sim_parallel(handbeispiel, (0, 0, 1, 0, 0), 2) == [1, 2, 3, 4, 5]     # 1, 3, 2, 4 in Stapel A, 5 in Stapel B


def test_sortierte_folge_und_umkehrfolge():
    assert S.sofort_zuordnung((1, 2, 3, 4, 5)) == (1, (0, 0, 0, 0, 0))   # sofort ausgeben: jeder Container ist sofort an der Reihe
    assert S.sofort_zuordnung((5, 4, 3, 2, 1))[0] == 1


def test_randfaelle():
    assert S.sofort_zuordnung(()) == (0, ())
    assert S.sofort_zuordnung((1,)) == (1, (0,))
    assert S.sofort_min((2, 1)) == 1 and S.sofort_min((1, 2)) == 1


def test_zuordnung_sortiert_in_allen_folgen_bis_n_6():
    for n in range(1, 7):
        for p in permutations(range(1, n + 1)):
            k, z = S.sofort_zuordnung(p)
            assert S.sim_parallel(p, z, k) == list(range(1, n + 1)), p
            assert max(z) + 1 == k


def test_ein_stapel_genau_bei_231_vermeidern():
    """sofort = 1 genau dann, wenn die Folge das Muster 231 vermeidet (Catalan-Zahlen 1, 2, 5, 14, 42, 132)."""
    def enthaelt_231(p):
        n = len(p)
        return any(p[k] < p[i] < p[j] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))
    for n, cat in zip(range(1, 7), (1, 2, 5, 14, 42, 132)):
        ein = [p for p in permutations(range(1, n + 1)) if S.sofort_min(p) == 1]
        assert len(ein) == cat
        assert all(not enthaelt_231(p) for p in ein)


def test_obergrenze_und_budget(handbeispiel):
    lang = tuple(range(1, S.SOFORT_N_MAX + 2))
    assert S.sofort_zuordnung(lang) is None                      # n = 25: nicht gerechnet
    assert S.sofort_zuordnung(tuple(range(1, S.SOFORT_N_MAX + 1))) == (1, (0,) * S.SOFORT_N_MAX)
    assert S.sofort_zuordnung(handbeispiel, budget=0) is None    # Knotenbudget erschöpft: nicht gerechnet (statt falscher Zahl)


def test_zufallsfolgen_an_der_obergrenze_in_kurzer_zeit_und_nie_ueber_lis():
    rng = SplitMix64(777)
    t0 = time.time()
    for _ in range(300):
        p = modell_folge(rng, S.SOFORT_N_MAX, None)
        erg = S.sofort_zuordnung(p)
        assert erg is not None and erg[0] <= lis_laenge(p)
        assert S.sim_parallel(p, erg[1], erg[0]) == list(range(1, S.SOFORT_N_MAX + 1))
    assert time.time() - t0 < 30
