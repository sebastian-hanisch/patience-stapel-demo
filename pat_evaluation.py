"""Kennzahlen und Verdikte (reine Funktionen: Verdikt = (Art, Text), die App ruft st.<Art>(Text))."""

import math
import re
from dataclasses import dataclass
from fractions import Fraction

import pat_constants as C
import pat_patience as P
import pat_sofort as S
import pat_tables as T
from pat_model import modell_folge
from pat_rng import SplitMix64

REGEL_KURZ = {"erster": "erster passender", "engste": "engste Passung", "groesste": "größte Spitze", "rechts": "ganz rechts"}


# --- Zahlen deutsch formatieren -------------------------------------------------------------------------------------------------------------
def ganz(x) -> str:
    """Ganzzahl mit Leerzeichen als Tausendertrenner (362 880)."""
    return f"{int(x):,}".replace(",", " ")


def zahl(x, stellen: int = 1) -> str:
    """Dezimalzahl mit Komma; Tausender mit Leerzeichen."""
    text = f"{float(x):,.{stellen}f}"
    return text.replace(",", " ").replace(".", ",")


def prozent(anteil, stellen: int = 1) -> str:
    return zahl(float(anteil) * 100, stellen)


def folge_text(a) -> str:
    return "(" + ", ".join(str(x) for x in a) + ")"


# --- Eingabe -------------------------------------------------------------------------------------------------------------------------------
def parse_folge(text: str):
    """Liest eine Folge von Abholrängen (Ganzzahlen, getrennt durch Komma, Semikolon oder Leerzeichen). Rückgabe: (Tupel, None) oder (None, Meldung)."""
    teile = [t for t in re.split(r"[,;\s]+", text.strip()) if t]
    if not teile:
        return (), None
    werte = []
    for t in teile:
        if not re.fullmatch(r"\d+", t):
            return None, f"„{t}“ ist keine ganze Zahl ab 1: eine Folge besteht aus Abholrängen 1, 2, 3, …"
        werte.append(int(t))
    if len(werte) > C.FOLGE_MAX:
        return None, f"Die Folge ist zu lang: höchstens {C.FOLGE_MAX} Container, eingegeben sind {len(werte)}."
    if min(werte) < 1 or max(werte) > C.RANG_MAX:
        return None, f"Die Abholränge müssen zwischen 1 und {C.RANG_MAX} liegen."
    vorhanden = set(werte)
    fehlend = [r for r in range(1, max(werte) + 1) if r not in vorhanden]
    if fehlend:
        return None, "Die Folge ist keine Permutation: fehlende Ränge " + ", ".join(str(r) for r in fehlend) + (
            " (Ränge doppelt zu vergeben ist erlaubt, Lücken nicht)." if len(set(werte)) < len(werte) else ".")
    return tuple(werte), None


# --- Einstellungen und Analyse der aktuellen Folge -------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Settings:
    quelle: str = C.DEFAULT_QUELLE
    folge: str = C.DEFAULT_FOLGE
    n: int = C.DEFAULT_N
    d: float = C.DEFAULT_D
    seed: int = C.DEFAULT_SEED
    gleiche: str = C.DEFAULT_GLEICHE
    regel: str = C.DEFAULT_REGEL


@dataclass(frozen=True)
class Analysis:
    folge: tuple
    art: str                 # "perm" (Permutation), "wort" (Gleichstände) oder "fehler"
    meldung: str | None
    herkunft: str            # Text, woher die Folge stammt
    stapel: list             # Stapel der gewählten Regel (bei Wörtern nach `gleiche`)
    anzahl_je_regel: dict
    lis: int
    lds: int
    lis_werte: tuple         # Werte einer längsten wachsenden Teilfolge (nur Permutation)
    abholen: list
    wachsend: list
    blockierende: int
    sofort: tuple | None     # (k, Zuordnung) oder None (nicht gerechnet)
    gleichstand: tuple | None  # (teilen, verschieden) bei Wörtern


