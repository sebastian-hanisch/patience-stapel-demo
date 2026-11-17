"""Gemeinsame Einstellungen: Wurzelordner im Importpfad, Marker `slow` für Aufzählungen bis n = 9 (`pytest -m slow`)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: Aufzählung aller Folgen bis n = 9 oder lange Neu-Rechnung (rund 1 bis 3 Minuten); mit `pytest -m slow` ausführen")


@pytest.fixture
def handbeispiel():
    """Die Mini-Instanz, an der jede Einheit von Hand geprüft wird: Ankunftsfolge (1, 3, 5, 2, 4) der Abholränge.

    Von Hand: 1 neuer Stapel [1]; 3 neuer Stapel [3]; 5 neuer Stapel [5]; 2 kommt auf den ersten Stapel mit größerer Spitze (3); 4 auf den ersten mit
    größerer Spitze (5): [[1], [3, 2], [5, 4]], 3 Stapel. Die längsten wachsenden Teilfolgen haben die Länge 3 ((1, 2, 4), (1, 3, 4), (1, 3, 5))."""
    return (1, 3, 5, 2, 4)
