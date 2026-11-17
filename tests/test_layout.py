"""Layout (DEMO-PLAYBOOK §2): fester Kopf, Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben.

Die Hervorhebung ist zustandslos (`aktives_preset` vergleicht jeden Szenario-Regler aus SETTING_SPECS mit dem Preset). Der Test unten stellt
sicher, dass wirklich JEDER Regler der Seitenleiste dort steht: sonst bliebe das Preset trotz Änderung markiert. Die Experiment-Regler im Hauptbereich
(szenario=False) ändern das Preset bewusst nicht; auch das ist ein Test."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import pat_constants as C
import pat_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")
REGLER_ARTEN = ("slider", "number_input", "select_slider", "selectbox", "radio", "toggle", "checkbox", "text_input")
# ein anderer Wert je Szenario-Regler (Quelle, Folge, Länge, D, Zufalls-Seed, Gleichstandsregel)
ANDERER_WERT = {"quelle_sel": "v", "folge_text": "2, 1, 3", "n_zufall": 7, "d_sel": 4.0, "seed_input": 4242, "gleiche_sel": "verschieden"}
ANDERER_EXPERIMENT_WERT = {"regel_sel": "groesste", "richtung_sel": "wachsend", "n_regeln": 6, "n_stich": 5, "modell_stich": "v", "d_stich": 8.0, "t_stich": 400,
                           "n_faden": 7, "d_faden": 2.0}


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _typen(at) -> dict:
    """Button-Typ je Preset-Name (die Preset-Buttons der Seitenleiste)."""
    return {b.label: b.proto.type for b in at.sidebar.button if b.label in C.PRESETS}


def test_presets_stehen_in_der_seitenleiste_und_nicht_im_hauptbereich():
    at = _app()
    assert [b.label for b in at.sidebar.button][: len(C.PRESETS)] == list(C.PRESETS)  # die ersten Buttons der Seitenleiste
    assert not [b for b in at.main.button if b.label in C.PRESETS]


def test_titel_steht_im_festen_kopf():
    at = _app()
    assert "st-key-kopf" in " ".join(h.proto.body for h in at.get("html"))  # das Stylesheet setzt an der Klasse des Containers an
    assert at.title[0].value


def test_beim_start_ist_genau_das_standard_preset_hervorgehoben():
    typen = _typen(_app())
    assert [name for name, typ in typen.items() if typ == "primary"] == [next(iter(C.PRESETS))]


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_angeklicktes_preset_ist_hervorgehoben_und_bleibt_es_im_naechsten_lauf(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]
    at.run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]


def test_jeder_regler_der_seitenleiste_steht_in_setting_specs():
    at = _app()
    schluessel = {w.key for art in REGLER_ARTEN for w in getattr(at.sidebar, art) if w.key}
    fehlt = schluessel - set(P.SETTING_SPECS)
    assert not fehlt, f"Regler {sorted(fehlt)} fehlen in SETTING_SPECS: ihre Änderung hebt das aktive Preset nicht auf"


def test_jeder_szenario_regler_hat_einen_anderen_wert_in_der_testtabelle():
    assert set(ANDERER_WERT) == {k for k, s in P.SETTING_SPECS.items() if s.szenario}
    assert set(ANDERER_EXPERIMENT_WERT) == {k for k, s in P.SETTING_SPECS.items() if not s.szenario}
    for key, wert in {**ANDERER_WERT, **ANDERER_EXPERIMENT_WERT}.items():
        assert wert != P.SETTING_SPECS[key].default, key


@pytest.mark.parametrize("state_key", list(ANDERER_WERT))
def test_jede_aenderung_eines_szenario_reglers_hebt_die_hervorhebung_auf(state_key):
    at = _app()
    at.session_state[state_key] = ANDERER_WERT[state_key]
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    assert "primary" not in _typen(at).values(), state_key
    # erneutes Anklicken markiert wieder
    name = next(iter(C.PRESETS))
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert _typen(at)[name] == "primary"


@pytest.mark.parametrize("state_key", list(ANDERER_EXPERIMENT_WERT))
def test_experiment_regler_aendern_das_preset_nicht_und_laufen_ohne_fehler(state_key):
    at = _app()
    at.session_state[state_key] = ANDERER_EXPERIMENT_WERT[state_key]
    at.run()
    assert not at.exception, (state_key, [str(e) for e in at.exception])
    assert _typen(at)[next(iter(C.PRESETS))] == "primary"
