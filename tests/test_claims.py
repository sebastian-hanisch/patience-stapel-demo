"""Claims: jede Zahl der README-Tabelle „Befunde“ (B1 bis B14) wird hier nachgerechnet oder gegen die eingefrorene Tabelle gehalten.

Die Tests rechnen mit den Auswertungsfunktionen der App; jeder prüft außerdem, dass die Zahl in der README genau so (deutsch formatiert) steht, damit Text und Test
nicht auseinanderlaufen. Ganzzahlen und Brüche exakt; Stichprobenmittel als Band. B15 steht in tests/test_presets.py."""

import math
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

import pat_evaluation as E
import pat_model as M
import pat_patience as P
import pat_sofort as S
import pat_tables as T
import pat_texts as X

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
ZEILE_B = {z.split("|")[1].strip(): z for z in README.splitlines() if z.startswith("| B")}


def _in_readme(*texte, zeile=None):
    """Jeder Text steht in der README (bei `zeile` in genau der Tabellenzeile dieses Befunds)."""
    quelle = ZEILE_B[zeile] if zeile else README
    for t in texte:
        assert t in quelle, f"„{t}“ steht nicht in {'Zeile ' + zeile if zeile else 'der README'}"


def _fakt(n):
    return math.factorial(n)


# --- B1, B2 -------------------------------------------------------------------------------------------------------------------------------
def test_b01_handbeispiel(handbeispiel):
    a = handbeispiel
    assert P.stapel_legen(a, "erster") == P.stapel_legen(a, "engste") == [[1], [3, 2], [5, 4]]
    assert len(P.stapel_legen(a, "erster")) == P.lis_laenge(a) == 3
    assert sorted(c for c in combinations(a, 3) if c[0] < c[1] < c[2]) == [(1, 2, 4), (1, 3, 4), (1, 3, 5)]
    assert len(P.stapel_legen(a, "groesste")) == len(P.stapel_legen(a, "rechts")) == 4
    assert P.stapel_wachsend(a) == [[1, 3, 5], [2, 4]] and P.lds_laenge(a) == 2 and P.blockierende(P.stapel_wachsend(a)) == 3
    assert S.konfliktkanten(a) == {(3, 5)} and S.sofort_min(a) == 2
    zeile = [0] * 5
    for p in permutations(range(1, 6)):
        zeile[P.lis_laenge(p) - 1] += 1
    assert zeile == [1, 41, 61, 16, 1] == T.zeile(5)["verteilung"] and zeile[2] == 61
    assert T.mittel_lis(5) == Fraction(67, 24) and T.mittel_sofort(5) == Fraction(9, 5)
    assert T.mittel_lis(5) - T.mittel_sofort(5) == Fraction(119, 120)
    _in_readme("[[1], [3, 2], [5, 4]]", "(1, 2, 4), (1, 3, 4), (1, 3, 5)", "1, 41, 61, 16, 1", "67/24", "9/5", "119/120", zeile="B1")


def test_b02_beispiel_aldous_diaconis():
    a = (7, 2, 8, 1, 3, 4, 10, 6, 9, 5)
    assert P.stapel_legen(a, "erster") == [[7, 2, 1], [8, 3], [4], [10, 6, 5], [9]] and P.lis_laenge(a) == 5
    assert tuple(a[i] for i in P.lis_teilfolge(a)) == (1, 3, 4, 6, 9)
    _in_readme("[[7, 2, 1], [8, 3], [4], [10, 6, 5], [9]]", "7 2 8 1 3 4 10 6 9 5", zeile="B2")


# --- B3, B4 -------------------------------------------------------------------------------------------------------------------------------
def test_b03_zaehlung_der_aufgezaehlten_folgen():
    """Die Zahl der Folgen, über die die Orakel-Tests laufen (n <= 7 Brute Force, n <= 8 Matching, n <= 9 O(n²)); die Vergleiche selbst stehen in test_oracle_patience_stapel.py."""
    assert [sum(_fakt(n) for n in range(1, m + 1)) for m in (7, 8, 9)] == [5913, 46233, 409113]
    assert sum(T.zeile(n)["folgen"] for n in range(1, 10)) == 409113
    _in_readme("5 913", "46 233", "409 113", zeile="B3")


