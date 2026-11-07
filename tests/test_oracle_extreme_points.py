"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 30 Sekunden.

  Extreme Points (einfach, voll)  gegen  eine Umsetzung, die die Eckpunkte nicht fortschreibt, sondern nach jedem Quader aus der Liste der bisherigen Quader NEU erzeugt (Erzeugungsregel einmal je
                                          Quader gegen die Quader davor, danach alle Punkte im Inneren eines Quaders streichen).
  Schichten                       gegen  eine naive Neuberechnung (Schichten und Regale jedes Mal aus der Platzierungsliste gelesen).
  Stützfläche                     gegen  ein Voxelraster: je Zelle der Grundfläche, ob die Zelle darunter von einem anderen Quader desselben Behälters belegt ist.
  Optimum                         gegen  CP-SAT (nie über der Packung, nie unter der Schranke), in tests/test_claims.py für die Optima des Rasters.
  Eigenschaften:  Packungen zulässig (unabhängiger Prüfer) und nie unter der Schranke, gemeinsames Skalieren, Zustand ist der Anfang der Packung, jeder Eckpunkt liegt auf drei Flächen
                  oder Wänden, die Punkte von EP einfach sind unter den Punkten von EP voll nur dann enthalten, wenn beide gleich gesetzt haben.
"""

import random

import pytest

import ept_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=30, seed0=0, kante_hi=None):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        hi = kante_hi or cap
        yield cap, tuple(tuple(rng.randint(1, min(hi, cap)) for _ in range(3)) for _ in range(n))


# --- Extreme Points: Eckpunkte aus der Liste der Quader neu erzeugt ---------------------------------------------------------------------------------


def innen(p, q):
    return q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5]


def projektion(p, achse, davor):
    """Nächste Fläche in negativer Richtung der Achse unter den Quadern `davor` (jeder Quader (x, y, z, w, d, h)), sonst die Wand 0."""
    a, b = [k for k in range(3) if k != achse]
    kandidaten = [0]
    for q in davor:
        if q[achse] + q[3 + achse] <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            kandidaten.append(q[achse] + q[3 + achse])
    return max(kandidaten)


def eckpunkte_neu(gesetzt, cap, voll):
    """Alle Eckpunkte eines Behälters aus den gesetzten Quadern (in der Reihenfolge des Setzens), ohne eine laufende Menge: je Quader die drei Ecken (und bei `voll` deren Projektionen gegen die
    Quader davor), dann alle Punkte streichen, die an die Wand stoßen oder in einem Quader liegen."""
    punkte = {(0, 0, 0)}
    for s, q in enumerate(gesetzt):
        x, y, z, w, d, h = q
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            punkte.add(p)
            if voll:
                for a in achsen:
                    r = list(p)
                    r[a] = projektion(p, a, gesetzt[:s])
                    punkte.add(tuple(r))
    return sorted((p for p in punkte if max(p) < cap and not any(innen(p, q) for q in gesetzt)), key=lambda p: (p[2], p[1], p[0]))


def ep_naiv(kisten, order, cap, voll):
    """Extreme Points mit neu erzeugten Eckpunkten vor jedem Quader."""
    behaelter = []                                   # je Behälter: Liste (x, y, z, w, d, h) in der Reihenfolge des Setzens
    platz = []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, lst in enumerate(behaelter):
            for (x, y, z) in eckpunkte_neu(lst, cap, voll):
                if x + w <= cap and y + d <= cap and z + h <= cap and not any(A._ueberlappt((x, y, z, w, d, h), q) for q in lst):
                    wahl = (b, x, y, z)
                    break
            if wahl:
                break
        if wahl is None:
            behaelter.append([])
            wahl = (len(behaelter) - 1, 0, 0, 0)
        b, x, y, z = wahl
        behaelter[b].append((x, y, z, w, d, h))
        platz.append((i, b, x, y, z))
    return platz, behaelter


@pytest.mark.parametrize("verfahren,voll", [(A.EP_EINFACH, False), (A.EP_VOLL, True)])
def test_extreme_points_gegen_neu_erzeugte_eckpunkte(verfahren, voll):
    geprueft = mehrere_behaelter = viele_in_einem = 0
    for cap, kisten in list(instanzen(30, 1, 14, cap_lo=10, cap_hi=24, seed0=500)) + list(instanzen(30, 6, 16, cap_lo=12, cap_hi=24, seed0=600, kante_hi=7)):
        rng = random.Random(cap)
        for order in (A.reihenfolge(kisten, A.VOLUMEN), rng.sample(range(len(kisten)), len(kisten))):
            bins, platz, zustand = A.pack(kisten, order, cap, verfahren)
            platz_naiv, behaelter = ep_naiv(kisten, order, cap, voll)
            assert platz == platz_naiv, (cap, kisten, order)
            assert [list(z) for z in zustand] == [eckpunkte_neu(lst, cap, voll) for lst in behaelter], (cap, kisten, order)
            geprueft += 1
            mehrere_behaelter += len(bins) >= 2
            viele_in_einem += max(len(b) for b in bins) >= 4
    assert geprueft == 120 and mehrere_behaelter >= 40 and viele_in_einem >= 60          # der Test prüft wirklich etwas (nicht nur ein Quader je Behälter)


def test_projektionen_aendern_die_packung_in_vielen_instanzen():
    verschieden = 0
    for cap, kisten in list(instanzen(30, 6, 16, cap_lo=12, cap_hi=24, seed0=600, kante_hi=7)):
        order = A.reihenfolge(kisten, A.VOLUMEN)
        verschieden += A.pack(kisten, order, cap, A.EP_EINFACH)[1] != A.pack(kisten, order, cap, A.EP_VOLL)[1]
    assert verschieden >= 10


def test_eckpunkte_liegen_an_wand_oder_flaeche_und_nie_im_inneren():
    for cap, kisten in instanzen(25, 2, 14, cap_lo=10, cap_hi=30, seed0=700):
        for verfahren in (A.EP_EINFACH, A.EP_VOLL):
            bins, platz, zustand = A.pack(kisten, A.reihenfolge(kisten, A.VOLUMEN), cap, verfahren)
            for b, punkte in enumerate(zustand):
                gesetzt = [(x, y, z, *kisten[i]) for i, bb, x, y, z in platz if bb == b]
                for p in punkte:
                    assert max(p) < cap and not any(innen(p, q) for q in gesetzt), (cap, kisten, p)
                    for achse in range(3):
                        if p[achse] > 0:                       # in negativer Richtung jeder Achse liegt der Punkt auf einer Fläche (Rand eines Quaders) oder an der Wand
                            a, c = [k for k in range(3) if k != achse]
                            davor = [q for q in gesetzt if q[achse] + q[3 + achse] == p[achse] and q[a] <= p[a] <= q[a] + q[3 + a] and q[c] <= p[c] <= q[c] + q[3 + c]]
                            assert davor or any(q[achse] + q[3 + achse] == p[achse] for q in gesetzt), (cap, kisten, p, achse)


def test_gemeinsame_punkte_wenn_beide_verfahren_gleich_gesetzt_haben():
    """Nach dem ersten Quader haben beide Verfahren dieselbe Lage; EP voll hat dann mindestens die Punkte von EP einfach."""
    for cap, kisten in instanzen(25, 1, 1, cap_lo=10, cap_hi=30, seed0=900):
        einfach = A.pack(kisten, [0], cap, A.EP_EINFACH)[2][0]
        voll = A.pack(kisten, [0], cap, A.EP_VOLL)[2][0]
        assert set(einfach) <= set(voll) and A.pack(kisten, [0], cap, A.EP_EINFACH)[1] == A.pack(kisten, [0], cap, A.EP_VOLL)[1]


# --- Schichten: naive Neuberechnung -----------------------------------------------------------------------------------------------------------------


def schichten_naiv(kisten, order, cap):
    """Schichten ohne laufende Zähler: Schichten, Regale und belegte Breite werden vor jedem Quader aus der Platzierungsliste gelesen."""
    platz = []                                       # (Quader, Behälter, x, y, z)

    def schichten_von(b):
        zs = sorted({p[4] for p in platz if p[0] is not None and p[1] == b})
        return zs

    def lagen(b):
        """Schichten (z, Höhe) des Behälters: die Höhe ist die des Quaders, der zuerst auf dieser z-Ebene gesetzt wurde."""
        out = []
        for z in schichten_von(b):
            erster = next(p for p in platz if p[1] == b and p[4] == z)
            out.append((z, kisten[erster[0]][2]))
        return out

    def regale(b, z):
        """Regale der Schicht: (y, Tiefe, belegte Breite); Tiefe = Tiefe des ersten Quaders des Regals."""
        ys = sorted({p[3] for p in platz if p[1] == b and p[4] == z})
        out = []
        for y in ys:
            im = [p for p in platz if p[1] == b and p[4] == z and p[3] == y]
            out.append((y, kisten[im[0][0]][1], sum(kisten[p[0]][0] for p in im)))
        return out

    anzahl_b = 0
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b in range(anzahl_b):
            for z, hoehe in lagen(b):
                if h > hoehe:
                    continue
                rs = regale(b, z)
                for y, tiefe, belegt in rs:
                    if d <= tiefe and belegt + w <= cap:
                        wahl = (b, belegt, y, z)
                        break
                if wahl:
                    break
                y0 = sum(r[1] for r in rs)
                if y0 + d <= cap:
                    wahl = (b, 0, y0, z)
                    break
            if wahl:
                break
            z0 = sum(hh for _, hh in lagen(b))
            if z0 + h <= cap:
                wahl = (b, 0, 0, z0)
                break
        if wahl is None:
            wahl = (anzahl_b, 0, 0, 0)
            anzahl_b += 1
        b, x, y, z = wahl
        platz.append((i, b, x, y, z))
    return platz


def test_schichten_gegen_die_naive_zweitumsetzung():
    for cap, kisten in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=300):
        rng = random.Random(cap)
        for order in (A.reihenfolge(kisten, A.HOEHE), A.reihenfolge(kisten, A.VOLUMEN), rng.sample(range(len(kisten)), len(kisten))):
            assert A.pack(kisten, order, cap, A.SCHICHTEN)[1] == schichten_naiv(kisten, order, cap), (cap, kisten, order)


# --- Stützfläche: Voxelraster ----------------------------------------------------------------------------------------------------------------------


def stuetz_voxel(kisten, platz, i):
    """Anteil der Zellen (x, y) der Grundfläche von Quader i, unter denen die Zelle (x, y, z - 1) von einem anderen Quader desselben Behälters belegt ist (am Boden: alle)."""
    _, b, x0, y0, z0 = next(p for p in platz if p[0] == i)
    w, d, _h = kisten[i]
    if z0 == 0:
        return 1.0
    belegt = 0
    for x in range(x0, x0 + w):
        for y in range(y0, y0 + d):
            if any(j != i and bb == b and x2 <= x < x2 + kisten[j][0] and y2 <= y < y2 + kisten[j][1] and z2 <= z0 - 1 < z2 + kisten[j][2] for j, bb, x2, y2, z2 in platz):
                belegt += 1
    return belegt / (w * d)


def test_stuetzflaeche_gegen_das_voxelraster():
    for cap, kisten in instanzen(25, 2, 12, cap_lo=10, cap_hi=24, seed0=1100):
        for verfahren in (A.EP_EINFACH, A.EP_VOLL):
            platz = A.pack(kisten, A.reihenfolge(kisten, A.VOLUMEN), cap, verfahren)[1]
            for i in range(len(kisten)):
                assert A.stuetzflaeche(kisten, platz, i) == pytest.approx(stuetz_voxel(kisten, platz, i)), (cap, kisten, verfahren, i)
            u, s = A.stuetz_kennzahlen(kisten, platz)
            assert u == sum(stuetz_voxel(kisten, platz, i) < 0.8 - 1e-9 for i in range(len(kisten))) and s == sum(stuetz_voxel(kisten, platz, i) == 0 for i in range(len(kisten)))


# --- Eigenschaften ------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("verfahren", range(3))
def test_alle_packungen_sind_zulaessig_und_nie_unter_der_schranke(verfahren):
    for cap, kisten in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=1300):
        for schluessel in range(5):
            order = A.reihenfolge(kisten, schluessel)
            bins, platz, _ = A.pack(kisten, order, cap, verfahren)
            assert A.packung_pruefen(kisten, platz, cap) and len(bins) >= A.schranke(kisten, cap), (cap, kisten, schluessel)
            for b in bins:
                assert sum(kisten[i][0] * kisten[i][1] * kisten[i][2] for i in b) <= cap ** 3


@pytest.mark.parametrize("verfahren", range(3))
def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht(verfahren):
    for cap, kisten in instanzen(25, 1, 12, cap_lo=10, cap_hi=30, seed0=1500):
        gross = tuple(tuple(3 * x for x in k) for k in kisten)
        for k in range(5):
            assert A.anzahl(gross, k, verfahren, 3 * cap) == A.anzahl(kisten, k, verfahren, cap), (cap, kisten, k)


@pytest.mark.parametrize("verfahren", range(3))
def test_zustand_ist_der_anfang_der_packung(verfahren):
    for cap, kisten in instanzen(20, 2, 12, cap_lo=10, cap_hi=40, seed0=1700):
        order = A.reihenfolge(kisten, A.GRUNDFLAECHE)
        voll = A.pack(kisten, order, cap, verfahren)[1]
        for k in range(len(order) + 1):
            assert A.pack(kisten, order[:k], cap, verfahren)[1] == voll[:k]


def test_optimum_von_cpsat_liegt_zwischen_schranke_und_packung():
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    for cap, kisten in instanzen(8, 3, 7, cap_lo=10, cap_hi=20, seed0=1900):
        beste = min(A.anzahl(kisten, k, v, cap) for k in range(5) for v in range(3))
        opt = optimum_cpsat(kisten, cap, beste, 20.0, 2)
        assert opt >= 0 and A.schranke(kisten, cap) <= opt <= beste, (cap, kisten)
