"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in ept_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import ept_algorithm as A
import ept_constants as C
from ept_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "ept_precomputed.json"
SCHLUESSEL_LISTE = tuple(sorted(C.SCHLUESSEL))
VERFAHREN_LISTE = tuple(sorted(C.VERFAHREN))
VOLUMEN, HOEHE = C.VOLUMEN, C.HOEHE
SCHICHTEN, EP_EINFACH, EP_VOLL = C.SCHICHTEN, C.EP_EINFACH, C.EP_VOLL


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    schluessel: int = VOLUMEN
    verfahren: int = EP_VOLL
    schritt: int = 0            # 0 = alle Quader, sonst der Zwischenstand nach so vielen Quadern
    behaelter: int = 1          # welcher Behälter gezeichnet wird (1 = erster); größere Werte zeigen den letzten


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    order: tuple          # alle Quadernummern in der Reihenfolge, in der gepackt wird
    schritt: int          # Zahl der gesetzten Quader im gezeigten Zustand (1 bis n; bei n = 0: 0)
    bins: tuple           # Behälter (Quadernummern) im gezeigten Zustand
    platz: tuple          # Platzierungen im gezeigten Zustand
    zustand: tuple        # Schichten oder Eckpunkte je Behälter im gezeigten Zustand
    gezeigt: int          # Nummer (ab 0) des gezeichneten Behälters im gezeigten Zustand
    count: int            # Behälterzahl der ganzen Packung (alle Quader)
    liefer: int           # Behälterzahl in Lieferreihenfolge mit demselben Verfahren
    schranke: int
    opt: object           # Optimum (int) bei den Handbeispielen, sonst None
    tabelle: tuple        # tabelle[schluessel][verfahren] = Behälterzahl, 5 x 3
    unter80: int          # Quader der ganzen Packung mit Stützfläche unter 80 %
    schwebend: int        # Quader der ganzen Packung ohne jede Stütze
    settings: Settings


def tabelle(inst: Instance) -> tuple:
    """Behälterzahl für jede Kombination aus Schlüssel (Zeile) und Verfahren (Spalte)."""
    return tuple(tuple(A.anzahl(inst.kisten, k, v, inst.cap) for v in VERFAHREN_LISTE) for k in SCHLUESSEL_LISTE)


