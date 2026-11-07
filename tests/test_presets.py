"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import ept_algorithm as A
import ept_constants as C
import ept_evaluation as ev
import ept_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    schluessel = ("quelle_select", "n_select", "seed_input", "schluessel_select", "verfahren_select", "schritt_input", "behaelter_input")
    assert [P.SETTING_SPECS[k].default for k in schluessel] == [s.quelle, s.n_index, s.seed, s.schluessel, s.verfahren, s.schritt, s.behaelter]


def _a(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("Beispiel 1, Volumen, EP voll")
    assert eins.count == 1 == eins.opt and "Sie passen alle in einen Behälter, das Optimum." in C.PRESET_HELP["Beispiel 1, Volumen, EP voll"] and len(eins.bins) == 1 and len(eins.bins[0]) == 12
    zwei = _a("Beispiel 1, Volumen, EP einfach")
    assert zwei.count == 2 and zwei.opt == 1 and "Es werden zwei Behälter, obwohl einer genügt." in C.PRESET_HELP["Beispiel 1, Volumen, EP einfach"]
    drei = _a("Beispiel 2, Volumen, EP voll")
    assert drei.count == 2 == drei.opt and drei.schranke == 1 and "Die Schranke sagt einen Behälter, das Optimum sind zwei" in C.PRESET_HELP["Beispiel 2, Volumen, EP voll"]
    vier = _a("Beispiel 2, Lieferung, Schichten")
    assert vier.count == 5 and vier.opt == 2 and "fünf Behälter statt zwei" in C.PRESET_HELP["Beispiel 2, Lieferung, Schichten"]
    fuenf = _a("Mittlere Quader, 40 Stück, EP voll")
    assert (fuenf.count, fuenf.schranke, fuenf.inst.n, fuenf.unter80, fuenf.schwebend) == (5, 3, 40, 12, 1)
    hilfe = C.PRESET_HELP["Mittlere Quader, 40 Stück, EP voll"]
    assert "fünf Behälter bei Schranke 3" in hilfe and "12 von 40 Quadern" in hilfe and "einer schwebt" in hilfe
    assert all(A.packung_pruefen(x.inst.kisten, x.platz, x.inst.cap) for x in (eins, zwei, drei, vier, fuenf))


def test_beispiel_1_ist_nur_mit_projektionen_und_volumen_in_einem_behaelter():
    """Die Aussage „nur diese Kombination findet den einen Behälter“ der README: unter allen 15 Kombinationen braucht nur (Volumen, EP voll) einen Behälter."""
    a = _a("Beispiel 1, Volumen, EP voll")
    assert [(k, v) for k in range(5) for v in range(3) if a.tabelle[k][v] == 1] == [(C.VOLUMEN, C.EP_VOLL)]
