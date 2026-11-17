"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und die erwartete Aussage je Preset (Verdikt, kein Preset ohne Wirkung meldet eine Wirkung)."""

import pat_constants as C
import pat_evaluation as E
import pat_presets as P


def _settings(preset):
    return E.Settings(quelle=preset["quelle"], folge=preset["folge"], n=preset["n"], d=preset["d"], seed=preset["seed"], gleiche=preset["gleiche"])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["quelle"] in C.QUELLEN and preset["gleiche"] in C.GLEICHE and preset["d"] in C.D_OPTIONEN, name
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name
        werte, meldung = E.parse_folge(preset["folge"])
        assert meldung is None and werte is not None, name


def test_default_preset_equals_the_default_settings():
    erstes = next(iter(C.PRESETS.values()))
    assert _settings(erstes) == E.Settings()


def test_setting_specs_cover_every_preset_key_and_szenario_regler():
    assert set(P.PRESET_KEYS.values()) == {k for k, s in P.SETTING_SPECS.items() if s.szenario}
    for key, spec in P.SETTING_SPECS.items():
        assert spec.default is not None and (spec.options is None or spec.default in spec.options), key


def test_erwartete_aussage_je_preset():
    """Jedes Preset meldet die Zahl, die von Hand nachgerechnet ist (DEMO-PLAYBOOK §11a Punkt 7)."""
    erwartet = {
        "Handbeispiel (1, 3, 5, 2, 4)": ("success", "legt **3** Stapel", "**2** Stapel: Zwischenausgabe spart 1"),
        "Aldous/Diaconis, n = 10": ("success", "legt **5** Stapel", "n = 10 ist nicht aufgezählt"),
        "Bereits in Abholreihenfolge": ("success", "legt **8** Stapel", "**1** Stapel: Zwischenausgabe spart 7"),
        "Umkehrfolge": ("success", "legt **1** Stapel", "beide **1** Stapel"),
        "Zielgruppen mit Gleichständen": ("info", "genügen **3** Stapel", None),
    }
    for name, (kind, text1, text3) in erwartet.items():
        a = E.analyse(_settings(C.PRESETS[name]))
        k1, t1 = E.verdict_patience(a, "erster")
        assert k1 == kind and text1 in t1, name
        if text3:
            assert text3 in E.verdict_faden_folge(a)[1] or text3 in t1, name


def test_zufallspresets_ziehen_permutationen_der_richtigen_laenge():
    a = E.analyse(_settings(C.PRESETS["Zufallsfolge, n = 9"]))
    assert a.art == "perm" and len(a.folge) == 9 and "Modell U" in a.herkunft
    b = E.analyse(_settings(C.PRESETS["Fast sortierte Ankunft (D = 0,5)"]))
    assert b.art == "perm" and len(b.folge) == 10 and "Modell V" in b.herkunft and "D = 0,5" in b.herkunft
    assert b.lis >= 7                                    # D = 0,5: fast in Ankunftsreihenfolge, die LIS ist lang
    assert b.sofort[0] <= 2
