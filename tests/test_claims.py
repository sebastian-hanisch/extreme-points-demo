"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (ept_precomputed.json): jede Zelle bis n = 40 frisch gerechnet, bei n = 80 die ersten drei Instanzen einzeln (Stichprobe in der Datei); alle Zellen vollständig prüft
  `python generate_precomputed.py --check` (parallel). Die Optima bei 12 und 20 Quadern stammen aus CP-SAT und werden stichprobenweise noch einmal gerechnet.
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import ept_algorithm as A
import ept_constants as C
import ept_evaluation as ev
from ept_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
KLEINE_ZELLEN = [(v, ni) for v, ni in ZELLEN if C.MESS_N[ni] <= 40]
BUD_VOLUMEN, BUD_HOEHE = C.VOLUMEN, C.HOEHE


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def gerundete():
    return {k: ev.gerundet(ev.referenz(z)[1]) for k, z in alle().items()}


def _opt(v, ni):
    return ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)].get("opt")


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.CAP == 100 and daten["cpsat_zeit"] == C.CPSAT_ZEIT == 30.0
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN} and len(ZELLEN) == 16
    assert set(daten["stichprobe"]) == set(daten["zellen"])
    for (v, ni), n in ((k, C.MESS_N[k[1]]) for k in ZELLEN):
        z = daten["zellen"][ev.zelle_schluessel(v, ni)]
        assert ("opt" in z) == (n in C.EXAKT_N)
        if "opt" in z:
            assert len(z["opt"]) == 100
        assert set(daten["stichprobe"][ev.zelle_schluessel(v, ni)]) == {str(j) for j in C.STICHPROBE_J}


@pytest.mark.parametrize("v,ni", KLEINE_ZELLEN)
def test_jede_zelle_bis_n_40_stimmt_mit_frischer_rechnung(v, ni):
    gespeichert = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    opt = gespeichert.get("opt")
    frisch = ev.messzelle(v, ni, opt)
    if opt is not None:
        frisch["opt"] = opt
    assert frisch == gespeichert


def _addiere(a, b):
    if isinstance(a, dict):
        return {k: _addiere(a[k], b[k]) for k in a}
    if isinstance(a, list):
        return [x + y for x, y in zip(a, b)]
    return a + b


