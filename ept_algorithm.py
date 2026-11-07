"""Kern der Demo (nur Standardbibliothek): Schlüssel, die drei Verfahren (Schichten, Extreme Points einfach, Extreme Points mit Projektionen), Schranken, Stützfläche und der unabhängige Prüfer.

Quader (Breite, Tiefe, Höhe), ohne Drehung, in Behälter der Kantenlänge `cap`. Eine Reihenfolge der Quader und ein Verfahren machen daraus eine Packung: Jeder Quader kommt in den ersten Behälter,
in dem das Verfahren eine Stelle für ihn hat, sonst in einen neuen. Eine Packung ist eine Liste (Quader, Behälter, x, y, z) mit der linken hinteren unteren Ecke."""

SCHICHTEN, EP_EINFACH, EP_VOLL = 0, 1, 2
LIEFERUNG, VOLUMEN, GRUNDFLAECHE, HOEHE, KANTE = 0, 1, 2, 3, 4


# --- Schlüssel --------------------------------------------------------------------------------------------------------------------------------------


def schluessel_wert(kisten, schluessel: int) -> list:
    """Wert jedes Quaders unter dem Schlüssel (Lieferung: 0 für alle)."""
    if schluessel == LIEFERUNG:
        return [0] * len(kisten)
    f = {VOLUMEN: lambda k: k[0] * k[1] * k[2], GRUNDFLAECHE: lambda k: k[0] * k[1], HOEHE: lambda k: k[2], KANTE: lambda k: max(k)}[schluessel]
    return [f(k) for k in kisten]


def reihenfolge(kisten, schluessel: int) -> list:
    """Quadernummern, absteigend nach dem Schlüssel; Gleichstände bleiben in der Lieferreihenfolge (bei der Lieferung ist es die Lieferreihenfolge selbst)."""
    werte = schluessel_wert(kisten, schluessel)
    if schluessel == LIEFERUNG:
        return list(range(len(kisten)))
    return sorted(range(len(kisten)), key=lambda i: (-werte[i], i))


# --- Geometrie --------------------------------------------------------------------------------------------------------------------------------------


def _ueberlappt(a, b) -> bool:
    """Zwei Quader (x, y, z, w, d, h) überlappen in einem Rauminhalt über null (Berührung zählt nicht)."""
    return a[0] < b[0] + b[3] and b[0] < a[0] + a[3] and a[1] < b[1] + b[4] and b[1] < a[1] + a[4] and a[2] < b[2] + b[5] and b[2] < a[2] + a[5]


def _pruefe_kisten(kisten, cap: int):
    for k in kisten:
        if len(k) != 3 or any(not isinstance(x, int) or x <= 0 or x > cap for x in k):
            raise ValueError(f"Quader {k!r} ungültig (drei ganze Maße, je 1 bis {cap})")


