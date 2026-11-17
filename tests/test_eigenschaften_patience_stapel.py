"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Aussagen, die für Patience gelten müssen, ohne dass man das richtige Ergebnis kennt.
Je Eigenschaft 30 bis 50 Zufallsfolgen mit festem Zufalls-Seed (SplitMix64), dazu Randfälle."""

import pytest

import pat_patience as P
import pat_sofort as S
from pat_model import modell_folge
from pat_rng import SplitMix64


def _folgen(n_lo=1, n_hi=12, anzahl=40, seed=2024):
    rng = SplitMix64(seed)
    return [tuple(modell_folge(rng, n_lo + rng.below(n_hi - n_lo + 1), None)) for _ in range(anzahl)]


def test_spiegeln_der_folge_vertauscht_lis_und_lds():
    for p in _folgen():
        assert P.lis_laenge(p[::-1]) == P.lds_laenge(p) and P.lds_laenge(p[::-1]) == P.lis_laenge(p)


def test_umkehren_der_raenge_vertauscht_lis_und_lds():
    for p in _folgen():
        n = len(p)
        assert P.lis_laenge([n + 1 - x for x in p]) == P.lds_laenge(p)


def test_die_inverse_permutation_hat_dieselbe_lis():
    for p in _folgen():
        inv = [0] * len(p)
        for i, x in enumerate(p):
            inv[x - 1] = i + 1
        assert P.lis_laenge(inv) == P.lis_laenge(p) and P.lds_laenge(inv) == P.lds_laenge(p)


def test_monotones_umnummerieren_aendert_die_stapel_nicht():
    for p in _folgen():
        gestreckt = [3 * x + 7 for x in p]
        alt = P.stapel_legen(p, "erster")
        neu = P.stapel_legen(gestreckt, "erster")
        assert neu == [[3 * x + 7 for x in s] for s in alt]


def test_streichen_senkt_die_stapelzahl_um_hoechstens_1_und_einfuegen_erhoeht_um_hoechstens_1():
    rng = SplitMix64(5)
    for p in _folgen():
        i = rng.below(len(p))
        kleiner = [x - (x > p[i]) for k, x in enumerate(p) if k != i]       # Container i streichen, Ränge neu nummerieren
        assert 0 <= P.lis_laenge(p) - P.lis_laenge(kleiner) <= 1
        # Einfügen eines neuen Containers an zufälliger Stelle mit zufälligem Rang
        pos, rang = rng.below(len(p) + 1), 1 + rng.below(len(p) + 1)
        groesser = [x + (x >= rang) for x in p]
        groesser.insert(pos, rang)
        assert 0 <= P.lis_laenge(groesser) - P.lis_laenge(p) <= 1


def test_spitzen_wachsen_und_jeder_stapel_ist_fallend_jeder_container_liegt_einmal_und_abholen_gibt_1_bis_n():
    for p in _folgen(anzahl=50):
        assert P.spitzen_wachsen(p)
        st = P.stapel_legen(p, "erster")
        assert all(x > y for s in st for x, y in zip(s, s[1:]))
        assert sorted(x for s in st for x in s) == list(range(1, len(p) + 1))
        assert P.abholen(st) == list(range(1, len(p) + 1))


def test_jede_gierige_regel_braucht_mindestens_lis_stapel_und_legt_fallende_stapel():
    for p in _folgen(anzahl=50):
        for regel in P.REGELN:
            st = P.stapel_legen(p, regel)
            assert len(st) >= P.lis_laenge(p)
            assert all(x > y for s in st for x, y in zip(s, s[1:]))
            assert P.abholen(st) == list(range(1, len(p) + 1))


def test_sofort_nie_ueber_lis_und_ein_stapel_genau_bei_231_vermeidern():
    for p in _folgen(n_hi=10, anzahl=50):
        s = S.sofort_min(p)
        assert 1 <= s <= P.lis_laenge(p)
        n = len(p)
        hat_231 = any(p[k] < p[i] < p[j] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))
        assert (s == 1) == (not hat_231)


def test_wachsende_stapel_sind_nur_dann_blockierfrei_wenn_jeder_stapel_einen_container_hat():
    for p in _folgen():
        st = P.stapel_wachsend(p)
        assert len(st) == P.lds_laenge(p)
        assert P.blockierende(st) == len(p) - len(st)         # jeder Container außer dem untersten jedes Stapels blockiert
        assert P.blockierende(P.stapel_legen(p, "erster")) == 0


def test_gleichstaende_streng_gegen_nicht_fallend_ordnet_sich():
    rng = SplitMix64(9)
    for _ in range(40):
        w = tuple(1 + rng.below(4) for _ in range(8))
        teilen = P.min_stapel_gleichstaende(w, True)
        verschieden = P.min_stapel_gleichstaende(w, False)
        assert teilen <= verschieden                 # Gleiche teilen dürfen nie mehr Stapel brauchen als Gleiche trennen


@pytest.mark.parametrize("n", [1, 2, 3, 30])
def test_sortierte_folge_und_umkehrfolge_fuer_jedes_n(n):
    assert len(P.stapel_legen(tuple(range(1, n + 1)), "erster")) == n
    assert len(P.stapel_legen(tuple(range(n, 0, -1)), "erster")) == 1
