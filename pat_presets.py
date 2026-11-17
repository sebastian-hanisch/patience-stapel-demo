"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button.

Zwei Arten von Reglern: **Szenario-Regler** (Folge und ihre Quelle; ihre Werte setzen die Presets, ihre Änderung hebt die Markierung des aktiven
Presets auf) und **Experiment-Regler** (Regel, Richtung, n und Stichprobe der Experimente 2 bis 5; sie gehören zur Adresszeile, ändern aber das Preset
nicht). Der Schritt-Regler von Experiment 1 zeigt nur an, wie weit die Container schon gelegt sind; er steht nicht im Permalink."""

import random
from dataclasses import dataclass

import streamlit as st

import pat_constants as C
import pat_patience as P


def _d_oder_uniform(wert):
    return "uniform" if str(wert) == "uniform" else float(wert)


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: object
    default: object
    lo: float | None = None
    hi: float | None = None
    options: tuple | None = None
    szenario: bool = True


SETTING_SPECS = {
    "quelle_sel": SettingSpec("quelle", str, C.DEFAULT_QUELLE, options=C.QUELLEN),
    "folge_text": SettingSpec("folge", str, C.DEFAULT_FOLGE),
    "n_zufall": SettingSpec("n", int, C.DEFAULT_N, C.N_MIN, C.N_MAX),
    "d_sel": SettingSpec("d", float, C.DEFAULT_D, options=C.D_OPTIONEN),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "gleiche_sel": SettingSpec("gleiche", str, C.DEFAULT_GLEICHE, options=C.GLEICHE),
    # Experiment-Regler
    "regel_sel": SettingSpec("regel", str, C.DEFAULT_REGEL, options=P.REGELN, szenario=False),
    "richtung_sel": SettingSpec("richtung", str, C.DEFAULT_RICHTUNG, options=C.RICHTUNGEN, szenario=False),
    "n_regeln": SettingSpec("nr", int, C.DEFAULT_N_REGELN, C.N_TABELLE_MIN, C.N_TABELLE_MAX, szenario=False),
    "n_stich": SettingSpec("ns", int, C.DEFAULT_N_STICH, C.N_STICH_MIN, C.N_STICH_MAX, szenario=False),
    "modell_stich": SettingSpec("ms", str, "u", options=("u", "v"), szenario=False),
    "d_stich": SettingSpec("ds", float, C.DEFAULT_D, options=C.D_OPTIONEN, szenario=False),
    "t_stich": SettingSpec("t", int, C.DEFAULT_T, C.T_MIN, C.T_MAX, szenario=False),
    "n_faden": SettingSpec("nf", int, C.DEFAULT_N_FADEN, C.N_FADEN_MIN, C.N_FADEN_MAX, szenario=False),
    "d_faden": SettingSpec("df", _d_oder_uniform, C.DEFAULT_D_FADEN, options=C.D_FADEN_OPTIONEN, szenario=False),
}
PRESET_KEYS = {"quelle": "quelle_sel", "folge": "folge_text", "n": "n_zufall", "d": "d_sel", "seed": "seed_input", "gleiche": "gleiche_sel"}
SCHRITT_KEY = "schritt_sel"


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default
    st.session_state.setdefault(SCHRITT_KEY, C.FOLGE_MAX)   # „alle Container gelegt“; die App begrenzt auf die Länge der Folge


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def begrenzen(spec: SettingSpec, wert):
    """Wert aus der Adresszeile auf die Reglergrenzen bzw. Auswahlmöglichkeiten begrenzen; None, wenn er unbrauchbar ist."""
    try:
        wert = spec.caster(wert)
    except (ValueError, TypeError):
        return None
    if spec.options is not None:
        return wert if wert in spec.options else None
    if isinstance(wert, str):
        return wert[:200]
    if spec.lo is not None:
        wert = max(spec.lo, wert)
    if spec.hi is not None:
        wert = min(spec.hi, wert)
    return wert


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            wert = begrenzen(spec, qp[spec.url_param])
            if wert is not None:
                st.session_state[state_key] = wert
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]
    st.session_state[SCHRITT_KEY] = C.FOLGE_MAX


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Szenario-Reglern entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Szenario-Regler aus SETTING_SPECS mit dem Session State. Die Experiment-Regler (szenario=False) ändern
    das Preset nicht. tests/test_layout.py prüft, dass jeder Regler der Seitenleiste in SETTING_SPECS steht."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
            if spec.szenario
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Eine Beispielfolge laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    """Neue Zufallsfolge: neuer Zufalls-Seed; bei Quelle „Eingabe“ wechselt die Quelle zu Modell U (sonst täte der Knopf nichts)."""
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
    if st.session_state.get("quelle_sel", C.DEFAULT_QUELLE) == "eingabe":
        st.session_state["quelle_sel"] = "u"