def test_b04_erster_gleich_engste_in_allen_folgen():
    assert 1 + sum(T.zeile(n)["regeln"]["erster_gleich_engste"] for n in range(2, 10)) == 409113
    assert all(T.zeile(n)["regeln"]["erster_gleich_lis"] == T.zeile(n)["folgen"] for n in range(2, 10))
    _in_readme("409 113 von 409 113", zeile="B4")


# --- B5 -----------------------------------------------------------------------------------------------------------------------------------
def test_b05_regeln_mit_mehr_stapeln_als_noetig():
    erwartet = {4: (1, 1, 1, "4,2", 24), 6: (135, 120, 61, "18,8", 720), 8: (14993, 12886, 7793, "37,2", 40320), 9: (168927, 144527, 89131, "46,6", 362880)}
    for n, (g, r, z, pg, f) in erwartet.items():
        t = T.zeile(n)["regeln"]
        assert (t["groesste"], t["rechts"], t["zufall"], T.zeile(n)["folgen"]) == (g, r, z, f), n
        assert E.prozent(Fraction(g, f)) == pg
        _in_readme(E.ganz(g), E.ganz(f), zeile="B5")
    assert E.prozent(Fraction(12886, 40320)) == "32,0" and E.prozent(Fraction(7793, 40320)) == "19,3" and E.prozent(Fraction(144527, 362880)) == "39,8"
    assert E.prozent(Fraction(89131, 362880)) == "24,6" and E.prozent(Fraction(120, 720)) == "16,7" and E.prozent(Fraction(61, 720)) == "8,5"
    # Zufallswahl: als Band 18,9 bis 19,3 % bei n = 8 (SplitMix64 gibt 19,3 %, ein Strom von numpy gab in einer früheren Messung 18,9 %)
    anteil = Fraction(T.zeile(8)["regeln"]["zufall"], T.zeile(8)["folgen"])
    assert Fraction(189, 1000) - Fraction(1, 200) <= anteil <= Fraction(193, 1000) + Fraction(1, 200)
    _in_readme("14 993 (37,2 %), 12 886 (32,0 %), 7 793 (19,3 %)", "18,9 bis 19,3 %", zeile="B5")


# --- B6 -----------------------------------------------------------------------------------------------------------------------------------
def test_b06_gleichstaende():
    w = (1, 2, 2, 3)
    assert P.min_stapel_gleichstaende(w, True) == 3 and P.min_stapel_gleichstaende(w, False) == 4
    erwartet = {(2, 2, 2, 2): (2520, 2062), (3, 3, 2): (560, 551), (2, 2, 1, 1, 1, 1): (10080, 5013), (4, 4): (70, 70)}
    for gruppen, (woerter, verschieden) in erwartet.items():
        basis = [r for r, g in enumerate(gruppen, 1) for _ in range(g)]
        alle = sorted(set(permutations(basis)))
        assert len(alle) == woerter, gruppen
        assert sum(1 for x in alle if P.min_stapel_gleichstaende(x, True) != P.min_stapel_gleichstaende(x, False)) == verschieden, gruppen
    assert E.prozent(Fraction(2062, 2520)) == "81,8"
    _in_readme("2 062 von 2 520 Wörtern (81,8 %)", "551 von 560", "5 013 von 10 080", "70 von 70", zeile="B6")
    for text in ("2 062 von 2 520",):
        assert text in X.GRENZEN


# --- B7 -----------------------------------------------------------------------------------------------------------------------------------
def test_b07_die_falle_lis_gegen_lds():
    ungleich = {4: 20, 5: 84, 6: 464, 7: 3758, 8: 30456, 9: 262904}
    summen = {4: 58, 5: 335, 6: 2261, 7: 17465, 8: 152020, 9: 1473057}
    for n in ungleich:
        z = T.zeile(n)
        assert z["lis_ungleich_lds"] == ungleich[n] and z["summe_lis"] == z["summe_lds"] == summen[n], n
    for n in range(4, 8):                                    # bis n = 7 hier nachgezählt, die übrigen aus der Tabelle (Neu-Rechnung in test_tables.py)
        zaehl = sum(1 for p in permutations(range(1, n + 1)) if P.lis_laenge(p) != P.lds_laenge(p))
        assert zaehl == ungleich[n]
    assert E.prozent(Fraction(262904, 362880)) == "72,4" and E.zahl(T.mittel_lis(9), 3) == "4,059"
    _in_readme("262 904 von 362 880 Folgen (n = 9, 72,4 %)", "4,059", "20 von 24", "3 758 von 5 040", "30 456 von 40 320", "1 473 057", zeile="B7")