def wirksamer_schritt(settings: Settings, n: int) -> int:
    """Zahl der gezeigten Schritte: 0 oder mehr als n bedeutet alle Quader."""
    return n if settings.schritt <= 0 or settings.schritt > n else settings.schritt


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    order = A.reihenfolge(inst.kisten, s.schluessel)
    schritt = wirksamer_schritt(s, inst.n)
    bins_voll, platz_voll, _ = A.pack(inst.kisten, order, inst.cap, s.verfahren)
    assert A.packung_pruefen(inst.kisten, platz_voll, inst.cap)
    bins, platz, zustand = A.pack(inst.kisten, order[:schritt], inst.cap, s.verfahren)
    assert A.packung_pruefen(inst.kisten, platz, inst.cap, vollstaendig=False)
    tab = tabelle(inst)
    unter80, schwebend = A.stuetz_kennzahlen(inst.kisten, platz_voll)
    gezeigt = max(0, min(s.behaelter, len(bins)) - 1)
    return Analysis(inst, tuple(order), schritt, tuple(tuple(b) for b in bins), tuple(platz), tuple(zustand), gezeigt, len(bins_voll), tab[0][s.verfahren], A.schranke(inst.kisten, inst.cap),
                    C.BEISPIEL_OPTIMUM.get(s.quelle), tab, unter80, schwebend, s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def beste_schluessel(tab: tuple, verfahren: int) -> list:
    """Schlüssel mit der kleinsten Behälterzahl in der Spalte des Verfahrens."""
    spalte = [tab[k][verfahren] for k in SCHLUESSEL_LISTE]
    return [k for k in SCHLUESSEL_LISTE if tab[k][verfahren] == min(spalte)]


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Behälterzahl der ganzen Packung gegen die Lieferreihenfolge (gleiches Verfahren), gegen das Optimum, wo es bekannt ist, und gegen den besten Schlüssel."""
    s = a.settings
    schluessel = C.SCHLUESSEL_MIT[s.schluessel]
    verfahren = C.VERFAHREN_KURZ[s.verfahren]
    if a.opt is None:
        opt_teil = f" Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        opt_teil = f" Das ist das Optimum (die Schranke allein ergäbe {a.schranke})."
    else:
        opt_teil = f" Das Optimum ist **{a.opt}**: {a.count - a.opt} zu viel (die Schranke ist {a.schranke})."
    beste = beste_schluessel(a.tabelle, s.verfahren)
    bester = a.tabelle[beste[0]][s.verfahren]
    if a.count == bester:
        passt = " Für dieses Verfahren ist das einer der besten Schlüssel dieser Instanz."
    else:
        passt = f" Für dieses Verfahren ist in der Tabelle {' oder '.join(C.SCHLUESSEL_KURZ[k] for k in beste)} besser ({bester})."
    if s.schluessel == 0:
        return "info", f"In der Lieferreihenfolge brauchen die Quader mit {verfahren} **{a.count}** Behälter." + opt_teil + passt
    kopf = f"Nach {schluessel} sortiert und mit {verfahren} gesetzt brauchen die Quader **{a.count}** Behälter, in Lieferreihenfolge {a.liefer}."
    if a.count > a.liefer:
        return "warning", kopf + f" Sortieren schadet hier um {a.count - a.liefer}." + opt_teil + passt
    if a.count < a.liefer:
        return "success", kopf + f" Sortieren spart hier {a.liefer - a.count}." + opt_teil + passt
    return "info", kopf + " Sortieren ändert hier nichts." + opt_teil + passt


def spannen(t: tuple) -> tuple[int, int]:
    """(verfahren, schluessel) der 5 x 3 Tabelle: größter Unterschied zwischen den Verfahren innerhalb einer Zeile; größter Unterschied zwischen den Schlüsseln innerhalb einer Spalte."""
    verfahren = max(max(z) - min(z) for z in t)
    schluessel = max(max(t[k][v] for k in range(len(t))) - min(t[k][v] for k in range(len(t))) for v in range(len(t[0])))
    return verfahren, schluessel


def verdict_tabelle(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was verändert die Behälterzahl mehr, das Verfahren oder der Schlüssel? Gezählt über die ganze 5 x 3 Tabelle dieser Instanz."""
    verfahren, schluessel = spannen(a.tabelle)
    teil = (f"Zwischen den drei Verfahren unterscheidet sich die Behälterzahl bei gleichem Schlüssel um bis zu **{verfahren}**; "
            f"zwischen den fünf Schlüsseln bei gleichem Verfahren um bis zu **{schluessel}**.")
    if verfahren > schluessel:
        return "success", teil + " Hier zählt das Verfahren mehr als der Schlüssel."
    if verfahren == schluessel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier zählt der Schlüssel mehr als das Verfahren."


def verdict_stuetz(a: Analysis) -> tuple[str, str]:
    """Verdikt zur Stützfläche der ganzen Packung: Quader mit weniger als 80 % Stützfläche und Quader ohne jede Stütze. Die Packung kennt hier keine Stützbedingung (Stück 10 führt sie ein)."""
    n = a.inst.n
    teil = f"In dieser Packung haben **{a.unter80}** von {n} Quadern weniger als 80 % Stützfläche, **{a.schwebend}** schweben ohne jede Stütze."
    if a.schwebend > 0:
        return "warning", teil + " Dieses Stück kennt keine Stützbedingung: Solche Quader würden in der Wirklichkeit nicht stehen."
    if a.unter80 > 0:
        return "info", teil + " Dieses Stück kennt keine Stützbedingung; Stück 10 verlangt eine Mindest-Stützfläche."
    return "success", teil + " Alle Quader liegen auf mindestens 80 % ihrer Grundfläche auf (ohne dass dieses Stück das verlangt)."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, opt: list | None = None, instanzen=None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über INSTANZEN feste Instanzen (oder nur über die Nummern `instanzen`, so rechnen die Tests
    Stichproben nach).

    ueber_schranke[k][v] = Summe über alle Instanzen von (Behälter mit Schlüssel k und Verfahren v minus Schranke). ep_voll_gegen_schichten und ep_voll_gegen_ep_einfach: [weniger, gleich, mehr] =
    Zahl der Instanzen, in denen EP voll mit Volumen weniger, gleich viele, mehr Behälter braucht als Schichten mit Volumen beziehungsweise EP einfach mit Volumen. gross_ueber_volumen: Zahl der
    Instanzen, in denen die Schranke „große Quader“ über der Volumenschranke liegt. stuetz_unter80 und stuetz_schwebend: Summe über die Quader aller Instanzen (EP voll mit Volumen) mit Stützfläche
    unter 80 % beziehungsweise ohne jede Stütze. Mit `opt` (Optimum je Instanz, -1 = nicht entschieden) zusätzlich, nur über die entschiedenen Instanzen: ueber_opt[k][v], trifft_opt[k][v] (Zahl der
    Instanzen mit Behälter gleich Optimum), opt_minus_schranke (Summe), opt_ueber_schranke (Zahl der Instanzen mit Optimum über der Schranke) und entschieden."""
    n = C.MESS_N[n_index]
    ks = [str(k) for k in SCHLUESSEL_LISTE]
    vs = [str(v) for v in VERFAHREN_LISTE]
    out = {"ueber_schranke": {k: dict.fromkeys(vs, 0) for k in ks}, "ep_voll_gegen_schichten": [0, 0, 0], "ep_voll_gegen_ep_einfach": [0, 0, 0], "gross_ueber_volumen": 0,
           "stuetz_unter80": 0, "stuetz_schwebend": 0}
    if opt is not None:
        out.update({"entschieden": 0, "ueber_opt": {k: dict.fromkeys(vs, 0) for k in ks}, "trifft_opt": {k: dict.fromkeys(vs, 0) for k in ks}, "opt_minus_schranke": 0, "opt_ueber_schranke": 0})
    for j in (range(C.INSTANZEN) if instanzen is None else instanzen):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        volumen, gross, s = A.schranken(inst.kisten, inst.cap)
        t = tabelle(inst)
        out["gross_ueber_volumen"] += gross > volumen
        for k in SCHLUESSEL_LISTE:
            for v in VERFAHREN_LISTE:
                out["ueber_schranke"][str(k)][str(v)] += t[k][v] - s
        voll, schicht, einfach = t[VOLUMEN][EP_VOLL], t[VOLUMEN][SCHICHTEN], t[VOLUMEN][EP_EINFACH]
        out["ep_voll_gegen_schichten"][0 if voll < schicht else 1 if voll == schicht else 2] += 1
        out["ep_voll_gegen_ep_einfach"][0 if voll < einfach else 1 if voll == einfach else 2] += 1
        platz = A.pack(inst.kisten, A.reihenfolge(inst.kisten, VOLUMEN), inst.cap, EP_VOLL)[1]
        u, sw = A.stuetz_kennzahlen(inst.kisten, platz)
        out["stuetz_unter80"] += u
        out["stuetz_schwebend"] += sw
        if opt is not None and opt[j] >= 0:
            out["entschieden"] += 1
            out["opt_minus_schranke"] += opt[j] - s
            out["opt_ueber_schranke"] += opt[j] > s
            for k in SCHLUESSEL_LISTE:
                for v in VERFAHREN_LISTE:
                    out["ueber_opt"][str(k)][str(v)] += t[k][v] - opt[j]
                    out["trifft_opt"][str(k)][str(v)] += t[k][v] == opt[j]
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    n = C.MESS_N[n_index]
    exakt = "entschieden" in z
    e = z.get("entschieden", 0)

    def tab(summen, nenner):
        return {s: {v: summen[str(s)][str(v)] / nenner for v in VERFAHREN_LISTE} for s in SCHLUESSEL_LISTE}

    return {
        "verteilung": verteilung,
        "name": C.VERTEILUNG_LANG[verteilung],
        "n": n,
        "instanzen": k,
        "exakt": exakt,
        "entschieden": e,
        "offen": (k - e) if exakt else 0,
        "mittel_schranke": tab(z["ueber_schranke"], k),
        "mittel_opt": tab(z["ueber_opt"], e) if exakt and e else None,
        "anteil_opt": {s: {v: 100.0 * z["trifft_opt"][str(s)][str(v)] / e for v in VERFAHREN_LISTE} for s in SCHLUESSEL_LISTE} if exakt and e else None,
        "opt_minus_schranke": z["opt_minus_schranke"] / e if exakt and e else None,
        "opt_ueber_schranke": z.get("opt_ueber_schranke", 0),
        "voll_gegen_schichten": tuple(z["ep_voll_gegen_schichten"]),
        "voll_gegen_einfach": tuple(z["ep_voll_gegen_ep_einfach"]),
        "gross_ueber_volumen": z["gross_ueber_volumen"],
        "stuetz_unter80": 100.0 * z["stuetz_unter80"] / (n * k),
        "stuetz_schwebend": 100.0 * z["stuetz_schwebend"] / (n * k),
    }


def referenz(z: dict) -> tuple[str, dict]:
    """(Name der Vergleichsbasis, Mittel je Schlüssel und Verfahren): das Optimum, wo es für mindestens eine Instanz der Zelle bekannt ist, sonst die Schranke."""
    if z["exakt"] and z["entschieden"]:
        return "dem Optimum", z["mittel_opt"]
    return "der Schranke", z["mittel_schranke"]


def gerundet(m: dict) -> dict:
    return {k: {v: round(m[k][v], 2) for v in VERFAHREN_LISTE} for k in SCHLUESSEL_LISTE}


def beste_schluessel_zelle(g: dict, verfahren: int) -> list:
    """Schlüssel mit dem kleinsten (auf zwei Stellen gerundeten) Mittel für das Verfahren."""
    kleinster = min(g[k][verfahren] for k in SCHLUESSEL_LISTE)
    return [k for k in SCHLUESSEL_LISTE if g[k][verfahren] == kleinster]


def verdict_messung(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: bester Schlüssel je Verfahren; Extreme Points mit Projektionen und Volumen gegen Schichten mit Höhe. Auf zwei Stellen gerundet verglichen."""
    basis, m = referenz(z)
    g = gerundet(m)
    n_inst = z["entschieden"] if basis == "dem Optimum" else z["instanzen"]
    teile = []
    for v in VERFAHREN_LISTE:
        gleich = beste_schluessel_zelle(g, v)
        teile.append(f"{C.VERFAHREN_KURZ[v]} {'alle Schlüssel gleich' if len(gleich) == len(SCHLUESSEL_LISTE) else ' und '.join(C.SCHLUESSEL_KURZ[k] for k in gleich)}")
    kopf = f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} ist der beste Schlüssel je Verfahren (Mittel über {basis}, {n_inst} Instanzen): " + ", ".join(teile) + "."
    zahlen = (f" Schichten mit Höhe {g[HOEHE][SCHICHTEN]:.2f}; EP einfach mit Volumen {g[VOLUMEN][EP_EINFACH]:.2f}; EP voll mit Volumen {g[VOLUMEN][EP_VOLL]:.2f}.")
    fuss = ""
    if basis == "dem Optimum" and z["offen"]:
        fuss += f" {z['offen']} von {z['instanzen']} Instanzen sind nicht entschieden und fehlen im Mittel."
    if basis == "der Schranke":
        fuss += " Bei dieser Quaderzahl fehlt das Optimum und die Schranke ist locker: Lesen Sie nur die Unterschiede zwischen den Kombinationen, nicht den Abstand."
    schicht, voll = g[HOEHE][SCHICHTEN], g[VOLUMEN][EP_VOLL]
    if voll < schicht:
        return "success", kopf + zahlen + " **Extreme Points mit Projektionen und Volumen** sind hier besser als Schichten mit Höhe." + fuss
    if voll == schicht:
        return "info", kopf + zahlen + " Beide Kombinationen sind hier gleich gut." + fuss
    return "warning", kopf + zahlen + " Hier sind **Schichten mit Höhe** besser als Extreme Points mit Projektionen und Volumen." + fuss