def aktuelle_folge(s: Settings):
    """(Folge, Herkunftstext, Meldung) je nach Quelle."""
    if s.quelle == "u":
        return tuple(modell_folge(SplitMix64(s.seed), s.n, None)), f"Zufallsfolge aus Modell U, n = {s.n}, Zufalls-Seed {s.seed}", None
    if s.quelle == "v":
        return (tuple(modell_folge(SplitMix64(s.seed), s.n, s.d)),
                f"Zufallsfolge aus Modell V (ausgedacht), n = {s.n}, D = {zahl(s.d, 1)}, Zufalls-Seed {s.seed}", None)
    werte, meldung = parse_folge(s.folge)
    return werte, "Eingabe von Hand", meldung


def analyse(s: Settings) -> Analysis:
    folge, herkunft, meldung = aktuelle_folge(s)
    leer = Analysis((), "fehler", meldung, herkunft, [], {}, 0, 0, (), [], [], 0, None, None)
    if folge is None:
        return leer
    teilen = s.gleiche == "teilen"
    if not P.ist_permutation(folge):
        # Wort mit Gleichständen (Lücken hat parse_folge schon abgewiesen)
        st = P.stapel_legen(folge, s.regel if s.regel != "zufall" else "erster", gleiche_teilen=teilen)
        gl = (P.min_stapel_gleichstaende(folge, True), P.min_stapel_gleichstaende(folge, False))
        anzahl = {r: len(P.stapel_legen(folge, r, gleiche_teilen=teilen)) for r in P.REGELN}
        return Analysis(folge, "wort", None, herkunft, st, anzahl, gl[0] if teilen else gl[1], 0, (), P.abholen(st), [], 0, None, gl)
    anzahl = {r: len(P.stapel_legen(folge, r)) for r in P.REGELN}
    st = P.stapel_legen(folge, s.regel)
    pos = P.lis_teilfolge(folge)
    wachsend = P.stapel_wachsend(folge)
    return Analysis(folge, "perm", None, herkunft, st, anzahl, P.lis_laenge(folge), P.lds_laenge(folge), tuple(folge[i] for i in pos), P.abholen(st),
                    wachsend, P.blockierende(wachsend), S.sofort_zuordnung(folge), None)


def stapel_bis(a, schritt: int, regel: str, gleiche_teilen: bool = True):
    """Die Stapel nach den ersten `schritt` Containern (die Regeln legen Container einzeln; das Präfix gibt dieselben Stapel wie die ganze Folge)."""
    return P.stapel_legen(a[:schritt], regel, gleiche_teilen=gleiche_teilen)


# --- Verdikte ------------------------------------------------------------------------------------------------------------------------------
def verdict_patience(a: Analysis, regel: str) -> tuple[str, str]:
    """Kernfrage 1 / Experiment 1: Wie viele Stapel braucht diese Folge?"""
    if a.art == "fehler":
        return "warning", a.meldung or "Keine Folge eingegeben."
    if not a.folge:
        return "info", "Leere Folge: es gibt nichts einzulagern, 0 Stapel."
    if a.art == "wort":
        teilen, verschieden = a.gleichstand
        return "info", (
            f"{folge_text(a.folge)} mit Gleichständen (Zielgruppen): teilen sich Gleiche einen Stapel, genügen **{teilen}** Stapel (längste streng wachsende "
            f"Teilfolge); müssen Gleiche in verschiedene Stapel, sind es **{verschieden}** (längste nicht fallende Teilfolge)."
        )
    k = a.anzahl_je_regel[regel]
    werte = ", ".join(str(x) for x in a.lis_werte)
    ersten = f"{folge_text(a.folge)}: „{REGEL_KURZ[regel]}“ legt **{k}** Stapel; die längste wachsende Teilfolge hat die Länge **{a.lis}** (z. B. {werte})."
    vergleich = "Zum Vergleich: " + ", ".join(f"{REGEL_KURZ[r]} {a.anzahl_je_regel[r]}" for r in P.REGELN) + "."
    z = T.zeile(len(a.folge))
    if z is not None and "regeln" in z:
        auf = (f"Alle {ganz(z['folgen'])} Folgen mit n = {len(a.folge)}: erster passender legt in {ganz(z['regeln']['erster_gleich_lis'])} von "
               f"{ganz(z['folgen'])} genau LIS Stapel (vorgerechnete Aufzählung).")
    else:
        auf = f"Für n = {len(a.folge)} ist nicht aufgezählt; die Aufzählung reicht bis n = {C.REGELN_N_MAX}."
    if k == a.lis:
        return "success", f"{ersten} Das ist die kleinste Zahl ohne Umsetzen. {vergleich} {auf}"
    return "warning", f"{ersten} Diese Regel legt {k - a.lis} Stapel mehr als nötig. {vergleich} {auf}"


