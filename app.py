"""Patience: Wie viele Stapel braucht eine Ankunftsfolge? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Container einer Ankunftsfolge auf fallende Stapel legen: Mindestzahl = längste wachsende Teilfolge, gierige Regeln, die Richtung als Falle,
Verteilung der Stapelzahl, „sofort“ gegen „verzögert“. Aufbau nach DEMO-PLAYBOOK §2.

Lauffähig mit: streamlit run app.py
"""

import math

import pandas as pd
import streamlit as st

import pat_constants as C
import pat_evaluation as E
import pat_model as M
import pat_patience as P
import pat_sofort as S
import pat_tables as T
import pat_texts as X
from pat_layout import dunkles_design, kopf_css
from pat_presets import (
    SCHRITT_KEY,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
    SETTING_SPECS,
)
from pat_visualization import build_abstand, build_regeln, build_richtung, build_stapel, build_verteilung

st.set_page_config(page_title="Patience – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _sample(n, d, anzahl, seed, mit_sofort):
    return M.stichprobe(n, d, anzahl, seed, mit_sofort)


def _show(verdict):
    kind, text = verdict
    getattr(st, kind)(text)


def _d_text(d):
    return "uniform (Modell U)" if d == "uniform" else f"D = {E.zahl(d, 1)}"


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in pat_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🃏 Patience: Wie viele Stapel braucht eine Ankunftsfolge?")
st.markdown(X.EINLEITUNG)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/patience-stapel-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Stellen Sie sich vor, Container kommen nacheinander an, jeder mit einer Abholnummer: Die kleinste Nummer wird zuerst geholt. Sie werden auf Stapel gelegt und danach nicht mehr umgesetzt. Ein Container darf nur auf einen Container mit größerer Nummer gelegt werden, damit der früher benötigte oben liegt. Wie viele Stapel braucht man mindestens? Die Demo zeigt, dass es so viele sind, wie die längste Kette in der Ankunftsfolge lang ist, deren Nummern von Container zu Container steigen (die längste wachsende Teilfolge). Der Name Patience für dieses Legen stammt vom Kartenspiel. Die Demo prüft, welche Legeregel das erreicht und welche mehr Stapel braucht, warum man die Richtung der Stapel nicht verwechseln darf und was es spart, zwischendurch auszugeben. Das Ankunftsmodell ist ausgedacht: ein Rechenmodell, kein echter Betrieb.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/patience-stapel-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktioniert Patience", expanded=True):
    st.markdown(X.KONVENTION)
    st.markdown(X.SO_FUNKTIONIERT)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Ankunftsfolge")
    quelle = st.selectbox("Quelle der Folge", C.QUELLEN, key="quelle_sel", format_func=C.QUELLE_NAMEN.get,
                          help="Eine Folge von Hand eingeben oder eine Zufallsfolge aus dem ausgedachten Ankunftsmodell ziehen.")
    st.text_input("Folge von Hand (Abholränge)", key="folge_text", disabled=quelle != "eingabe",
                  help="Abholränge in Ankunftsreihenfolge, durch Komma getrennt: 1 wird zuerst geholt. Alle Ränge von 1 bis zum größten müssen vorkommen; "
                       "kommt ein Rang mehrfach vor, gelten die Container als Zielgruppe (Gleichstand).")
    n_zufall = st.slider("Länge der Zufallsfolge n", *bounds("n_zufall"), key="n_zufall", disabled=quelle == "eingabe",
                         help="Zahl der Container einer Zufallsfolge.")
    st.caption(f"Zufallsfolge: n = {n_zufall} gibt {E.ganz(math.factorial(n_zufall))} mögliche Folgen.")
    st.select_slider("Verweilzeit D (Modell V)", options=C.D_OPTIONEN, key="d_sel", disabled=quelle != "v",
                     format_func=lambda d: E.zahl(d, 1),
                     help="Mittlere Verweilzeit in Ankunftsabständen. Klein: die Container werden fast in der Reihenfolge abgeholt, in der sie ankommen; groß: beliebig durcheinander.")
    st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, disabled=quelle == "eingabe",
                    help="Legt die Zufallsfolge fest; derselbe Zufalls-Seed gibt dieselbe Folge. In den Experimenten 4 und 5 ist er auch der Zufalls-Seed der Stichprobe.")
    st.button("🎲 Neue Zufallsfolge", width="stretch", on_click=randomize_seed)

