"""Randfälle: leere Eingabe, ein Quader, Quader gleich Behälter, genau passende Plätze, Gleichstände, Schritte, ungültige Eingaben, Grenzen der Regler."""

import pytest

import ept_algorithm as A
import ept_constants as C
import ept_evaluation as ev
from ept_scenario import Instance, mess_seed, zufallsinstanz

VERFAHREN = range(3)


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_leere_eingabe_ergibt_keine_behaelter(verfahren):
    assert A.pack((), [], 10, verfahren) == ([], [], [])
    assert A.schranken((), 10) == (0, 0, 0)
    assert A.stuetz_kennzahlen((), []) == (0, 0)


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_ein_quader_und_quader_gleich_behaelter(verfahren):
    bins, platz, _ = A.pack(((7, 3, 5),), [0], 10, verfahren)
    assert bins == [[0]] and platz == [(0, 0, 0, 0, 0)]
    bins, platz, _ = A.pack(((10, 10, 10), (1, 1, 1)), [0, 1], 10, verfahren)
    assert bins == [[0], [1]] and platz == [(0, 0, 0, 0, 0), (1, 1, 0, 0, 0)]


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_acht_gleiche_wuerfel_fuellen_den_behaelter_genau(verfahren):
    kisten = ((5, 5, 5),) * 8
    bins, platz, _ = A.pack(kisten, list(range(8)), 10, verfahren)
    assert bins == [list(range(8))] and A.packung_pruefen(kisten, platz, 10)
    assert sorted((x, y, z) for _i, _b, x, y, z in platz) == [(x, y, z) for x in (0, 5) for y in (0, 5) for z in (0, 5)]
    bins, _, _ = A.pack(((5, 5, 5),) * 9, list(range(9)), 10, verfahren)
    assert len(bins) == 2                                                            # der neunte braucht einen neuen Behälter


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_kein_platz_oeffnet_einen_neuen_behaelter(verfahren):
    # zwei Quader der Höhe 6 und 5 über der ganzen Grundfläche passen nicht übereinander (11 > 10)
    bins, _, _ = A.pack(((10, 10, 6), (10, 10, 5)), [0, 1], 10, verfahren)
    assert bins == [[0], [1]]


def test_projektion_findet_den_platz_ueber_zwei_quadern():
    # Von Hand (Behälter 10): A (6,10,2) bei (0,0,0), dann B (4,10,6) bei (6,0,0). Die Ecke über B ist (6,0,6); ihre Projektion in -x gleitet über A hinweg (A endet bei z = 2) bis zur Wand: (0,0,6).
    # C (10,10,4) passt nur dorthin (bei (6,0,6) wäre er zu breit); ohne Projektionen gibt es den Punkt (0,0,6) nicht, und C braucht einen neuen Behälter.
    # D (6,10,2) passt danach bei (0,0,2) zwischen A und C.
    kisten = ((6, 10, 2), (4, 10, 6), (10, 10, 4), (6, 10, 2))
    voll = A.pack(kisten, [0, 1, 2, 3], 10, A.EP_VOLL)
    assert voll[0] == [[0, 1, 2, 3]] and voll[1] == [(0, 0, 0, 0, 0), (1, 0, 6, 0, 0), (2, 0, 0, 0, 6), (3, 0, 0, 0, 2)]
    einfach = A.pack(kisten, [0, 1, 2, 3], 10, A.EP_EINFACH)
    assert einfach[0] == [[0, 1, 3], [2]] and (2, 1, 0, 0, 0) in einfach[1]


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_anfang_der_reihenfolge_ist_der_anfang_der_packung(verfahren):
    kisten = zufallsinstanz(1, 20, 3).kisten
    order = A.reihenfolge(kisten, A.VOLUMEN)
    voll = A.pack(kisten, order, 100, verfahren)[1]
    for k in (0, 1, 7, 19, 20):
        assert A.pack(kisten, order[:k], 100, verfahren)[1] == voll[:k]


def test_gleichstaende_der_schluessel_bleiben_in_lieferreihenfolge():
    kisten = ((3, 3, 3), (3, 3, 3), (1, 1, 1), (3, 3, 3))
    for schluessel in (A.VOLUMEN, A.GRUNDFLAECHE, A.HOEHE, A.KANTE):
        assert A.reihenfolge(kisten, schluessel) == [0, 1, 3, 2]


def test_ungueltige_instanzen_werden_abgelehnt():
    for kisten in (((0, 3, 3),), ((11, 3, 3),), ((3, 3),), ((3.5, 2, 2),), ((3, 3, 3, 3),)):
        with pytest.raises(ValueError):
            Instance(kisten, 10)
    with pytest.raises(ValueError):
        Instance(((1, 1, 1),), 0)


def test_analyse_an_den_grenzen_der_regler():
    for quelle in C.QUELLEN:
        for n_index in range(len(C.N_WERTE)):
            for seed in (0, C.SEED_MAX):
                for schritt in (0, 1, 12, 13, 200):
                    a = ev.analyse(ev.Settings(quelle, n_index, seed, A.VOLUMEN, A.EP_VOLL, schritt, 50))
                    assert A.packung_pruefen(a.inst.kisten, a.platz, a.inst.cap, vollstaendig=False)
                    assert 0 <= a.gezeigt < max(1, len(a.bins)) and 1 <= a.schritt <= a.inst.n
    a = ev.analyse(ev.Settings(0, 0, 7, 1, 2, 3, 1))
    assert a.schritt == 3 and len(a.platz) == 3
    assert ev.wirksamer_schritt(ev.Settings(schritt=0), 12) == 12 and ev.wirksamer_schritt(ev.Settings(schritt=13), 12) == 12 and ev.wirksamer_schritt(ev.Settings(schritt=-4), 12) == 12


def test_der_gezeigte_behaelter_wird_auf_den_letzten_begrenzt():
    a = ev.analyse(ev.Settings(1, 0, 7, 0, A.SCHICHTEN, 0, 1))          # Beispiel 2, Lieferung, Schichten: fünf Behälter
    assert a.count == 5 and a.gezeigt == 0
    for wunsch, erwartet in ((2, 1), (5, 4), (6, 4), (50, 4)):
        assert ev.analyse(ev.Settings(1, 0, 7, 0, A.SCHICHTEN, 0, wunsch)).gezeigt == erwartet
    assert ev.analyse(ev.Settings(1, 0, 7, 0, A.SCHICHTEN, 2, 5)).gezeigt == len(ev.analyse(ev.Settings(1, 0, 7, 0, A.SCHICHTEN, 2, 5)).bins) - 1      # nach 2 Quadern gibt es weniger Behälter


def test_zufallsinstanzen_wachsen_mit_n_und_bleiben_im_bereich():
    for v, (_, _, bereiche) in enumerate(C.VERTEILUNGEN):
        for n in C.N_WERTE:
            inst = zufallsinstanz(v, n, mess_seed(v, 0, 5))
            assert inst.n == n and all(bereiche[a][0] <= k[a] <= bereiche[a][1] for k in inst.kisten for a in range(3))


def test_mess_seeds_sind_verschieden():
    seeds = {mess_seed(v, ni, j) for v in range(4) for ni in range(4) for j in range(C.INSTANZEN)}
    assert len(seeds) == 4 * 4 * C.INSTANZEN
