"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Regler an seine
Grenzen (auch unter den Quellen „Zufall, Modell U“ und „Zufall, Modell V“, wo die Folge-Regler wirken) und prüft, dass kein Python-Fehler auftritt - insbesondere
`StreamlitDuplicateElementId` (mehrere st.plotly_chart ohne eindeutiges key=) und `StreamlitAPIException` bei Reglern mit berechneten Grenzen (min == max).
Regler, die unter der gewählten Quelle abgeschaltet sind, setzt der Test über den Session State (AppTest darf abgeschaltete Regler nicht anklicken)."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import pat_constants as C

AUSWAHL = {"d_sel": C.D_OPTIONEN, "d_stich": C.D_OPTIONEN, "d_faden": C.D_FADEN_OPTIONEN}
APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "▶"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app(quelle=None) -> AppTest:
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    if quelle:
        at.session_state["quelle_sel"] = quelle
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _regler(bereich):
    """(Schlüssel, kleinster Wert, größter Wert) aller Schieber, Auswahl-Schieber und Zahlenfelder eines Bereichs (App, Seitenleiste)."""
    out = []
    for s in bereich.slider:
        art = type(s.value)                      # AppTest liefert die Grenzen als Gleitkomma, der Regler arbeitet mit Ganzzahlen
        out.append((s.key, art(s.min), art(s.max)))
    for s in bereich.select_slider:
        optionen = AUSWAHL[s.key]                # AppTest nennt die Optionen nur als angezeigten Text
        out.append((s.key, optionen[0], optionen[-1]))
    for s in bereich.number_input:
        art = type(s.value)
        out.append((s.key, art(s.min), art(s.max)))
    return out


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


@pytest.mark.parametrize("quelle", ["eingabe", "u", "v"])
def test_every_regler_at_its_min_and_max_does_not_raise(quelle):
    at0 = _fresh_app(quelle)
    regler = _regler(at0) if quelle == "eingabe" else _regler(at0.sidebar)     # unter den Zufallsquellen wirken die Regler der Seitenleiste
    assert regler, "keine Regler gefunden"
    for key, lo, hi in regler:
        for rand in (lo, hi):
            at = _fresh_app(quelle)
            at.session_state[key] = rand
            at.run(timeout=TIMEOUT)
            assert not at.exception, (quelle, key, rand, [str(e) for e in at.exception])