ss = st.session_state
settings = E.Settings(ss["quelle_sel"], ss["folge_text"], int(ss["n_zufall"]), float(ss["d_sel"]), int(ss["seed_input"]), ss["gleiche_sel"], ss["regel_sel"])
a = _analysis(settings)
n_folge = len(a.folge)

# --- Ergebnis (Experiment 1: Patience von Hand) --------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis: Experiment 1, Patience von Hand")
st.caption(f"Folge: {a.herkunft}" + (f", {E.folge_text(a.folge)}" if a.folge else "") + ".")
if a.art == "fehler":
    st.warning(a.meldung or "Keine Folge eingegeben.")
c1, c2, c3 = st.columns(3)
c1.selectbox("Regel", P.REGELN, key="regel_sel", format_func=P.REGEL_NAMEN.get,
             help="Wohin der nächste Container kommt, wenn mehrere Stapel passen. Nur wenn die Spitzen von links nach rechts wachsen, sind erster passender und engste Passung dieselbe Regel (Experiment 2).")
c2.radio("Gleiche Ränge", C.GLEICHE, key="gleiche_sel", format_func=C.GLEICHE_NAMEN.get, disabled=a.art != "wort",
         help="Wirkt nur, wenn ein Rang mehrfach vorkommt (Zielgruppen): dürfen Gleiche sich einen Stapel teilen?")
if n_folge >= 1:
    ss[SCHRITT_KEY] = int(min(max(ss.get(SCHRITT_KEY, n_folge), 0), n_folge))
    schritt = c3.slider("Schritt: Container gelegt", 0, n_folge, key=SCHRITT_KEY,
                        help="Wie viele Container schon angekommen sind; der Schieber ändert nur die Anzeige, nicht die Folge.")
else:
    schritt = 0

if a.art in ("perm", "wort") and n_folge:
    teilen = ss["gleiche_sel"] == "teilen"
    stapel_jetzt = E.stapel_bis(a.folge, schritt, ss["regel_sel"], teilen)
    lis_jetzt = P.lis_laenge(a.folge[:schritt], streng=teilen) if schritt else 0
    werte = tuple(a.folge[i] for i in P.lis_teilfolge(a.folge[:schritt])) if (a.art == "perm" and schritt) else ()
    m1, m2 = st.columns(2)
    m1.metric(f"Stapel nach {schritt} von {n_folge} Containern", len(stapel_jetzt), delta=f"{len(stapel_jetzt) - lis_jetzt:+d} gegen LIS", delta_color="inverse")
    m2.metric("Mindestzahl Stapel (LIS)", lis_jetzt, delta="Referenz", delta_color="off")
    st.plotly_chart(build_stapel(stapel_jetzt, markiert=werte, zuletzt=a.folge[schritt - 1] if schritt else None), width="stretch", key="stapel_chart")
    st.caption("Oben liegt der Kleinste: der wird zuerst geholt. Grün: eine längste wachsende Teilfolge der bisherigen Container (nur bei Folgen ohne gleiche Ränge); "
               "orangefarbener Rand: der zuletzt gelegte Container.")
    if schritt == n_folge:
        st.markdown("**Abholen von der kleinsten Spitze, ohne Umsetzen:** " + ", ".join(str(x) for x in P.abholen(stapel_jetzt)))
    else:
        st.caption("Abgeholt wird erst, wenn alle Container gelegt sind (Schritt = Länge der Folge).")

# --- Kernfragen ----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
st.markdown("**1. Wie viele Stapel braucht diese Folge, und woran sieht man es?**")
_show(E.verdict_patience(a, ss["regel_sel"]))
st.markdown("**2. Auf welche Richtung kommt es an?**")
_show(E.verdict_richtung_folge(a))
st.markdown("**3. Was kostet das Warten gegenüber sofort ausgeben?**")
_show(E.verdict_faden_folge(a))

st.markdown("---")

