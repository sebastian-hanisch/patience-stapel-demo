"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# --- Ankunftsfolge (Seitenleiste) -----------------------------------------------------------------------------------------------------------
QUELLEN = ("eingabe", "u", "v")
QUELLE_NAMEN = {"eingabe": "Eingabe von Hand", "u": "Zufallsfolge, Modell U (alle Folgen gleich wahrscheinlich)", "v": "Zufallsfolge, Modell V (Verweilzeit D)"}
DEFAULT_QUELLE = "eingabe"
DEFAULT_FOLGE = "1, 3, 5, 2, 4"
FOLGE_MAX = 30                       # längste Eingabe; „sofort“ nur bis SOFORT_N_MAX (pat_sofort)
RANG_MAX = 99                        # größter Abholrang einer Eingabe (bei Gleichständen: größte Zielgruppe)
N_MIN, N_MAX, DEFAULT_N = 3, 30, 9   # Länge der Zufallsfolge
D_OPTIONEN = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
DEFAULT_D = 0.5
SEED_MAX, DEFAULT_SEED = 999999, 15000
GLEICHE = ("teilen", "verschieden")
GLEICHE_NAMEN = {"teilen": "Gleiche teilen sich einen Stapel", "verschieden": "Gleiche brauchen verschiedene Stapel"}
DEFAULT_GLEICHE = "teilen"

# --- Experiment-Regler (Hauptbereich beim Experiment) ---------------------------------------------------------------------------------------
DEFAULT_REGEL = "erster"
DEFAULT_RICHTUNG = "fallend"
RICHTUNGEN = ("fallend", "wachsend")
N_TABELLE_MIN, N_TABELLE_MAX, DEFAULT_N_REGELN = 4, 9, 8      # Experiment 2: eingefrorene Aufzählung der Regeln
N_STICH_MIN, N_STICH_MAX, DEFAULT_N_STICH = 2, 20, 9           # Experiment 4: exakt bis TABELLE_N_MAX, darüber Stichprobe
T_MIN, T_MAX, T_SCHRITT, DEFAULT_T = 200, 2000, 200, 1000
N_FADEN_MIN, N_FADEN_MAX, DEFAULT_N_FADEN = 2, 20, 10          # Experiment 5
D_FADEN_OPTIONEN = D_OPTIONEN + ("uniform",)
DEFAULT_D_FADEN = "uniform"
T_FADEN = 2000                                                  # Zahl der Folgen der Stichprobe in Experiment 5
SPINNER_AB_N = 16                                               # Stichproben ab dieser Länge zeigen einen Spinner mit Zeitangabe
TABELLE_N_MAX = 10                                              # größtes n der eingefrorenen Aufzählung (pat_tables.json)
REGELN_N_MAX = 9                                                # größtes n der Regel-Zählungen und Mengenvergleiche

# --- Farben ---------------------------------------------------------------------------------------------------------------------------------
COLOR_BOX = "#7f8c9a"
COLOR_LIS = "#2F6B65"
COLOR_NEU = "#d98c1f"
COLOR_LINE = "#4c78a8"
COLOR_FALSCH = "#b5483a"

# --- Presets: jedes setzt alle Szenario-Regler -------------------------------------------------------------------------------------------------
PRESETS = {
    "Handbeispiel (1, 3, 5, 2, 4)": {"quelle": "eingabe", "folge": "1, 3, 5, 2, 4", "n": DEFAULT_N, "d": DEFAULT_D, "seed": DEFAULT_SEED, "gleiche": DEFAULT_GLEICHE},
    "Aldous/Diaconis, n = 10": {"quelle": "eingabe", "folge": "7, 2, 8, 1, 3, 4, 10, 6, 9, 5", "n": DEFAULT_N, "d": DEFAULT_D, "seed": DEFAULT_SEED, "gleiche": DEFAULT_GLEICHE},
    "Bereits in Abholreihenfolge": {"quelle": "eingabe", "folge": "1, 2, 3, 4, 5, 6, 7, 8", "n": DEFAULT_N, "d": DEFAULT_D, "seed": DEFAULT_SEED, "gleiche": DEFAULT_GLEICHE},
    "Umkehrfolge": {"quelle": "eingabe", "folge": "8, 7, 6, 5, 4, 3, 2, 1", "n": DEFAULT_N, "d": DEFAULT_D, "seed": DEFAULT_SEED, "gleiche": DEFAULT_GLEICHE},
    "Zufallsfolge, n = 9": {"quelle": "u", "folge": DEFAULT_FOLGE, "n": 9, "d": DEFAULT_D, "seed": DEFAULT_SEED, "gleiche": DEFAULT_GLEICHE},
    "Fast sortierte Ankunft (D = 0,5)": {"quelle": "v", "folge": DEFAULT_FOLGE, "n": 10, "d": 0.5, "seed": DEFAULT_SEED, "gleiche": DEFAULT_GLEICHE},
    "Zielgruppen mit Gleichständen": {"quelle": "eingabe", "folge": "1, 2, 2, 3", "n": DEFAULT_N, "d": DEFAULT_D, "seed": DEFAULT_SEED, "gleiche": "teilen"},
}
PRESET_HELP = {
    "Handbeispiel (1, 3, 5, 2, 4)": "Fünf Container, von Hand nachgerechnet: erster passender legt 3 Stapel, die längste wachsende Teilfolge hat die Länge 3.",
    "Aldous/Diaconis, n = 10": "Zehn Container (7 2 8 1 3 4 10 6 9 5), das Beispiel aus Aldous und Diaconis 1999: 5 Stapel.",
    "Bereits in Abholreihenfolge": "Acht Container kommen in der Reihenfolge an, in der sie geholt werden: ohne Zwischenausgabe 8 Stapel, mit Zwischenausgabe 1 Stapel.",
    "Umkehrfolge": "Acht Container kommen in umgekehrter Abholreihenfolge: ein Stapel genügt, mit und ohne Zwischenausgabe.",
    "Zufallsfolge, n = 9": "Eine Zufallsfolge aus Modell U (alle 362 880 Folgen gleich wahrscheinlich); der Zufalls-Seed in der Seitenleiste ändert sie.",
    "Fast sortierte Ankunft (D = 0,5)": "Zehn Container aus Modell V mit kurzer Verweilzeit: fast in der Ankunftsreihenfolge abgeholt. Ausgedachtes Modell, keine reale Ankunftsfolge.",
    "Zielgruppen mit Gleichständen": "Vier Container mit nur drei Abholrängen (1, 2, 2, 3): teilen sich Gleiche einen Stapel, genügen 3 Stapel, sonst sind es 4.",
}
