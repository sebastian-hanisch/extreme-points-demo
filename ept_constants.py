"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Behälter 100 x 100 x 100 (Breite, Tiefe, Höhe)

# --- Beispiele (Quader als (Breite, Tiefe, Höhe) in Lieferreihenfolge; zwölf Quader aus dem Messraster, Zelle „mittel, n = 12“) ----------------------
# Beispiel 1 (Instanz 45 von 100): Schranke 1, Optimum 1 (alle zwölf Quader passen in einen Behälter); Schichten 2 mit jedem Schlüssel, EP einfach 2 mit jedem Schlüssel, EP voll 2 außer
# mit dem Volumen: dort 1. Beispiel 2 (Instanz 4 von 100): Schranke 1, Optimum 2 (CP-SAT); Schichten Lieferung / Volumen / Grundfläche / Höhe / Kante 5 / 5 / 5 / 3 / 3, EP einfach 3 / 2 / 2 / 2 / 3,
# EP voll 3 / 2 / 2 / 2 / 2 (Phase 0, in den Tests nachgerechnet).
BEISPIELE = {
    0: ((26, 29, 38), (41, 58, 28), (50, 32, 45), (26, 51, 32), (43, 50, 20), (42, 35, 39), (26, 47, 21), (54, 35, 21), (50, 33, 20), (22, 54, 41), (34, 39, 25), (51, 39, 37)),
    1: ((43, 57, 41), (57, 50, 43), (27, 59, 56), (24, 29, 39), (48, 40, 32), (25, 20, 51), (47, 50, 56), (60, 46, 51), (21, 57, 57), (50, 53, 42), (45, 23, 60), (33, 45, 28)),
}
BEISPIEL_OPTIMUM = {0: 1, 1: 2}

# Quellen der Instanz: 0 und 1 = Handbeispiele, 2 bis 5 = Zufallsinstanzen mit der jeweiligen Verteilung
QUELLEN = {0: "Beispiel 1 (zwölf Quader)", 1: "Beispiel 2 (zwölf andere Quader)", 2: "zufällig, mittlere Quader", 3: "zufällig, breit gestreute Quader",
           4: "zufällig, kleine Quader", 5: "zufällig, flache Quader"}
ZUFALL_QUELLEN = (2, 3, 4, 5)
N_WERTE = (12, 20, 40)                    # Zahl der Quader der Zufallsinstanzen in der App

# Verteilungen: (Schlüssel, Name, Bereiche der Breite, Tiefe und Höhe)
VERTEILUNGEN = (
    ("mittel", "mittlere Quader (alle Kanten 20 bis 60)", ((20, 60), (20, 60), (20, 60))),
    ("breit", "breit gestreute Quader (alle Kanten 5 bis 70)", ((5, 70), (5, 70), (5, 70))),
    ("klein", "kleine Quader (alle Kanten 10 bis 40)", ((10, 40), (10, 40), (10, 40))),
    ("flach", "flache Quader (Breite und Tiefe 30 bis 80, Höhe 5 bis 30)", ((30, 80), (30, 80), (5, 30))),
)
VERTEILUNG_KURZ = ("mittel", "breit", "klein", "flach")
VERTEILUNG_LANG = ("mittlere Quader", "breit gestreute Quader", "kleine Quader", "flache Quader")
VERTEILUNG_DAT = ("mittleren Quadern", "breit gestreuten Quadern", "kleinen Quadern", "flachen Quadern")   # nach „bei“

SCHLUESSEL = {0: "Lieferreihenfolge (nicht sortiert)", 1: "nach Volumen (größtes zuerst)", 2: "nach Grundfläche (größte zuerst)", 3: "nach Höhe (höchster zuerst)",
              4: "nach längster Kante (längste zuerst)"}
SCHLUESSEL_KURZ = {0: "Lieferung", 1: "Volumen", 2: "Grundfläche", 3: "Höhe", 4: "Kante"}
SCHLUESSEL_MIT = {0: "der Lieferreihenfolge", 1: "dem Volumen", 2: "der Grundfläche", 3: "der Höhe", 4: "der längsten Kante"}
VOLUMEN, HOEHE = 1, 3                     # die Schlüssel, die in den Befunden einzeln vorkommen