# --- Experiment 2: Regeln ----------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Welche Regel? Gierig ist nicht gleich gierig")
st.caption("Vorgerechnete Aufzählung aller n! Folgen (Zähleinheit: Folge, fallende Stapel, jede Regel legt nur auf einen Stapel, auf dem der Container passt).")
n_regeln = st.slider("Länge n (aufgezählt)", *bounds("n_regeln"), key="n_regeln", help="Alle n! Folgen dieser Länge sind vorgerechnet.")
z2 = T.zeile(n_regeln)
st.caption(f"n = {n_regeln}: {E.ganz(z2['folgen'])} Folgen.")
st.plotly_chart(build_regeln(z2), width="stretch", key="regeln_chart")
st.caption("Erster passender und engste Passung legen in allen aufgezählten Folgen dieselben Stapel: Die Spitzen wachsen nach jedem Schritt von links nach rechts, "
           "also ist der erste passende Stapel der mit der kleinsten passenden Spitze. Dieser Vergleich hat damit **keinen Befund**. Die Zufallswahl hängt am Zufallsstrom und ist als Band zu lesen; ihr Erwartungswert über alle Zufallspfade liegt bei n = 4 bei 2,1 %, bei n = 6 bei 9,5 %, bei n = 8 bei 19,2 % und bei n = 9 bei 24,6 % (README, B5).")
_show(E.verdict_regeln(n_regeln))

st.markdown("---")

# --- Experiment 3: Richtung --------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Die Falle, welche Richtung?")
richtung = st.radio("Richtung der Stapel", C.RICHTUNGEN, key="richtung_sel", horizontal=True,
                    help="Fallend: ein Container nur auf einen größeren (Container-Stapel). Wachsend: nur auf einen kleineren; dann blockiert jeder Container den darunter.")
if a.art == "perm" and n_folge:
    if richtung == "fallend":
        st.plotly_chart(build_stapel(P.stapel_legen(a.folge, "erster"), markiert=a.lis_werte, hoehe=300), width="stretch", key="richtung_chart")
        st.caption(f"Fallend: {a.lis} Stapel (LIS), blockierfrei: nichts liegt über einem kleineren.")
    else:
        st.plotly_chart(build_stapel(a.wachsend, rot=P.blockierende_werte(a.wachsend), hoehe=300), width="stretch", key="richtung_chart")
        st.caption(f"Wachsend: {a.lds} Stapel (LDS); rot: die {a.blockierende} Container, die über einem kleineren liegen und es blockieren.")
else:
    st.info("Die Anzeige gilt für Folgen ohne gleiche Ränge (Permutationen).")
tab3 = pd.DataFrame([
    {"n": n, "Folgen": T.zeile(n)["folgen"], "Mittel der Stapelzahl (beide Richtungen)": float(T.mittel_lis(n)),
     "Folgen mit LIS ≠ LDS": T.zeile(n)["lis_ungleich_lds"], "Anteil": 100.0 * T.zeile(n)["lis_ungleich_lds"] / T.zeile(n)["folgen"]}
    for n in range(2, C.REGELN_N_MAX + 1)
])
st.dataframe(tab3, hide_index=True, width="stretch",
             column_config={"Mittel der Stapelzahl (beide Richtungen)": st.column_config.NumberColumn(format="%.3f"),
                            "Folgen mit LIS ≠ LDS": st.column_config.NumberColumn(format="%d"),
                            "Anteil": st.column_config.NumberColumn("Anteil der Folgen mit LIS ≠ LDS (%)", format="%.1f %%")})
st.plotly_chart(build_richtung(T.modell_v()), width="stretch", key="richtung_modell_chart")
st.caption("Modell V (ausgedacht): kleines D heißt, die Abholreihenfolge ist fast die Ankunftsreihenfolge; dort liegt die falsche Richtung am weitesten daneben. Vorgerechnet: 2000 Zufallsfolgen je D.")
_show(E.verdict_richtung_tabelle())

st.markdown("---")

# --- Experiment 4: Verteilung der Stapelzahl ---------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Wie viele Stapel braucht eine Folge?")
e1, e2, e3, e4 = st.columns(4)
n_stich = e1.slider("Länge n", *bounds("n_stich"), key="n_stich", help=f"Bis n = {C.TABELLE_N_MAX} liegt die Aufzählung aller Folgen vor, darüber nur Stichprobe.")
modell_stich = e2.radio("Modell", ("u", "v"), key="modell_stich", format_func=lambda m: "Modell U" if m == "u" else "Modell V", horizontal=True,
                        help="Modell U: alle Folgen gleich wahrscheinlich. Modell V: ausgedacht, Verweilzeit D.")
