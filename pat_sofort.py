"""„Sofort“: kleinste Zahl paralleler Stapel, wenn zwischendurch ausgegeben werden darf (Ziel: Ausgabe 1, 2, ..., n).

Zwei Container i < j (Ankunftsreihenfolge) dürfen nie in denselben Stapel, wenn a_i < a_j und ein späterer Container kleiner als a_i ist
(Muster 231 aus a_i, a_j und dem späteren Container); die Mindestzahl ist die chromatische Zahl dieses Konfliktgraphen. Gegenprobe in den Tests:
Simulation aller Zuordnungen. Gerechnet wird mit Rückverfolgung über Bitmasken. Der Rechenaufwand hat einen langen Ausläufer: ab n = 30 dauerte
ein Einzelfall in einer früheren Messung bis zu 2,5 Sekunden, bis n = 24 höchstens 8 Millisekunden, darum die Obergrenze SOFORT_N_MAX und ein Knotenbudget.

Eigene Fassung dieses Repos, nichts aus anderen Demos importiert."""

from pat_patience import lis_laenge

SOFORT_N_MAX = 24            # darüber meldet die App „nicht gerechnet“
KNOTEN_BUDGET = 400_000      # Obergrenze der Suchknoten je Färbungsversuch; danach „nicht gerechnet“


class BudgetErschoepft(Exception):
    pass


def konfliktgraph(a) -> list:
    """Nachbarschaft als Bitmasken: Bit j in adj[i] heißt, die Container i und j (Positionen) dürfen nicht in denselben Stapel."""
    n = len(a)
    suffix_min = [n + 1] * (n + 1)
    for j in range(n - 1, -1, -1):
        suffix_min[j] = min(a[j], suffix_min[j + 1])
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if a[i] < a[j] and suffix_min[j + 1] < a[i]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return adj


def konfliktkanten(a) -> set:
    """Konfliktkanten als Paare von Rängen (kleinerer zuerst gekommen), für Anzeige und Handrechnung."""
    adj = konfliktgraph(a)
    return {(a[i], a[j]) for i in range(len(a)) for j in range(i + 1, len(a)) if adj[i] >> j & 1}


def _faerben(adj, k, budget):
    """Färbt mit höchstens k Farben (Rückverfolgung, Farben symmetriebrechend nacheinander geöffnet). Gibt die Farbliste je Position oder None."""
    n = len(adj)
    ordnung = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))
    klassen = [0] * k
    farbe = [-1] * n
    zaehler = [0]

    def rek(idx, benutzt):
        if idx == n:
            return True
        zaehler[0] += 1
        if zaehler[0] > budget:
            raise BudgetErschoepft
        v = ordnung[idx]
        for c in range(min(benutzt + 1, k)):
            if adj[v] & klassen[c]:
                continue
            klassen[c] |= 1 << v
            farbe[v] = c
            if rek(idx + 1, max(benutzt, c + 1)):
                return True
            klassen[c] &= ~(1 << v)
            farbe[v] = -1
        return False

    return list(farbe) if rek(0, 0) else None


def sofort_zuordnung(a, budget: int = KNOTEN_BUDGET):
    """(k, Zuordnung): kleinste Zahl paralleler Stapel mit Zwischenausgabe und ein Stapelindex je Container (Ankunftsreihenfolge).
    Gibt None zurück, wenn n über SOFORT_N_MAX liegt oder das Knotenbudget erschöpft ist („nicht gerechnet“)."""
    n = len(a)
    if n > SOFORT_N_MAX:
        return None
    if n == 0:
        return 0, ()
    adj = konfliktgraph(a)
    if not any(adj):
        return 1, (0,) * n
    try:
        for k in range(2, lis_laenge(a) + 1):
            farbe = _faerben(adj, k, budget)
            if farbe is not None:
                return k, tuple(farbe)
    except BudgetErschoepft:
        return None
    raise AssertionError("die Färbung mit LIS Farben existiert immer (Patience-Stapel sind unabhängige Mengen)")


def sofort_min(a):
    """Kleinste Zahl paralleler Stapel mit Zwischenausgabe; None, wenn nicht gerechnet."""
    erg = sofort_zuordnung(a)
    return None if erg is None else erg[0]


def sim_parallel(a, zuordnung, k: int) -> list:
    """k parallele Stapel, jeder Container kommt auf den ihm zugeordneten; nach jedem Einlagern wird ausgegeben, was an der Reihe ist
    (1, 2, 3, ...). Rückgabe: die Ausgabereihenfolge (vollständig 1..n genau dann, wenn die Zuordnung sortiert)."""
    stapel = [[] for _ in range(k)]
    naechster = 1
    aus = []
    for x, s in zip(a, zuordnung):
        stapel[s].append(x)
        bewegt = True
        while bewegt:
            bewegt = False
            for st in stapel:
                if st and st[-1] == naechster:
                    aus.append(st.pop())
                    naechster += 1
                    bewegt = True
    return aus
