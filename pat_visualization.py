"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import pat_constants as C

REGEL_ACHSE = {"erster": "erster passender", "engste": "engste Passung", "groesste": "größte Spitze", "rechts": "ganz rechts", "zufall": "Zufallswahl"}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_stapel(stapel, markiert=(), zuletzt=None, hoehe=360, titel_y="Höhe im Stapel (unten zuerst gelegt)", rot=()):
    """Stapel als Säulen von Containern; oben liegt der Kleinste, der zuerst geholt wird. `markiert`: Ränge einer längsten wachsenden Teilfolge
    (farbig); `zuletzt`: Rang des zuletzt gelegten Containers (orangefarbener Rand). Beschriftung als Text im Marker, die x-Achse zeigt Textmarken."""
    anzahl = max(len(stapel), 1)
    max_h = max((len(s) for s in stapel), default=1)
    groesse = max(14, min(34, 280 / (max_h + 1), 620 / (anzahl + 1)))
    markiert = set(markiert)
    rot = set(rot)
    fig = go.Figure()
    xs, ys, texte, farben, raender, rand_b = [], [], [], [], [], []
    for j, s in enumerate(stapel, 1):
        for h, rang in enumerate(s, 1):
            xs.append(j)
            ys.append(h)
            texte.append(str(rang))
            farben.append(C.COLOR_FALSCH if rang in rot else (C.COLOR_LIS if rang in markiert else C.COLOR_BOX))
            if zuletzt is not None and rang == zuletzt and h == len(s):
                raender.append(C.COLOR_NEU)
                rand_b.append(4)
            else:
                raender.append("rgba(0,0,0,0)")
                rand_b.append(0)
    if xs:
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text", text=texte, textfont=dict(color="white", size=max(9, int(groesse * 0.45))),
            marker=dict(symbol="square", size=groesse, color=farben, line=dict(color=raender, width=rand_b)),
            hovertemplate="Stapel %{x}, Höhe %{y}: Rang %{text}<extra></extra>", showlegend=False,
        ))
    else:
        fig.add_annotation(text="noch kein Container gelegt", x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_xaxes(range=[0.4, max(anzahl, 5) + 0.6], tickmode="array", tickvals=list(range(1, anzahl + 1)),
                     ticktext=[f"Stapel {j}" for j in range(1, anzahl + 1)] if anzahl <= 12 else [str(j) for j in range(1, anzahl + 1)], showgrid=False)
    fig.update_yaxes(range=[0.3, max(max_h, 3) + 0.9], title_text=titel_y, showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(height=hoehe, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_regeln(zeile):
    """Anteil der Folgen (Prozent), in denen eine Regel mehr Stapel legt als nötig (Aufzählung aller n! Folgen)."""
    f = zeile["folgen"]
    r = zeile["regeln"]
    werte = {"erster": 0, "engste": 0, "groesste": r["groesste"], "rechts": r["rechts"], "zufall": r["zufall"]}
    namen = [REGEL_ACHSE[k] for k in werte]
    anteile = [100.0 * v / f for v in werte.values()]
    fig = go.Figure(go.Bar(x=namen, y=anteile, marker_color=[C.COLOR_LIS if v == 0 else C.COLOR_FALSCH for v in werte.values()],
                           text=[f"{a:.1f}".replace(".", ",") + " %" for a in anteile], textposition="outside", hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_yaxes(title_text="Folgen mit mehr Stapeln als nötig (%)", range=[0, max(anteile + [10]) * 1.25])
    return _base(fig)


def build_richtung(modell_v):
    """Modell V, n = 10: Mittel der LIS (richtige Richtung) gegen Mittel der LDS (falsche Richtung) je D."""
    schluessel = ["0.5", "1.0", "2.0", "4.0", "8.0", "16.0", "uniform"]
    namen = [("D = " + k.replace(".0", "").replace(".", ",")) if k != "uniform" else "uniform (Modell U)" for k in schluessel]
    lis = [modell_v[k]["summe_lis"] / modell_v[k]["anzahl"] for k in schluessel]
    lds = [modell_v[k]["summe_lds"] / modell_v[k]["anzahl"] for k in schluessel]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=namen, y=lis, name="fallende Stapel (LIS, richtig)", marker_color=C.COLOR_LIS, hovertemplate="%{x}: %{y:.2f}<extra>LIS</extra>"))
    fig.add_trace(go.Bar(x=namen, y=lds, name="wachsende Stapel (LDS, falsche Richtung)", marker_color=C.COLOR_FALSCH, hovertemplate="%{x}: %{y:.2f}<extra>LDS</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Mittel Stapel (n = 10, Zufallsfolgen)")
    return _base(fig)


def build_verteilung(exakt=None, stichprobe=None, n=None):
    """Anteil der Folgen mit genau k Stapeln (Prozent): exakt (alle n! Folgen) und/oder Stichprobe."""
    fig = go.Figure()
    if exakt is not None:
        gesamt = sum(exakt)
        ks = list(range(1, len(exakt) + 1))
        fig.add_trace(go.Bar(x=[str(k) for k in ks], y=[100.0 * v / gesamt for v in exakt], name="exakt (alle Folgen)", marker_color=C.COLOR_LIS,
                             hovertemplate="%{x} Stapel: %{y:.2f} %<extra>exakt</extra>"))
    if stichprobe is not None:
        anzahl = sum(stichprobe.values())
        n_ = n if n is not None else max(stichprobe)
        ks = list(range(1, n_ + 1))
        fig.add_trace(go.Bar(x=[str(k) for k in ks], y=[100.0 * stichprobe.get(k, 0) / anzahl for k in ks], name="Stichprobe", marker_color=C.COLOR_LINE,
                             hovertemplate="%{x} Stapel: %{y:.2f} %<extra>Stichprobe</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Zahl der Stapel k (kleinste Zahl ohne Umsetzen)")
    fig.update_yaxes(title_text="Anteil der Folgen (%)")
    return _base(fig)


def build_abstand(abstand_liste, titel="exakt (alle Folgen)", farbe=None):
    """Verteilung des Abstands verzögert minus sofort (0, 1, 2, ...) als Anteil der Folgen in Prozent."""
    gesamt = sum(abstand_liste)
    fig = go.Figure(go.Bar(x=[str(k) for k in range(len(abstand_liste))], y=[100.0 * v / gesamt for v in abstand_liste], name=titel,
                           marker_color=farbe or C.COLOR_LIS, hovertemplate="Abstand %{x}: %{y:.2f} %<extra></extra>"))
    fig.update_xaxes(title_text="Abstand: Stapel verzögert minus Stapel sofort")
    fig.update_yaxes(title_text="Anteil der Folgen (%)")
    return _base(fig)
