"""Rechnet die eingefrorenen Tabellen `pat_tables.json` vor (Aufzählung aller n! Folgen, Zähleinheit: Folge) und prüft sie.

    python tools/pat_make_tables.py --schreiben      # rechnet n <= 10 (rund 3 bis 6 Minuten) und schreibt pat_tables.json
    python tools/pat_make_tables.py --check          # rechnet n <= 8 neu (wenige Sekunden) und vergleicht mit der Datei
    python tools/pat_make_tables.py --check --voll   # wie --check, aber bis n = 10 (nur vor einem Release)

Je n stehen in der Datei: die Verteilung der Stapelzahl (Zahl der Folgen mit genau k Stapeln), die Zählungen der gierigen Regeln (erster passender, engste
Passung, größte Spitze, ganz rechts, Zufallswahl mit Zufalls-Seed 11; n <= 9), LIS != LDS, die Summen von LIS und LDS, „sofort“ gegen „verzögert“ (Summen,
Verteilung des Abstands, Folgen mit sofort = LIS, sofort <= 2, sofort = 1) und die Mengenvergleiche A_k (sofort <= k) gegen B_k (LIS <= k). Dazu Modell V
(n = 10, 2000 Folgen je D) und die Abhängigkeit des Abstands von n im Modell U (Stichprobe). Alles mit festen Zufalls-Seeds aus dem ganzzahligen SplitMix64."""

import argparse
import json
import math
import sys
import time
from collections import Counter
from itertools import permutations
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

import pat_model as M  # noqa: E402
import pat_patience as P  # noqa: E402
import pat_sofort as S  # noqa: E402
from pat_rng import SplitMix64  # noqa: E402

DATEI = WURZEL / "pat_tables.json"
N_MAX_STANDARD = 8
N_MAX_VOLL = 10
N_MAX_REGELN = 9          # die Regel-Zählungen laufen nur bis n = 9 (n = 10 dauert ohne neuen Befund zu lang)
ZUFALL_SEED_REGELN = 11   # Zufalls-Seed der Zufallswahl
SEED_MODELL_V = 15000     # Zufalls-Seed 15000 + Index von D
SEED_ABSTAND_N = 16000    # Zufalls-Seed 16000 + n
D_ALLE = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, None)
N_ABSTAND = (10, 12, 14, 16, 20)


def rechne_n(n: int) -> dict:
    """Alle Zählungen für genau die n! Folgen der Länge n."""
    verteilung = [0] * n
    summe_lis = summe_lds = ungleich = 0
    summe_sofort = gleich = verletzt = z_sofort_le2 = z_sofort_1 = 0
    abstand: Counter = Counter()
    a1 = b2 = a1b2 = a2 = b3 = a2b3 = nur_a = nur_b = 0
    mit_regeln = 2 <= n <= N_MAX_REGELN
    erster_gleich_engste = opt_erster = groesste = rechts = zufall = summe_mehr_groesste = 0
    rng = SplitMix64(ZUFALL_SEED_REGELN)
    for p in permutations(range(1, n + 1)):
        lis = P.lis_laenge(p)
        lds = P.lds_laenge(p)
        verteilung[lis - 1] += 1
        summe_lis += lis
        summe_lds += lds
        ungleich += lis != lds
        s = S.sofort_min(p)
        summe_sofort += s
        gleich += s == lis
        verletzt += s > lis
        abstand[lis - s] += 1
        z_sofort_le2 += s <= 2
        z_sofort_1 += s == 1
        x1, y2, x2, y3 = s <= 1, lis <= 2, s <= 2, lis <= 3
        a1 += x1
        b2 += y2
        a1b2 += x1 and y2
        a2 += x2
        b3 += y3
        a2b3 += x2 and y3
        nur_a += x2 and not y3
        nur_b += y3 and not x2
        if mit_regeln:
            e = P.stapel_legen(p, "erster")
            erster_gleich_engste += e == P.stapel_legen(p, "engste")
            opt_erster += len(e) == lis
            g = len(P.stapel_legen(p, "groesste"))
            if g > lis:
                groesste += 1
                summe_mehr_groesste += g - lis
            rechts += len(P.stapel_legen(p, "rechts")) > lis
            zufall += len(P.stapel_legen(p, "zufall", rng)) > lis
    groesster = max(abstand)
    erg = {
        "folgen": math.factorial(n),
        "verteilung": verteilung,
        "summe_lis": summe_lis, "summe_lds": summe_lds, "lis_ungleich_lds": ungleich,
        "sofort": {
            "summe_sofort": summe_sofort, "gleich_lis": gleich, "verletzt": verletzt, "le2": z_sofort_le2, "gleich1": z_sofort_1,
            "groesster_abstand": groesster, "abstand": [abstand[k] for k in range(groesster + 1)],
        },
        "mengen": {"A1": a1, "B2": b2, "A1_und_B2": a1b2, "A2": a2, "B3": b3, "A2_und_B3": a2b3, "nur_A2": nur_a, "nur_B3": nur_b},
    }
    if mit_regeln:
        erg["regeln"] = {
            "erster_gleich_engste": erster_gleich_engste, "erster_gleich_lis": opt_erster, "groesste": groesste, "rechts": rechts,
            "zufall": zufall, "summe_mehr_groesste": summe_mehr_groesste,
        }
    return erg