def _nicht_kleiner(a, b):
    if isinstance(a, dict):
        return all(_nicht_kleiner(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return all(x >= y for x, y in zip(a, b))
    return a >= b


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_stichprobe_jeder_zelle_stimmt_mit_frischer_rechnung(v, ni):
    schl = ev.zelle_schluessel(v, ni)
    daten = ev.vorberechnet()
    summe = None
    for j in C.STICHPROBE_J:
        gespeichert = daten["stichprobe"][schl][str(j)]
        assert ev.messzelle(v, ni, _opt(v, ni), [j]) == gespeichert, (schl, j)
        summe = gespeichert if summe is None else {k: _addiere(summe[k], gespeichert[k]) for k in gespeichert}
    zelle = daten["zellen"][schl]
    for k in summe:                          # die Stichprobe ist Teil der Zelle: jede Summe der Zelle ist mindestens so groß (alle Beiträge sind nicht negativ)
        assert _nicht_kleiner(zelle[k], summe[k]), (schl, k)


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_summen_sind_in_sich_stimmig(v, ni):
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    k = C.INSTANZEN
    assert sum(z["ep_voll_gegen_schichten"]) == k and sum(z["ep_voll_gegen_ep_einfach"]) == k and 0 <= z["gross_ueber_volumen"] <= k
    assert 0 <= z["stuetz_schwebend"] <= z["stuetz_unter80"] <= k * C.MESS_N[ni]                  # schwebend zählt auch als unter 80 %
    for kk in "01234":
        assert all(z["ueber_schranke"][kk][vv] >= 0 for vv in "012")
    if "opt" in z:
        offen = z["opt"].count(-1)
        assert z["entschieden"] == k - offen and z["opt_ueber_schranke"] <= z["entschieden"] and z["opt_minus_schranke"] >= 0
        for kk in "01234":
            assert all(0 <= z["trifft_opt"][kk][vv] <= z["entschieden"] and z["ueber_opt"][kk][vv] >= 0 for vv in "012")


def test_gespeicherte_optima_liegen_zwischen_schranke_und_der_besten_kombination():
    """Für jede entschiedene Instanz bei 12 und 20 Quadern: Schranke <= Optimum <= beste der 15 Kombinationen (die Packung mit dieser Zahl existiert)."""
    for v, ni in ZELLEN:
        if C.MESS_N[ni] not in C.EXAKT_N:
            continue
        for j, o in enumerate(_opt(v, ni)):
            if o < 0:
                continue
            inst = zufallsinstanz(v, C.MESS_N[ni], mess_seed(v, ni, j))
            assert A.schranke(inst.kisten, inst.cap) <= o <= min(min(r) for r in ev.tabelle(inst)), (v, ni, j)


@pytest.mark.parametrize("n", C.EXAKT_N)
@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_stichprobe_der_optima_stimmt_mit_cpsat_ueberein(v, n):
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    ni = C.MESS_N.index(n)
    opt = _opt(v, ni)
    for j in range(5):
        inst = zufallsinstanz(v, n, mess_seed(v, ni, j))
        ober = min(min(r) for r in ev.tabelle(inst))
        untergrenze = A.schranke(inst.kisten, inst.cap)
        ist = ober if ober == untergrenze else optimum_cpsat(inst.kisten, inst.cap, ober, C.CPSAT_ZEIT, 2)
        assert ist == opt[j] >= untergrenze, (v, n, j)


# --- Beispiele ------------------------------------------------------------------------------------------------------------------------------------


def test_beispiele_sind_instanzen_des_rasters_mit_dem_optimum_von_cpsat():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for b, j in ((0, 45), (1, 4)):
        inst = zufallsinstanz(0, 12, mess_seed(0, 0, j))
        assert inst.kisten == beispiel(b).kisten
        ober = min(min(r) for r in ev.tabelle(inst))
        opt = ober if ober == A.schranke(inst.kisten, inst.cap) else optimum_cpsat(inst.kisten, inst.cap, ober, 60.0, 2)
        assert opt == _opt(0, 0)[j] == C.BEISPIEL_OPTIMUM[b]
    assert C.BEISPIEL_OPTIMUM == {0: 1, 1: 2}


def test_beispiel_tabellen_in_der_readme():
    t1, t2 = ev.tabelle(beispiel(0)), ev.tabelle(beispiel(1))
    assert [[t1[k][v] for v in range(3)] for k in range(5)] == [[2, 2, 2], [2, 2, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2]]
    assert [[t2[k][v] for v in range(3)] for k in range(5)] == [[5, 3, 3], [5, 2, 2], [5, 2, 2], [3, 2, 2], [3, 3, 2]]
    assert "Beispiel 1 (zwölf Quader, Schranke 1, Optimum 1)" in README and "Beispiel 2 (zwölf andere Quader, Schranke 1, Optimum 2)" in README
    assert "das finden nur **EP voll mit Volumen**. Alle anderen 14 Kombinationen brauchen **2**" in README
    assert [(k, v) for k in range(5) for v in range(3) if t1[k][v] == 1] == [(C.VOLUMEN, C.EP_VOLL)] and sum(t1[k][v] == 2 for k in range(5) for v in range(3)) == 14
    assert [t2[k][0] for k in range(5)] == [5, 5, 5, 3, 3] and [k for k in range(1, 5) if t2[k][2] == 2] == [1, 2, 3, 4]
    assert "Schichten brauchen mit jedem Schlüssel **3 bis 5** Behälter, EP voll mit Volumen, Grundfläche, Höhe und Kante **2**" in README


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_instanz_fuer_instanz_zaehlungen():
    z = alle()
    schichten = [sum(x["voll_gegen_schichten"][i] for x in z.values()) for i in range(3)]
    einfach = [sum(x["voll_gegen_einfach"][i] for x in z.values()) for i in range(3)]
    assert schichten == [1100, 500, 0] and sum(schichten) == 1600 and einfach == [275, 1308, 17] and sum(einfach) == 1600
    assert "in **1100** von 1600 Instanzen weniger Behälter, in 500 gleich viele und in **0** mehr" in README
    assert "in **275** von 1600 Instanzen weniger Behälter, in 1308 gleich viele und in **17** mehr" in README
    assert all(x["voll_gegen_schichten"][2] == 0 for x in z.values())


def test_mittelwerte_ep_voll_gegen_schichten_und_ep_einfach():
    g = gerundete()
    gegen_hoehe = ([k for k, x in g.items() if x[BUD_VOLUMEN][C.EP_VOLL] < x[BUD_HOEHE][C.SCHICHTEN]], [k for k, x in g.items() if x[BUD_VOLUMEN][C.EP_VOLL] == x[BUD_HOEHE][C.SCHICHTEN]])
    assert len(gegen_hoehe[0]) == 14 and gegen_hoehe[1] == [(2, 0), (2, 1)]                # klein, n = 12 und 20
    gegen_einfach = [sum(x[BUD_VOLUMEN][C.EP_VOLL] < x[BUD_VOLUMEN][C.EP_EINFACH] for x in g.values()), sum(x[BUD_VOLUMEN][C.EP_VOLL] == x[BUD_VOLUMEN][C.EP_EINFACH] for x in g.values()),
                     sum(x[BUD_VOLUMEN][C.EP_VOLL] > x[BUD_VOLUMEN][C.EP_EINFACH] for x in g.values())]
    assert gegen_einfach == [14, 2, 0]
    assert "braucht EP voll mit Volumen in **14** von 16 Zellen weniger Behälter als Schichten mit Höhe" in README and "in zwei gleich (kleine Quader bei 12 und 20: ein Behälter genügt)" in README
    assert "im Mittel in **14** von 16 Zellen weniger, in zwei gleich, in keiner mehr" in README


def test_bester_schluessel_je_verfahren():
    g = gerundete()

    def zaehlung(verfahren):
        alleine, gleichauf, alle_gleich = {}, [], []
        for zelle, x in g.items():
            beste = ev.beste_schluessel_zelle(x, verfahren)
            if len(beste) == 5:
                alle_gleich.append(zelle)
            elif len(beste) == 1:
                alleine[beste[0]] = alleine.get(beste[0], 0) + 1
            else:
                gleichauf.append((zelle, beste))
        return alleine, gleichauf, alle_gleich

    assert zaehlung(C.SCHICHTEN) == ({C.HOEHE: 14, C.VOLUMEN: 2}, [], [])
    alleine, gleichauf, alle_gleich = zaehlung(C.EP_VOLL)
    assert alleine == {C.VOLUMEN: 14} and gleichauf == [((2, 1), [1, 2, 3, 4])] and alle_gleich == [(2, 0)]
    assert zaehlung(C.EP_EINFACH)[0][C.VOLUMEN] == 9
    assert [z for z, x in g.items() if ev.beste_schluessel_zelle(x, C.SCHICHTEN) == [C.VOLUMEN]] == [(3, 1), (3, 3)]
    assert round(g[(3, 1)][C.VOLUMEN][C.SCHICHTEN] - g[(3, 1)][C.HOEHE][C.SCHICHTEN], 2) == -0.01 and round(g[(3, 3)][C.VOLUMEN][C.SCHICHTEN] - g[(3, 3)][C.HOEHE][C.SCHICHTEN], 2) == -0.06
    assert "Bei Schichten die **Höhe** in 14 Zellen (das Volumen in zwei: flach bei n = 20 und n = 80, mit Abständen von 0,01 und 0,06)" in README
    assert "bei EP voll das **Volumen** in **14** Zellen (bei kleinen Quadern mit n = 20 gleichauf mit Grundfläche, Höhe und Kante, bei n = 12 alle fünf gleich); bei EP einfach ist es das Volumen in 9 Zellen allein (in 4 weiteren gleichauf)" in README
    mittel80 = g[(0, 3)]
    assert (mittel80[C.VOLUMEN][C.SCHICHTEN], mittel80[C.HOEHE][C.SCHICHTEN]) == (3.75, 2.99) and "mittlere Quader, n = 80: 3,75 gegen 2,99" in README


def test_optimum_getroffen_schranke_locker_und_offene_instanzen():
    zeilen = ev.optimum_zeilen()
    assert len(zeilen) == 8

    def spanne(n, k):
        return (min(round(r[k]) for r in zeilen if r["n"] == n), max(round(r[k]) for r in zeilen if r["n"] == n))

    assert [spanne(12, k) for k in ("schichten", "einfach", "voll")] == [(31, 100), (44, 100), (48, 100)]
    assert [spanne(20, k) for k in ("schichten", "einfach", "voll")] == [(3, 100), (40, 100), (49, 100)]
    assert [r["n"] for r in zeilen if all(round(r[k]) == 100 for k in ("schichten", "einfach", "voll"))] == [12, 20] and [r["verteilung"] for r in zeilen if round(r["voll"]) == 100] == [2, 2]
    assert ("treffen bei 12 Quadern Schichten 31 bis 100 %, EP einfach 44 bis 100 %, EP voll 48 bis 100 % der entschiedenen Instanzen das Optimum, bei 20 Quadern 3 bis 100 %, "
            "40 bis 100 % und 49 bis 100 % (100 % nur bei kleinen Quadern)") in README
    z = alle()
    ueber12 = [z[(v, 0)]["opt_ueber_schranke"] for v in range(4)]
    ueber20 = [z[(v, 1)]["opt_ueber_schranke"] for v in range(4)]
    ent12, ent20 = [z[(v, 0)]["entschieden"] for v in range(4)], [z[(v, 1)]["entschieden"] for v in range(4)]
    assert (ueber12, sum(ueber12), sum(ent12)) == ([41, 53, 0, 59], 153, 399) and (sum(ueber20), sum(ent20)) == (91, 395)
    assert sum(x["gross_ueber_volumen"] for x in z.values()) == 11
    assert "in **153** von 399 entschiedenen Instanzen über der Schranke (41 mittel, 53 breit, 0 klein, 59 flach), bei 20 in **91** von 395; große Quader liegen nur in **11** von 1600 Instanzen über der Volumenschranke" in README
    offen12, offen20 = [z[(v, 0)]["offen"] for v in range(4)], [z[(v, 1)]["offen"] for v in range(4)]
    assert (sum(offen12), offen20, sum(offen20)) == (1, [2, 1, 0, 2], 5)
    assert "**1** von 400 bei 12 und **5** von 400 bei 20 Quadern (2 bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 2 bei flachen bei 20)" in README
    assert "die nicht entschiedenen Instanzen (1 und 5 von je 400) sind die für CP-SAT schweren" in README


def test_stuetzflaeche_in_der_readme():
    zeilen = ev.stuetz_zeilen()
    assert len(zeilen) == 16
    assert (min(round(r["unter80"]) for r in zeilen), max(round(r["unter80"]) for r in zeilen)) == (2, 43)
    assert (round(min(r["schwebend"] for r in zeilen), 1), round(max(r["schwebend"] for r in zeilen), 1)) == (0.1, 4.2)
    flach = [round(r["unter80"]) for r in zeilen if r["verteilung"] == 3]
    assert (min(flach), max(flach)) == (41, 43)
    assert "haben **2 bis 43 %** der Quader weniger als 80 % Stützfläche (flache Quader 41 bis 43 %), und **0,1 bis 4,2 %** schweben ohne jede Stütze" in README
    assert ev.verdict_stuetz_raster(zeilen)[0] == "warning"


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Texte ---------------------------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"Behälter {C.CAP} mal {C.CAP} mal {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and "(12, 20, 40, 80)" in t and "30 Sekunden Zeitlimit" in t and "bei 12 und 20 Quadern" in t
    assert C.MESS_N == (12, 20, 40, 80) and C.EXAKT_N == (12, 20) and C.CPSAT_ZEIT == 30.0


def test_readme_nennt_die_verteilungen_und_das_raster_wie_der_code():
    assert "*mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)" in README
    assert [vt[2] for vt in C.VERTEILUNGEN] == [((20, 60),) * 3, ((5, 70),) * 3, ((10, 40),) * 3, ((30, 80), (30, 80), (5, 30))]
    assert "vier Verteilungen × vier Quaderzahlen (12, 20, 40, 80) × **100 feste Instanzen** je Zelle × fünf Schlüssel × drei Verfahren" in README


def test_readme_hat_keine_offenen_platzhalter_ausser_dem_live_link():
    ohne_link = README.replace("<!-- TODO nach dem Deploy", "")
    assert "{{" not in README and "TESTZAHL" not in README and ohne_link.count("TODO") == 0
