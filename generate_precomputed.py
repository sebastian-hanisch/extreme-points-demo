"""Erzeugt ept_precomputed.json: das Messraster (vier Verteilungen × Quaderzahlen 12, 20, 40, 80 × 100 feste Instanzen × fünf Schlüssel × drei Verfahren), die Optima bei 12 und 20 Quadern (CP-SAT)
und die Stichprobe (die ersten Instanzen jeder Zelle einzeln, für die Tests).

    python generate_precomputed.py                         # rechnet alles neu (Optima mit CP-SAT, Zeitlimit je Instanz, mehrere Prozesse)
    python generate_precomputed.py --keep-opt              # behält die in der Datei gespeicherten Optima und rechnet Raster und Stichprobe neu
    python generate_precomputed.py --nur-stichprobe        # ergänzt in der vorhandenen Datei nur die Stichprobe
    python generate_precomputed.py --check                 # rechnet das Raster (parallel) mit den gespeicherten Optima nach und vergleicht mit der Datei

Das Optimum je Instanz rechnet dev/opt.py (CP-SAT) mit der besten gefundenen Behälterzahl aller 15 Kombinationen als Obergrenze; -1 = in der Zeit nicht entschieden."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import ept_algorithm as A
import ept_constants as C
import ept_evaluation as ev
from ept_scenario import mess_seed, zufallsinstanz


def optimum_instanz(v: int, ni: int, j: int) -> int:
    from dev.opt import optimum_cpsat

    inst = zufallsinstanz(v, C.MESS_N[ni], mess_seed(v, ni, j))
    ober = min(min(z) for z in ev.tabelle(inst))
    return ober if ober == A.schranke(inst.kisten, inst.cap) else optimum_cpsat(inst.kisten, inst.cap, ober, C.CPSAT_ZEIT, 2)


def _optima(args):
    v, ni, j0, j1 = args
    return v, ni, j0, [optimum_instanz(v, ni, j) for j in range(j0, j1)]


def _zelle(args):
    v, ni, opt = args
    t = time.perf_counter()
    z = ev.messzelle(v, ni, opt)
    if opt is not None:
        z["opt"] = opt
    return v, ni, z, time.perf_counter() - t


def _stichprobe_zelle(args):
    v, ni, opt = args
    return ev.zelle_schluessel(v, ni), {str(j): ev.messzelle(v, ni, opt, [j]) for j in C.STICHPROBE_J}


def _frisch(args):
    v, ni, opt = args
    z = ev.messzelle(v, ni, opt)
    if opt is not None:
        z["opt"] = opt
    return ev.zelle_schluessel(v, ni), z


def _pool():
    return ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2)))


def optima_rechnen() -> dict:
    """Optimum je Instanz für die Zellen mit n in EXAKT_N; die 100 Instanzen jeder Zelle werden in Stücken zu 10 auf die Prozesse verteilt."""
    auftraege = [(v, ni, j0, j0 + 10) for v in range(len(C.VERTEILUNGEN)) for ni, n in enumerate(C.MESS_N) if n in C.EXAKT_N for j0 in range(0, C.INSTANZEN, 10)]
    teile = {}
    with _pool() as pool:
        for v, ni, j0, werte in pool.map(_optima, auftraege):
            teile[(v, ni, j0)] = werte
            print(f"Optima {ev.zelle_schluessel(v, ni)} ab {j0}: {sum(1 for w in werte if w < 0)} offen", flush=True)
    return {ev.zelle_schluessel(v, ni): [w for j0 in range(0, C.INSTANZEN, 10) for w in teile[(v, ni, j0)]] for (v, ni, j) in teile if j == 0}


def stichprobe_ergaenzen(daten: dict) -> None:
    auftraege = [(v, ni, daten["zellen"][ev.zelle_schluessel(v, ni)].get("opt")) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]
    with _pool() as pool:
        daten["stichprobe"] = dict(pool.map(_stichprobe_zelle, auftraege))


def erzeugen(behalten: bool) -> dict:
    optima = {k: z["opt"] for k, z in ev.vorberechnet()["zellen"].items() if "opt" in z} if behalten else optima_rechnen()
    auftraege = [(v, ni, optima.get(ev.zelle_schluessel(v, ni)) if n in C.EXAKT_N else None) for v in range(len(C.VERTEILUNGEN)) for ni, n in enumerate(C.MESS_N)]
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "cpsat_zeit": C.CPSAT_ZEIT, "zellen": {}}
    with _pool() as pool:
        for v, ni, z, sekunden in pool.map(_zelle, auftraege):
            daten["zellen"][ev.zelle_schluessel(v, ni)] = z
            print(f"{ev.zelle_schluessel(v, ni)}: {sekunden:.0f} s", flush=True)
    stichprobe_ergaenzen(daten)
    return daten


def schreiben(daten: dict) -> None:
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    auftraege = [(v, ni, gespeichert["zellen"][ev.zelle_schluessel(v, ni)].get("opt")) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]
    schlecht = 0
    with _pool() as pool:
        for schl, frisch in pool.map(_frisch, auftraege):
            if frisch != gespeichert["zellen"][schl]:
                schlecht += 1
                print("ABWEICHUNG", schl, flush=True)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    if "--nur-stichprobe" in sys.argv:
        d = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
        stichprobe_ergaenzen(d)
        schreiben(d)
        sys.exit(0)
    schreiben(erzeugen("--keep-opt" in sys.argv))