def verdict_richtung_folge(a: Analysis) -> tuple[str, str]:
    """Kernfrage 2: Auf welche Richtung kommt es an?"""
    if a.art != "perm" or not a.folge:
        return "info", "Die Richtungsfrage gilt für Folgen ohne gleiche Ränge (Permutationen); die aktuelle Eingabe ist keine."
    n = len(a.folge)
    if a.lis == a.lds and n == 1:
        return "info", (f"{folge_text(a.folge)}: fallende Stapel brauchen {a.lis} (LIS), wachsende {a.lds} (LDS): bei einem einzigen Container sind beide Zahlen gleich. "
                        "Die Richtung zeigt sich erst bei längeren Folgen (siehe Experiment 3).")
    if a.lis == a.lds:
        return "info", (f"{folge_text(a.folge)}: fallende Stapel brauchen {a.lis} (LIS), wachsende {a.lds} (LDS): hier gleich viele. "
                        f"Das ist Zufall dieser Folge: nicht jede Folge ist so; zum Vergleich unterscheiden sich beide Zahlen bei n = 9 in 72,4 % aller Folgen (siehe Experiment 3).")
    zusatz = (f"die wachsenden Stapel haben **{a.blockierende}** blockierende Container (sie liegen über einem kleineren), sind also **nicht blockierfrei**"
              if a.blockierende else "die wachsenden Stapel haben keinen blockierenden Container")
    return "warning", (f"{folge_text(a.folge)}: fallende Stapel (ein Container nur auf einen größeren) brauchen **{a.lis}** Stapel (LIS), wachsende **{a.lds}** (LDS); "
                       f"{zusatz}. Wer die Richtung verwechselt, rechnet mit der falschen Zahl.")


def verdict_faden_folge(a: Analysis) -> tuple[str, str]:
    """Kernfrage 3: Was kostet das Warten gegenüber sofort ausgeben?"""
    if a.art != "perm" or not a.folge:
        return "info", "Die Frage gilt für Folgen ohne gleiche Ränge (Permutationen); die aktuelle Eingabe ist keine."
    if a.sofort is None:
        return "warning", (f"„Sofort“ ist für n = {len(a.folge)} nicht gerechnet: die Rechenzeit hat einen langen Ausläufer, darum gilt die Obergrenze n = "
                           f"{S.SOFORT_N_MAX} (oder das Knotenbudget war erschöpft). Verzögert (erst alles einlagern) sind es {a.lis} Stapel.")
    k = a.sofort[0]
    if k == a.lis:
        return "info", f"{folge_text(a.folge)}: sofort ausgeben und verzögert (erst alles einlagern) brauchen beide **{a.lis}** Stapel."
    return "success", (f"{folge_text(a.folge)}: verzögert (erst alles einlagern) **{a.lis}** Stapel, sofort (zwischendurch ausgeben) **{k}** Stapel: "
                       f"Zwischenausgabe spart {a.lis - k}.")


