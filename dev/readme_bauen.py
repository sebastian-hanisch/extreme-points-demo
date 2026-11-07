"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import ept_constants as C  # noqa: E402
import ept_evaluation as ev  # noqa: E402
from ept_scenario import beispiel  # noqa: E402

KOMBIS = ((C.HOEHE, C.SCHICHTEN), (C.VOLUMEN, C.SCHICHTEN), (C.VOLUMEN, C.EP_EINFACH), (C.HOEHE, C.EP_VOLL), (C.VOLUMEN, C.EP_VOLL))      # (Schlüssel, Verfahren) der Tabelle A


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def tabellen():
    """(A, B, C, Beispiel 1, Beispiel 2): A = Behälter über der Vergleichsbasis je Zelle für fünf Kombinationen, B = Anteil Optimum getroffen, C = Stützfläche, die Beispiele = Behälterzahlen je
    Verfahren und Schlüssel."""
    kopf = " | ".join(f"{C.VERFAHREN_KURZ[v]} {C.SCHLUESSEL_KURZ[k]}" for k, v in KOMBIS)
    ta = ["| Verteilung | n | Basis | " + kopf + " |", "|---|---|---|" + "---|" * len(KOMBIS)]
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            z = ev.zeile(v, ni)
            b, m = ev.referenz(z)
            ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {'Optimum' if b == 'dem Optimum' else 'Schranke'} | " + " | ".join(de(m[k][vf]) for k, vf in KOMBIS) + " |")
    tb = ["| Verteilung | n | Schichten Höhe | EP einfach Volumen | EP voll Volumen |", "|---|---|---|---|---|"]
    for r in ev.optimum_zeilen():
        tb.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {r['n']} | {r['schichten']:.0f} % | {r['einfach']:.0f} % | {r['voll']:.0f} % |")
    tc = ["| Verteilung | n | unter 80 % Stützfläche | ohne jede Stütze |", "|---|---|---|---|"]
    for r in ev.stuetz_zeilen():
        tc.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {r['n']} | {r['unter80']:.1f} % | {r['schwebend']:.1f} % |".replace(".", ","))
    bsp = []
    for b in (0, 1):
        t = ev.tabelle(beispiel(b))
        zeilen = ["| Schlüssel | " + " | ".join(C.VERFAHREN_KURZ[v] for v in range(3)) + " |", "|---|---|---|---|"]
        for k in range(5):
            zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(str(t[k][vf]) for vf in range(3)) + " |")
        bsp.append("\n".join(zeilen))
    return "\n".join(ta), "\n".join(tb), "\n".join(tc), bsp[0], bsp[1]


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    ta, tb, tc, b1, b2 = tabellen()
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", ta).replace("{{TABELLE_B}}", tb).replace("{{TABELLE_C}}", tc).replace("{{BEISPIEL_1}}", b1).replace("{{BEISPIEL_2}}", b2)
            .replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
