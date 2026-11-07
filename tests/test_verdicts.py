"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen (kleiner als nach Rundung auf zwei Stellen, Gleichstand) und jede genannte Zahl direkt."""

import ept_constants as C
import ept_evaluation as ev
from ept_scenario import Instance

SCH, E1, EV = C.SCHICHTEN, C.EP_EINFACH, C.EP_VOLL


def _analysis(schluessel, verfahren, count, liefer, opt, tabelle, schranke=2, unter80=0, schwebend=0, n=12):
    inst = Instance(((5, 5, 5),) * n, 100)
    s = ev.Settings(schluessel=schluessel, verfahren=verfahren)
    return ev.Analysis(inst, tuple(range(n)), n, (), (), (), 0, count, liefer, schranke, opt, tabelle, unter80, schwebend, s)


def _tab(werte):
    """5 x 3 Tabelle: werte = {(schluessel, verfahren): Zahl}, sonst 5."""
    return tuple(tuple(werte.get((k, v), 5) for v in range(3)) for k in range(5))


def test_aktuell_ohne_sortieren_nennt_nur_die_lieferreihenfolge():
    t = _tab({(0, EV): 3, (1, EV): 2})
    kind, text = ev.verdict_aktuell(_analysis(0, EV, 3, 3, 2, t))
    assert kind == "info"
    assert text == ("In der Lieferreihenfolge brauchen die Quader mit EP voll **3** Behälter. Das Optimum ist **2**: 1 zu viel (die Schranke ist 2). "
                    "Für dieses Verfahren ist in der Tabelle Volumen besser (2).")


def test_aktuell_sortieren_spart_ist_ein_erfolg_und_nennt_das_optimum():
    t = _tab({(0, EV): 3, (1, EV): 2})
    kind, text = ev.verdict_aktuell(_analysis(1, EV, 2, 3, 2, t))
    assert kind == "success"
    assert text == ("Nach dem Volumen sortiert und mit EP voll gesetzt brauchen die Quader **2** Behälter, in Lieferreihenfolge 3. Sortieren spart hier 1. "
                    "Das ist das Optimum (die Schranke allein ergäbe 2). Für dieses Verfahren ist das einer der besten Schlüssel dieser Instanz.")


def test_aktuell_sortieren_schadet_ist_eine_warnung():
    t = _tab({(0, SCH): 3, (3, SCH): 4, (1, SCH): 2})
    kind, text = ev.verdict_aktuell(_analysis(3, SCH, 4, 3, None, t))
    assert kind == "warning" and "Sortieren schadet hier um 1." in text
    assert "Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist 2." in text and "Für dieses Verfahren ist in der Tabelle Volumen besser (2)." in text


def test_aktuell_gleich_viele_ist_info_und_mehrere_beste_schluessel_werden_genannt():
    t = _tab({(0, E1): 4, (1, E1): 3, (3, E1): 3, (4, E1): 4})
    kind, text = ev.verdict_aktuell(_analysis(4, E1, 4, 4, 3, t, schranke=1))
    assert kind == "info" and "Sortieren ändert hier nichts." in text and "Volumen oder Höhe besser (3)" in text
    assert "Das Optimum ist **3**: 1 zu viel (die Schranke ist 1)." in text