# --- B8 -----------------------------------------------------------------------------------------------------------------------------------
def test_b08_modell_v_n_10():
    v = T.modell_v()
    lis = {"0.5": "9,3955", "1.0": "8,3275", "2.0": "7,0950", "4.0": "6,0775", "8.0": "5,2790", "16.0": "4,8585", "uniform": "4,3095"}
    lds = {"0.5": "1,4835", "1.0": "1,9825", "2.0": "2,4945", "4.0": "3,0255", "8.0": "3,5485", "16.0": "3,8510", "uniform": "4,3325"}
    sofort = {"0.5": "1,0035", "1.0": "1,0950", "2.0": "1,4655", "4.0": "2,0385", "8.0": "2,5130", "16.0": "2,8715", "uniform": "3,3185"}
    ein = {"0.5": 1993, "1.0": 1814, "2.0": 1143, "4.0": 421, "8.0": 124, "16.0": 46, "uniform": 4}
    for k, m in v.items():
        assert m["anzahl"] == 2000
        assert E.zahl(Fraction(m["summe_lis"], 2000), 4) == lis[k] and E.zahl(Fraction(m["summe_lds"], 2000), 4) == lds[k] and E.zahl(Fraction(m["summe_sofort"], 2000), 4) == sofort[k]
        assert m["ein_stapel"] == ein[k]
    assert [v[k]["seed"] for k in lis] == [15000 + i for i in range(7)]
    assert T.mittel_lis(10) == Fraction(15730705, 3628800) and E.zahl(T.mittel_lis(10), 3) == "4,335"
    assert E.zahl(Fraction(16796, 3628800) * 100, 2) == "0,46"
    _in_readme(*lis.values(), *lds.values(), *sofort.values(), "1 993 / 1 814 / 1 143 / 421 / 124 / 46 / 4", "0,46 %", zeile="B8")
    # Neu-Rechnung als Band (drei Standardfehler, grob 0,08 für das Mittel der LIS bei n = 10 und 2 000 Folgen); Zufalls-Seed wie in der Tabelle
    for idx, D in ((0, 0.5), (3, 4.0), (6, None)):
        r = M.stichprobe(10, D, 2000, 15000 + idx)
        schluessel = "uniform" if D is None else str(D)
        assert abs(r["summe_lis"] / 2000 - v[schluessel]["summe_lis"] / 2000) < 0.08
        assert abs(r["summe_lds"] / 2000 - v[schluessel]["summe_lds"] / 2000) < 0.08


# --- B9 -----------------------------------------------------------------------------------------------------------------------------------
def test_b09_verteilung_der_stapelzahl():
    assert T.zeile(4)["verteilung"] == [1, 13, 9, 1]
    assert T.zeile(7)["verteilung"] == [1, 428, 2332, 1821, 421, 36, 1]
    assert T.zeile(9)["verteilung"] == [1, 4861, 89497, 167449, 83029, 16465, 1513, 64, 1]
    # Eulersche Zeile zum Vergleich: Folgen mit genau k-1 Anstiegen (n = 4): 1, 11, 11, 1
    euler = [0] * 4
    for p in permutations(range(1, 5)):
        euler[sum(1 for i in range(3) if p[i] < p[i + 1])] += 1
    assert euler == [1, 11, 11, 1] != T.zeile(4)["verteilung"]
    erwartet = {2: "1,3", 3: "26,0", 4: "72,1", 5: "95,0", 6: "99,6"}
    for k, p in erwartet.items():
        assert E.prozent(T.anteil_hoechstens(T.zeile(9)["verteilung"], k)) == p, k
    assert T.zeile(10)["verteilung"] == [1, 16795, 569794, 1604098, 1100902, 296326, 38281, 2521, 81, 1]
    _in_readme("1, 13, 9, 1", "1, 11, 11, 1", "1, 428, 2 332, 1 821, 421, 36, 1", "1, 4 861, 89 497, 167 449, 83 029, 16 465, 1 513, 64, 1", zeile="B9")
    _in_readme("1,3 %", "26,0 %", "72,1 %", "95,0 %", "99,6 %", zeile="B9")
    _in_readme("1, 16 795, 569 794, 1 604 098, 1 100 902, 296 326, 38 281, 2 521, 81, 1")


