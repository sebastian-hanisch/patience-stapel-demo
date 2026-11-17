"""Einheiten von pat_patience an Handbeispielen (DEMO-PLAYBOOK §1b): jede Erwartung ist von Hand gerechnet, nicht aus dem Code abgeschrieben."""

from itertools import combinations, permutations

import pytest

import pat_patience as P
from pat_rng import SplitMix64


def test_erster_passender_legt_die_stapel_von_hand(handbeispiel):
    assert P.stapel_legen(handbeispiel, "erster") == [[1], [3, 2], [5, 4]]
    assert P.stapel_legen(handbeispiel, "engste") == [[1], [3, 2], [5, 4]]


def test_groesste_spitze_und_ganz_rechts_legen_vier_stapel(handbeispiel):
    # 2 kommt auf die 5 (größte bzw. rechteste passende Spitze), danach passt 4 nirgends
    assert P.stapel_legen(handbeispiel, "groesste") == [[1], [3], [5, 2], [4]]
    assert P.stapel_legen(handbeispiel, "rechts") == [[1], [3], [5, 2], [4]]


def test_lis_ist_drei_und_es_gibt_genau_drei_laengste(handbeispiel):
    drei = sorted(c for c in combinations(handbeispiel, 3) if c[0] < c[1] < c[2])
    assert drei == [(1, 2, 4), (1, 3, 4), (1, 3, 5)]
    assert not [c for c in combinations(handbeispiel, 4) if c[0] < c[1] < c[2] < c[3]]
    assert P.lis_laenge(handbeispiel) == 3
    werte = tuple(handbeispiel[i] for i in P.lis_teilfolge(handbeispiel))
    assert werte in drei


def test_lds_und_wachsende_stapel_mit_drei_blockierenden(handbeispiel):
    assert P.lds_laenge(handbeispiel) == 2
    assert P.stapel_wachsend(handbeispiel) == [[1, 3, 5], [2, 4]]
    assert P.blockierende(P.stapel_wachsend(handbeispiel)) == 3          # 3 und 5 über der 1, 4 über der 2
    assert P.blockierende_werte(P.stapel_wachsend(handbeispiel)) == {3, 5, 4}
    assert P.blockierende(P.stapel_legen(handbeispiel, "erster")) == 0    # fallende Stapel sind blockierfrei


def test_abholen_von_der_kleinsten_spitze(handbeispiel):
    assert P.abholen(P.stapel_legen(handbeispiel, "erster")) == [1, 2, 3, 4, 5]
    st = P.stapel_legen(handbeispiel, "erster")
    P.abholen(st)
    assert st == [[1], [3, 2], [5, 4]]                                      # die Stapel werden nicht verändert


def test_quellenbeispiel_aldous_diaconis():
    a = (7, 2, 8, 1, 3, 4, 10, 6, 9, 5)
    assert P.stapel_legen(a, "erster") == [[7, 2, 1], [8, 3], [4], [10, 6, 5], [9]]
    assert P.lis_laenge(a) == 5
    assert tuple(a[i] for i in P.lis_teilfolge(a)) == (1, 3, 4, 6, 9)


def test_gleichstaende_teilen_oder_verschieden():
    w = (1, 2, 2, 3)
    assert P.min_stapel_gleichstaende(w, True) == 3        # streng wachsend: (1, 2, 3)
    assert P.min_stapel_gleichstaende(w, False) == 4       # nicht fallend: (1, 2, 2, 3)
    assert P.stapel_legen(w, "erster", gleiche_teilen=True) == [[1], [2, 2], [3]]
    assert P.stapel_legen(w, "erster", gleiche_teilen=False) == [[1], [2], [2], [3]]


def test_randfaelle():
    assert P.stapel_legen((), "erster") == [] and P.lis_laenge(()) == 0 and P.lis_teilfolge(()) == () and P.abholen([]) == []
    assert P.stapel_legen((1,), "erster") == [[1]] and P.lis_laenge((1,)) == 1 and P.lis_teilfolge((1,)) == (0,)
    assert len(P.stapel_legen((2, 1), "erster")) == 1 and len(P.stapel_legen((1, 2), "erster")) == 2
    assert P.lis_laenge((1, 2, 3, 4, 5)) == 5 and P.lis_laenge((5, 4, 3, 2, 1)) == 1                 # sortiert: n Stapel, Umkehrfolge: 1
    assert P.lds_laenge((1, 2, 3, 4, 5)) == 1 and P.lds_laenge((5, 4, 3, 2, 1)) == 5
    assert P.stapel_wachsend((5, 4, 3, 2, 1)) == [[5], [4], [3], [2], [1]]
    assert P.ist_permutation((2, 1, 3)) and not P.ist_permutation((1, 1, 3)) and P.ist_permutation(())


def test_unbekannte_regel_wirft():
    with pytest.raises(ValueError):
        P.stapel_legen((2, 1), "gibt_es_nicht")


def test_jeder_regel_zweig_weicht_auf_mindestens_einer_folge_ab():
    """Zweig-Test: keine Regel ist ein toter Zweig (jede weicht auf einer kleinen Folge von „erster passender“ ab, ganz rechts auch von „größte Spitze“)."""
    folgen = [p for n in range(3, 7) for p in permutations(range(1, n + 1))]
    assert any(P.stapel_legen(p, "groesste") != P.stapel_legen(p, "erster") for p in folgen)
    assert any(P.stapel_legen(p, "rechts") != P.stapel_legen(p, "erster") for p in folgen)
    assert any(P.stapel_legen(p, "rechts") != P.stapel_legen(p, "groesste") for p in folgen)
    rng = SplitMix64(11)
    assert any(P.stapel_legen(p, "zufall", rng) != P.stapel_legen(p, "erster") for p in folgen[:200])


def test_zufallswahl_legt_nur_auf_passende_stapel_und_ist_reproduzierbar():
    for p in list(permutations(range(1, 7)))[:100]:
        st = P.stapel_legen(p, "zufall", SplitMix64(11))
        assert all(x > y for s in st for x, y in zip(s, s[1:])), p       # jeder Stapel fallend
        assert sorted(x for s in st for x in s) == sorted(p)
        assert len(st) >= P.lis_laenge(p)
        assert st == P.stapel_legen(p, "zufall", SplitMix64(11))


def test_spitzen_wachsen_nach_jedem_schritt():
    for p in permutations(range(1, 7)):
        assert P.spitzen_wachsen(p)
