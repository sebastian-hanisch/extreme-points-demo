# Die dritte Dimension: Extreme Points – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-extreme-points-demo.streamlit.app/)** -->

Stück 9 der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Stück 7 und 8 haben Rechtecke gepackt; diese Demo packt **Quader** in Behälter: mit **Schichten** (dem Gegenstück zum Regal) und mit **Extreme Points**, ohne und mit Projektionen der Eckpunkte, dazu fünf Sortierschlüssel. Die Fall-Demos zu Container und Palette zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Beim Regal war die Höhe der beste Schlüssel, bei freier Platzierung die Fläche. In 3D gibt es fünf Schlüssel und drei Verfahren, und die Frage bleibt: Was verändert die Behälterzahl mehr? Die Demo zeigt an zwölf Quadern, die alle in **einen** Behälter passen, dass das nur Extreme Points mit Projektionen und dem Volumen als Schlüssel finden, und misst dasselbe an je 100 Zufallsinstanzen in 16 Zellen. Dazu eine Warnung: Ohne Stützbedingung stehen viele Quader nicht sicher; die Demo zählt sie, Stück 10 verlangt die Stützfläche.

## Modell

Quader mit ganzzahliger Breite, Tiefe und Höhe, ohne Drehung, in Behältern der Größe 100 mal 100 mal 100, alle vorab bekannt; jeder Quader kommt in den ersten Behälter, in dem das Verfahren eine Stelle für ihn hat, sonst in einen neuen. **Schichten:** eine Schicht hat die Höhe ihres ersten Quaders und ist innen ein Regalplan; ein Quader kommt in die erste Schicht, deren Höhe reicht und in der innen noch Platz ist, sonst in eine neue Schicht obenauf. **Extreme Points:** je Behälter eine Liste von Eckpunkten; der Quader kommt an den passenden Punkt mit kleinstem (z, y, x); danach entfällt der Punkt, und es kommen die Ecken rechts, hinten und oben vom Quader hinzu (**EP einfach**), bei **EP voll** zusätzlich deren Projektionen in negativer Richtung der beiden anderen Achsen auf die nächste Fläche oder die Wand. **Schlüssel** (absteigend, Gleichstand: Lieferreihenfolge): Lieferreihenfolge, Volumen, Grundfläche, Höhe, längste Kante. **Schranken:** das Volumen aller Quader durch das Behältervolumen, aufgerundet, und die Zahl der Quader, die in allen drei Maßen über die Hälfte reichen; das Größere von beiden. **Optimum** über alle Packungen mit CP-SAT (nur Generator und Tests). **Stützfläche:** der Anteil der Grundfläche eines Quaders, der auf dem Boden oder auf Oberseiten anderer Quader aufliegt. **Vier Verteilungen:** *mittel* (alle Kanten 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *flach* (Breite und Tiefe 30 bis 80, Höhe 5 bis 30). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`ept_algorithm.py`): `schluessel_wert`, `reihenfolge`, `pack` (drei Verfahren; liefert Behälter, Platzierungen und den Zustand je Behälter: Schichten oder Eckpunkte; ein Anfang der Reihenfolge liefert den Zustand nach so vielen Schritten), `schranken`, `stuetzflaeche`, `stuetz_kennzahlen`, `packung_pruefen` (unabhängiger Prüfer: jeder Quader genau einmal, im Behälter, keine Überlappung).
- **Handbeispiele:** zwei feste Mengen von je zwölf Quadern aus dem Raster. Die App zeichnet einen gewählten Behälter in 3D samt Eckpunkten (Schritt-Regler) und zeigt alle 15 Kombinationen aus Schlüssel und Verfahren.
- **Messraster:** vier Verteilungen × vier Quaderzahlen (12, 20, 40, 80) × **100 feste Instanzen** je Zelle × fünf Schlüssel × drei Verfahren. Maßstab ist bei 12 und 20 Quadern das Optimum (CP-SAT, 30 Sekunden Zeitlimit je Instanz, nur die entschiedenen Instanzen), bei 40 und 80 die Schranke. Die Summen stehen als ganze Zahlen in `ept_precomputed.json` (erzeugt von `generate_precomputed.py`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_extreme_points.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Vergleichsbasis). **Alle Packungen sind ohne Stützbedingung gebaut.**

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Quader, Schranke 1, Optimum 1) | Alle zwölf Quader passen in **einen** Behälter; das finden nur **EP voll mit Volumen**. Alle anderen 14 Kombinationen brauchen **2** (Tabelle unten) |
| Beispiel 2 (zwölf andere Quader, Schranke 1, Optimum 2) | Die Schranke ist locker. Schichten brauchen mit jedem Schlüssel **3 bis 5** Behälter, EP voll mit Volumen, Grundfläche, Höhe und Kante **2** (Tabelle unten) |
| Extreme Points gegen Schichten, Instanz für Instanz | EP voll mit Volumen braucht gegenüber Schichten mit Volumen in **1100** von 1600 Instanzen weniger Behälter, in 500 gleich viele und in **0** mehr |
| Mittelwerte | Im Mittel braucht EP voll mit Volumen in **14** von 16 Zellen weniger Behälter als Schichten mit Höhe (dem besten Schlüssel der Schichten), in zwei gleich (kleine Quader bei 12 und 20: ein Behälter genügt) |
| Welcher Schlüssel ist am besten? | Bei Schichten die **Höhe** in 14 Zellen (das Volumen in zwei: flach bei n = 20 und n = 80, mit Abständen von 0,01 und 0,06); bei EP voll das **Volumen** in **14** Zellen (bei kleinen Quadern mit n = 20 gleichauf mit Grundfläche, Höhe und Kante, bei n = 12 alle fünf gleich); bei EP einfach ist es das Volumen in 9 Zellen |
| Schlüssel und Verfahren gehören zusammen | Mit Schichten ist das Volumen als Schlüssel schlechter als die Höhe (mittlere Quader, n = 80: 3,75 gegen 2,99) |
| Helfen die Projektionen? | EP voll braucht gegenüber EP einfach (beide mit Volumen) in **275** von 1600 Instanzen weniger Behälter, in 1308 gleich viele und in **17** mehr; im Mittel in **14** von 16 Zellen weniger, in zwei gleich, in keiner mehr |
| Wie nah am Optimum? | Mit dem jeweils besten Schlüssel treffen bei 12 Quadern Schichten 31 bis 100 %, EP einfach 44 bis 100 %, EP voll 48 bis 100 % der entschiedenen Instanzen das Optimum, bei 20 Quadern 3 bis 100 %, 40 bis 100 % und 49 bis 100 % (100 % nur bei kleinen Quadern) |
| Wie locker ist die Schranke? | Das Optimum liegt bei 12 Quadern in **153** von 399 entschiedenen Instanzen über der Schranke (41 mittel, 53 breit, 0 klein, 59 flach), bei 20 in **91** von 395; große Quader liegen nur in **11** von 1600 Instanzen über der Volumenschranke |
| Wie viele Instanzen sind nicht entschieden? | **1** von 400 bei 12 und **5** von 400 bei 20 Quadern (2 bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 2 bei flachen bei 20); bei 40 und 80 gibt es kein Optimum |
| **Stehen die Quader sicher?** | **Nein, nicht ohne Bedingung:** In den Packungen von EP voll mit Volumen haben **2 bis 43 %** der Quader weniger als 80 % Stützfläche (flache Quader 41 bis 43 %), und **0,1 bis 4,2 %** schweben ohne jede Stütze |

