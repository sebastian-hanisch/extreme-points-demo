"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Behälter 10 mal 10 mal 10; Quader 0: (4, 4, 2), 1: (2, 5, 8), 2: (7, 5, 2), 3: (4, 8, 2); Volumen 246, Schranke 1), Reihenfolge 0, 1, 2, 3:
  Extreme Points voll: E = {(0,0,0)}. 0 -> (0,0,0); neue Ecken (4,0,0), (0,4,0), (0,0,2), ihre Projektionen fallen auf sie selbst (an der Wand).    E = {(4,0,0), (0,4,0), (0,0,2)}
      1 (2,5,8): tiefster, hinterster, linkester Punkt (4,0,0) passt (x 4 bis 6, kein Überlapp mit 0) -> (4,0,0); neue Ecken (6,0,0), (4,5,0), (4,0,8); Projektionen: (4,5,0) in -x bis zur Fläche von
      Quader 0? Nein, Quader 0 reicht nur bis y = 4, also bis zur Wand: (0,5,0); (4,0,8) in -x: Quader 0 reicht nur bis z = 2, also (0,0,8).
      E = {(6,0,0), (0,4,0), (0,5,0), (4,5,0), (0,0,2), (0,0,8), (4,0,8)}.
      2 (7,5,2): (6,0,0) zu breit (13), (0,4,0) überlappt Quader 1 (y 4 bis 5), (0,5,0) passt -> (0,5,0); neue Ecken (7,5,0) mit Projektion (7,0,0), (0,10,0) entfällt (an der Decke), (0,5,2) mit
      Projektion (0,0,2); (4,5,0) liegt im Quader 2 und entfällt.   E = {(6,0,0), (7,0,0), (0,4,0), (7,5,0), (0,0,2), (0,5,2), (0,0,8), (4,0,8)}
      3 (4,8,2): (6,0,0) überlappt Quader 2 (x 6 bis 7), die anderen z = 0 sind zu breit oder überlappen Quader 1, (0,0,2) passt (z 2 bis 4 auf Quader 0 und 2) -> (0,0,2).   => ein Behälter.
  Extreme Points einfach: wie oben bis Quader 1, aber E = {(6,0,0), (0,4,0), (4,5,0), (0,0,2), (4,0,8)}. 2 (7,5,2): (6,0,0) zu breit, (0,4,0) überlappt 1, (4,5,0) zu breit (11), (0,0,2) überlappt 1,
      (4,0,8) zu breit -> neuer Behälter, (0,0,0). 3 (4,8,2): Behälter 0 enthält nur die Quader 0 und 1, der erste Punkt (6,0,0) passt (x 6 bis 10, y 0 bis 8, z 0 bis 2; Quader 1 endet bei x = 6) -> [[0, 1, 3], [2]].
  Schichten: 0 -> Schicht 0 (z = 0, Höhe 2), Regal 0 (y = 0, Tiefe 4, belegt x bis 4). 1 (2,5,8): Höhe 8 > 2, neue Schicht z = 2 (Höhe 8), 2 + 8 = 10 passt -> (0,0,2). 2 (7,5,2): Schicht 0, Regal 0 hat Tiefe
      4 < 5, neues Regal bei y = 4 (4 + 5 = 9) -> (0,4,0). 3 (4,8,2): Schicht 0: Regal-Tiefen 4 und 5 reichen nicht, ein neues Regal bei y = 9 passt nicht (9 + 8 > 10); Schicht 1: ein neues Regal bei
      y = 5 passt nicht (5 + 8 > 10); eine dritte Schicht bei z = 10 passt nicht -> neuer Behälter.   => [[0, 1, 2], [3]]
