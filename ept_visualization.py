"""Plotly-Abbildungen: ein Behälter in 3D (Mesh3d) und das Messraster als Balken. Die Balkendiagramme haben gesperrte Achsen (fixedrange), damit Touch-Geräte beim Scrollen nicht hängen bleiben."""

import plotly.graph_objects as go

import ept_constants as C

# Ecken eines Quaders (x, y, z, w, d, h): 0 bis 3 unten (gegen den Uhrzeigersinn von oben gesehen: (x,y), (x+w,y), (x+w,y+d), (x,y+d)), 4 bis 7 darüber.
# Zwei Dreiecke je Seitenfläche: unten, oben, vorn (y), hinten (y + d), links (x), rechts (x + w).
DREIECKE = ((0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (3, 7, 6), (3, 6, 2), (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5))
KANTEN = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))


def ecken(x, y, z, w, d, h):
    return [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z), (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]


def quader_mesh(x, y, z, w, d, h, farbe, name, text):
    e = ecken(x, y, z, w, d, h)
    return go.Mesh3d(x=[p[0] for p in e], y=[p[1] for p in e], z=[p[2] for p in e], i=[t[0] for t in DREIECKE], j=[t[1] for t in DREIECKE], k=[t[2] for t in DREIECKE],
                     color=farbe, opacity=0.85, flatshading=True, name=name, hovertext=text, hoverinfo="text", showlegend=False)


def kantenlinien(boxen, farbe, breite):
    """Alle Kanten der Quader (x, y, z, w, d, h) als eine Linie mit Lücken."""
    xs, ys, zs = [], [], []
    for b in boxen:
        e = ecken(*b)
        for a, c in KANTEN:
            xs += [e[a][0], e[c][0], None]
            ys += [e[a][1], e[c][1], None]
            zs += [e[a][2], e[c][2], None]
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color=farbe, width=breite), hoverinfo="skip", showlegend=False)


def build_behaelter(kisten, platz, behaelter, cap, zustand, verfahren):
    """Ein Behälter in 3D: der Rahmen rot, jeder Quader massiv (Farbe nach der Reihenfolge des Setzens, Beschriftung beim Überfahren: Nummer in der Lieferreihenfolge), bei Extreme Points die
    Eckpunkte als Marker, bei Schichten die Oberkanten der Schichten als dünne Linien. `zustand` ist der Zustand des gezeigten Behälters (Schichten oder Eckpunkte)."""
    fig = go.Figure()
    fig.add_trace(kantenlinien([(0, 0, 0, cap, cap, cap)], C.COLOR_LINE, 4))
    gesetzt = [(s, p) for s, p in enumerate(platz) if p[1] == behaelter]
    for s, (i, _b, x, y, z) in gesetzt:
        w, d, h = kisten[i]
        fig.add_trace(quader_mesh(x, y, z, w, d, h, C.KISTEN_FARBEN[s % len(C.KISTEN_FARBEN)], f"Quader {i + 1}",
                                  f"Schritt {s + 1}: Quader {i + 1}, {w} × {d} × {h}, Ecke ({x}, {y}, {z})"))
    if gesetzt:
        fig.add_trace(kantenlinien([(x, y, z, *kisten[i]) for _s, (i, _b, x, y, z) in gesetzt], "white", 2))
    if verfahren == C.SCHICHTEN:
        for z0, h in zustand:
            fig.add_trace(go.Scatter3d(x=[0, cap, cap, 0, 0], y=[0, 0, cap, cap, 0], z=[z0 + h] * 5, mode="lines", line=dict(color=C.COLOR_PUNKT, width=2, dash="dash"),
                                       hoverinfo="skip", showlegend=False))
    else:
        punkte = list(zustand)
        if punkte:
            fig.add_trace(go.Scatter3d(x=[p[0] for p in punkte], y=[p[1] for p in punkte], z=[p[2] for p in punkte], mode="markers", marker=dict(size=4, color=C.COLOR_PUNKT, symbol="diamond"),
                                       hovertext=[f"Eckpunkt ({p[0]}, {p[1]}, {p[2]})" for p in punkte], hoverinfo="text", showlegend=False))
    achse = dict(range=[0, cap], showbackground=False, showgrid=True, zeroline=False)
    fig.update_layout(height=460, margin=dict(l=0, r=0, t=0, b=0), scene=dict(xaxis=dict(title="x (Breite)", **achse), yaxis=dict(title="y (Tiefe)", **achse), zaxis=dict(title="z (Höhe)", **achse),
                                                                               aspectmode="cube", camera=dict(eye=dict(x=1.6, y=-1.6, z=1.0))))
    return fig


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_messung(mittel, titel):
    """Gruppierte Balken: je Schlüssel die mittleren Behälter über der Bezugsgröße für die drei Verfahren."""
    fig = go.Figure()
    for v in sorted(C.VERFAHREN):
        fig.add_trace(go.Bar(name=C.VERFAHREN_KURZ[v], x=[C.SCHLUESSEL_KURZ[k] for k in sorted(C.SCHLUESSEL)], y=[mittel[k][v] for k in sorted(C.SCHLUESSEL)], marker_color=C.VERFAHREN_FARBEN[v],
                             hovertemplate="%{x}: %{y:.2f}<extra>" + C.VERFAHREN_KURZ[v] + "</extra>"))
    fig.update_layout(barmode="group", height=320, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(title_text=titel)
    return lock_axes(fig)