# --- B10 ----------------------------------------------------------------------------------------------------------------------------------
def test_b10_sofort_gegen_verzoegert():
    erwartet = {4: ("1,458", "2,417", "0,958", 9, "37,5", 3), 6: ("2,142", "3,140", "0,999", 278, "38,6", 5), 8: ("2,771", "3,770", "0,999", 15779, "39,1", 7),
                9: ("3,061", "4,059", "0,999", 142955, "39,4", 8), 10: ("3,337", "4,335", "0,998", 1431973, "39,5", 9)}
    for n, (s, lv, d, gleich, pg, gmax) in erwartet.items():
        z = T.zeile(n)
        assert E.zahl(T.mittel_sofort(n), 3) == s and E.zahl(T.mittel_lis(n), 3) == lv and E.zahl(T.mittel_lis(n) - T.mittel_sofort(n), 3) == d, n
        assert z["sofort"]["gleich_lis"] == gleich and E.prozent(Fraction(gleich, z["folgen"])) == pg and z["sofort"]["groesster_abstand"] == gmax, n
        _in_readme(s, lv, zeile="B10")
    assert sum(_fakt(n) for n in range(1, 11)) == 4037913 and sum(T.zeile(n)["sofort"]["verletzt"] for n in range(1, 11)) == 0
    assert all(T.zeile(n)["sofort"]["gleich1"] == math.comb(2 * n, n) // (n + 1) for n in range(1, 11))
    n = 10
    assert S.sofort_min(tuple(range(1, n + 1))) == 1 and P.lis_laenge(tuple(range(1, n + 1))) == n            # größter Abstand n - 1 bei 1, 2, ..., n
    assert T.zeile(10)["sofort"]["groesster_abstand"] == n - 1 and T.zeile(10)["sofort"]["abstand"][-1] == 1  # genau eine Folge mit dem größten Abstand
    exakt = [float(T.mittel_lis(n) - T.mittel_sofort(n)) for n in range(6, 11)]
    assert min(exakt) >= 0.998 and max(exakt) <= 1.000
    _in_readme("4 037 913", "0 Verletzungen", "1 431 973 von 3 628 800", "142 955", "15 779 von 40 320", "278 von 720", "9 von 24", zeile="B10")


# --- B11 ----------------------------------------------------------------------------------------------------------------------------------
def test_b11_sofort_hoechstens_zwei():
    assert [T.zeile(n)["sofort"]["le2"] for n in range(1, 11)] == [1, 2, 6, 23, 103, 513, 2760, 15741, 93944, 581303]
    assert sum(1 for p in permutations(range(1, 8)) if S.sofort_min(p) <= 2) == 2760
    _in_readme("1, 2, 6, 23, 103, 513, 2 760, 15 741", "93 944", "581 303", zeile="B11")


# --- B12 ----------------------------------------------------------------------------------------------------------------------------------
def test_b12_gleiche_zahl_andere_menge():
    m = {n: T.zeile(n)["mengen"] for n in range(4, 10)}
    assert [(m[n]["A2"], m[n]["B3"]) for n in range(4, 10)] == [(23, 23), (103, 103), (513, 513), (2760, 2761), (15741, 15767), (93944, 94359)]
    assert [(m[n]["nur_A2"], m[n]["nur_B3"]) for n in range(4, 7)] == [(1, 1), (14, 14), (137, 137)]
    assert [m[n]["A1_und_B2"] for n in range(4, 10)] == [7, 11, 16, 22, 29, 37]
    assert all(m[n]["A1"] == m[n]["B2"] == math.comb(2 * n, n) // (n + 1) for n in m)
    nur_a = [p for p in permutations(range(1, 5)) if S.sofort_min(p) <= 2 and P.lis_laenge(p) > 3]
    nur_b = [p for p in permutations(range(1, 5)) if P.lis_laenge(p) <= 3 and S.sofort_min(p) > 2]
    assert nur_a == [(1, 2, 3, 4)] and nur_b == [(2, 3, 4, 1)]
    assert S.sofort_min((1, 2, 3, 4)) == 1 and P.lis_laenge((1, 2, 3, 4)) == 4
    _in_readme("1 / 14 / 137", "2 760 gegen 2 761", "15 741 gegen 15 767", "93 944 gegen 94 359", "7, 11, 16, 22, 29, 37", zeile="B12")


# --- B13 ----------------------------------------------------------------------------------------------------------------------------------
def test_b13_abhaengigkeit_des_abstands_von_n():
    erwartet = {"10": ("1,001", "0,012", 8000), "12": ("0,997", "0,012", 8000), "14": ("0,991", "0,012", 8000), "16": ("0,971", "0,012", 8000), "20": ("0,974", "0,017", 4000)}
    for n, (abstand, se, anzahl) in erwartet.items():
        r = T.abstand_n()[n]
        assert r["anzahl"] == anzahl and r["seed"] == 16000 + int(n) and r["offen"] == 0
        d = r["summe_lis"] - r["summe_sofort"]
        assert E.zahl(d / anzahl, 3) == abstand and E.zahl(E.abstand_se(d, r["summe_abstand2"], anzahl), 3) == se, n
        _in_readme(abstand, zeile="B13")
    # Neu-Rechnung als Band (drei Standardfehler um den Wert der Tabelle)
    for n in (10, 20):
        r = T.abstand_n()[str(n)]
        neu = M.stichprobe(n, None, r["anzahl"], 16000 + n, mit_sofort=True)
        d_tab = (r["summe_lis"] - r["summe_sofort"]) / r["anzahl"]
        d_neu = (neu["summe_lis"] - neu["summe_sofort"]) / neu["anzahl"]
        assert abs(d_neu - d_tab) <= 3 * E.abstand_se(r["summe_lis"] - r["summe_sofort"], r["summe_abstand2"], r["anzahl"])
    _in_readme("0,012 bis 0,017", "n = 6 bis 10 zwischen 0,998 und 1,000", "0,971 bis 1,001 in der Tabelle", "0,995 bis 1,005 in der unabhängigen Stichprobe", zeile="B13")


# --- B14 ----------------------------------------------------------------------------------------------------------------------------------
def min_stapel_mit_hoehe(a, h):
    """Kleinste Zahl fallender Stapel der Höhe höchstens h (Brute Force über alle Zuordnungen, Rückverfolgung)."""
    n = len(a)
    best = [n]
    spitzen: list = []
    hoehen: list = []

    def rek(i):
        if len(spitzen) >= best[0]:
            return
        if i == n:
            best[0] = len(spitzen)
            return
        for b in range(len(spitzen)):
            if a[i] < spitzen[b] and hoehen[b] < h:
                alt = spitzen[b]
                spitzen[b] = a[i]
                hoehen[b] += 1
                rek(i + 1)
                spitzen[b] = alt
                hoehen[b] -= 1
        spitzen.append(a[i])
        hoehen.append(1)
        rek(i + 1)
        spitzen.pop()
        hoehen.pop()

    rek(0)
    return best[0]


def test_b14_hoehengrenze_ist_weder_lis_noch_max_lis_n_durch_h():
    n, h = 6, 2
    gleich_lis = gleich_max = 0
    for p in permutations(range(1, n + 1)):
        m = min_stapel_mit_hoehe(p, h)
        gleich_lis += m == P.lis_laenge(p)
        gleich_max += m == max(P.lis_laenge(p), math.ceil(n / h))
    assert (gleich_lis, gleich_max) == (483, 612)
    assert min_stapel_mit_hoehe((1, 2, 3, 4, 5, 6), 6) == 6 and min_stapel_mit_hoehe((6, 5, 4, 3, 2, 1), 6) == 1 and min_stapel_mit_hoehe((6, 5, 4, 3, 2, 1), 2) == 3
    _in_readme("483 von 720", "612 von 720", zeile="B14")
    assert "483 von 720" in X.GRENZEN and "612 gleich max(LIS, ⌈n/H⌉)" in X.GRENZEN


# --- Text in App und README ---------------------------------------------------------------------------------------------------------------
def test_modell_hinweis_steht_in_app_und_readme_gleichlautend():
    assert X.MODELL_HINWEIS in README
    assert "Es ist ein **Modell, kein Fall aus der Praxis**" in README and "keine reale Ankunftsfolge" in README


def test_grenzen_tabelle_der_app_nennt_nur_zahlen_der_readme():
    for text in ("3 628 800", "3,337", "4,335", "483 von 720", "2 062 von 2 520"):
        assert text in X.GRENZEN and text in README, text


def test_alle_befund_zeilen_haben_einen_test():
    nummern = sorted(ZEILE_B, key=lambda b: int(b[1:]))
    assert nummern == [f"B{i}" for i in range(1, 16)]
    quelle = (Path(__file__)).read_text(encoding="utf-8")
    for b in nummern[:-1]:                                    # B15 steht in tests/test_presets.py
        assert f"def test_b{int(b[1:]):02d}_" in quelle, b
