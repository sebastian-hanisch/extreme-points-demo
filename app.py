"""Packen: die dritte Dimension, Extreme Points - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 9 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Quader ohne Überlappung in Behälter: Schichten, Extreme Points ohne und mit Projektionen, dazu fünf Sortierschlüssel.
Das Messraster (vorberechnet in ept_precomputed.json) zeigt an je 100 Zufallsinstanzen, was an Verfahren und Schlüssel hängt und wie viele Quader ohne Stützbedingung nicht sicher stehen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import ept_constants as C
from ept_evaluation import (
    SCHLUESSEL_LISTE,
    VERFAHREN_LISTE,
    Settings,
    analyse,
    optimum_zeilen,
    referenz,
    stuetz_zeilen,
    verdict_aktuell,
    verdict_instanz,
    verdict_messung,
    verdict_optimum,
    verdict_stuetz,
    verdict_stuetz_raster,
    verdict_tabelle,
    zeile,
)
from ept_layout import dunkles_design, kopf_css
from ept_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from ept_visualization import build_behaelter, build_messung

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in ept_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📦 Die dritte Dimension: Extreme Points")
st.markdown(
    """
Stück 8 hat Rechtecke in Behälter gesetzt und den freien Platz verwaltet. Hier sind es **Quader**, und die Frage wird größer: **Was bringen Extreme Points gegenüber Schichten**, dem Gegenstück zum Regal? **Was bringen ihre Projektionen**? Und **welcher Sortierschlüssel passt zu welchem Verfahren**, jetzt mit fünf Schlüsseln statt zwei? Dazu eine Warnung, die erst Stück 10 behebt: **Ohne Stützbedingung stehen viele Quader nicht sicher.** Die Demo zeigt an zwölf Quadern, wie ein Behälter Schritt für Schritt gefüllt wird, und an einem Messraster aus je 100 Zufallsinstanzen, wie viel an Verfahren und Schlüssel hängt.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Packen in 3D", expanded=True):
    st.markdown(
        """
1. **Schlüssel wählen:** Die Quader werden in der Lieferreihenfolge genommen oder absteigend nach Volumen, Grundfläche, Höhe oder längster Kante sortiert.
2. **Verfahren anwenden, Quader für Quader:** *Schichten* setzen den Quader in die erste Schicht, deren Höhe reicht und in der innen noch ein Platz frei ist (eine Schicht hat die Höhe ihres ersten Quaders, innen ein Regalplan); sonst kommt eine neue Schicht obenauf. *Extreme Points* führen eine Liste von **Eckpunkten**: Der Quader kommt an den tiefsten, hintersten, linkesten Eckpunkt, an dem er passt. Danach werden neue Eckpunkte erzeugt: die Ecken rechts, hinten und oben vom Quader, bei *EP voll* zusätzlich deren **Projektionen** auf die nächste Fläche. Passt der Quader in keinen Behälter, wird ein neuer geöffnet.
3. **Schritt-Regler:** Mit dem Regler *Schritt* sehen Sie den Zustand nach den ersten k Quadern, bei Extreme Points mit den Eckpunkten (grüne Rauten), bei Schichten mit den Oberkanten der Schichten (gestrichelt). Der Regler *Behälter* wählt, welcher Behälter gezeichnet wird.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Quader**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Die beiden Beispiele haben je zwölf feste Quader. Die anderen vier sind Zufallsinstanzen mit verschiedener Verteilung der Kanten.")
    n_index = st.selectbox("Zahl der Quader (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select",
                           help="Gilt nur für Zufallsinstanzen.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1,
                           help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Packen**")
    schluessel = st.selectbox("Sortierschlüssel", list(C.SCHLUESSEL), format_func=C.SCHLUESSEL.get, key="schluessel_select",
                              help="Wonach die Quader sortiert werden, absteigend. „Lieferreihenfolge“ sortiert nicht.")
    verfahren = st.selectbox("Verfahren", list(C.VERFAHREN), format_func=C.VERFAHREN.get, key="verfahren_select",
                             help="Wie der Platz im Behälter verwaltet wird und wohin der nächste Quader kommt.")
    schritt = st.number_input("Schritt (0 = alle Quader)", *bounds("schritt_input"), key="schritt_input", step=1,
                              help="Zeigt den Zustand nach den ersten k Quadern in der Reihenfolge des Schlüssels. Größere Werte als die Zahl der Quader zeigen alle.")
    behaelter = st.number_input("Behälter (der gezeichnet wird)", *bounds("behaelter_input"), key="behaelter_input", step=1,
                                help="Nummer des Behälters, der gezeichnet wird. Gibt es weniger Behälter, wird der letzte gezeigt.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "schluessel_select": int(schluessel), "verfahren_select": int(verfahren),
                   "schritt_input": int(schritt), "behaelter_input": int(behaelter)})

settings = Settings(int(quelle), int(n_index), int(seed), int(schluessel), int(verfahren), int(schritt), int(behaelter))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
if a.opt is not None:
    m1.metric("Behälter (ganze Packung)", a.count, delta=a.count - a.opt, delta_color="inverse", help="Delta: gewählte Behälterzahl minus Optimum.")
    m2.metric("Optimum (exakt, über alle Packungen)", a.opt, delta="Referenz", delta_color="off")
else:
    m1.metric("Behälter (ganze Packung)", a.count)
    m2.metric("Optimum", "nicht berechnet", delta="nur für die Beispiele", delta_color="off")
m3.metric("Untere Schranke", a.schranke, delta="Volumen oder große Quader", delta_color="off")
volumen = sum(w * d * h for w, d, h in a.inst.kisten)
st.caption(f"{a.inst.n} Quader, Gesamtvolumen {volumen} von {a.inst.cap ** 3} je Behälter. In Lieferreihenfolge brauchen sie mit dem gewählten Verfahren {a.liefer} Behälter.")
st.markdown(f"**Zustand nach {a.schritt} von {a.inst.n} Quadern, Behälter {a.gezeigt + 1} von {len(a.bins)}:** der rote Rahmen ist der Behälter, die Farbe zeigt die Reihenfolge des Setzens, die Beschriftung beim Überfahren die Nummer in der Lieferreihenfolge.")
st.plotly_chart(build_behaelter(a.inst.kisten, a.platz, a.gezeigt, a.inst.cap, a.zustand[a.gezeigt] if a.zustand else (), settings.verfahren), width="stretch", key="main_chart")
st.caption("Die Quader sind maßstäblich; der Behälter lässt sich mit der Maus drehen. Grüne Rauten: Eckpunkte (Extreme Points); gestrichelt grün: Oberkanten der Schichten.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verändert die Behälterzahl mehr, das Verfahren oder der Sortierschlüssel?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Schlüssel \\ Verfahren | " + " | ".join(C.VERFAHREN_KURZ[v] for v in VERFAHREN_LISTE) + " |", "|---|" + "---|" * len(VERFAHREN_LISTE)]
for k in SCHLUESSEL_LISTE:
    zellen = []
    for v in VERFAHREN_LISTE:
        wert = str(a.tabelle[k][v])
        zellen.append(f"**{wert}**" if (k, v) == (settings.schluessel, settings.verfahren) else wert)
    zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(zellen) + " |")
st.markdown("Behälterzahl der ganzen Packung für alle 15 Kombinationen (die gewählte ist fett):\n\n" + "\n".join(zeilen))
kind, text = verdict_tabelle(a)
getattr(st, kind)(text)

st.markdown("### ⚠️ Stehen die Quader sicher?")
kind, text = verdict_stuetz(a)
getattr(st, kind)(text)
st.caption("Stützfläche eines Quaders: der Anteil seiner Grundfläche, der auf dem Boden oder auf den Oberseiten anderer Quader aufliegt. Diese Demo verlangt keine; Stück 10 (Stützfläche und Schwerpunkt) tut es.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Behälter {C.CAP} mal {C.CAP} mal {C.CAP}, ganzzahlige Maße der Quader ohne Drehung, ohne Stützbedingung. "
    "Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Verteilung der Quader", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Quader n", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(ni))

st.markdown("### Experiment 1: Welcher Schlüssel zu welchem Verfahren?")
basis, mittel = referenz(z)
st.plotly_chart(build_messung(mittel, f"Behälter über {basis} (Mittel)"), width="stretch", key="exp_chart")
tab = ["| Schlüssel | " + " | ".join(C.VERFAHREN_KURZ[v] for v in VERFAHREN_LISTE) + " |", "|---|" + "---|" * len(VERFAHREN_LISTE)]
for k in SCHLUESSEL_LISTE:
    tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(f"{mittel[k][v]:.2f}" for v in VERFAHREN_LISTE) + " |")
st.markdown("\n".join(tab))
st.caption(f"Mittlere Behälter über {basis}: Mittel über die Instanzen der Zelle" + (" (nur die entschiedenen)" if z["exakt"] else "") + ". „EP einfach“ nutzt nur die drei Nachfolgepunkte, „EP voll“ dazu die Projektionen.")
kind, text = verdict_messung(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Instanz für Instanz")
kind, text = verdict_instanz(z)
getattr(st, kind)(text)

st.markdown("### Experiment 3: Wie nah am Optimum?")
oz = optimum_zeilen()
tab2 = ["| Quader | Schichten | EP einfach | EP voll |", "|---|---|---|---|"]
for r in oz:
    f = lambda x: "-" if x is None else f"{x:.0f} %"  # noqa: E731
    offen = f", {r['offen']} offen" if r["offen"] else ""
    tab2.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} {r['n']}{offen} | {f(r['schichten'])} | {f(r['einfach'])} | {f(r['voll'])} |")
st.markdown("\n".join(tab2))
st.caption(
    "Anteil der entschiedenen Instanzen, in denen die Kombination genau das Optimum braucht: Schichten mit Höhe, EP einfach mit Volumen, EP voll mit Volumen (jeweils der Schlüssel, der zum Verfahren passt). "
    "„offen“ hinter dem Namen: Zahl der nicht entschiedenen Instanzen; die entschiedenen sind die leichteren. Das Optimum gilt über alle Packungen. Kleine Quader passen bei 12 und 20 Stück in einen Behälter: trivial."
)
kind, text = verdict_optimum(oz)
getattr(st, kind)(text)

st.markdown("### Experiment 4: Wie viele Quader stehen nicht sicher?")
sz = stuetz_zeilen()
tab3 = ["| Quader | unter 80 % Stützfläche | ohne jede Stütze |", "|---|---|---|"]
for r in sz:
    tab3.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} {r['n']} | {r['unter80']:.1f} % | {r['schwebend']:.1f} % |")
st.markdown("\n".join(tab3))
st.caption("Anteil der Quader aller Instanzen der Zelle, in Packungen von EP voll mit Volumen, ohne Stützbedingung.")
kind, text = verdict_stuetz_raster(sz)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Keine Stützbedingung** | Viele Quader liegen auf weniger als 80 % ihrer Grundfläche, einige schweben (Experiment 4). Mit einer Mindest-Stützfläche ändern sich Behälterzahlen und Reihenfolge der Quader; das misst Stück 10. |
| **Keine Drehung** | Dürfen die Quader gedreht werden, ändert sich die Aufgabe, und viele Verfahren nutzen das; die Demo misst es nicht. |
| **Immer der tiefste, hinterste, linkeste Eckpunkt** | Andere Regeln für die Wahl unter den Eckpunkten können andere Ergebnisse geben; die Demo misst nur diese. |
| **Die Kanten sind zufällig verteilt** | Nur vier Verteilungen mit festen Bereichen sind gemessen. Andere Verteilungen können anders ausfallen. |
| **Die Schranke ist scharf** | In 3D ist sie locker; bei 40 und 80 Quadern fehlt das Optimum ganz, dort zählt nur der Vergleich der Kombinationen. |
| **Alle Quader sind vor dem Packen bekannt** | Wer jeden Quader sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Quader mit ganzzahliger Breite, Tiefe und Höhe und Behälter der Größe $C \times C \times C$. *Gesucht:* eine überlappungsfreie Platzierung aller Quader in möglichst wenigen Behältern, ohne Drehung.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Quader |
| $w_i$, $d_i$, $h_i$ | Breite, Tiefe und Höhe von Quader $i$, $1 \le w_i, d_i, h_i \le C$ |
| $C$ | Kantenlänge eines Behälters |
| $(x_i, y_i, z_i)$ | linke hintere untere Ecke von Quader $i$ |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Platzierungen |
| $L$ | untere Schranke für $\mathrm{OPT}$ |

**Reihenfolge.** Ein Schlüssel ordnet jedem Quader eine Zahl $s_i$ zu: $w_i d_i h_i$, $w_i d_i$, $h_i$ oder $\max(w_i, d_i, h_i)$; die Quader werden nach fallendem $s_i$ genommen, Gleichstände in der Lieferreihenfolge. Jedes Verfahren setzt die Quader der Reihe nach, jeder kommt in den ersten Behälter, in dem es nach der Regel des Verfahrens eine Stelle gibt, sonst in einen neuen; gesetzte Quader bleiben liegen.

**Schichten.** Eine Schicht beginnt bei der Höhe $z$ und hat die Höhe ihres ersten Quaders $h_1$; innen ist sie ein Regalplan der Grundfläche $C \times C$ (Regale der Tiefe des ersten Quaders des Regals). Ein Quader passt in eine Schicht, wenn $h_i \le h_1$ und er in ein Regal passt (Tiefe höchstens die des Regals, belegte Breite plus $w_i$ höchstens $C$) oder ein neues Regal in die Schicht passt; sonst öffnet er eine Schicht über der letzten, wenn $z + h_i \le C$.

**Extreme Points.** Die Menge $E$ der Eckpunkte eines Behälters beginnt mit $\{(0,0,0)\}$. Ein Quader $(w, d, h)$ passt an $p = (x, y, z) \in E$, wenn $x + w \le C$, $y + d \le C$, $z + h \le C$ und der Quader keinen gesetzten überlappt; er kommt an den passenden Punkt mit kleinstem $(z, y, x)$ (lexikographisch). Danach entfällt $p$, und es kommen hinzu: $(x + w, y, z)$, $(x, y + d, z)$, $(x, y, z + h)$; bei *EP voll* zusätzlich zu jedem dieser drei Punkte seine Projektionen: der Punkt wird in negativer Richtung jeder der beiden anderen Achsen bis zur nächsten Fläche eines gesetzten Quaders oder bis zur Wand verschoben. Punkte im Inneren eines Quaders entfallen.

**Stützfläche.** Die Stützfläche von Quader $i$ mit $z_i > 0$ ist $\sum_j |\,[x_i, x_i + w_i) \cap [x_j, x_j + w_j)\,| \cdot |\,[y_i, y_i + d_i) \cap [y_j, y_j + d_j)\,|$ über die Quader $j$ desselben Behälters mit $z_j + h_j = z_i$, geteilt durch $w_i d_i$; am Boden ist sie 1.

**Schranken.** $L_{\mathrm{Vol}} = \left\lceil \tfrac{1}{C^3} \sum_i w_i d_i h_i \right\rceil \le \mathrm{OPT}$. Quader mit $w_i, d_i, h_i > C/2$ („große“) enthalten in jedem Behälter den Mittelpunkt und überlappen deshalb paarweise; also $L_{\mathrm{gr}} = |\{ i : w_i, d_i, h_i > C/2 \}| \le \mathrm{OPT}$ und $L = \max(L_{\mathrm{Vol}}, L_{\mathrm{gr}})$.

**Exaktes Optimum** (nur Generator und Tests, nicht diese App). CP-SAT: Jeder Quader liegt in genau einem Behälter, und je zwei Quader im selben Behälter sind in mindestens einer von sechs Richtungen getrennt ($x_i + w_i \le x_j$, $x_j + w_j \le x_i$ und ebenso in $y$ und $z$); minimiert wird die Zahl benutzter Behälter. Das Optimum gilt über alle Packungen.

**Literatur** (nur Name und Gegenstand, aus dem Gedächtnis, Original nicht gelesen). Crainic, Perboli und Tadei (2008) beschreiben Extreme Points für das dreidimensionale Packen. Die Demo übernimmt daraus keine Zahl, keine Gütegarantie und keine Aussage zu Dichte oder Geschwindigkeit; die Projektionen sind hier nach eigener Lesart umgesetzt.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