def packung_pruefen(kisten, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jeder Quader höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Quader eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(kisten))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(kisten) for i in nummern):
        return False
    je = {}
    for i, b, x, y, z in platz:
        w, d, h = kisten[i]
        if x < 0 or y < 0 or z < 0 or x + w > cap or y + d > cap or z + h > cap:
            return False
        je.setdefault(b, []).append((x, y, z, w, d, h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                if _ueberlappt(lst[a], lst[c]):
                    return False
    return True


def schranken(kisten, cap: int):
    """(Volumenschranke, Zahl der großen Quader, Schranke): das Volumen aller Quader durch das Behältervolumen aufgerundet; die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen
    (zwei solche überlappen in jedem Behälter über dem Mittelpunkt, jeder braucht also einen eigenen Behälter); das Größere von beiden."""
    volumen = -(-sum(w * d * h for w, d, h in kisten) // cap ** 3)
    gross = sum(1 for w, d, h in kisten if 2 * w > cap and 2 * d > cap and 2 * h > cap)
    return volumen, gross, max(volumen, gross)


def schranke(kisten, cap: int) -> int:
    return schranken(kisten, cap)[2]


def stuetzflaeche(kisten, platz, i: int) -> float:
    """Anteil der Grundfläche von Quader i, der auf dem Boden oder auf den Oberseiten anderer Quader desselben Behälters aufliegt (1,0 am Boden)."""
    _, b, x, y, z = next(p for p in platz if p[0] == i)
    w, d, _h = kisten[i]
    if z == 0:
        return 1.0
    flaeche = 0
    for j, bb, x2, y2, z2 in platz:
        if bb == b and j != i and z2 + kisten[j][2] == z:
            flaeche += max(0, min(x + w, x2 + kisten[j][0]) - max(x, x2)) * max(0, min(y + d, y2 + kisten[j][1]) - max(y, y2))
    return flaeche / (w * d)


def stuetz_kennzahlen(kisten, platz) -> tuple:
    """(Zahl der Quader mit Stützfläche unter 80 %, Zahl der Quader ohne jede Stütze) einer Packung. Die Grenzen sind exakt: 80 % zählt nicht als darunter."""
    f = [stuetzflaeche(kisten, platz, p[0]) for p in platz]
    return sum(1 for s in f if s < 0.8), sum(1 for s in f if s == 0)


# --- Schichten ----------------------------------------------------------------------------------------------------------------------------------------


def _schichten(kisten, order, cap):
    behaelter = []          # je Behälter: Liste von Schichten {"z", "h", "regale": [{"y", "d", "x"}]}
    platz = []
    for i in order:
        w, d, h = kisten[i]
        gesetzt = False
        for b, lagen in enumerate(behaelter):
            for s in lagen:
                if h > s["h"]:
                    continue
                for r in s["regale"]:
                    if d <= r["d"] and r["x"] + w <= cap:
                        platz.append((i, b, r["x"], r["y"], s["z"]))
                        r["x"] += w
                        gesetzt = True
                        break
                if gesetzt:
                    break
                y0 = sum(r["d"] for r in s["regale"])
                if y0 + d <= cap:
                    s["regale"].append({"y": y0, "d": d, "x": w})
                    platz.append((i, b, 0, y0, s["z"]))
                    gesetzt = True
                    break
            if gesetzt:
                break
            z0 = sum(s["h"] for s in lagen)
            if z0 + h <= cap:
                lagen.append({"z": z0, "h": h, "regale": [{"y": 0, "d": d, "x": w}]})
                platz.append((i, b, 0, 0, z0))
                gesetzt = True
                break
        if not gesetzt:
            behaelter.append([{"z": 0, "h": h, "regale": [{"y": 0, "d": d, "x": w}]}])
            platz.append((i, len(behaelter) - 1, 0, 0, 0))
    bins = [[] for _ in behaelter]
    for i, b, _x, _y, _z in platz:
        bins[b].append(i)
    zustand = [tuple((s["z"], s["h"]) for s in lagen) for lagen in behaelter]
    return bins, platz, zustand


# --- Extreme Points -------------------------------------------------------------------------------------------------------------------------------------


def _projiziere(p, achse: int, gesetzt):
    """Punkt p in negativer Richtung der Achse (0 x, 1 y, 2 z) bis zur nächsten Fläche eines gesetzten Quaders oder bis zur Wand schieben."""
    a, b = [k for k in (0, 1, 2) if k != achse]
    wert = 0
    for q in gesetzt:
        qa = q[achse] + q[3 + achse]
        if qa <= p[achse] and q[a] <= p[a] < q[a] + q[3 + a] and q[b] <= p[b] < q[b] + q[3 + b]:
            wert = max(wert, qa)
    r = list(p)
    r[achse] = wert
    return tuple(r)


def _extreme_points(kisten, order, cap, voll: bool):
    behaelter = []          # je Behälter: {"punkte": set, "gesetzt": [(x, y, z, w, d, h)]}
    platz = []
    bins = []
    for i in order:
        w, d, h = kisten[i]
        wahl = None
        for b, c in enumerate(behaelter):
            for (x, y, z) in sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0])):
                if x + w > cap or y + d > cap or z + h > cap:
                    continue
                if any(_ueberlappt((x, y, z, w, d, h), q) for q in c["gesetzt"]):
                    continue
                wahl = (b, x, y, z)
                break
            if wahl:
                break
        if not wahl:
            behaelter.append({"punkte": {(0, 0, 0)}, "gesetzt": []})
            bins.append([])
            wahl = (len(behaelter) - 1, 0, 0, 0)
        b, x, y, z = wahl
        c = behaelter[b]
        platz.append((i, b, x, y, z))
        bins[b].append(i)
        c["punkte"].discard((x, y, z))
        for p, achsen in (((x + w, y, z), (1, 2)), ((x, y + d, z), (0, 2)), ((x, y, z + h), (0, 1))):
            if max(p) < cap:
                c["punkte"].add(p)
            if voll:
                for a in achsen:
                    q = _projiziere(p, a, c["gesetzt"])
                    if max(q) < cap:
                        c["punkte"].add(q)
        c["gesetzt"].append((x, y, z, w, d, h))
        # Punkte im Inneren eines Quaders entfallen (sie wären nie zulässig); Punkte auf dem Rand bleiben
        c["punkte"] = {p for p in c["punkte"] if not any(q[0] <= p[0] < q[0] + q[3] and q[1] <= p[1] < q[1] + q[4] and q[2] <= p[2] < q[2] + q[5] for q in c["gesetzt"])}
    return bins, platz, [tuple(sorted(c["punkte"], key=lambda p: (p[2], p[1], p[0]))) for c in behaelter]


def pack(kisten, order, cap: int, verfahren: int):
    """Packt die Quader in der Reihenfolge `order` (jeder höchstens einmal, auch ein Anfang der Reihenfolge ist erlaubt). Gibt (bins, platz, zustand) zurück: bins[b] = Quadernummern,
    platz = (Quader, Behälter, x, y, z), zustand[b] = bei Schichten die Schichten (z, Höhe), bei Extreme Points die Eckpunkte (x, y, z) des Behälters nach dem letzten Quader."""
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(kisten) for i in order):
        raise ValueError("die Reihenfolge darf jeden Quader höchstens einmal enthalten")
    if verfahren not in (SCHICHTEN, EP_EINFACH, EP_VOLL):
        raise ValueError(f"Verfahren {verfahren!r} unbekannt")
    _pruefe_kisten(kisten, cap)
    if verfahren == SCHICHTEN:
        return _schichten(kisten, order, cap)
    return _extreme_points(kisten, order, cap, verfahren == EP_VOLL)


def anzahl(kisten, schluessel: int, verfahren: int, cap: int) -> int:
    """Behälterzahl der Packung aller Quader mit dem Schlüssel und dem Verfahren."""
    return len(pack(kisten, reihenfolge(kisten, schluessel), cap, verfahren)[0])