**Beispiel 1** (Behälterzahl je Schlüssel und Verfahren):

{{BEISPIEL_1}}

**Beispiel 2:**

{{BEISPIEL_2}}

**Behälter über der Vergleichsbasis** (Mittel; Basis: Optimum bei 12 und 20 Quadern, nur über die entschiedenen Instanzen, sonst die Schranke; fünf Kombinationen aus Verfahren und Schlüssel; bei 40 und 80 Quadern ist die Schranke locker, dort zählt nur der Vergleich der Kombinationen):

{{TABELLE_A}}

**Optimum getroffen** (Anteil der entschiedenen Instanzen, in denen die Kombination genau das Optimum braucht; bei kleinen Quadern passen alle in einen Behälter):

{{TABELLE_B}}

**Stützfläche** (Anteil der Quader aller Instanzen der Zelle, in Packungen von EP voll mit Volumen, ohne Stützbedingung):

{{TABELLE_C}}

## Ehrliche Grenzen

- Alle Aussagen gelten für Quader ohne Drehung, vier Verteilungen mit festen Bereichen, vier Quaderzahlen, eine Behältergröße, **ohne Stützbedingung, Gewicht und Schwerpunkt** und genau diese drei Verfahren mit der festen Wahl „tiefster, hinterster, linkester Eckpunkt“. Andere Regeln, Drehung und Praxisdaten sind nicht gemessen.
- Die **Projektionen** der Eckpunkte sind nach eigener Lesart der Originalarbeit (Crainic, Perboli, Tadei 2008) umgesetzt; das Original wurde nicht gelesen, und es wird keine Zahl und keine Aussage der Arbeit übernommen. Die Zahlen gelten für diese Umsetzung.
- Das Optimum gilt über **alle** Packungen. Es kommt aus CP-SAT mit 30 Sekunden Zeitlimit je Instanz; die nicht entschiedenen Instanzen (1 und 5 von je 400) sind die schweren und fehlen im Mittel. Bei 40 und 80 Quadern fehlt das Optimum; die Schranke ist in 3D locker, also ist dort nur der Vergleich der Kombinationen belastbar, nicht der Abstand zur Schranke.
- **Ohne Stützbedingung** gelten die Behälterzahlen für Packungen, die in der Wirklichkeit teilweise nicht stehen würden (Tabelle oben). Mit einer Mindest-Stützfläche ändern sich Zahlen und Reihenfolge der Quader; das misst Stück 10.
- Zur **Laufzeit** der Verfahren macht die Demo keine Aussage.
- Das Raster sagt nichts über Quader, die einzeln nacheinander ohne Kenntnis der späteren eintreffen (Online-Packen, Konzepte-Reihe Online-Algorithmen).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

