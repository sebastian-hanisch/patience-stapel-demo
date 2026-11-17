"""Randfälle der Analyse und der Presets: n = 0, 1, 2, Gleichstand, Obergrenzen, ungültige Eingaben, Regler an den Rändern."""

import pat_constants as C
import pat_evaluation as E
import pat_presets as PR
from pat_model import stichprobe


def test_leere_folge_einzelner_container_und_zwei_container():
    a = E.analyse(E.Settings(folge=""))
    assert a.art == "perm" and a.folge == () and a.anzahl_je_regel["erster"] == 0 and a.lis == 0 and a.sofort == (0, ())
    a = E.analyse(E.Settings(folge="1"))
    assert a.stapel == [[1]] and a.lis == 1 and a.sofort[0] == 1 and a.abholen == [1]
    a = E.analyse(E.Settings(folge="2, 1"))
    assert a.lis == 1 and a.lds == 2 and len(a.stapel) == 1
    a = E.analyse(E.Settings(folge="1, 2"))
    assert a.lis == 2 and a.lds == 1 and len(a.stapel) == 2 and a.sofort[0] == 1


def test_gleichstand_wort_und_alle_gleich():
    a = E.analyse(E.Settings(folge="1, 1, 1, 1"))
    assert a.art == "wort" and a.gleichstand == (1, 4)       # teilen: ein Stapel (streng wachsend: 1); verschieden: vier (nicht fallend: 4)
    a = E.analyse(E.Settings(folge="1, 2, 2, 3", gleiche="verschieden"))
    assert a.art == "wort" and len(a.stapel) == 4 and a.lis == 4
    a = E.analyse(E.Settings(folge="1, 2, 2, 3", gleiche="teilen"))
    assert len(a.stapel) == 3 and a.lis == 3


def test_ungueltige_eingabe_gibt_meldung_statt_zahl():
    a = E.analyse(E.Settings(folge="1, 3, 5"))
    assert a.art == "fehler" and "fehlende Ränge 2, 4" in a.meldung and a.stapel == [] and a.sofort is None


def test_obergrenzen_der_laenge():
    a = E.analyse(E.Settings(quelle="u", n=C.N_MAX, seed=3))
    assert len(a.folge) == 30 and a.sofort is None and a.lis >= 1                  # n = 30: LIS gerechnet, sofort nicht
    a = E.analyse(E.Settings(quelle="u", n=24, seed=3))
    assert a.sofort is not None                                                      # n = 24: sofort gerechnet
    a = E.analyse(E.Settings(quelle="v", n=C.N_MIN, d=C.D_OPTIONEN[-1], seed=0))
    assert len(a.folge) == 3


def test_schritt_praefix_gibt_dieselben_stapel_wie_die_ganze_folge():
    a = E.analyse(E.Settings())
    for s in range(len(a.folge) + 1):
        for regel in ("erster", "groesste"):
            ganz = E.stapel_bis(a.folge, len(a.folge), regel)
            teil = E.stapel_bis(a.folge, s, regel)
            # die Regeln legen Container einzeln: jeder Stapel nach s Containern ist der Anfang desselben Stapels der ganzen Folge
            assert len(teil) <= len(ganz) and all(ganz[j][: len(t)] == t for j, t in enumerate(teil))
            assert sorted(x for st in teil for x in st) == sorted(a.folge[:s])
    assert E.stapel_bis(a.folge, 0, "erster") == []


def test_stichprobe_mit_null_folgen_und_ohne_container():
    r = stichprobe(5, None, 0, 1, mit_sofort=True)
    assert r["verteilung"] == {} and r["summe_lis"] == 0
    r = stichprobe(0, None, 3, 1, mit_sofort=True)
    assert r["verteilung"] == {0: 3} and r["summe_lis"] == 0


def test_permalink_begrenzt_und_weist_unbrauchbares_ab():
    spec = PR.SETTING_SPECS["n_zufall"]
    assert PR.begrenzen(spec, "500") == C.N_MAX and PR.begrenzen(spec, "-3") == C.N_MIN and PR.begrenzen(spec, "abc") is None
    assert PR.begrenzen(PR.SETTING_SPECS["quelle_sel"], "u") == "u" and PR.begrenzen(PR.SETTING_SPECS["quelle_sel"], "xyz") is None
    assert PR.begrenzen(PR.SETTING_SPECS["d_faden"], "uniform") == "uniform" and PR.begrenzen(PR.SETTING_SPECS["d_faden"], "4") == 4.0
    assert PR.begrenzen(PR.SETTING_SPECS["d_faden"], "3") is None
    assert len(PR.begrenzen(PR.SETTING_SPECS["folge_text"], "1," * 500)) == 200
