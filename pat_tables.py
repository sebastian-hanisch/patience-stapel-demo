"""Liest die eingefrorenen, vorgerechneten Tabellen `pat_tables.json` (Aufzählung aller n! Folgen bis n = 10, Zähleinheit: Folge).

Erzeugt von `tools/pat_make_tables.py` (Prüfung mit `--check`). In der App und in der README heißen diese Zahlen „vorgerechnet“."""

import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

DATEI = Path(__file__).with_name("pat_tables.json")


@lru_cache(maxsize=1)
def tabellen() -> dict:
    return json.loads(DATEI.read_text(encoding="utf-8"))


def zeile(n: int):
    """Die Zählungen für alle n! Folgen der Länge n, oder None, wenn n nicht aufgezählt ist."""
    return tabellen()["n"].get(str(n))


def anteil_hoechstens(verteilung, k: int) -> Fraction:
    """Anteil der Folgen mit höchstens k Stapeln, aus der Verteilung (Zahl der Folgen mit genau 1, 2, ... Stapeln)."""
    return Fraction(sum(verteilung[:k]), sum(verteilung))


def mittel_lis(n: int) -> Fraction:
    z = zeile(n)
    return Fraction(z["summe_lis"], z["folgen"])


def mittel_sofort(n: int) -> Fraction:
    z = zeile(n)
    return Fraction(z["sofort"]["summe_sofort"], z["folgen"])


def modell_v() -> dict:
    return tabellen()["modell_v_n10"]


def abstand_n() -> dict:
    return tabellen()["abstand_n"]