def verdict_instanz(z: dict) -> tuple[str, str]:
    """Verdikt zu Experiment 2: Instanz für Instanz EP voll mit Volumen gegen Schichten mit Volumen und gegen EP einfach mit Volumen."""
    b, g, s = z["voll_gegen_schichten"]
    eb, eg, es = z["voll_gegen_einfach"]
    teil = (f"Von {z['instanzen']} Instanzen braucht EP voll mit Volumen in **{b}** weniger Behälter als Schichten mit Volumen, in {g} gleich viele und in {s} mehr. "
            f"Gegenüber EP einfach mit Volumen sind es {eb} weniger, {eg} gleich viele und {es} mehr.")
    if b > s:
        return "success", teil + " Extreme Points mit Projektionen sind hier das bessere Verfahren."
    if b == s:
        return "info", teil + " Beide Verfahren sind hier gleich gut."
    return "warning", teil + " Hier sind Schichten besser."


def optimum_zeilen(daten: dict | None = None) -> list:
    """Experiment 3: für alle Zellen mit Optimum (n = 12 und 20, vier Verteilungen): Anteil der entschiedenen Instanzen, in denen Schichten mit Höhe, EP einfach mit Volumen und EP voll mit Volumen
    das Optimum treffen."""
    zeilen = []
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            if n in C.EXAKT_N:
                z = zeile(v, ni, daten)
                t = z["anteil_opt"]
                zeilen.append({"verteilung": v, "n": n, "entschieden": z["entschieden"], "offen": z["offen"], "instanzen": z["instanzen"],
                               "schichten": None if t is None else t[HOEHE][SCHICHTEN], "einfach": None if t is None else t[VOLUMEN][EP_EINFACH],
                               "voll": None if t is None else t[VOLUMEN][EP_VOLL]})
    return zeilen