def test_spannen_und_tabellenverdikt():
    # Spannen: größter Unterschied der Verfahren innerhalb einer Zeile (Schlüssel), größter Unterschied der Schlüssel innerhalb einer Spalte (Verfahren)
    t = _tab({(1, SCH): 4, (1, E1): 3, (1, EV): 2})            # Zeile Volumen (4, 3, 2): Spanne 2; die anderen Zeilen (5, 5, 5): 0; Spalte Schichten (5, 4, 5, 5, 5): 1, EP einfach (5, 3, 5, 5, 5): 2, EP voll (5, 2, ...): 3
    assert ev.spannen(t) == (2, 3)
    t2 = _tab({(1, SCH): 2, (1, E1): 2, (1, EV): 2, (0, SCH): 9, (0, E1): 9, (0, EV): 9})
    assert ev.spannen(t2) == (0, 7)
    kind, text = ev.verdict_tabelle(_analysis(1, EV, 2, 9, 1, t2))
    assert kind == "warning" and "um bis zu **0**" in text and "um bis zu **7**" in text and "Hier zählt der Schlüssel mehr als das Verfahren." in text
    t3 = _tab({(1, SCH): 5, (1, E1): 3, (1, EV): 2})           # Zeile Volumen (5, 3, 2): 3; Spalte EP voll (5, 2, 5, 5, 5): 3
    assert ev.spannen(t3) == (3, 3)
    kind, text = ev.verdict_tabelle(_analysis(1, EV, 2, 5, 1, t3))
    assert kind == "info" and "Beide wirken hier gleich stark." in text
    t4 = _tab({(1, SCH): 6, (1, E1): 3, (1, EV): 2})           # Zeile Volumen (6, 3, 2): 4; Spalte EP voll: 3
    assert ev.spannen(t4) == (4, 3)
    kind, text = ev.verdict_tabelle(_analysis(1, EV, 2, 5, 1, t4))
    assert kind == "success" and "um bis zu **4**" in text and "um bis zu **3**" in text and "Hier zählt das Verfahren mehr als der Schlüssel." in text


def test_stuetz_verdikt_drei_zweige_und_die_zahlen():
    kind, text = ev.verdict_stuetz(_analysis(1, EV, 2, 2, 2, _tab({}), unter80=4, schwebend=1))
    assert kind == "warning" and text.startswith("In dieser Packung haben **4** von 12 Quadern weniger als 80 % Stützfläche, **1** schweben ohne jede Stütze.") and "würden in der Wirklichkeit nicht stehen" in text
    kind, text = ev.verdict_stuetz(_analysis(1, EV, 2, 2, 2, _tab({}), unter80=1, schwebend=0))
    assert kind == "info" and "**1** von 12" in text and "**0** schweben" in text and "Stück 10 verlangt eine Mindest-Stützfläche." in text
    kind, text = ev.verdict_stuetz(_analysis(1, EV, 2, 2, 2, _tab({}), unter80=0, schwebend=0))
    assert kind == "success" and "Alle Quader liegen auf mindestens 80 % ihrer Grundfläche auf" in text


# --- Messraster ----------------------------------------------------------------------------------------------------------------------------


def _mittel(werte):
    """werte = {(schluessel, verfahren): Mittel}, sonst 3,0."""
    return {k: {v: werte.get((k, v), 3.0) for v in range(3)} for k in range(5)}


def _z(werte, exakt=True, entschieden=100, offen=0, verteilung=0, n=12, voll_gegen_schichten=(60, 40, 0), voll_gegen_einfach=(10, 85, 5)):
    m = _mittel(werte)
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": n, "instanzen": 100, "exakt": exakt, "entschieden": entschieden, "offen": offen, "mittel_schranke": m,
            "mittel_opt": m if exakt and entschieden else None, "anteil_opt": None, "opt_minus_schranke": None, "opt_ueber_schranke": 0, "voll_gegen_schichten": voll_gegen_schichten,
            "voll_gegen_einfach": voll_gegen_einfach, "gross_ueber_volumen": 0, "stuetz_unter80": 0.0, "stuetz_schwebend": 0.0}


def test_messung_ep_voll_besser_ist_ein_erfolg_mit_allen_zahlen():
    z = _z({(3, SCH): 1.20, (1, SCH): 1.60, (1, E1): 0.70, (1, EV): 0.50, (3, EV): 0.90, (2, EV): 0.80, (4, EV): 0.95, (0, EV): 1.0})
    kind, text = ev.verdict_messung(z)
    assert kind == "success"
    assert text == ("Für mittlere Quader mit n = 12 ist der beste Schlüssel je Verfahren (Mittel über dem Optimum, 100 Instanzen): Schichten Höhe, EP einfach Volumen, EP voll Volumen. "
                    "Schichten mit Höhe 1.20; EP einfach mit Volumen 0.70; EP voll mit Volumen 0.50. **Extreme Points mit Projektionen und Volumen** sind hier besser als Schichten mit Höhe.")


