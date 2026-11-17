"""Verdikte und Eingabe (reine Funktionen in pat_evaluation) an von Hand gesetzten Werten: jede Schwelle der Art und jede Zahl im Text steht hier."""

import pytest

import pat_evaluation as E
import pat_model as M


def _a(folge="1, 3, 5, 2, 4", **kw):
    return E.analyse(E.Settings(folge=folge, **kw))


# --- Formatierung --------------------------------------------------------------------------------------------------------------------------
def test_zahlen_deutsch_mit_komma_und_leerzeichen():
    assert E.ganz(362880) == "362 880" and E.ganz(5) == "5" and E.ganz(3628800) == "3 628 800"
    assert E.zahl(3.3367, 3) == "3,337" and E.zahl(1234.5, 1) == "1 234,5" and E.zahl(0.5, 1) == "0,5"
    assert E.prozent(0.72449) == "72,4" and E.folge_text((1, 3, 5)) == "(1, 3, 5)"


# --- Eingabe -------------------------------------------------------------------------------------------------------------------------------
def test_parse_folge_gueltige_und_ungueltige_eingaben():
    assert E.parse_folge("1, 3, 5, 2, 4") == ((1, 3, 5, 2, 4), None)
    assert E.parse_folge("2 1;3") == ((2, 1, 3), None)
    assert E.parse_folge("") == ((), None) and E.parse_folge("   ") == ((), None)
    assert E.parse_folge("1, 2, 2, 3") == ((1, 2, 2, 3), None)                       # Gleichstände (Zielgruppen) sind erlaubt
    werte, meldung = E.parse_folge("1, 3, 5")
    assert werte is None and "fehlende Ränge 2, 4" in meldung
    werte, meldung = E.parse_folge("1, x, 3")
    assert werte is None and "„x“" in meldung
    assert E.parse_folge("0, 1")[0] is None and E.parse_folge("-1, 1")[0] is None and E.parse_folge("1.5")[0] is None
    assert E.parse_folge(", ".join(str(i) for i in range(1, 32)))[0] is None        # 31 Container: zu lang
    assert E.parse_folge(", ".join(str(i) for i in range(1, 31)))[0] is not None    # 30 Container: erlaubt
    assert E.parse_folge("1, 100")[0] is None


# --- Kernfrage 1 ----------------------------------------------------------------------------------------------------------------------------
def test_verdikt_patience_erster_passender_ist_optimal():
    kind, text = E.verdict_patience(_a(), "erster")
    assert kind == "success"
    assert "(1, 3, 5, 2, 4): „erster passender“ legt **3** Stapel" in text and "Länge **3**" in text
    assert "größte Spitze 4" in text and "ganz rechts 4" in text
    assert "Alle 120 Folgen mit n = 5: erster passender legt in 120 von 120 genau LIS Stapel" in text


def test_verdikt_patience_groesste_spitze_legt_einen_stapel_zu_viel():
    kind, text = E.verdict_patience(_a(), "groesste")
    assert kind == "warning" and "legt **4** Stapel" in text and "1 Stapel mehr als nötig" in text


def test_verdikt_patience_ohne_aufzaehlung_ab_n_10():
    kind, text = E.verdict_patience(_a("7, 2, 8, 1, 3, 4, 10, 6, 9, 5"), "erster")
    assert kind == "success" and "**5** Stapel" in text and "Länge **5**" in text and "1, 3, 4, 6, 9" in text
    assert "Für n = 10 ist nicht aufgezählt" in text


def test_verdikt_patience_gleichstaende_fehler_und_leere_folge():
    kind, text = E.verdict_patience(_a("1, 2, 2, 3"), "erster")
    assert kind == "info" and "genügen **3** Stapel" in text and "sind es **4**" in text
    kind, text = E.verdict_patience(_a("1, 3, 5"), "erster")
    assert kind == "warning" and "fehlende Ränge 2, 4" in text
    kind, text = E.verdict_patience(_a(""), "erster")
    assert kind == "info" and "Leere Folge" in text


# --- Kernfrage 2 ----------------------------------------------------------------------------------------------------------------------------
def test_verdikt_richtung_folge():
    kind, text = E.verdict_richtung_folge(_a())
    assert kind == "warning" and "brauchen **3** Stapel (LIS), wachsende **2** (LDS)" in text and "**3** blockierende Container" in text
    kind, text = E.verdict_richtung_folge(_a("2, 1, 3"))     # LIS = 2, LDS = 2
    assert kind == "info" and "hier gleich viele" in text and "nicht jede Folge ist so" in text and "72,4 %" in text
    kind, text = E.verdict_richtung_folge(_a("1"))           # n = 1: LIS = LDS = 1, der Satz „unterscheiden sich oft“ wäre falsch
    assert kind == "info" and "bei einem einzigen Container sind beide Zahlen gleich" in text and "unterscheiden sich" not in text
    assert E.verdict_richtung_folge(_a("1, 2, 2, 3"))[0] == "info"
    kind, text = E.verdict_richtung_folge(_a("3, 2, 1"))     # LIS = 1, LDS = 3: wachsende Stapel [3], [2], [1] haben keinen Blocker
    assert kind == "warning" and "keinen blockierenden Container" in text


# --- Kernfrage 3 ----------------------------------------------------------------------------------------------------------------------------
def test_verdikt_faden_folge_sortiert_umkehr_und_handbeispiel():
    kind, text = E.verdict_faden_folge(_a("1, 2, 3, 4, 5, 6, 7, 8"))
    assert kind == "success" and "**8** Stapel, sofort (zwischendurch ausgeben) **1** Stapel" in text and "spart 7" in text
    kind, text = E.verdict_faden_folge(_a("8, 7, 6, 5, 4, 3, 2, 1"))
    assert kind == "info" and "beide **1** Stapel" in text
    kind, text = E.verdict_faden_folge(_a())
    assert kind == "success" and "**3** Stapel, sofort (zwischendurch ausgeben) **2** Stapel" in text and "spart 1" in text