def verdict_regeln(n: int) -> tuple[str, str]:
    """Experiment 2 (Aufzählung aller n! Folgen, n <= 9)."""
    z = T.zeile(n)
    r = z["regeln"]
    f = z["folgen"]
    return "info", (
        f"n = {n}: erster passender und engste Passung legen in {ganz(r['erster_gleich_engste'])} von {ganz(f)} Folgen dieselben Stapel (Befund: keiner); "
        f"größte Spitze braucht in {ganz(r['groesste'])} Folgen ({prozent(Fraction(r['groesste'], f))} %) mehr Stapel als nötig, ganz rechts in "
        f"{ganz(r['rechts'])} ({prozent(Fraction(r['rechts'], f))} %), Zufallswahl in {ganz(r['zufall'])} ({prozent(Fraction(r['zufall'], f))} %, einzelne Ziehung mit Zufalls-Seed 11)."
    )


def verdict_richtung_tabelle() -> tuple[str, str]:
    """Experiment 3: im Mittel unsichtbar, in der einzelnen Folge sichtbar (n = 9 aufgezählt, n = 10 Modell V)."""
    z = T.zeile(9)
    v = T.modell_v()
    mv = v["0.5"]
    return "info", (
        f"Über alle {ganz(z['folgen'])} Folgen mit n = 9 sind die Mittel gleich ({zahl(T.mittel_lis(9), 3)} Stapel in beiden Richtungen), aber LIS ≠ LDS in "
        f"{prozent(Fraction(z['lis_ungleich_lds'], z['folgen']))} % der Folgen. Fast sortierte Ankunft (Modell V, D = 0,5, n = 10, {ganz(mv['anzahl'])} Zufallsfolgen, "
        f"Zufalls-Seed {mv['seed']}): LIS im Mittel {zahl(Fraction(mv['summe_lis'], mv['anzahl']), 2)}, LDS {zahl(Fraction(mv['summe_lds'], mv['anzahl']), 2)}."
    )


def verteilung_median(verteilung) -> int:
    """Kleinste Stapelzahl k, mit der mindestens die Hälfte der Folgen auskommt."""
    return next(k for k in range(1, len(verteilung) + 1) if T.anteil_hoechstens(verteilung, k) >= Fraction(1, 2))


def verdict_verteilung_exakt(n: int) -> tuple[str, str]:
    """Experiment 4, Modell U mit aufgezähltem n (n <= 10)."""
    z = T.zeile(n)
    ver = z["verteilung"]
    k = verteilung_median(ver)
    text = (f"n = {n}: {' / '.join(ganz(x) for x in ver)} Folgen brauchen 1 bis {n} Stapel; "
            f"{prozent(T.anteil_hoechstens(ver, k))} % kommen mit höchstens {k} Stapeln aus.")
    if n == 4:
        text += " Die Zeile 1, 13, 9, 1 ist nicht die Eulersche Zeile 1, 11, 11, 1."
    return "info", text


def verdict_verteilung_stichprobe(r: dict, exakt_n: int | None) -> tuple[str, str]:
    """Experiment 4, Stichprobe (Modell V oder n über der Aufzählung)."""
    modell = "Modell U" if r["D"] is None else f"Modell V (ausgedacht, D = {zahl(r['D'], 1)})"
    anzahl = r["anzahl"]
    mittel = Fraction(r["summe_lis"], anzahl)
    text = (f"{ganz(anzahl)} Zufallsfolgen aus {modell}, n = {r['n']}, Zufalls-Seed {r['seed']}: im Mittel {zahl(mittel, 2)} Stapel, "
            f"am häufigsten {max(r['verteilung'], key=lambda k: r['verteilung'][k])}.")
    if r["D"] is None and exakt_n is not None:
        text += f" Exakt (alle {ganz(T.zeile(exakt_n)['folgen'])} Folgen): {zahl(T.mittel_lis(exakt_n), 3)}."
    elif r["D"] is None:
        text += f" Für n = {r['n']} ist nicht aufgezählt; die Stichprobe schwankt (Standardfehler des Mittels grob 1/(2·√{ganz(anzahl)}) · Streuung)."
    return "info", text


