# Patience: Wie viele Stapel braucht eine Ankunftsfolge? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-patience-stapel-demo.streamlit.app/)** -->

Eine von mehreren Demos zu **Sortiermaschinen und Permutationen** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Sie zeigt den **Platz einer Folge**: Container kommen nacheinander
an, jeder mit einem Abholrang (1 = wird zuerst geholt), und werden **ohne Umsetzen** auf Stapel gelegt. Wie viele Stapel braucht die Folge mindestens? Nachbar-Demos: [`gleise-durchgaenge-demo`](https://github.com/sebastian-hanisch/gleise-durchgaenge-demo)
(dort zählen Durchgänge über feste Gleise, hier der Platz in LIFO-Stapeln mit freier Wahl beim Ausgeben), [`stapel-sortieren-demo`](https://github.com/sebastian-hanisch/stapel-sortieren-demo) (ein Stapel, der sortiert),
[`maschinen-vergleich-demo`](https://github.com/sebastian-hanisch/maschinen-vergleich-demo) (der Hauptbefund zu „gleiche Zahl, andere Menge“), [`erdos-szekeres-demo`](https://github.com/sebastian-hanisch/erdos-szekeres-demo) (wie viele Container in W Stapel passen),
[`tableaux-rsk-demo`](https://github.com/sebastian-hanisch/tableaux-rsk-demo) (die Zeilen der Verteilung als Tableaux), [`zufallsfolgen-lis-demo`](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo) (die Länge der längsten wachsenden Teilfolge bei großem n),
[`sortierbar-umstauen-demo`](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) (dieselbe Zahl mit Höhengrenze und Umsetzen), [`mehrhafenstau-demo`](https://github.com/sebastian-hanisch/mehrhafenstau-demo) (Patience als Referenzformel für Zielhäfen in einer Seefracht-Bucht),
[`ketten-antiketten-demo`](https://github.com/sebastian-hanisch/ketten-antiketten-demo) (derselbe Satz als Dilworth und Mirsky für Aufgabenpläne).

**Das Ankunftsmodell ist ausgedacht** (Modell U: alle Folgen gleich wahrscheinlich; Modell V: Container bleiben eine exponentialverteilte Zeit mit dem Mittel D, abgeholt wird in der Reihenfolge der Abfahrtszeiten). Es ist ein **Modell, kein Fall aus der Praxis**: Es gibt keine reale Ankunftsfolge dahinter, keine Hafen-, Bahnhofs- oder Bestandszahl.

## Warum dieses Problem

Wer Container fallend stapelt und erst alles einlagert, braucht für eine Ankunftsfolge so viele Stapel, wie die längste wachsende Teilfolge lang ist. **Wie viele Stapel braucht eine Folge, welche Regel erreicht das, auf welche Richtung kommt es an, und was kostet es, erst alles einzulagern, statt zwischendurch auszugeben?**

Im Handbeispiel (1, 3, 5, 2, 4) sind es 3 Stapel. Die Zahl stimmt mit drei unabhängigen Rechenwegen überein (Brute Force über alle Mengenpartitionen bis n = 7, Dilworth-Matching bis n = 8, ein zweites Programm bis n = 9, also in allen 409 113 Folgen mit n ≤ 9 mit mindestens einem unabhängigen Weg; im Normalbetrieb der Tests reicht Dilworth bis n = 7 und das zweite Programm bis n = 8, die größere Reichweite läuft mit `-m slow`, siehe Verifikation; B3). Die **Richtung ist die Falle**: Bei wachsenden Stapeln wäre die Zahl die längste fallende Teilfolge; über alle 362 880 Folgen mit n = 9 gemittelt fällt der Unterschied nicht auf (die Mittel sind gleich, 4,059), in der einzelnen Folge liegt die falsche Zahl in 72,4 % der Folgen daneben, und bei fast sortierter Ankunft (Modell V, D = 0,5, n = 10, 2 000 Zufallsfolgen) rechnet die falsche Richtung im Mittel mit 1,48 statt 9,40 Stapeln.
Wer zwischendurch ausgeben darf, braucht über alle 3 628 800 Folgen mit n = 10 im Mittel 3,337 statt 4,335 Stapel (Abstand 0,998), nie mehr als beim Verzögern (0 Verletzungen in allen 4 037 913 Folgen mit n ≤ 10, dazu das Argument, dass jede verzögerte Belegung auch eine sofortige ist), bei fast sortierter Ankunft aber 1,00 statt 9,40. Ein ehrlicher **Negativbefund**: „erster passender“ und „engste Passung“ legen in allen 409 113 Folgen mit n ≤ 9 dieselben Stapel, ein Vergleich der beiden hat keinen Befund; nur die anderen Regeln (größte passende Spitze 37,2 %, ganz rechts 32,0 %, Zufallswahl 19,3 % der Folgen bei n = 8 in einer einzelnen Ziehung, der Erwartungswert liegt bei 19,2 %; B5) brauchen mehr Stapel als nötig.
Alles gilt in diesem Modell, für fallende Stapel unbegrenzter Höhe und Folgen aus lauter verschiedenen Abholrängen (Gleichstände siehe Befund B6); Zähleinheit ist die Folge bzw. die Zufallsfolge, n ≤ 10 exakt aufgezählt, bis n = 20 als Stichprobe.

## Modell

* **Ankunftsfolge** π = (π₁, …, π_n): Der i-te angekommene Container hat den Abholrang πᵢ (1 = wird zuerst geholt, alle Ränge verschieden). **Konvention:** Container-Stapel sind **fallend**: ein Container kommt nur auf einen Container mit größerem Rang, oben liegt der Kleinste. In Ankunftsreihenfolge ist jeder Stapel also eine fallende Teilfolge.
* **Verzögert** (Patience): erst alles einlagern, dann von der kleinsten Spitze abholen, ohne Umsetzen. Mindestzahl Stapel = Länge der **längsten wachsenden** Teilfolge (LIS). Bei **wachsenden** Stapeln (ein Container nur auf einen kleineren) ist sie die der längsten fallenden (LDS); der Satz „Mindestzahl = längste fallende Teilfolge“ ohne diese Bedingung wäre falsch.
* **Sofort:** parallele Stapel mit Zwischenausgabe: ausgegeben wird, was gerade an der Reihe ist (Ziel: Ausgabe 1, 2, …, n). Mindestzahl = chromatische Zahl des Konfliktgraphen, in dem zwei Container i < j verbunden sind, wenn πᵢ < πⱼ und ein Container, der später als j ankommt, kleiner als πᵢ ist (Muster 231). Jede verzögerte Belegung ist auch eine sofortige, also gilt sofort ≤ LIS.
* **Regeln** (jede legt nur auf einen Stapel, auf dem der Container passt, sonst auf einen neuen): erster passender (ganz links), engste Passung (kleinste passende Spitze), größte passende Spitze, ganz rechts, Zufallswahl unter den passenden.
* **Gleichstände** (mehrere Container mit demselben Rang, Zielgruppen): Dürfen sich Gleiche einen Stapel teilen, ist die Mindestzahl die längste **streng wachsende** Teilfolge; müssen Gleiche in verschiedene Stapel, die längste **nicht fallende**.
* **Modell U:** alle n! Folgen gleich wahrscheinlich (Fisher–Yates mit ganzzahligem SplitMix64). **Modell V** (ausgedacht): Container i kommt zur Zeit i und bleibt eine exponentialverteilte Zeit mit dem Mittel D (in Ankunftsabständen); der Abholrang ist die Reihenfolge der Abfahrtszeiten. Kleines D heißt: die Container werden fast in der Reihenfolge abgeholt, in der sie ankommen; Modell U ist der Grenzfall D gegen unendlich.
* Die Formeln stehen im 📐-Expander der App.

**Quellen (nur so zitiert, wie sie gelesen sind).** Aldous und Diaconis, Bulletin of the AMS 36 (1999), Lemma 1: Patience legt genau LIS Stapel, jede legale Strategie mindestens so viele (gelesen in der Fassung der Berkeley-Kopie); das Beispiel 7 2 8 1 3 4 10 6 9 5 mit 5 Stapeln stammt von dort und ist hier nachgerechnet.
Schensted 1961, Satz 1 und 2 (LIS und LDS als Spalten und Zeilen des Einfügetableaus). Tarjan, Vorfassung 1971 (Stanford-Bericht), Lemma 3: blockierfreie Ablage in m Stapeln genau dann, wenn LIS ≤ m (die Fassung im Journal of the ACM von 1972 ist nicht gelesen). Dass „in m parallelen Stapeln sortierbar“ genau die m-Färbbarkeit des Konfliktgraphen heißt, steht hier nur über Tarjan 1971 und Bóna als Zitat. Dilworth und Mirsky sind Lehrbuch und nicht neu gelesen; die Zählfolgen A047874 (Zeile n = 7) und A216040 (n ≤ 7) sind nach dem Quellenbericht übernommen, die übrigen Zahlen sind eigene Nachrechnung in diesem Modell. Nichts davon ist neu: alles ist Lehrbuch, neu ist nur die Vorführbarkeit mit Zähleinheit.

## Methodik

* **Aufzählung vorgerechnet:** Alle n! Folgen bis n = 10 (4 037 913 Folgen bis dahin) sind in `pat_tables.json` eingefroren (Skript `tools/pat_make_tables.py`, Prüfung mit `--check`); in App und README heißen diese Zahlen **vorgerechnet**. Live gerechnet werden nur die einzelne Folge (LIS, Stapel, sofort bis n = 24) und die Stichproben (n bis 20, bis 2 000 Zufallsfolgen).
* **Drei unabhängige Rechenwege für die Mindestzahl** (Tests in `tests/test_oracle_patience_stapel.py`): Brute Force über alle Mengenpartitionen (jeder Block entlang der Ankunft fallend), Dilworth (kleinste Kettenüberdeckung = n minus maximales Matching, gerechnet mit scipy) und ein numpy-Programm mit O(n²); dazu die Verteilung der Stapelzahl gegen die Summe der Quadrate der Standard-Young-Tableaux (Hakenformel, nur Ganzzahlen) und „sofort“ gegen das Nachspielen aller Zuordnungen.
* **Sofort:** Färbung des Konfliktgraphen mit Rückverfolgung über Bitmasken, Knotenbudget 400 000, Obergrenze n = 24 (darüber meldet die App „nicht gerechnet“; die Rechenzeit hat einen langen Ausläufer).
* **Zufall** nur über den ganzzahligen SplitMix64 (`pat_rng.py`, geprüfte Vorlage, unverändert kopiert; Zufalls-Seed als Zahl). `below(n)` ist der Rest der Division: der Fehler gegenüber einer exakten Gleichverteilung ist höchstens n/2⁶⁴ (für n ≤ 30 unter 2·10⁻¹⁸) und ohne Belang. Modell V zieht die Exponentialverteilung über einen plattformfesten Logarithmus (`exact_log`), nicht über die C-Bibliothek.
* **Stichproben** werden als Band gelesen: Vergleiche der Mittel in den Tests mit drei Standardfehlern Toleranz, nicht bitgleich.

## Befunde (gemessen, keine Behauptungen)

Zähleinheit ist die Folge (alle n! Folgen gleich gewichtet), wo nichts anderes steht; „vorgerechnet“ heißt aus `pat_tables.json`. Die Spalte „Test“ nennt die Testfunktion in `tests/test_claims.py` (Ganzzahlen und Brüche exakt; Stichprobenmittel als Band), die die Zahl rechnet oder gegen die Tabelle hält.

| Nr | Befund (Voraussetzung) | Test |
|---|---|---|
| B1 | Handbeispiel (1, 3, 5, 2, 4), n = 5: erster passender und engste Passung legen [[1], [3, 2], [5, 4]] = 3 Stapel = LIS 3 (drei längste Teilfolgen: (1, 2, 4), (1, 3, 4), (1, 3, 5)); größte Spitze und ganz rechts legen 4 Stapel; wachsende Stapel [1, 3, 5] und [2, 4]: 2 = LDS, aber 3 blockierende Container; sofort 2 (Konfliktkante 3–5); die Folge gehört zu den 61 Folgen mit 3 Stapeln der Zeile 1, 41, 61, 16, 1; Mittel über alle 120 Folgen: LIS 67/24, sofort 9/5, Abstand 119/120 | `test_b01` |
| B2 | Beispiel von Aldous und Diaconis (n = 10): 7 2 8 1 3 4 10 6 9 5 gibt 5 Stapel [[7, 2, 1], [8, 3], [4], [10, 6, 5], [9]], LIS 5 (1 3 4 6 9) | `test_b02` |
| B3 | Mindestzahl Stapel = LIS: Brute Force über alle Mengenpartitionen in allen 5 913 Folgen mit n ≤ 7, Dilworth-Matching in allen 46 233 Folgen mit n ≤ 8, O(n²)-Programm in allen 409 113 Folgen mit n ≤ 9 (fallende Stapel unbegrenzter Höhe, alle Ränge verschieden); bei wachsenden Stapeln gleich LDS | `test_b03` (Zählung der Folgen) und die Orakel-Tests |
| B4 | „Erster passender“ und „engste Passung“ legen in 409 113 von 409 113 Folgen mit n ≤ 9 identische Stapel. Beweis: nach jedem Schritt wachsen die Spitzen von links nach rechts (Invariante); links vom ersten passenden Stapel sind alle Spitzen kleiner als der neue Container, rechts davon größer als die alte Spitze, also ist der erste passende der mit der kleinsten Spitze über dem Container. Befund: keiner | `test_b04` |
| B5 | Regeln, die mehr Stapel als nötig legen (Folgen): n = 4: 1 von 24 (4,2 %) bei größter Spitze, ganz rechts und Zufallswahl; n = 6: 135 (18,8 %), 120 (16,7 %), 61 (8,5 %) von 720; **n = 8: 14 993 (37,2 %), 12 886 (32,0 %), 7 793 (19,3 %) von 40 320**; n = 9: 168 927 (46,6 %), 144 527 (39,8 %), 89 131 (24,6 %) von 362 880. Zufallswahl mit Zufalls-Seed 11, als Band 18,9 bis 19,3 % bei n = 8 zu lesen (18,9 % mit dem Zufallsstrom von numpy in einer früheren Messung, 19,3 % mit SplitMix64). Die Zufallswahl-Zahlen sind je eine einzelne Ziehung; der Erwartungswert (Rekursion über alle Zufallspfade, unabhängig nachgerechnet) liegt bei n = 4 bei 2,1 %, bei n = 6 bei 9,5 %, bei n = 8 bei 19,2 % und bei n = 9 bei 24,6 %, die Ziehung weicht bei n = 4 und n = 6 sichtbar ab | `test_b05` |
| B6 | Gleichstände (Zähleinheit: Wörter, alle Anordnungen einer Mehrfachmenge): (1, 2, 2, 3) braucht 3 Stapel, wenn Gleiche sich einen Stapel teilen, und 4, wenn nicht. Beide Aussagen stimmen mit dem Dilworth-Matching überein; die beiden Lesarten (Gleiche teilen sich einen Stapel, Gleiche getrennt) brauchen verschieden viele Stapel in 2 062 von 2 520 Wörtern (81,8 %) bei den Gruppen (2, 2, 2, 2), in 551 von 560 bei (3, 3, 2), in 5 013 von 10 080 bei (2, 2, 1, 1, 1, 1) und in 70 von 70 bei (4, 4) | `test_b06` |
| B7 | Die Falle: LIS und LDS haben über alle n! Folgen dieselbe Verteilung (Spiegeln der Folge), die Summen sind gleich (n = 4 bis 9: 58, 335, 2 261, 17 465, 152 020, 1 473 057), das Mittel bei n = 9 ist 4,059. In der einzelnen Folge ist LIS ≠ LDS in 20 von 24 (n = 4), 84 von 120, 464 von 720, 3 758 von 5 040, 30 456 von 40 320 und **262 904 von 362 880 Folgen (n = 9, 72,4 %)** | `test_b07` |
| B8 | Modell V, n = 10, 2 000 Zufallsfolgen je D, Zufalls-Seeds 15 000 + Index von D (D = 0,5; 1; 2; 4; 8; 16; Modell U): Mittel LIS (richtige Richtung) 9,3955 / 8,3275 / 7,0950 / 6,0775 / 5,2790 / 4,8585 / 4,3095; Mittel LDS (falsche Richtung) 1,4835 / 1,9825 / 2,4945 / 3,0255 / 3,5485 / 3,8510 / 4,3325 (bei Modell U exakt beide 4,335 über alle Folgen); Mittel sofort 1,0035 / 1,0950 / 1,4655 / 2,0385 / 2,5130 / 2,8715 / 3,3185. Zahl der 2 000 Folgen, die schon ein Stapel mit Zwischenausgabe sortiert: 1 993 / 1 814 / 1 143 / 421 / 124 / 46 / 4 (Modell U exakt Catalan(10)/10! = 0,46 %). vorgerechnet; die Neu-Rechnung im Test liegt innerhalb von drei Standardfehlern. Die vier Dezimalstellen sind Scheingenauigkeit: der Standardfehler der Mittel für LIS liegt bei etwa 0,02, der für sofort bei etwa 0,02 bis 0,03, die Mittel sind auf eine Dezimalstelle zu lesen | `test_b08` |
| B9 | Verteilung der Stapelzahl (Folgen mit genau 1, 2, … Stapeln): n = 4: 1, 13, 9, 1 (nicht die Eulersche Zeile 1, 11, 11, 1); n = 7: 1, 428, 2 332, 1 821, 421, 36, 1 (gleich A047874 nach dem Quellenbericht); **n = 9: 1, 4 861, 89 497, 167 449, 83 029, 16 465, 1 513, 64, 1**. Jede Zeile gleich der Summe der f² über die Formen mit erster Zeile k (n ≤ 10, Hakenformel). Anteil mit höchstens k Stapeln, n = 9: k ≤ 2: 1,3 %, ≤ 3: 26,0 %, ≤ 4: 72,1 %, ≤ 5: 95,0 %, ≤ 6: 99,6 % | `test_b09` |
| B10 | Sofort gegen verzögert, Mittel über alle Folgen: n = 4: 1,458 gegen 2,417 (Abstand 0,958, gleich viele in 9 von 24 = 37,5 %, größter Abstand 3); n = 6: 2,142 gegen 3,140 (0,999; 278 von 720 = 38,6 %; 5); n = 8: 2,771 gegen 3,770 (0,999; 15 779 von 40 320 = 39,1 %; 7); n = 9: 3,061 gegen 4,059 (0,999; 142 955 = 39,4 %; 8); **n = 10: 3,337 gegen 4,335 (0,998; 1 431 973 von 3 628 800 = 39,5 %; 9)**. In allen 4 037 913 Folgen mit n ≤ 10 braucht sofort nie mehr Stapel als verzögert (0 Verletzungen); sofort = 1 genau in Catalan(n) Folgen (n ≤ 10). Der größte Abstand n − 1 gehört der sortierten Folge 1, 2, …, n (sofort 1, verzögert n) | `test_b10` |
| B11 | Folgen mit sofort ≤ 2: 1, 2, 6, 23, 103, 513, 2 760, 15 741 für n = 1 bis 8 (n ≤ 7 gleich A216040 nach dem Quellenbericht, n = 8 eigene Zählung), 93 944 für n = 9 und 581 303 für n = 10 (eigene Zählung, kein Beleg) | `test_b11` und die Orakel-Tests |
| B12 | Gleiche Zahl, andere Menge: A₂ („zwei parallele Stapel sortieren“, sofort ≤ 2) und B₃ („blockierfrei in 3 fallenden Stapeln“, LIS ≤ 3) haben bei n = 4, 5, 6 je 23, 103, 513 Folgen, aber 1 / 14 / 137 Folgen nur in A₂ und ebenso viele nur in B₃; erst bei n = 7 unterscheiden sich die Zahlen: 2 760 gegen 2 761, n = 8: 15 741 gegen 15 767, n = 9: 93 944 gegen 94 359. Bei n = 4 liegt (1, 2, 3, 4) nur in A₂ (sofort 1, verzögert 4 Stapel) und (2, 3, 4, 1) nur in B₃. Auch bei k = 1 haben A₁ (Vermeider von 231) und B₂ (Vermeider von 123) je Catalan(n) Folgen, aber nur 7, 11, 16, 22, 29, 37 gemeinsame (n = 4 bis 9) | `test_b12` |
| B13 | Abhängigkeit von n im Modell U (Stichprobe, Zufalls-Seed 16 000 + n): Abstand LIS − sofort 1,001 (n = 10, 8 000 Folgen), 0,997 (12), 0,991 (14), 0,971 (16, je 8 000 Folgen), 0,974 (n = 20, 4 000 Folgen); Standardfehler 0,012 bis 0,017. Exakt liegt der Abstand für n = 6 bis 10 zwischen 0,998 und 1,000. Der Abstand liegt also in allen Stichproben nahe 1 (0,971 bis 1,001 in der Tabelle, 0,995 bis 1,005 in der unabhängigen Stichprobe); ein Sinken mit n ist innerhalb der Streuung (Standardfehler 0,012 bis 0,017) nicht erkennbar (eine unabhängige Stichprobe mit je 20 000 Folgen gab 1,005 bei n = 12, 0,998 bei n = 16 und 0,995 bei n = 20); eine Erklärung gibt es nicht, und für n über 20 ist nichts gemessen | `test_b13` |
| B14 | Höhengrenze (nur als Grenze der Aussage): bei fallenden Stapeln der Höhe höchstens H = 2 und n = 6 ist die Mindestzahl in 483 von 720 Folgen gleich LIS und in 612 von 720 gleich max(LIS, ⌈n/H⌉); sie ist weder das eine noch das andere. Der Teil ohne Höhengrenze ist B3 | `test_b14` |
| B15 | Aus den Presets: „Bereits in Abholreihenfolge“ (n = 8) meldet 8 gegen 1 Stapel (verzögert gegen sofort), „Umkehrfolge“ (n = 8) meldet 1 gegen 1, „Zielgruppen mit Gleichständen“ (1, 2, 2, 3) meldet 3 Stapel, wenn Gleiche sich einen Stapel teilen, gegen 4, wenn Gleiche getrennt liegen müssen | `tests/test_presets.py::test_erwartete_aussage_je_preset` |

**Rechenzeit** (Messung dieser README, nicht im Test; Windows, Python 3.14): „sofort“ für 5 000 Zufallsfolgen aus Modell U mit n = 24 brauchte im Median 0,09 ms, im 99. Perzentil 0,75 ms und höchstens 12 ms je Folge; bei n = 20 (1 500 Folgen) lag das Maximum bei 4 ms. Eine frühere Messung mit einer anderen Fassung des Verfahrens fand bei n = 30 einzelne Folgen mit mehr als 2 Sekunden, darum die Obergrenze n = 24; der Test `tests/test_sofort.py` rechnet 300 Folgen mit n = 24 in unter 30 Sekunden. Ein Seitenaufruf der App mit den Voreinstellungen braucht rund eine Sekunde (AppTest); eine Stichprobe mit n = 20 und 2 000 Zufallsfolgen aus Modell V rund 1,5 Sekunden, aus Modell U etwa 0,2 Sekunden.

## Befunde und Korrekturen gegenüber dem Plan

* Der Anteil „LIS ≠ LDS“ bei n = 9 steht als 72,4 % (262 904 von 362 880 = 0,72449); die Zählung aus der ersten Rechnung hat sich im Bau bestätigt, ebenso alle Zeilen der Verteilung, die Regel-Zählungen und die Mengenvergleiche (die Tabelle `pat_tables.json` stimmt mit den Zahlen der ersten Rechnung überein).
* Die Aufzählung reicht für die Verteilung der Stapelzahl und für „sofort gegen verzögert“ bis n = 10 (für die Regel-Zählungen bis n = 9); neu in dieser Demo sind die Zeile n = 10 der Verteilung (1, 16 795, 569 794, 1 604 098, 1 100 902, 296 326, 38 281, 2 521, 81, 1), die 581 303 Folgen mit sofort ≤ 2 bei n = 10 (gegen 586 590 mit LIS ≤ 3) und die Mengenzahlen von B12 für n = 10.
* **Mittel 3,337 gegen 4,335** bei n = 10 sind exakt über alle 3 628 800 Folgen; die Werte 3,33 und 4,32 aus einer Stichprobe von 2 000 Folgen liegen im Standardfehler daneben und stehen nirgends als Ergebnis.
* „Sofort einlagern“ heißt hier genauer **„sofort ausgeben“**: gemessen ist die Mindestzahl paralleler Stapel mit Zwischenausgabe gegen „alles einlagern, dann abholen“.
* Die Zufallswahl bei n = 8 liegt mit dem ganzzahligen Generator bei 19,3 %, nicht bei den 18,9 % einer früheren Messung mit dem Zufallsstrom von numpy (gleicher Zufalls-Seed 11, anderer Strom); als Band 18,9 bis 19,3 % zu lesen.
* Im ersten Entwurf stand „410 000 Folgen mit n ≤ 9“; die genaue Summe von 1! bis 9! ist 409 113.
* **Abweichung vom Plan:** Experiment 2 (Regeln) und Experiment 3 (Richtung) haben keine eigenen Regler für Regel und Modell, sondern zeigen alle Regeln bzw. alle Werte von D auf einmal (Diagramm und Tabelle); die Regel für die Folge von Hand wählt Experiment 1. Alle fünf Experimente sind gebaut, keines wurde gestrichen.

## Ehrliche Grenzen

* Alle Aussagen gelten für **fallende Stapel unbegrenzter Höhe** und (außer B6) Folgen aus paarweise verschiedenen Abholrängen. Mit Höhengrenze ist die Mindestzahl weder LIS noch max(LIS, ⌈n/H⌉) (B14); die Höhengrenze selbst ist nicht Gegenstand dieser Demo.
* Das Ankunftsmodell ist ausgedacht. Modell V kennt nur die Rangfolge der Abfahrten und eine exponentialverteilte Verweilzeit; **andere Verweilzeitverteilungen** (nicht exponential, Lognormal) sind nicht gemessen. Eine reale Ankunftsfolge liegt nicht vor.
* Exakt aufgezählt ist nur bis n = 10, Stichproben nur bis n = 20; **für größere n sagt die Demo nichts** (auch nicht, ob der Abstand „sofort gegen verzögert“ bei etwa 1 bleibt). Für den Abstand nahe 1 gibt es keine Erklärung, nur die Messung (B10, B13).
* „Sofort“ mit **Gleichständen** ist nicht gemessen; „sofort“ ist nur bis n = 24 gerechnet.
* Zufallswahl und Modell V sind Stichproben mit festem Zufalls-Seed. Der Erwartungswert der Zufallswahl über alle Zufallspfade steht nur für n = 4, 6, 8 und 9 in B5 (Rekursion, unabhängig nachgerechnet); für andere n steht er nicht da.
* Das Mindestzahl-Ergebnis „blockierfreie Ablage in m Stapeln genau dann, wenn LIS ≤ m“ (Tarjan) ist nur in der Vorfassung von 1971 gelesen; Greene, Dilworth, Mirsky sind Lehrbuch.
* Die Zahlen sind unter Windows (Python 3.14) und in der Linux-CI gerechnet; die Zählungen sind ganzzahlig, die Stichproben plattformfest (ganzzahliger Generator, `exact_log`).
* Der Satz „Mindestzahl = LIS“ ohne Höhengrenze ist hier belegt (B3). Texte in anderen Demos, die ihn „nicht nachgeprüft“ nennen, ändert diese Demo nicht.
* Bei einer Folge mit Gleichständen zeigen die Experimente 3 und 5 nur einen Hinweis, weil die Aussagen dort Permutationen voraussetzen.

## Verifikation

Die Suite hat 172 Tests im Normalbetrieb; dazu kommen 2 langsame Tests, die nur mit `-m slow` laufen.

- **Kern:** Patience-Regeln, Konfliktgraph und Färbung, Modell U und V an Handbeispielen (`tests/test_patience.py`, `tests/test_sofort.py`, `tests/test_model.py`), Randfälle (`tests/test_edge_cases.py`: n = 0, 1, 2, Gleichstand, Obergrenzen, ungültige Eingaben).
- **Orakel** (`tests/test_oracle_patience_stapel.py`): Brute Force über Mengenpartitionen (n ≤ 7), Dilworth-Matching (n ≤ 7, mit `-m slow` n ≤ 8), numpy-Programm (n ≤ 8, mit `-m slow` n ≤ 9), Summe der f² (n ≤ 8 aufgezählt, n ≤ 10 gegen die eingefrorene Tabelle), „sofort“ gegen das Nachspielen aller Zuordnungen (n ≤ 6), A216040 (n ≤ 8), Gleichstände gegen Dilworth in allen 2 520 Wörtern.
- **Eigenschaften** (`tests/test_eigenschaften_patience_stapel.py`): Spiegeln vertauscht LIS und LDS, die Inverse hat dieselbe LIS, Umnummerieren ändert die Stapel nicht, Streichen und Einfügen ändern die Stapelzahl um höchstens 1, Spitzen wachsen, jeder Stapel ist fallend, sofort ≤ LIS.
- **Claims:** `tests/test_claims.py` rechnet jede Zahl der Tabelle oben (Zahl → Test).
- **Tabelle:** `tests/test_tables.py` rechnet n ≤ 7 neu und prüft die Invarianten der Datei; mit `-m slow` kommt die Neu-Rechnung bis n = 8 über das Werkzeug dazu (`python tools/pat_make_tables.py --check`, mit `--voll` bis n = 10, nur vor einem Release).
- **Presets, Layout, Oberfläche:** `tests/test_presets.py` (je Preset die erwartete Aussage), `tests/test_layout.py` (Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, jede Änderung eines Szenario-Reglers hebt die Markierung auf, Experiment-Regler ändern sie nicht), `tests/test_app.py` (jeder Button, jeder Regler am Minimum und Maximum, auch unter den Zufallsquellen), `tests/test_footer.py`, `tests/test_runtime_imports.py`.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Gerüst nach DEMO-PLAYBOOK §2) |
| `pat_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `pat_patience.py` | Kern: Stapel legen nach vier Regeln und Zufallswahl, LIS und LDS, wachsende Stapel, Gleichstände |
| `pat_sofort.py` | „Sofort“: Konfliktgraph (Muster 231), Färbung, Nachspielen |
| `pat_model.py` | Ankunftsmodell U und V (ausgedacht), Stichproben |
| `pat_rng.py` | SplitMix64 (geprüfte Vorlage, unverändert kopiert) |
| `pat_tables.json` | eingefrorene Aufzählung aller Folgen bis n = 10 und die Stichproben von Modell V |
| `pat_tables.py` | Leser der Tabelle |
| `pat_evaluation.py` | Eingabe, Analyse der Folge, Verdikte als reine Funktionen |
| `pat_texts.py` | Texte, die auch in der README stehen |
| `pat_layout.py` | Fester Kopf (Stylesheet) |
| `pat_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Knopf |
| `pat_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tools/pat_make_tables.py` | rechnet `pat_tables.json` vor (`--schreiben`) und prüft sie (`--check`, `--voll`) |
| `pytest.ini` | Marker `slow`: Aufzählungen bis n = 9 laufen mit `pytest -m slow` |
| `requirements-dev.txt` | Laufzeit plus pytest, numpy und scipy für die Orakel-Tests |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handbeispiele, Orakel, Eigenschaften, Claims, Tabelle, Verdikte, Randfälle, Presets, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

* **Höhengrenze und Umsetzen:** nur als Grenze der Aussage genannt (B14); dort setzt [`sortierbar-umstauen-demo`](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) an.
* **Greene und Erdős–Szekeres** (wie viele Container in W Stapel passen): [`erdos-szekeres-demo`](https://github.com/sebastian-hanisch/erdos-szekeres-demo); **Schensted-Einfügen und die Tableaux**: [`tableaux-rsk-demo`](https://github.com/sebastian-hanisch/tableaux-rsk-demo); die Summe der f² dient hier nur als Orakel.
* **Erwartungswert der LIS bei großem n** (2√n, Tracy–Widom): [`zufallsfolgen-lis-demo`](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo); hier nur n ≤ 10 exakt und die Stichproben bis n = 20.
* **Catalan-Zahlen, Muster-Klassen und Wachstum** der Vermeidermengen: nur als Verweis.
* **Dilworth, Mirsky und König** werden nicht vorgeführt; das Matching steht nur im Test als Orakel.
* **PDF-Export** und eine Gleichstands-Messung für „sofort“.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v          # Normalbetrieb
pytest tests/ -m slow     # Aufzählungen bis n = 9 und Neu-Rechnung der Tabelle bis n = 8
```

Gebaut mit Streamlit, Plotly und pandas; die Orakel-Tests nutzen numpy und scipy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