{{ANNAHMEN}}

## Verifikation

- **Kern:** alle drei Verfahren an einer von Hand gerechneten Mini-Instanz (vier Quader, Behälter 10 mal 10 mal 10, mit Platzierungen, Eckpunkten nach jedem Schritt und den Schichten; Extreme Points mit Projektionen brauchen einen Behälter, ohne zwei, Schichten zwei); Stützfläche von Hand (87,5 %, genau 80 %, 60 %, schwebend, anderer Behälter, andere Höhe); beide Handbeispiele mit allen 15 Behälterzahlen; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Quader, Quader gleich Behälter, acht Würfel füllen den Behälter genau, kein Platz, ein Fall, in dem nur die Projektion den Platz findet, Anfang der Reihenfolge, Gleichstände, ungültige Eingaben, Grenzen der Regler).
- **Orakel** (`tests/test_oracle_extreme_points.py`): Extreme Points mit und ohne Projektionen gegen eine Umsetzung, die die Eckpunkte vor jedem Quader aus der Liste der gesetzten Quader neu erzeugt (120 Läufe, davon mindestens 40 mit mehreren Behältern; die Projektionen ändern die Packung in mindestens 10 von 30 Instanzen); Schichten gegen eine naive Neuberechnung; die Stützfläche gegen ein Voxelraster; das Optimum von CP-SAT nie unter der Schranke und nie über der Packung; Eigenschaften: Packungen zulässig und nie unter der Schranke, gemeinsames Skalieren, Zustand ist der Anfang der Packung, Eckpunkte nie im Inneren eines Quaders.
- **Messraster:** jede Zelle bis n = 40 wird frisch gerechnet und exakt mit `ept_precomputed.json` verglichen, bei n = 80 die ersten drei Instanzen jeder Zelle (Stichprobe in der Datei); alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel). Die Optima werden stichprobenweise mit CP-SAT nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **3D-Darstellung:** Die zwölf Dreiecke je Quader decken jede der sechs Seitenflächen lückenlos und ohne Überlappung ab (`tests/test_visualization.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Schritt, Behälter und Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** {{TESTS}}.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt.py` | exaktes Optimum mit CP-SAT (nur für Generator und Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `ept_algorithm.py` | Kern: Schlüssel, Verfahren, Schranken, Stützfläche, Packungsprüfer |
| `ept_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `ept_evaluation.py` | Analyse, Verdikte, Messzellen |
| `ept_layout.py` | Fester Kopf (Stylesheet) und Tabellen auf dem Telefon |
| `ept_precomputed.json` | vorberechnete Summen, Optima und Stichprobe des Messrasters |
| `ept_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `ept_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds |
| `ept_visualization.py` | Plotly-Abbildungen (3D-Behälter, Balken mit gesperrten Achsen) |
| `generate_precomputed.py` | erzeugt `ept_precomputed.json` (Messraster, Optima mit CP-SAT, Stichprobe); `--check` vergleicht, `--keep-opt` behält die gespeicherten Optima, `--nur-stichprobe` ergänzt die Stichprobe |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, 3D-Darstellung, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Stützfläche, Schwerpunkt und Gewicht als Bedingung:** Stück 10. Hier werden sie nur als Kennzahl gezählt.
- **Drehung der Quader und andere Regeln für die Wahl des Eckpunkts:** nicht Gegenstand dieses Stücks.
- **Suche nach der Reihenfolge in 3D:** Stück 12 gilt für 2D; in 3D nicht gemessen.
- **Laufzeitvergleich der Verfahren:** hängt an der Umsetzung, keine Aussage.
- **Optimum bei 40 und 80 Quadern:** CP-SAT entscheidet dort nur einen Teil der Instanzen; die Schranke ist der Maßstab.
- **Gütegarantien und Zahlen aus der Literatur:** Das Original wurde nicht gelesen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