def test_messung_gleich_nach_rundung_und_schlechter():
    basis = {(3, SCH): 1.20, (1, EV): 1.204}                          # beide 1,20 nach Rundung
    kind, text = ev.verdict_messung(_z(basis))
    assert kind == "info" and "Beide Kombinationen sind hier gleich gut." in text
    kind, text = ev.verdict_messung(_z({(3, SCH): 1.20, (1, EV): 1.206}))        # 1,21 gegen 1,20
    assert kind == "warning" and "Hier sind **Schichten mit Höhe** besser" in text
    kind, text = ev.verdict_messung(_z({(3, SCH): 1.206, (1, EV): 1.204}))       # 1,21 gegen 1,20
    assert kind == "success"


def test_messung_alle_schluessel_gleich_wird_so_genannt():
    kind, text = ev.verdict_messung(_z({}))
    assert "Schichten alle Schlüssel gleich, EP einfach alle Schlüssel gleich, EP voll alle Schlüssel gleich" in text and kind == "info"


def test_messung_offene_instanzen_und_schranke_als_basis():
    kind, text = ev.verdict_messung(_z({(1, EV): 0.5}, entschieden=73, offen=27, n=20))
    assert "73 Instanzen)" in text and "27 von 100 Instanzen sind nicht entschieden und fehlen im Mittel." in text
    kind, text = ev.verdict_messung(_z({(1, EV): 0.5}, exakt=False, entschieden=0, n=40, verteilung=3))
    assert text.startswith("Für flache Quader mit n = 40") and "(Mittel über der Schranke, 100 Instanzen)" in text
    assert "Bei dieser Quaderzahl fehlt das Optimum und die Schranke ist locker" in text and "nicht entschieden" not in text
    kind, text = ev.verdict_messung(_z({(1, EV): 0.5}, exakt=True, entschieden=0, offen=100))
    assert "über der Schranke" in text


def test_referenz_nimmt_das_optimum_nur_mit_entschiedenen_instanzen():
    assert ev.referenz(_z({}))[0] == "dem Optimum"
    assert ev.referenz(_z({}, exakt=False, entschieden=0))[0] == "der Schranke"
    assert ev.referenz(_z({}, entschieden=0, offen=100))[0] == "der Schranke"


def test_instanz_verdikt_drei_zweige():
    kind, text = ev.verdict_instanz(_z({}, voll_gegen_schichten=(60, 40, 0), voll_gegen_einfach=(10, 85, 5)))
    assert kind == "success"
    assert text == ("Von 100 Instanzen braucht EP voll mit Volumen in **60** weniger Behälter als Schichten mit Volumen, in 40 gleich viele und in 0 mehr. "
                    "Gegenüber EP einfach mit Volumen sind es 10 weniger, 85 gleich viele und 5 mehr. Extreme Points mit Projektionen sind hier das bessere Verfahren.")
    assert ev.verdict_instanz(_z({}, voll_gegen_schichten=(5, 90, 5)))[0] == "info" and "Beide Verfahren sind hier gleich gut." in ev.verdict_instanz(_z({}, voll_gegen_schichten=(5, 90, 5)))[1]
    kind, text = ev.verdict_instanz(_z({}, voll_gegen_schichten=(3, 90, 7)))
    assert kind == "warning" and "Hier sind Schichten besser." in text


def _zeile(v, n, schichten, einfach, voll, entschieden=100, offen=0):
    return {"verteilung": v, "n": n, "entschieden": entschieden, "offen": offen, "instanzen": 100, "schichten": schichten, "einfach": einfach, "voll": voll}


def test_optimum_verdikt_nennt_seltensten_und_haeufigsten_und_alle_zahlen():
    zeilen = [_zeile(0, 12, 31.0, 44.0, 48.0, 99, 1), _zeile(0, 20, 3.0, 40.0, 49.0), _zeile(2, 12, 100.0, 100.0, 100.0)]
    kind, text = ev.verdict_optimum(zeilen)
    assert kind == "info"
    assert text == ("EP voll mit Volumen trifft das Optimum am seltensten bei mittleren Quadern mit n = 12 (48 % der 99 entschiedenen Instanzen, Schichten mit Höhe 31 %, EP einfach mit Volumen 44 %) "
                    "und am häufigsten bei kleinen Quadern mit n = 12 (100 % der 100 entschiedenen Instanzen).")


