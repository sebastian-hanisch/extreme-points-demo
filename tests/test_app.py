"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und die Zahlenfelder an ihre Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import ept_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
WUERFEL = "🎲 Neue Zufallsinstanz würfeln"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"quelle_select", "n_select", "schluessel_select", "verfahren_select", "exp_verteilung", "exp_n"} <= set(keys)
    werte = {"quelle_select": list(C.QUELLEN), "n_select": list(range(len(C.N_WERTE))), "schluessel_select": list(C.SCHLUESSEL), "verfahren_select": list(C.VERFAHREN),
             "exp_verteilung": list(range(len(C.VERTEILUNGEN))), "exp_n": list(range(len(C.MESS_N)))}
    for key in keys:
        for wert in werte[key]:
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_zahlenfelder_an_ihren_grenzen_loesen_keinen_fehler_aus():
    for quelle in (0, 5):
        for wert in (0, C.SEED_MAX):
            at = _fresh_app()
            at.selectbox(key="quelle_select").set_value(quelle).run(timeout=TIMEOUT)
            at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (quelle, wert, [str(e) for e in at.exception])
    for key, werte in (("schritt_input", (0, 1, 5, 12, 13, 200)), ("behaelter_input", (1, 2, 50))):
        for wert in werte:
            at = _fresh_app()
            at.number_input(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_vom_beispiel_zu_einer_zufallsinstanz():
    at = _fresh_app()
    assert at.selectbox(key="quelle_select").value == 0
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 2 and not at.exception
    at.selectbox(key="quelle_select").set_value(5).run(timeout=TIMEOUT)
    seed_vorher = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 5 and at.number_input(key="seed_input").value != seed_vorher


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    texte = [e.value for e in at.info] + [e.value for e in at.success] + [e.value for e in at.warning]
    assert any("Nach dem Volumen sortiert und mit EP voll gesetzt brauchen die Quader **1** Behälter, in Lieferreihenfolge 2." in t and "Das ist das Optimum (die Schranke allein ergäbe 1)." in t for t in texte)


def test_schritt_regler_zeigt_den_zustand_und_haelt_die_grenzen():
    at = _fresh_app()
    for wert, erwartet in ((0, 12), (1, 1), (5, 5), (12, 12), (13, 12), (200, 12)):
        at.number_input(key="schritt_input").set_value(wert).run(timeout=TIMEOUT)
        assert not at.exception, (wert, [str(e) for e in at.exception])
        assert any(f"Zustand nach {erwartet} von 12 Quadern" in m.value for m in at.markdown), wert


def test_behaelter_regler_zeigt_den_gewaehlten_oder_den_letzten_behaelter():
    at = _fresh_app()
    at.selectbox(key="quelle_select").set_value(1).run(timeout=TIMEOUT)                # Beispiel 2
    at.selectbox(key="schluessel_select").set_value(0).run(timeout=TIMEOUT)            # Lieferung
    at.selectbox(key="verfahren_select").set_value(0).run(timeout=TIMEOUT)             # Schichten: fünf Behälter
    for wert, erwartet in ((1, 1), (3, 3), (5, 5), (6, 5), (50, 5)):
        at.number_input(key="behaelter_input").set_value(wert).run(timeout=TIMEOUT)
        assert not at.exception, (wert, [str(e) for e in at.exception])
        assert any(f"Behälter {erwartet} von 5:" in m.value for m in at.markdown), wert


def test_expander_stehen_unter_ihren_namen():
    labels = [e.label for e in _fresh_app().expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels


def test_stuetzkennzahl_steht_unter_dem_ergebnis():
    at = _fresh_app()
    assert any("Stehen die Quader sicher?" in m.value for m in at.markdown)
    assert any("In dieser Packung haben **4** von 12 Quadern weniger als 80 % Stützfläche, **0** schweben ohne jede Stütze." in i.value for i in at.info)       # Beispiel 1, Volumen, EP voll