d_stich = e3.select_slider("Verweilzeit D", options=C.D_OPTIONEN, key="d_stich", disabled=modell_stich != "v", format_func=lambda d: E.zahl(d, 1))
t_stich = e4.slider("Zahl der Zufallsfolgen", *bounds("t_stich"), key="t_stich", step=C.T_SCHRITT)
d_arg = None if modell_stich == "u" else float(d_stich)
if n_stich >= C.SPINNER_AB_N:
    with st.spinner("Stichprobe wird gezogen, rund 1 bis 3 Sekunden …"):
        r4 = _sample(n_stich, d_arg, int(t_stich), int(ss["seed_input"]), False)
else:
    r4 = _sample(n_stich, d_arg, int(t_stich), int(ss["seed_input"]), False)
exakt = T.zeile(n_stich)["verteilung"] if (modell_stich == "u" and n_stich <= C.TABELLE_N_MAX) else None
st.plotly_chart(build_verteilung(exakt, r4["verteilung"], n_stich), width="stretch", key="verteilung_chart")
if exakt is not None:
    tab4 = pd.DataFrame({"Stapel höchstens k": list(range(1, n_stich + 1)),
                         "Anteil der Folgen (exakt)": [100.0 * float(T.anteil_hoechstens(exakt, k)) for k in range(1, n_stich + 1)]})
    st.dataframe(tab4, hide_index=True, width="stretch",
                 column_config={"Anteil der Folgen (exakt)": st.column_config.NumberColumn(format="%.1f %%")})
    _show(E.verdict_verteilung_exakt(n_stich))
_show(E.verdict_verteilung_stichprobe(r4, n_stich if (modell_stich == "u" and n_stich <= C.TABELLE_N_MAX) else None))
st.caption("Für große n und die Größenordnung 2√n verweist die Demo nicht weiter: hier gilt nur n ≤ 10 exakt und n ≤ 20 als Stichprobe.")

st.markdown("---")

# --- Experiment 5: sofort gegen verzögert ------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Sofort gegen verzögert")
st.caption("**Verzögert** heißt: erst alles einlagern, dann abholen (Patience, LIS Stapel). **Sofort** heißt: parallele Stapel, aus denen zwischendurch ausgegeben wird, "
           "was gerade an der Reihe ist (Ziel: Ausgabe 1, 2, …, n); Mindestzahl = chromatische Zahl des Konfliktgraphen (Muster 231).")
f1, f2 = st.columns(2)
n_faden = f1.slider("Länge n", *bounds("n_faden"), key="n_faden", help=f"Bis n = {C.TABELLE_N_MAX} (Modell U) liegt die Aufzählung aller Folgen vor, darüber Stichprobe.")
d_faden = f2.select_slider("Verweilzeit D", options=C.D_FADEN_OPTIONEN, key="d_faden", format_func=_d_text,
                           help="uniform: Modell U (alle Folgen gleich wahrscheinlich); sonst Modell V (ausgedacht).")
exakt5 = d_faden == "uniform" and n_faden <= C.TABELLE_N_MAX
if exakt5:
    z5 = T.zeile(n_faden)
    s5 = z5["sofort"]
    mittel_sofort, mittel_lis = float(T.mittel_sofort(n_faden)), float(T.mittel_lis(n_faden))
    gleich_anteil = s5["gleich_lis"] / z5["folgen"]
    abstand_liste = s5["abstand"]
    verdict5 = E.verdict_faden_exakt(n_faden)
    quelle5 = f"alle {E.ganz(z5['folgen'])} Folgen (vorgerechnet)"
else:
    d5 = None if d_faden == "uniform" else float(d_faden)
    if n_faden >= C.SPINNER_AB_N:
        with st.spinner("Stichprobe wird gezogen, rund 1 bis 3 Sekunden …"):
            r5 = _sample(n_faden, d5, C.T_FADEN, int(ss["seed_input"]), True)
    else:
        r5 = _sample(n_faden, d5, C.T_FADEN, int(ss["seed_input"]), True)
    gerechnet = r5["anzahl"] - r5["offen"]
    mittel_sofort = r5["summe_sofort"] / gerechnet if gerechnet else 0.0
    mittel_lis = r5["summe_lis"] / r5["anzahl"]
    gleich_anteil = r5["gleich"] / gerechnet if gerechnet else 0.0
    abstand_liste = [r5["abstand"].get(k, 0) for k in range(max(r5["abstand"], default=0) + 1)]
    verdict5 = E.verdict_faden_stichprobe(r5)
    quelle5 = f"{E.ganz(r5['anzahl'])} Zufallsfolgen (Zufalls-Seed {r5['seed']})"