def test_optimum_verdikt_gleichstand_nimmt_das_kleinere_n_dann_die_kleinere_verteilung():
    # alle Zeilen gleich: Der seltenste und der häufigste Fall sind dieselbe Zelle (kleinstes n, dann kleinste Verteilung)
    zeilen = [_zeile(1, 20, 1.0, 2.0, 50.0), _zeile(0, 20, 1.0, 2.0, 50.0), _zeile(2, 12, 1.0, 2.0, 50.0)]
    text = ev.verdict_optimum(zeilen)[1]
    assert "am seltensten bei kleinen Quadern mit n = 12" in text and "am häufigsten bei kleinen Quadern mit n = 12" in text
    text = ev.verdict_optimum(zeilen[:2])[1]
    assert "am seltensten bei mittleren Quadern mit n = 20" in text and "am häufigsten bei mittleren Quadern mit n = 20" in text


def test_optimum_verdikt_ohne_zeile_mit_optimum():
    z = _zeile(0, 12, None, None, None, 0, 100)
    assert ev.verdict_optimum([z]) == ("info", "Es gibt keine Zelle mit bekanntem Optimum.") and ev.verdict_optimum([]) == ("info", "Es gibt keine Zelle mit bekanntem Optimum.")


def test_stuetz_raster_verdikt_spanne_und_zelle_mit_dem_groessten_anteil():
    zeilen = [{"verteilung": 0, "n": 12, "unter80": 16.3, "schwebend": 2.0}, {"verteilung": 3, "n": 80, "unter80": 42.5, "schwebend": 4.2}, {"verteilung": 2, "n": 12, "unter80": 1.8, "schwebend": 0.1}]
    kind, text = ev.verdict_stuetz_raster(zeilen)
    assert kind == "warning"
    assert text.startswith("Ohne Stützbedingung haben in diesen Packungen **2 bis 42 %** der Quader weniger als 80 % Stützfläche (am meisten bei flachen Quadern mit n = 80), und 0.1 bis 4.2 % schweben ganz.")
    assert "Stück 10 führt die Stützfläche als Bedingung ein." in text


def test_zeile_rechnet_mittel_anteile_und_stuetz_prozente_aus_den_summen():
    summen = {str(k): {str(v): 4 * (k + v + 1) for v in range(3)} for k in range(5)}
    zelle = {"ueber_schranke": summen, "ep_voll_gegen_schichten": [3, 1, 0], "ep_voll_gegen_ep_einfach": [1, 2, 1], "gross_ueber_volumen": 1, "stuetz_unter80": 6, "stuetz_schwebend": 3,
             "entschieden": 2, "ueber_opt": summen, "trifft_opt": {str(k): {str(v): 1 for v in range(3)} for k in range(5)}, "opt_minus_schranke": 3, "opt_ueber_schranke": 1}
    daten = {"instanzen": 4, "cap": 100, "zellen": {"mittel|12": zelle}}
    z = ev.zeile(0, 0, daten)
    assert z["exakt"] and z["entschieden"] == 2 and z["offen"] == 2
    assert z["mittel_schranke"][1][2] == 4 * 4 / 4 and z["mittel_opt"][1][2] == 4 * 4 / 2 and z["anteil_opt"][2][0] == 50.0
    assert z["voll_gegen_schichten"] == (3, 1, 0) and z["opt_minus_schranke"] == 1.5
    assert z["stuetz_unter80"] == 100.0 * 6 / (12 * 4) and z["stuetz_schwebend"] == 100.0 * 3 / (12 * 4)
    ohne = {"instanzen": 4, "cap": 100, "zellen": {"mittel|40": {k: zelle[k] for k in ("ueber_schranke", "ep_voll_gegen_schichten", "ep_voll_gegen_ep_einfach", "gross_ueber_volumen", "stuetz_unter80", "stuetz_schwebend")}}}
    z = ev.zeile(0, 2, ohne)
    assert not z["exakt"] and z["offen"] == 0 and z["mittel_opt"] is None and z["anteil_opt"] is None
