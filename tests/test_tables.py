"""Die eingefrorene Tabelle pat_tables.json: Aufbau, Neu-Rechnung (n <= 7 im Normalbetrieb, n <= 8 mit `pytest -m slow`), Invarianten."""

import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

import pat_tables as T

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL / "tools"))
import pat_make_tables as MK  # noqa: E402


def test_datei_hat_n_bis_10_und_stimmt_mit_der_summe_n_fakultaet_ueberein():
    assert sorted(int(k) for k in T.tabellen()["n"]) == list(range(1, 11))
    for n in range(1, 11):
        z = T.zeile(n)
        assert z["folgen"] == math.factorial(n) == sum(z["verteilung"]) == sum(z["sofort"]["abstand"])


def test_neu_rechnung_gleich_datei_bis_n_7():
    for n in range(1, 8):
        assert MK.rechne_n(n) == T.zeile(n), n


@pytest.mark.slow
def test_neu_rechnung_gleich_datei_bis_n_8_mit_dem_werkzeug():
    erg = subprocess.run([sys.executable, "-X", "utf8", str(WURZEL / "tools" / "pat_make_tables.py"), "--check"], capture_output=True, text=True, encoding="utf-8", timeout=600)
    assert erg.returncode == 0 and "alles gleich" in erg.stdout, erg.stdout + erg.stderr


def test_invarianten_der_zeilen():
    for n in range(1, 11):
        z = T.zeile(n)
        s = z["sofort"]
        assert z["summe_lis"] == z["summe_lds"]                                  # Spiegeln der Folge: gleiche Verteilung, gleiche Summe
        assert s["verletzt"] == 0                                                # sofort <= verzögert in jeder Folge
        assert s["gleich1"] == math.comb(2 * n, n) // (n + 1)                    # sofort = 1 genau die Catalan-Zahl
        assert s["abstand"][0] == s["gleich_lis"] and s["groesster_abstand"] == len(s["abstand"]) - 1
        assert s["summe_sofort"] + sum(k * c for k, c in enumerate(s["abstand"])) == z["summe_lis"]      # Summe sofort + Summe Abstände = Summe LIS
        m = z["mengen"]
        assert m["A1"] == m["B2"] == s["gleich1"]
        assert m["A2"] - m["A2_und_B3"] == m["nur_A2"] and m["B3"] - m["A2_und_B3"] == m["nur_B3"]
        assert s["le2"] == m["A2"] and m["B3"] == sum(z["verteilung"][:3])
        if 2 <= n <= 9:
            r = z["regeln"]
            assert r["erster_gleich_engste"] == r["erster_gleich_lis"] == z["folgen"]
            assert 0 <= r["zufall"] <= z["folgen"] and r["summe_mehr_groesste"] >= r["groesste"]       # jede betroffene Folge hat mindestens einen Stapel zu viel


def test_hilfsfunktionen():
    assert T.anteil_hoechstens([1, 13, 9, 1], 2) == Fraction(14, 24)
    assert T.mittel_lis(4) == Fraction(58, 24) and T.mittel_sofort(4) == Fraction(35, 24)
    assert T.zeile(11) is None


def test_datei_ist_gueltiges_json_mit_modell_v_und_abstand():
    daten = json.loads(T.DATEI.read_text(encoding="utf-8"))
    assert set(daten["modell_v_n10"]) == {"0.5", "1.0", "2.0", "4.0", "8.0", "16.0", "uniform"}
    assert set(daten["abstand_n"]) == {"10", "12", "14", "16", "20"}