g1, g2, g3 = st.columns(3)
g1.metric("Mittel verzögert (LIS)", E.zahl(mittel_lis, 3))
g2.metric("Mittel sofort", E.zahl(mittel_sofort, 3), delta=f"{mittel_sofort - mittel_lis:+.3f} gegen verzögert".replace(".", ","), delta_color="inverse")
g3.metric("Gleich viele Stapel", E.prozent(gleich_anteil) + " %", delta=quelle5, delta_color="off")
if abstand_liste and sum(abstand_liste):
    st.plotly_chart(build_abstand(abstand_liste), width="stretch", key="abstand_chart")
_show(verdict5)
st.markdown("**Dieselbe Folge, zwei Belegungen** (die Folge aus der Seitenleiste bzw. der Eingabe von oben)")
if a.art == "perm" and n_folge:
    if a.sofort is None:
        st.warning(f"„Sofort“ ist für n = {n_folge} nicht gerechnet (Obergrenze n = {S.SOFORT_N_MAX}; darüber hat die Rechenzeit einen langen Ausläufer).")
    else:
        k_s, zuordnung = a.sofort
        sofort_stapel = [[x for x, z in zip(a.folge, zuordnung) if z == c] for c in range(k_s)]
        h1, h2 = st.columns(2)
        h1.markdown(f"**Verzögert (Patience): {a.lis} Stapel**")
        h1.plotly_chart(build_stapel(P.stapel_legen(a.folge, "erster"), markiert=a.lis_werte, hoehe=280), width="stretch", key="belegung_patience")
        h2.markdown(f"**Sofort (mit Zwischenausgabe): {k_s} Stapel**")
        h2.plotly_chart(build_stapel(sofort_stapel, hoehe=280, titel_y="Container je Stapel in Ankunftsreihenfolge"), width="stretch", key="belegung_sofort")
        ausgabe = S.sim_parallel(a.folge, zuordnung, k_s)
        st.caption("Rechts zeigt jede Säule alle Container, die der Stapel in Ankunftsreihenfolge bekommt; sie werden zwischendurch ausgegeben, sobald der nächste Rang obenauf liegt. "
                   "Nachgespielt kommt dabei heraus: " + ", ".join(str(x) for x in ausgabe) + ".")
else:
    st.info("Die Gegenüberstellung gilt für Folgen ohne gleiche Ränge (Permutationen).")
