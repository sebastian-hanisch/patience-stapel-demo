"""pat_model: Modell V gegen die Definition (feste Zeiten), Modell U, Reproduzierbarkeit, Stichprobe."""

import pat_model as M
from pat_rng import SplitMix64


def test_rang_aus_zeiten_von_hand():
    # Abfahrten 3,5 / 1,2 / 9,0 / 4,1: die Reihenfolge der Abfahrten ist Container 2 (1,2), 1 (3,5), 4 (4,1), 3 (9,0); also Ränge 2, 1, 4, 3
    assert M.rang_aus_zeiten([3.5, 1.2, 9.0, 4.1]) == [2, 1, 4, 3]
    assert M.rang_aus_zeiten([]) == [] and M.rang_aus_zeiten([7.0]) == [1]
    assert M.rang_aus_zeiten([2.0, 2.0, 1.0]) == [2, 3, 1]          # gleiche Zeit: die frühere Ankunft zuerst


def test_modell_v_ist_die_definition_nachgerechnet():
    """Gleicher Zufalls-Seed, Zeiten selbst nachgezogen: Rang = Reihenfolge der Abfahrtszeiten i + Exp(D)."""
    for seed in range(5):
        n, D = 8, 2.0
        rng = SplitMix64(seed)
        zeiten = [i + rng.expovariate(D) for i in range(n)]
        erwartet = [1 + sum(1 for z in zeiten if z < zeiten[i]) for i in range(n)]
        assert M.modell_folge(SplitMix64(seed), n, D) == erwartet


def test_modelle_liefern_permutationen_und_sind_reproduzierbar():
    for D in (None, 0.5, 4.0, 16.0):
        for n in (0, 1, 2, 12):
            p = M.modell_folge(SplitMix64(1), n, D)
            assert sorted(p) == list(range(1, n + 1))
            assert p == M.modell_folge(SplitMix64(1), n, D)
    assert M.modell_folge(SplitMix64(1), 12, None) != M.modell_folge(SplitMix64(2), 12, None)


def test_kleines_d_gibt_fast_die_ankunftsreihenfolge():
    """D = 0,5: die Folge ist im Mittel viel länger wachsend als bei D = 16 (Band, nicht bitgleich)."""
    klein = M.stichprobe(10, 0.5, 300, 1)["summe_lis"] / 300
    gross = M.stichprobe(10, 16.0, 300, 1)["summe_lis"] / 300
    assert klein > 8.5 and gross < 6.0


def test_stichprobe_zaehlt_von_hand_nachgerechnet():
    r = M.stichprobe(1, None, 5, 3, mit_sofort=True)           # n = 1: immer (1,), LIS = LDS = sofort = 1
    assert r["verteilung"] == {1: 5} and r["summe_lis"] == 5 and r["summe_lds"] == 5 and r["ungleich"] == 0
    assert r["summe_sofort"] == 5 and r["gleich"] == 5 and r["ein_stapel"] == 5 and r["abstand"] == {0: 5} and r["offen"] == 0
    r2 = M.stichprobe(30, None, 3, 3, mit_sofort=True)         # über der Obergrenze: sofort nicht gerechnet, sonst Rest wie gewohnt
    assert r2["summe_sofort"] == 0 and r2["gleich"] == 0 and sum(r2["verteilung"].values()) == 3
    assert M.stichprobe(6, 2.0, 50, 9) == M.stichprobe(6, 2.0, 50, 9)