VERFAHREN = {
    0: "Schichten: erste passende Schicht, innen Regalplan",
    1: "Extreme Points: nur die drei Nachfolgepunkte",
    2: "Extreme Points: mit Projektionen",
}
VERFAHREN_KURZ = {0: "Schichten", 1: "EP einfach", 2: "EP voll"}
VERFAHREN_NAME = {0: "Schichten", 1: "Extreme Points ohne Projektionen", 2: "Extreme Points mit Projektionen"}
SCHICHTEN, EP_EINFACH, EP_VOLL = 0, 1, 2

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100                           # Instanzen je Zelle; der Wert steht neben jeder Zahl
MESS_N = (12, 20, 40, 80)
EXAKT_N = (12, 20)                        # in diesen Zellen gibt es das Optimum (CP-SAT mit Zeitlimit, ggf. nicht entschieden)
CPSAT_ZEIT = 30.0                         # Sekunden je Instanz
STICHPROBE_J = (0, 1, 2)                  # Instanzen jeder Zelle, die einzeln gespeichert und in den Tests frisch nachgerechnet werden

COLOR_LINE = "#c0392b"
COLOR_PUNKT = "#2F6B65"
KISTEN_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
VERFAHREN_FARBEN = {0: "#9d755d", 1: "#4c78a8", 2: "#2F6B65"}

PRESETS = {
    "Beispiel 1, Volumen, EP voll": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "verfahren": EP_VOLL, "schritt": 0, "behaelter": 1},
    "Beispiel 1, Volumen, EP einfach": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "verfahren": EP_EINFACH, "schritt": 0, "behaelter": 1},
    "Beispiel 2, Volumen, EP voll": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "verfahren": EP_VOLL, "schritt": 0, "behaelter": 1},
    "Beispiel 2, Lieferung, Schichten": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 0, "verfahren": SCHICHTEN, "schritt": 0, "behaelter": 1},
    "Mittlere Quader, 40 Stück, EP voll": {"quelle": 2, "n_index": 2, "seed": DEFAULT_SEED, "schluessel": VOLUMEN, "verfahren": EP_VOLL, "schritt": 0, "behaelter": 1},
}
PRESET_HELP = {
    "Beispiel 1, Volumen, EP voll": "Zwölf Quader nach dem Volumen sortiert und mit Extreme Points samt Projektionen gesetzt: Sie passen alle in einen Behälter, das Optimum.",
    "Beispiel 1, Volumen, EP einfach": "Dieselben zwölf Quader ohne die Projektionen der Eckpunkte: Es werden zwei Behälter, obwohl einer genügt.",
    "Beispiel 2, Volumen, EP voll": "Ein zweites Beispiel: Die Schranke sagt einen Behälter, das Optimum sind zwei, und diese Kombination findet sie.",
    "Beispiel 2, Lieferung, Schichten": "Dieselben Quader unsortiert in Schichten gesetzt: fünf Behälter statt zwei.",
    "Mittlere Quader, 40 Stück, EP voll": "Vierzig mittlere Quader: fünf Behälter bei Schranke 3. Ohne Stützbedingung stehen 12 von 40 Quadern auf weniger als 80 % ihrer Grundfläche, einer schwebt.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Quader mit ganzzahligen Maßen (Breite, Tiefe, Höhe), ohne Drehung; Behälter {CAP} mal {CAP} mal {CAP}; alle Quader sind vor dem Packen bekannt; jeder Quader kommt in den ersten Behälter, in dem das Verfahren eine Stelle für ihn hat; keine Stützbedingung, kein Gewicht, kein Schwerpunkt.

**Grenzen.** Das Messraster deckt vier Verteilungen der Kanten und vier Quaderzahlen (12, 20, 40, 80) ab, jeweils mit {INSTANZEN} Instanzen je Zelle. Die Wahl unter den Eckpunkten ist immer der mit kleinstem (z, y, x); andere Regeln, Drehung, Praxisdaten und weitere Verfahren kommen nicht vor. Die Projektionen der Eckpunkte sind nach eigener Lesart der Originalarbeit umgesetzt (das Original wurde nicht gelesen), die Zahlen gelten für diese Umsetzung. Das exakte Optimum (über alle Packungen, CP-SAT mit {int(CPSAT_ZEIT)} Sekunden Zeitlimit je Instanz) gibt es bei 12 und 20 Quadern, bei 40 und 80 Quadern fehlt es.

**Bekannte Probleme und Unsicherheiten.** Ohne Stützbedingung stehen viele Quader in diesen Packungen nicht sicher, einige schweben ganz: Die Behälterzahlen gelten für Packungen, die in der Wirklichkeit teilweise nicht stehen würden (Experiment 4; Stück 10 führt die Stützfläche ein). Bei 40 und 80 Quadern ist der Maßstab die Schranke, die in 3D locker ist: Ein Teil des Abstands ist Schranke, nicht schlechtes Packen. Die in 20 Quadern entschiedenen Instanzen können die für CP-SAT leichteren sein. Zur Laufzeit macht die Demo keine Aussage. Die App wurde im Browser bedient (Presets, Würfel-Button, Regler und die 3D-Ansicht auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
