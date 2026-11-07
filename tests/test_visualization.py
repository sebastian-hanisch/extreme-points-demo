"""3D-Darstellung: Die Dreiecke eines Quaders decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab (die Lehre aus pack_demo: eine falsche Dreiecksliste lässt ein Loch im Quader),
die Abbildung enthält genau die Quader, Eckpunkte und Schichten, die sie zeigen soll."""

import ept_algorithm as A
import ept_constants as C
import ept_evaluation as ev
import ept_visualization as V


def flaeche_dreieck(a, b, c):
    """Fläche eines Dreiecks im Raum (Betrag des halben Kreuzprodukts)."""
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    kreuz = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return (kreuz[0] ** 2 + kreuz[1] ** 2 + kreuz[2] ** 2) ** 0.5 / 2


def test_dreiecke_decken_jede_seitenflaeche_genau_zweimal_halb_ab():
    w, d, h = 3, 5, 7
    e = V.ecken(0, 0, 0, w, d, h)
    seiten = {"unten": (2, w * d), "oben": (2, w * d), "vorn": (2, w * h), "hinten": (2, w * h), "links": (2, d * h), "rechts": (2, d * h)}
    ebenen = {"unten": lambda p: p[2] == 0, "oben": lambda p: p[2] == h, "vorn": lambda p: p[1] == 0, "hinten": lambda p: p[1] == d, "links": lambda p: p[0] == 0, "rechts": lambda p: p[0] == w}
    summe = {name: 0.0 for name in seiten}
    anzahl = {name: 0 for name in seiten}
    for t in V.DREIECKE:
        pts = [e[i] for i in t]
        in_ebenen = [name for name in seiten if all(ebenen[name](p) for p in pts)]
        assert len(in_ebenen) == 1, t                                # jedes Dreieck liegt in genau einer Seitenfläche
        name = in_ebenen[0]
        anzahl[name] += 1
        summe[name] += flaeche_dreieck(*pts)
    assert len(V.DREIECKE) == 12
    for name, (n_dreiecke, flaeche) in seiten.items():
        assert anzahl[name] == n_dreiecke and abs(summe[name] - flaeche) < 1e-9, name      # zwei Dreiecke, zusammen die ganze Fläche (kein Loch, keine Doppelung)


def test_dreiecke_einer_seite_ueberlappen_nicht():
    """Die zwei Dreiecke einer Seite teilen sich genau die Diagonale: genau zwei gemeinsame Ecken."""
    for a in range(0, 12, 2):
        s1, s2 = set(V.DREIECKE[a]), set(V.DREIECKE[a + 1])
        assert len(s1 & s2) == 2 and len(s1 | s2) == 4


def test_die_zwoelf_kanten_verbinden_benachbarte_ecken():
    e = V.ecken(0, 0, 0, 2, 3, 4)
    for a, b in V.KANTEN:
        verschieden = sum(1 for i in range(3) if e[a][i] != e[b][i])
        assert verschieden == 1                                      # eine Kante ändert genau eine Koordinate
    assert len(V.KANTEN) == 12 and len({frozenset(k) for k in V.KANTEN}) == 12


def test_abbildung_enthaelt_quader_rahmen_und_eckpunkte(mini):
    bins, platz, zustand = A.pack(mini.kisten, [0, 1, 2, 3], 10, A.EP_VOLL)
    fig = V.build_behaelter(mini.kisten, platz, 0, 10, zustand[0], A.EP_VOLL)
    meshes = [t for t in fig.data if t.type == "mesh3d"]
    assert len(meshes) == 4 and all(len(m.x) == 8 and len(m.i) == 12 for m in meshes)
    marker = [t for t in fig.data if t.type == "scatter3d" and t.mode == "markers"]
    assert len(marker) == 1 and len(marker[0].x) == len(zustand[0])
    linien = [t for t in fig.data if t.type == "scatter3d" and t.mode == "lines"]
    assert len(linien) == 2                                         # Rahmen und Kanten der Quader


def test_abbildung_zeigt_nur_den_gewaehlten_behaelter_und_bei_schichten_ihre_oberkanten(mini):
    bins, platz, zustand = A.pack(mini.kisten, [0, 1, 2, 3], 10, A.SCHICHTEN)           # [[0, 1, 2], [3]]
    fig0 = V.build_behaelter(mini.kisten, platz, 0, 10, zustand[0], A.SCHICHTEN)
    fig1 = V.build_behaelter(mini.kisten, platz, 1, 10, zustand[1], A.SCHICHTEN)
    assert len([t for t in fig0.data if t.type == "mesh3d"]) == 3 and len([t for t in fig1.data if t.type == "mesh3d"]) == 1
    # Oberkanten der Schichten: eine gestrichelte Linie je Schicht (zwei im ersten, eine im zweiten Behälter), Höhe z + h
    gestrichelt = [t for t in fig0.data if t.type == "scatter3d" and t.line.dash == "dash"]
    assert [list(t.z)[0] for t in gestrichelt] == [2, 10] and len([t for t in fig1.data if t.type == "scatter3d" and t.line.dash == "dash"]) == 1
    assert not [t for t in fig0.data if t.type == "scatter3d" and t.mode == "markers"]


def test_leerer_behaelter_und_leerer_zustand_werfen_nicht():
    fig = V.build_behaelter((), [], 0, 10, (), A.EP_VOLL)
    assert len([t for t in fig.data if t.type == "mesh3d"]) == 0
    fig = V.build_behaelter((), [], 0, 10, (), A.SCHICHTEN)
    assert len(fig.data) == 1


def test_messdiagramm_hat_je_verfahren_einen_balken_je_schluessel():
    m = {k: {v: float(k + v) for v in range(3)} for k in range(5)}
    fig = V.build_messung(m, "Titel")
    assert len(fig.data) == 3 and all(len(t.x) == 5 for t in fig.data)
    assert [t.name for t in fig.data] == [C.VERFAHREN_KURZ[v] for v in range(3)] and list(fig.data[1].y) == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert fig.layout.xaxis.fixedrange and fig.layout.yaxis.fixedrange


def test_abbildung_zur_analyse_der_app():
    a = ev.analyse(ev.Settings())
    fig = V.build_behaelter(a.inst.kisten, a.platz, a.gezeigt, a.inst.cap, a.zustand[a.gezeigt], a.settings.verfahren)
    assert len([t for t in fig.data if t.type == "mesh3d"]) == a.inst.n          # Beispiel 1 mit EP voll und Volumen: alle zwölf Quader in einem Behälter