def rechne_modell_v(n: int = 10, anzahl: int = 2000) -> dict:
    """Modell V (und Modell U als „uniform“) bei n = 10, 2000 Folgen je D, Zufalls-Seeds 15000 + Index."""
    erg = {}
    for idx, D in enumerate(D_ALLE):
        r = M.stichprobe(n, D, anzahl, SEED_MODELL_V + idx, mit_sofort=True)
        erg["uniform" if D is None else str(D)] = {
            "seed": r["seed"], "anzahl": anzahl, "summe_lis": r["summe_lis"], "summe_lds": r["summe_lds"], "summe_sofort": r["summe_sofort"],
            "ein_stapel": r["ein_stapel"], "lis_gleich_lds": anzahl - r["ungleich"], "sofort_kleiner": anzahl - r["gleich"],
        }
    return erg


def rechne_abstand_n() -> dict:
    """Abstand LIS - sofort im Modell U in Abhängigkeit von n (Stichprobe, Zufalls-Seed 16000 + n)."""
    erg = {}
    for n in N_ABSTAND:
        anzahl = 8000 if n <= 16 else 4000
        r = M.stichprobe(n, None, anzahl, SEED_ABSTAND_N + n, mit_sofort=True)
        erg[str(n)] = {
            "seed": r["seed"], "anzahl": anzahl, "summe_lis": r["summe_lis"], "summe_sofort": r["summe_sofort"], "summe_abstand2": r["summe_abstand2"],
            "offen": r["offen"],
        }
    return erg


def rechne(nmax: int, mit_modell: bool) -> dict:
    daten = {"version": 1, "n": {}}
    for n in range(1, nmax + 1):
        t0 = time.time()
        daten["n"][str(n)] = rechne_n(n)
        print(f"n = {n}: fertig in {time.time() - t0:.1f} s", flush=True)
    if mit_modell:
        daten["modell_v_n10"] = rechne_modell_v()
        daten["abstand_n"] = rechne_abstand_n()
    return daten


def schreiben() -> None:
    daten = rechne(N_MAX_VOLL, True)
    DATEI.write_text(json.dumps(daten, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"geschrieben: {DATEI.name}")


def pruefen(nmax: int) -> int:
    gespeichert = json.loads(DATEI.read_text(encoding="utf-8"))
    neu = rechne(nmax, nmax >= N_MAX_VOLL)
    fehler = 0
    for n, zeile in neu["n"].items():
        if zeile != gespeichert["n"][n]:
            fehler += 1
            print(f"ABWEICHUNG bei n = {n}")
    for schluessel in ("modell_v_n10", "abstand_n"):
        if schluessel in neu and neu[schluessel] != gespeichert[schluessel]:
            fehler += 1
            print(f"ABWEICHUNG bei {schluessel}")
    print("PRÜFUNG: " + ("alles gleich" if not fehler else f"{fehler} Abweichungen"))
    return fehler


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--schreiben", action="store_true", help="n <= 10 rechnen und pat_tables.json schreiben")
    ap.add_argument("--check", action="store_true", help="neu rechnen und mit der Datei vergleichen (n <= 8, mit --voll n <= 10)")
    ap.add_argument("--voll", action="store_true", help="mit --check: bis n = 10 und mit den Stichproben")
    args = ap.parse_args()
    if args.schreiben:
        schreiben()
    elif args.check:
        sys.exit(1 if pruefen(N_MAX_VOLL if args.voll else N_MAX_STANDARD) else 0)
    else:
        ap.print_help()