Stützfläche: Quader 3 in der Packung von EP voll liegt bei z = 2 über Quader 0 (4 mal 4 = 16) und Quader 2 (x 0 bis 4, y 5 bis 8: 4 mal 3 = 12): 28 von 32 = 87,5 %.
"""

import pytest

import ept_algorithm as A
import ept_constants as C
from ept_scenario import beispiel


def test_reihenfolge_je_schluessel_mit_gleichstaenden_in_lieferreihenfolge(mini):
    k = mini.kisten                      # Volumen 32, 80, 70, 64; Grundfläche 16, 10, 35, 32; Höhe 2, 8, 2, 2; längste Kante 4, 8, 7, 8
    assert A.reihenfolge(k, A.LIEFERUNG) == [0, 1, 2, 3]
    assert A.reihenfolge(k, A.VOLUMEN) == [1, 2, 3, 0]
    assert A.reihenfolge(k, A.GRUNDFLAECHE) == [2, 3, 0, 1]
    assert A.reihenfolge(k, A.HOEHE) == [1, 0, 2, 3]                  # 8, dann dreimal 2 in Lieferreihenfolge
    assert A.reihenfolge(k, A.KANTE) == [1, 3, 2, 0]                  # 8 und 8 in Lieferreihenfolge, dann 7, dann 4
    assert A.schluessel_wert(k, A.VOLUMEN) == [32, 80, 70, 64] and A.schluessel_wert(k, A.LIEFERUNG) == [0, 0, 0, 0]


def test_extreme_points_voll_auf_der_mini_instanz_mit_den_eckpunkten(mini):
    bins, platz, zustand = A.pack(mini.kisten, [0, 1, 2, 3], 10, A.EP_VOLL)
    assert bins == [[0, 1, 2, 3]] and platz == [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)]
    # Schritt für Schritt: der Zustand nach k Quadern ist der Zustand des Anfangs der Reihenfolge
    assert A.pack(mini.kisten, [0], 10, A.EP_VOLL)[2] == [((4, 0, 0), (0, 4, 0), (0, 0, 2))]
    assert A.pack(mini.kisten, [0, 1], 10, A.EP_VOLL)[2] == [((6, 0, 0), (0, 4, 0), (0, 5, 0), (4, 5, 0), (0, 0, 2), (0, 0, 8), (4, 0, 8))]
    assert A.pack(mini.kisten, [0, 1, 2], 10, A.EP_VOLL)[2] == [((6, 0, 0), (7, 0, 0), (0, 4, 0), (7, 5, 0), (0, 0, 2), (0, 5, 2), (0, 0, 8), (4, 0, 8))]


def test_extreme_points_einfach_auf_der_mini_instanz(mini):
    bins, platz, zustand = A.pack(mini.kisten, [0, 1, 2, 3], 10, A.EP_EINFACH)
    assert bins == [[0, 1, 3], [2]] and platz == [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 1, 0, 0, 0), (3, 0, 6, 0, 0)]
    assert A.pack(mini.kisten, [0, 1], 10, A.EP_EINFACH)[2] == [((6, 0, 0), (0, 4, 0), (4, 5, 0), (0, 0, 2), (4, 0, 8))]


def test_schichten_auf_der_mini_instanz_mit_den_schichten(mini):
    bins, platz, zustand = A.pack(mini.kisten, [0, 1, 2, 3], 10, A.SCHICHTEN)
    assert bins == [[0, 1, 2], [3]] and platz == [(0, 0, 0, 0, 0), (1, 0, 0, 0, 2), (2, 0, 0, 4, 0), (3, 1, 0, 0, 0)]
    assert zustand == [((0, 2), (2, 8)), ((0, 2),)]            # je Behälter die Schichten (z, Höhe)
    assert A.pack(mini.kisten, [0, 1], 10, A.SCHICHTEN)[2] == [((0, 2), (2, 8))]


def test_anzahl_je_schluessel_und_verfahren_der_mini_instanz(mini):
    assert A.anzahl(mini.kisten, A.LIEFERUNG, A.EP_VOLL, 10) == 1 and A.anzahl(mini.kisten, A.LIEFERUNG, A.EP_EINFACH, 10) == 2 and A.anzahl(mini.kisten, A.LIEFERUNG, A.SCHICHTEN, 10) == 2


def test_schranken_der_mini_instanz(mini):
    assert A.schranken(mini.kisten, 10) == (1, 0, 1) and A.schranke(mini.kisten, 10) == 1
    # drei große Quader (alle Kanten über 5) brauchen drei Behälter, obwohl das Volumen (3 mal 216 = 648 von 1000 je Behälter) nur einen fordert
    assert A.schranken(((6, 6, 6), (6, 6, 6), (6, 6, 6)), 10) == (1, 3, 3)
    assert A.schranken(((5, 9, 9), (9, 5, 9)), 10) == (1, 0, 1)       # genau die Hälfte zählt nicht als groß
    assert A.schranken(((10, 10, 10), (10, 10, 10), (1, 1, 1)), 10) == (3, 2, 3)


def test_stuetzflaeche_der_mini_instanz_von_hand(mini):
    _, platz, _ = A.pack(mini.kisten, [0, 1, 2, 3], 10, A.EP_VOLL)
    assert [A.stuetzflaeche(mini.kisten, platz, i) for i in (0, 1, 2)] == [1.0, 1.0, 1.0]        # am Boden
    assert A.stuetzflaeche(mini.kisten, platz, 3) == 28 / 32
    assert A.stuetz_kennzahlen(mini.kisten, platz) == (0, 0)                                        # 87,5 % sind nicht unter 80 %


def test_stuetzflaeche_grenzen_und_schwebende_quader():
    # Quader 1 liegt voll auf Quader 0 (1,0), Quader 2 schwebt darüber bei z = 6 (0,0)
    kisten = ((10, 10, 2), (4, 4, 2), (4, 4, 2))
    platz = [(0, 0, 0, 0, 0), (1, 0, 0, 0, 2), (2, 0, 0, 5, 6)]
    assert A.packung_pruefen(kisten, platz, 10)
    assert [A.stuetzflaeche(kisten, platz, i) for i in (0, 1, 2)] == [1.0, 1.0, 0.0]
    assert A.stuetz_kennzahlen(kisten, platz) == (1, 1)                  # der schwebende Quader zählt auch als unter 80 %
    # genau 80 % zählen nicht als darunter: Quader 1 (5 mal 4) liegt auf x 4 bis 9, Quader 0 reicht bis x = 8: 4 mal 4 = 16 von 20
    kisten2 = ((8, 10, 2), (5, 4, 2))
    platz2 = [(0, 0, 0, 0, 0), (1, 0, 4, 0, 2)]
    assert A.packung_pruefen(kisten2, platz2, 10) and A.stuetzflaeche(kisten2, platz2, 1) == 0.8 and A.stuetz_kennzahlen(kisten2, platz2) == (0, 0)
    # 3 mal 4 = 12 von 20 = 60 %: Quader 1 auf x 2 bis 7, Quader 0 (Breite 5) reicht bis x = 5
    kisten3 = ((5, 10, 2), (5, 4, 2))
    platz3 = [(0, 0, 0, 0, 0), (1, 0, 2, 0, 2)]
    assert A.stuetzflaeche(kisten3, platz3, 1) == pytest.approx(0.6) and A.stuetz_kennzahlen(kisten3, platz3) == (1, 0)
    # Quader aus anderen Behältern und Oberseiten in anderer Höhe tragen nicht
    kisten4 = ((10, 10, 2), (4, 4, 2))
    assert A.stuetzflaeche(kisten4, [(0, 0, 0, 0, 0), (1, 1, 0, 0, 2)], 1) == 0.0
    assert A.stuetzflaeche(kisten4, [(0, 0, 0, 0, 0), (1, 0, 0, 0, 3)], 1) == 0.0


def test_packung_pruefen_erkennt_fehler(mini):
    gut = [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)]
    assert A.packung_pruefen(mini.kisten, gut, 10)
    assert not A.packung_pruefen(mini.kisten, gut[:3], 10) and A.packung_pruefen(mini.kisten, gut[:3], 10, vollstaendig=False)
    assert not A.packung_pruefen(mini.kisten, gut + [(0, 1, 0, 0, 0)], 10)                          # Quader 0 doppelt
    assert not A.packung_pruefen(mini.kisten, [(0, 0, 0, 0, 0), (1, 0, 3, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)], 10)    # Quader 1 bei x = 3 überlappt Quader 0
    assert not A.packung_pruefen(mini.kisten, [(0, 0, 0, 0, 0), (1, 0, 4, 0, 3), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)], 10)    # Quader 1 bei z = 3 ragt über die Decke (3 + 8 > 10)
    assert A.packung_pruefen(mini.kisten, [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 1, 0, 0, 0)], 10)         # Berührung ist keine Überlappung, anderer Behälter
    assert not A.packung_pruefen(mini.kisten, [(0, 0, -1, 0, 0), (1, 0, 4, 0, 0), (2, 0, 0, 5, 0), (3, 0, 0, 0, 2)], 10)    # negative Lage
    assert not A.packung_pruefen(mini.kisten, [(9, 0, 0, 0, 0)], 10, vollstaendig=False)             # Nummer außerhalb
    # drei Achsen: ein Paar überlappt nur, wenn es in allen drei Achsen überlappt (je Achse einzeln trennen genügt)
    k2 = ((4, 4, 4), (4, 4, 4))
    assert A.packung_pruefen(k2, [(0, 0, 0, 0, 0), (1, 0, 4, 0, 0)], 10) and A.packung_pruefen(k2, [(0, 0, 0, 0, 0), (1, 0, 0, 4, 0)], 10) and A.packung_pruefen(k2, [(0, 0, 0, 0, 0), (1, 0, 0, 0, 4)], 10)
    assert not A.packung_pruefen(k2, [(0, 0, 0, 0, 0), (1, 0, 3, 3, 3)], 10)


def test_pack_lehnt_ungueltige_eingaben_ab(mini):
    with pytest.raises(ValueError):
        A.pack(mini.kisten, [0, 0], 10, A.EP_VOLL)
    with pytest.raises(ValueError):
        A.pack(mini.kisten, [4], 10, A.EP_VOLL)
    with pytest.raises(ValueError):
        A.pack(((11, 3, 3),), [0], 10, A.EP_VOLL)
    with pytest.raises(ValueError):
        A.pack(((0, 3, 3),), [0], 10, A.EP_VOLL)
    with pytest.raises(ValueError):
        A.pack(((3, 3),), [0], 10, A.EP_VOLL)
    with pytest.raises(ValueError):
        A.pack(mini.kisten, [0], 10, 3)


def test_beispiele_der_app_mit_den_angaben_der_konstanten():
    """Die Behälterzahlen der beiden Handbeispiele aus dem Kommentar der Konstanten (Zeilen: Lieferung, Volumen, Grundfläche, Höhe, Kante; Spalten: Schichten, EP einfach, EP voll)."""
    b1 = [[A.anzahl(beispiel(0).kisten, k, v, C.CAP) for v in range(3)] for k in range(5)]
    b2 = [[A.anzahl(beispiel(1).kisten, k, v, C.CAP) for v in range(3)] for k in range(5)]
    assert b1 == [[2, 2, 2], [2, 2, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2]]
    assert b2 == [[5, 3, 3], [5, 2, 2], [5, 2, 2], [3, 2, 2], [3, 3, 2]]
    assert [A.schranke(beispiel(i).kisten, C.CAP) for i in (0, 1)] == [1, 1] and C.BEISPIEL_OPTIMUM == {0: 1, 1: 2}
    assert [sum(w * d * h for w, d, h in beispiel(i).kisten) for i in (0, 1)] == [563801, 981902]