st.markdown("**Gleiche Zahl, andere Menge** (eine Tabellenzeile; der Hauptbefund steht in der Nachbar-Demo [`maschinen-vergleich-demo`](" + X.GITHUB + "maschinen-vergleich-demo))")
tab5 = pd.DataFrame([
    {"n": n, "A₂: zwei parallele Stapel sortieren": T.zeile(n)["mengen"]["A2"], "B₃: blockierfrei in 3 fallenden Stapeln": T.zeile(n)["mengen"]["B3"],
     "nur in A₂": T.zeile(n)["mengen"]["nur_A2"], "nur in B₃": T.zeile(n)["mengen"]["nur_B3"]}
    for n in range(4, C.TABELLE_N_MAX + 1)
])
st.dataframe(tab5, hide_index=True, width="stretch", column_config={c: st.column_config.NumberColumn(format="%d") for c in tab5.columns})
_show(E.verdict_mengen(min(max(n_faden, 4), C.TABELLE_N_MAX)))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(X.GRENZEN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/patience-stapel-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben ist eine Ankunftsfolge; gesucht ist die kleinste Zahl Stapel $k$, in die man sie ohne Umsetzen so legen kann, dass man danach von den Spitzen aus in der Reihenfolge der Abholränge abholen kann.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Container |
| $\pi = (\pi_1, \dots, \pi_n)$ | Ankunftsfolge: $\pi_i$ ist der Abholrang des $i$-ten angekommenen Containers (Permutation von $1, \dots, n$) |
| $k$, $B_j$ | Zahl der Stapel, Stapel $j$ als Teilmenge der Positionen $\{1, \dots, n\}$ (jeder Container liegt in genau einem Stapel) |
| Spitze | der zuletzt gelegte Container eines Stapels |
| $\ell(\pi)$ (LIS) | Länge der längsten wachsenden Teilfolge von $\pi$ |
| $\ell^{-}(\pi)$ (LDS) | Länge der längsten fallenden Teilfolge von $\pi$ |
| $k^{*}(\pi)$ | kleinste Zahl Stapel ohne Umsetzen |
| $s(\pi)$ (sofort) | kleinste Zahl paralleler Stapel, wenn zwischendurch ausgegeben werden darf |
| $D$ | mittlere Verweilzeit des Modells V in Ankunftsabständen |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/patience-stapel-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Modell (fallende Stapel, unbegrenzte Höhe, paarweise verschiedene Ränge).** Gesucht ist eine Zerlegung der Positionen in $k$ Stapel $B_1, \dots, B_k$, sodass in jedem Stapel die Ränge in Ankunftsreihenfolge fallen:

$$\min k \quad \text{so, dass } \{1,\dots,n\} = B_1 \cup \dots \cup B_k,\; B_j \cap B_{j'} = \emptyset \text{ für } j \ne j',\; i < i' \text{ in } B_j \Rightarrow \pi_i > \pi_{i'}.$$

**Aussage.** Die kleinste Zahl Stapel ist die Länge der längsten wachsenden Teilfolge:

$$k^{*}(\pi) = \ell(\pi).$$

Beweis in zwei Schritten (eigene Überlegung, Mirsky für die Ordnung „früher und kleiner“): zwei Container einer wachsenden Teilfolge liegen nie im selben fallenden Stapel, also $k^{*} \ge \ell$. Legt „erster passender“ einen Container auf Stapel $j$, so endet in der Spitze von Stapel $j-1$ eine wachsende Teilfolge der Länge $j-1$, an die er sich anschließt: höchstens $\ell$ Stapel.

**Wachsende Stapel** (ein Container nur auf einen kleineren) brauchen $\ell^{-}(\pi)$ Stapel; dort liegt aber jeder Container, der nicht unten liegt, über einem kleineren, die Stapel sind nicht blockierfrei.

**Gleichstände.** Dürfen sich gleiche Ränge einen Stapel teilen, ist die Mindestzahl die Länge der längsten streng wachsenden Teilfolge; müssen Gleiche in verschiedene Stapel, die der längsten nicht fallenden.

**Sofort.** Zwei Container $i < j$ dürfen nicht in denselben Stapel, wenn $\pi_i < \pi_j$ und ein Container, der später als $j$ ankommt, kleiner als $\pi_i$ ist (Muster 231). Dann ist $s(\pi)$ die chromatische Zahl dieses Konfliktgraphen, und es gilt

$$s(\pi) \le \ell(\pi).$$

Der Grund: Die Stapel von Patience sind unabhängige Mengen dieses Graphen, jede verzögerte Belegung ist also auch eine sofortige.

**Quellen** (nur so zitiert, wie sie gelesen sind): Aldous und Diaconis, „Longest increasing subsequences: from patience sorting to the Baik–Deift–Johansson theorem“, Bulletin of the AMS 36 (1999), Lemma 1 (Patience legt genau $\ell(\pi)$ Stapel, jede legale Strategie mindestens so viele; gelesen in der Fassung der Berkeley-Kopie).
Schensted, „Longest increasing and decreasing subsequences“, Canadian Journal of Mathematics 13 (1961), Satz 1 und 2 (LIS und LDS am Einfügetableau). Tarjan, Vorfassung 1971 (Stanford-Bericht), Lemma 3: blockierfreie Ablage in $m$ Stapeln genau dann, wenn $\ell \le m$ (die Fassung im Journal of the ACM von 1972 ist nicht gelesen).
Dass „in $m$ parallelen Stapeln sortierbar genau dann, wenn der Konfliktgraph $m$-färbbar ist“, steht hier nur über Tarjan 1971 und Bóna als Zitat. Alles Übrige sind eigene Nachrechnungen in diesem Modell.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)

sync_query_params({k: ss[k] for k in SETTING_SPECS})