def test_verdikt_faden_folge_ueber_der_obergrenze_meldet_nicht_gerechnet():
    kind, text = E.verdict_faden_folge(E.analyse(E.Settings(quelle="u", n=30, seed=5)))
    assert kind == "warning" and "nicht gerechnet" in text and "n = 24" in text


# --- Experimente ----------------------------------------------------------------------------------------------------------------------------
def test_verdikt_regeln_n_8():
    kind, text = E.verdict_regeln(8)
    assert kind == "info"
    assert "40 320 von 40 320 Folgen dieselben Stapel (Befund: keiner)" in text
    assert "14 993 Folgen (37,2 %)" in text and "12 886 (32,0 %)" in text and "7 793 (19,3 %, einzelne Ziehung mit Zufalls-Seed 11)" in text


def test_verdikt_richtung_tabelle():
    kind, text = E.verdict_richtung_tabelle()
    assert kind == "info" and "362 880 Folgen mit n = 9" in text and "4,059" in text and "72,4 %" in text
    assert "LIS im Mittel 9,40, LDS 1,48" in text and "Zufalls-Seed 15000" in text


def test_verdikt_verteilung_exakt_n_9_und_n_4():
    _, text = E.verdict_verteilung_exakt(9)
    assert "1 / 4 861 / 89 497 / 167 449 / 83 029 / 16 465 / 1 513 / 64 / 1 Folgen brauchen 1 bis 9 Stapel" in text and "72,1 % kommen mit höchstens 4 Stapeln aus" in text
    _, text = E.verdict_verteilung_exakt(4)
    assert "1 / 13 / 9 / 1 Folgen" in text and "Eulersche Zeile 1, 11, 11, 1" in text
    assert "Eulersche" not in E.verdict_verteilung_exakt(5)[1]


def test_verteilung_median():
    assert E.verteilung_median([1, 13, 9, 1]) == 2          # 14 von 24 kommen mit höchstens 2 Stapeln aus: mehr als die Hälfte
    assert E.verteilung_median([1]) == 1
    assert E.verteilung_median([1, 1]) == 1                 # genau die Hälfte reicht


def test_verdikt_verteilung_stichprobe_nennt_modell_und_exakten_mittelwert():
    r = M.stichprobe(9, None, 200, 7)
    _, text = E.verdict_verteilung_stichprobe(r, 9)
    assert "200 Zufallsfolgen aus Modell U, n = 9, Zufalls-Seed 7" in text and "Exakt (alle 362 880 Folgen): 4,059" in text
    r = M.stichprobe(12, 2.0, 100, 7)
    _, text = E.verdict_verteilung_stichprobe(r, None)
    assert "Modell V (ausgedacht, D = 2,0)" in text and "Exakt" not in text
    _, text = E.verdict_verteilung_stichprobe(M.stichprobe(15, None, 100, 7), None)
    assert "nicht aufgezählt" in text


def test_verdikt_faden_exakt_n_10_und_n_4():
    _, text = E.verdict_faden_exakt(10)
    assert "Alle 3 628 800 Folgen mit n = 10: sofort höchstens so viele Stapel wie verzögert (0 Verletzungen)" in text
    assert "3,337 gegen 4,335" in text and "gleich viele in 39,5 %" in text and "größter Abstand 9" in text and "1 gegen 10 Stapel" in text
    _, text = E.verdict_faden_exakt(4)
    assert "1,458 gegen 2,417" in text and "größter Abstand 3" in text and "gleich viele in 37,5 %" in text and "1 gegen 4 Stapel" in text


def test_verdikt_faden_stichprobe():
    r = M.stichprobe(12, 0.5, 100, 3, mit_sofort=True)
    kind, text = E.verdict_faden_stichprobe(r)
    assert kind == "info" and "100 Zufallsfolgen aus Modell V (ausgedacht, D = 0,5), n = 12, Zufalls-Seed 3" in text and "0 Folgen mit sofort über verzögert" in text
    kind, text = E.verdict_faden_stichprobe(M.stichprobe(30, None, 5, 3, mit_sofort=True))
    assert kind == "warning" and "nicht gerechnet" in text
    r = M.stichprobe(10, None, 5, 3, mit_sofort=True)
    r["offen"] = r["anzahl"]
    assert E.verdict_faden_stichprobe(r)[0] == "warning"


def test_verdikt_mengen_n_7_gleiche_zahl_andere_menge():
    _, text = E.verdict_mengen(7)
    assert "2 760 Folgen gegen 2 761" in text and "nur in A₂ (zwei parallele Stapel sortieren) liegen 1 150" in text and "nur in B₃ (blockierfrei in 3 fallenden Stapeln) 1 151" in text
    _, text = E.verdict_mengen(4)
    assert "beide Mengen haben 23 Folgen" in text and "liegen 1," in text


def test_abstand_standardfehler_von_hand():
    # Abstände 0, 1, 1, 2: Summe 4, Quadratsumme 6, n = 4: Mittel 1, Varianz 6/4 - 1 = 0,5, Standardfehler sqrt(0,5 / 4)
    assert E.abstand_se(4, 6, 4) == pytest.approx((0.5 / 4) ** 0.5)
    assert E.abstand_se(0, 0, 10) == 0.0