def verdict_optimum(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 3: in welcher Zelle EP voll mit Volumen das Optimum am seltensten und in welcher am häufigsten trifft (auf ganze Prozent gerundet)."""
    gueltig = [z for z in zeilen if z["voll"] is not None]
    if not gueltig:
        return "info", "Es gibt keine Zelle mit bekanntem Optimum."
    selten = min(gueltig, key=lambda z: (round(z["voll"]), z["n"], z["verteilung"]))
    haeufig = max(gueltig, key=lambda z: (round(z["voll"]), -z["n"], -z["verteilung"]))
    return "info", (f"EP voll mit Volumen trifft das Optimum am seltensten bei {C.VERTEILUNG_DAT[selten['verteilung']]} mit n = {selten['n']} ({selten['voll']:.0f} % der {selten['entschieden']} "
                    f"entschiedenen Instanzen, Schichten mit Höhe {selten['schichten']:.0f} %, EP einfach mit Volumen {selten['einfach']:.0f} %) und am häufigsten bei "
                    f"{C.VERTEILUNG_DAT[haeufig['verteilung']]} mit n = {haeufig['n']} ({haeufig['voll']:.0f} % der {haeufig['entschieden']} entschiedenen Instanzen).")


def stuetz_zeilen(daten: dict | None = None) -> list:
    """Experiment 4: für alle 16 Zellen der Anteil der Quader mit Stützfläche unter 80 % und der schwebenden Quader (EP voll mit Volumen), in Prozent aller Quader der Zelle."""
    return [{"verteilung": v, "n": n, "unter80": (z := zeile(v, ni, daten))["stuetz_unter80"], "schwebend": z["stuetz_schwebend"]}
            for v in range(len(C.VERTEILUNGEN)) for ni, n in enumerate(C.MESS_N)]


def verdict_stuetz_raster(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 4: Spanne des Anteils mit Stützfläche unter 80 % (auf ganze Prozent gerundet), die Zelle mit dem größten Anteil und die Spanne der schwebenden Quader (eine Stelle)."""
    hoch = max(zeilen, key=lambda z: (round(z["unter80"]), -z["n"], -z["verteilung"]))
    tief = min(zeilen, key=lambda z: (round(z["unter80"]), z["n"], z["verteilung"]))
    sw_lo, sw_hi = min(z["schwebend"] for z in zeilen), max(z["schwebend"] for z in zeilen)
    return "warning", (f"Ohne Stützbedingung haben in diesen Packungen **{tief['unter80']:.0f} bis {hoch['unter80']:.0f} %** der Quader weniger als 80 % Stützfläche (am meisten bei "
                       f"{C.VERTEILUNG_DAT[hoch['verteilung']]} mit n = {hoch['n']}), und {sw_lo:.1f} bis {sw_hi:.1f} % schweben ganz. Die Behälterzahlen oben gelten also für Packungen, "
                       "die in der Wirklichkeit teilweise nicht stehen würden; Stück 10 führt die Stützfläche als Bedingung ein.")