def abstand_se(summe_abstand: int, summe_abstand2: int, anzahl: int) -> float:
    """Standardfehler des mittleren Abstands LIS - sofort aus Summe und Summe der Quadrate."""
    mittel = summe_abstand / anzahl
    var = summe_abstand2 / anzahl - mittel**2
    return math.sqrt(max(var, 0.0) / anzahl)


def verdict_faden_exakt(n: int) -> tuple[str, str]:
    """Experiment 5, Modell U, n <= 10: alle n! Folgen."""
    z = T.zeile(n)
    s = z["sofort"]
    f = z["folgen"]
    text = (f"Alle {ganz(f)} Folgen mit n = {n}: sofort höchstens so viele Stapel wie verzögert ({s['verletzt']} Verletzungen), im Mittel "
            f"{zahl(T.mittel_sofort(n), 3)} gegen {zahl(T.mittel_lis(n), 3)}, gleich viele in {prozent(Fraction(s['gleich_lis'], f))} %, größter Abstand {s['groesster_abstand']}.")
    if n >= 2:
        text += f" Die Folge 1 bis {n}: 1 gegen {n} Stapel."
    return "info", text


def verdict_faden_stichprobe(r: dict) -> tuple[str, str]:
    """Experiment 5, Stichprobe (Modell V oder n über der Aufzählung)."""
    n = r["n"]
    if n > S.SOFORT_N_MAX:
        return "warning", f"„Sofort“ ist für n = {n} nicht gerechnet (Obergrenze n = {S.SOFORT_N_MAX})."
    modell = "Modell U" if r["D"] is None else f"Modell V (ausgedacht, D = {zahl(r['D'], 1)})"
    gerechnet = r["anzahl"] - r["offen"]
    if gerechnet == 0:
        return "warning", "„Sofort“ ist hier nicht gerechnet (Knotenbudget erschöpft)."
    verletzt = sum(c for k, c in r["abstand"].items() if k < 0)
    return "info", (f"{ganz(r['anzahl'])} Zufallsfolgen aus {modell}, n = {n}, Zufalls-Seed {r['seed']}: sofort im Mittel {zahl(r['summe_sofort'] / gerechnet, 2)} Stapel, "
                    f"verzögert {zahl(r['summe_lis'] / r['anzahl'], 2)}; gleich viele in {prozent(Fraction(r['gleich'], gerechnet))} % der Folgen, "
                    f"{verletzt} Folgen mit sofort über verzögert, ein Stapel mit Zwischenausgabe genügt in {prozent(Fraction(r['ein_stapel'], gerechnet))} %.")


def mengen_zeile(n: int) -> dict:
    """„Gleiche Zahl, andere Menge“: A_2 (sofort <= 2) gegen B_3 (LIS <= 3), n <= 9 aufgezählt."""
    return T.zeile(n)["mengen"]


def verdict_mengen(n: int) -> tuple[str, str]:
    m = mengen_zeile(n)
    if m["A2"] == m["B3"]:
        kopf = f"n = {n}: beide Mengen haben {ganz(m['A2'])} Folgen"
    else:
        kopf = f"n = {n}: {ganz(m['A2'])} Folgen gegen {ganz(m['B3'])}"
    return "info", (f"{kopf}; nur in A₂ (zwei parallele Stapel sortieren) liegen {ganz(m['nur_A2'])}, nur in B₃ (blockierfrei in 3 fallenden Stapeln) {ganz(m['nur_B3'])}. "
                    "Gleiche Zahl heißt nicht gleiche Menge.")
