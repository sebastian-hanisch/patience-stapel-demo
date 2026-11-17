"""Texte der App, die auch in der README stehen (ein Test vergleicht beide Fassungen)."""

GITHUB = "https://github.com/sebastian-hanisch/"

MODELL_HINWEIS = (
    "**Das Ankunftsmodell ist ausgedacht** (Modell U: alle Folgen gleich wahrscheinlich; Modell V: Container bleiben eine exponentialverteilte Zeit mit dem Mittel D, "
    "abgeholt wird in der Reihenfolge der Abfahrtszeiten). Es ist ein **Modell, kein Fall aus der Praxis**: Es gibt keine reale Ankunftsfolge dahinter, "
    "keine Hafen-, Bahnhofs- oder Bestandszahl."
)

KONVENTION = (
    "**Konvention:** Ein Stapel ist **fallend**: ein Container kommt nur auf einen Container mit größerem Abholrang, oben liegt der Kleinste, der zuerst geholt wird. "
    "Die Mindestzahl Stapel ohne Umsetzen ist die Länge der längsten **wachsenden** Teilfolge (LIS); bei wachsenden Stapeln wäre es die der längsten fallenden (LDS)."
)

EINLEITUNG = f"""
Container kommen nacheinander an, jeder mit einem **Abholrang** (1 = wird zuerst geholt). Sie werden auf Stapel gelegt, ohne später umgesetzt zu werden. **Wie viele Stapel braucht eine
Ankunftsfolge mindestens, und wie legt man sie?** Die Antwort ist die Länge der längsten wachsenden Teilfolge; die Demo zeigt sie Container für Container, zählt, **welche Regel** sie erreicht und welche nicht,
**welche Richtung** man nicht verwechseln darf und was es kostet, erst alles einzulagern, statt zwischendurch auszugeben.

{MODELL_HINWEIS}

Weiter unten: **🎯 Ergebnis** (Patience von Hand), **❓ Kernfragen**, die Experimente **🔬 2 bis 5** (Regeln, Richtung, Verteilung der Stapelzahl, sofort gegen verzögert), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
Verwandt: [`mehrhafenstau-demo`]({GITHUB}mehrhafenstau-demo) (Patience als Referenzformel für Zielhäfen), [`ketten-antiketten-demo`]({GITHUB}ketten-antiketten-demo) (derselbe Satz als Dilworth und Mirsky).
"""

SO_FUNKTIONIERT = """
1. **Jeder Container kommt auf den ersten Stapel, dessen oberster Container einen größeren Rang hat** (den „ersten passenden“); gibt es keinen, beginnt rechts ein neuer Stapel.
2. **Abgeholt wird von der kleinsten Spitze**: erst wenn alle Container gelegt sind, kommen die Ränge 1, 2, 3, … der Reihe nach, ohne Umsetzen.
3. **Warum das reicht und nötig ist:** Container einer wachsenden Teilfolge können nie im selben fallenden Stapel liegen (der spätere, größere kann nicht auf den früheren, kleineren): mindestens so viele Stapel wie die LIS lang ist.
   Umgekehrt schließt sich jeder Container, der auf Stapel j kommt, an eine wachsende Teilfolge der Länge j − 1 an: höchstens LIS Stapel.
"""

GRENZEN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wo es weitergeht |
|---|---|---|
| **Stapel fallend, ohne Höhengrenze** | Mit Höhengrenze H ist die Mindestzahl weder die LIS noch max(LIS, ⌈n/H⌉) (frühere Messung: n = 6, H = 2, 483 von 720 Folgen gleich LIS, 612 gleich max(LIS, ⌈n/H⌉)). | [`sortierbar-umstauen-demo`](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) |
| **Erst alles einlagern, dann abholen** | Mit Zwischenausgabe braucht man im Mittel über alle 3 628 800 Folgen mit n = 10 nur 3,337 statt 4,335 Stapel (Experiment 5). | Experiment 5 |
| **Alle Ränge verschieden** | Bei Gleichständen entscheidet die Regel für Gleiche: bei den Zielgruppen (2, 2, 2, 2) brauchen die beiden Lesarten (Gleiche teilen sich einen Stapel, Gleiche getrennt) in 2 062 von 2 520 Anordnungen verschieden viele Stapel. | Preset „Zielgruppen mit Gleichständen“ |
| **Ausgedachtes Ankunftsmodell** | Modell U und V sind keine reale Ankunftsfolge; andere Verweilzeitverteilungen sind nicht gemessen. | [`mehrhafenstau-demo`](https://github.com/sebastian-hanisch/mehrhafenstau-demo) |
| **n höchstens 10 exakt, 20 Stichprobe** | Darüber sagt die Demo nichts; „sofort“ ist nur bis n = 24 gerechnet (Rechenzeit mit langem Ausläufer). | – |
"""
