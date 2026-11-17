"""Patience: Container in fallende Stapel legen (Kern der Demo, nur Standardbibliothek).

Konvention: Eine Ankunftsfolge a = (a_1, ..., a_n) nennt in Ankunftsreihenfolge den Abholrang jedes Containers (1 = wird zuerst geholt).
Ein Stapel ist **fallend**: ein Container kommt nur auf einen Container mit größerem Rang, oben liegt der Kleinste. In Ankunftsreihenfolge
ist jeder Stapel also eine fallende Teilfolge. Erst alles einlagern, dann von der kleinsten Spitze abholen heißt hier „verzögert“.
Mindestzahl Stapel ohne Umsetzen = Länge der längsten **wachsenden** Teilfolge (LIS); bei wachsenden Stapeln die der längsten fallenden (LDS).

Gleichstände (Wörter): Dürfen sich gleiche Ränge einen Stapel teilen („nicht steigend“), ist die Mindestzahl die längste streng wachsende
Teilfolge; müssen Gleiche in verschiedene Stapel („streng fallend“), die längste nicht fallende.
Eigene Fassung dieses Repos, nichts aus anderen Demos importiert."""

from bisect import bisect_left, bisect_right

REGELN = ("erster", "engste", "groesste", "rechts")
REGEL_NAMEN = {
    "erster": "erster passender Stapel (ganz links)",
    "engste": "engste Passung (kleinste passende Spitze)",
    "groesste": "größte passende Spitze",
    "rechts": "ganz rechts passender Stapel",
}


def lis_laenge(a, streng: bool = True) -> int:
    """Länge der längsten wachsenden Teilfolge (streng wachsend; mit streng=False: nicht fallend), O(n log n) mit Bisektion."""
    tails: list = []
    suche = bisect_left if streng else bisect_right
    for x in a:
        i = suche(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def lds_laenge(a) -> int:
    """Länge der längsten (streng) fallenden Teilfolge."""
    return lis_laenge([-x for x in a])


def lis_teilfolge(a) -> tuple:
    """Eine längste streng wachsende Teilfolge als Tupel von Positionen (0-basiert): die Spitzen der Patience-Rückverweise.

    Bei mehreren gleich langen wird die zurückverfolgte genommen, deren letzter Container die kleinste Spitze des letzten Stapels ist."""
    tails: list = []      # kleinster möglicher Schlusswert je Länge
    tail_pos: list = []   # Position dieses Schlusswerts
    vorgaenger = [-1] * len(a)
    for i, x in enumerate(a):
        j = bisect_left(tails, x)
        if j == len(tails):
            tails.append(x)
            tail_pos.append(i)
        else:
            tails[j] = x
            tail_pos[j] = i
        vorgaenger[i] = tail_pos[j - 1] if j > 0 else -1
    if not tails:
        return ()
    pos = tail_pos[-1]
    out = []
    while pos != -1:
        out.append(pos)
        pos = vorgaenger[pos]
    return tuple(reversed(out))


def ist_permutation(a) -> bool:
    return sorted(a) == list(range(1, len(a) + 1))


def stapel_legen(a, regel: str = "erster", rng=None, gleiche_teilen: bool = True) -> list:
    """Legt die Container in Ankunftsreihenfolge auf fallende Stapel, jeden nur auf einen Stapel, auf dem er passt (Spitze größer;
    bei Gleichständen mit gleiche_teilen=True auch gleich), sonst auf einen neuen Stapel rechts.

    Regeln: 'erster' (ganz links passend), 'engste' (kleinste passende Spitze), 'groesste' (größte passende Spitze), 'rechts' (ganz rechts passend),
    'zufall' (gleichverteilt unter den passenden Stapeln; braucht ein SplitMix64-Objekt mit below(n)). Rückgabe: Liste der Stapel, jeder von unten nach oben."""
    stapel: list = []
    spitzen: list = []
    for x in a:
        if gleiche_teilen:
            kandidaten = [j for j, t in enumerate(spitzen) if t >= x]
        else:
            kandidaten = [j for j, t in enumerate(spitzen) if t > x]
        if not kandidaten:
            stapel.append([x])
            spitzen.append(x)
            continue
        if regel == "erster":
            j = kandidaten[0]
        elif regel == "engste":
            j = min(kandidaten, key=lambda q: spitzen[q])
        elif regel == "groesste":
            j = max(kandidaten, key=lambda q: spitzen[q])
        elif regel == "rechts":
            j = kandidaten[-1]
        elif regel == "zufall":
            j = kandidaten[rng.below(len(kandidaten))]
        else:
            raise ValueError(f"unbekannte Regel: {regel}")
        stapel[j].append(x)
        spitzen[j] = x
    return stapel


def stapel_wachsend(a) -> list:
    """Wachsende Stapel (die Falle): ein Container kommt nur auf einen kleineren; erster passender. Mindestzahl = LDS.
    Oben liegt der Größte, der Kleinste liegt unten: jeder Container, der nicht unten liegt, blockiert den Container darunter."""
    stapel: list = []
    spitzen: list = []
    for x in a:
        j = next((q for q, t in enumerate(spitzen) if t < x), None)
        if j is None:
            stapel.append([x])
            spitzen.append(x)
        else:
            stapel[j].append(x)
            spitzen[j] = x
    return stapel


def blockierende(stapel) -> int:
    """Zahl der Container, die über einem kleineren Container desselben Stapels liegen (müssten vor diesem umgesetzt werden)."""
    return sum(1 for s in stapel for i, x in enumerate(s) if any(y < x for y in s[:i]))


def abholen(stapel) -> list:
    """Abholen von der kleinsten Spitze: Reihenfolge der geholten Container (ohne Umsetzen), Stapel werden nicht verändert."""
    kopie = [list(s) for s in stapel]
    aus = []
    while any(kopie):
        j = min((q for q in range(len(kopie)) if kopie[q]), key=lambda q: kopie[q][-1])
        aus.append(kopie[j].pop())
    return aus


def spitzen_wachsen(a, regel: str = "erster") -> bool:
    """Invariante von „erster passender“ und „engste Passung“: nach jedem Schritt wachsen die Spitzen von links nach rechts."""
    spitzen: list = []
    for x in a:
        j = next((q for q, t in enumerate(spitzen) if t > x), None)
        if j is None:
            spitzen.append(x)
        else:
            spitzen[j] = x
        if any(spitzen[q] >= spitzen[q + 1] for q in range(len(spitzen) - 1)):
            return False
    return True


def min_stapel_gleichstaende(a, gleiche_teilen: bool) -> int:
    """Mindestzahl Stapel bei möglichen Gleichständen: Gleiche teilen sich einen Stapel -> längste streng wachsende Teilfolge,
    Gleiche in verschiedene Stapel -> längste nicht fallende Teilfolge."""
    return lis_laenge(a, streng=gleiche_teilen)


def blockierende_werte(stapel) -> set:
    """Die Ränge der Container, die über einem kleineren Container desselben Stapels liegen."""
    return {x for s in stapel for i, x in enumerate(s) if any(y < x for y in s[:i])}
