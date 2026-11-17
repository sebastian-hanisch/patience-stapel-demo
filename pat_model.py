"""Das ausgedachte Ankunftsmodell (ein Modell, keine reale Ankunftsfolge) und Stichproben daraus.

**Modell U:** alle n! Ankunftsfolgen gleich wahrscheinlich (Fisher-Yates mit ganzzahligem SplitMix64).
**Modell V:** Container i kommt zur Zeit i (in Ankunftsabständen) und bleibt eine exponentialverteilte Zeit mit dem Mittel D; der Abholrang ist die
Reihenfolge der Abfahrtszeiten (nur diese Rangfolge geht ein, keine Zeiten). Kleines D heißt: die Container werden fast in der Reihenfolge abgeholt,
in der sie ankommen; großes D: beinahe beliebig durcheinander (Modell U ist der Grenzfall D gegen unendlich).
Es gibt keine Hafen-, Bahnhofs- oder Bestandszahl dahinter; die Quellenlage kennt keine reale Ankunftsfolge. Eigene Fassung dieses Repos."""

from collections import Counter

from pat_patience import lds_laenge, lis_laenge
from pat_rng import SplitMix64
from pat_sofort import SOFORT_N_MAX, sofort_min

D_WERTE = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)


def rang_aus_zeiten(abfahrten) -> list:
    """Abholrang (1 = zuerst geholt) aus den Abfahrtszeiten je Container in Ankunftsreihenfolge; bei gleicher Zeit zählt die frühere Ankunft zuerst."""
    reihenfolge = sorted(range(len(abfahrten)), key=lambda i: (abfahrten[i], i))
    rang = [0] * len(abfahrten)
    for r, i in enumerate(reihenfolge, 1):
        rang[i] = r
    return rang


def modell_folge(rng: SplitMix64, n: int, D) -> list:
    """Eine Ankunftsfolge aus Modell U (D = None) oder Modell V (Verweilzeit-Mittel D > 0)."""
    if D is None:
        p = list(range(1, n + 1))
        rng.shuffle(p)
        return p
    return rang_aus_zeiten([i + rng.expovariate(D) for i in range(n)])


def stichprobe(n: int, D, anzahl: int, seed: int, mit_sofort: bool = False) -> dict:
    """Kennzahlen aus `anzahl` Zufallsfolgen (Zähleinheit: Zufallsfolge). Rückgabe: Verteilung der LIS (Stapelzahl), Summen von LIS und LDS,
    Zahl der Folgen mit LIS != LDS und, mit mit_sofort (nur n <= SOFORT_N_MAX), Summe von sofort, Zahl der Folgen mit sofort = LIS und sofort = 1,
    Verteilung des Abstands LIS - sofort und die Summe der Abstandsquadrate (für den Standardfehler). Zahl nicht gerechneter Folgen in 'offen'."""
    rng = SplitMix64(seed)
    verteilung: Counter = Counter()
    summe_lis = summe_lds = ungleich = 0
    summe_sofort = gleich = ein_stapel = offen = 0
    abstand: Counter = Counter()
    summe_abstand2 = 0
    for _ in range(anzahl):
        p = modell_folge(rng, n, D)
        lis = lis_laenge(p)
        lds = lds_laenge(p)
        verteilung[lis] += 1
        summe_lis += lis
        summe_lds += lds
        ungleich += lis != lds
        if mit_sofort and n <= SOFORT_N_MAX:
            s = sofort_min(p)
            if s is None:
                offen += 1
                continue
            summe_sofort += s
            gleich += s == lis
            ein_stapel += s == 1
            abstand[lis - s] += 1
            summe_abstand2 += (lis - s) ** 2
    return {
        "n": n, "D": D, "anzahl": anzahl, "seed": seed, "verteilung": dict(verteilung), "summe_lis": summe_lis, "summe_lds": summe_lds,
        "ungleich": ungleich, "summe_sofort": summe_sofort, "gleich": gleich, "ein_stapel": ein_stapel, "abstand": dict(abstand),
        "summe_abstand2": summe_abstand2, "offen": offen,
    }
