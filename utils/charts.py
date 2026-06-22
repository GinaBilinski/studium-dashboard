import plotly.graph_objects as go
from utils.helpers import format_note

# Farben für Diagramme
GREY_SOLL = "#D3D8DE"
WHITE_REST = "#F0F2F6"
GREEN = "#22D173"
AMBER = "#FFCB00"
RED = "#ff3333"

# Balkendiagramm (ECTS-Fortschritt)
def stacked_progress(total, ist, soll):
    ist = max(0, min(ist, total))
    soll = max(0, min(soll, total))
    prog_color = GREEN if ist >= soll else (AMBER if (soll - ist) <= 5 else RED)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[total], y=[""], orientation="h",
        marker=dict(color=WHITE_REST),
        hoverinfo="skip", showlegend=False
    ))
    fig.add_trace(go.Bar(
        x=[ist], y=[""], orientation="h",
        marker=dict(color=prog_color),
        hoverinfo="skip", showlegend=False
    ))
    deficit = max(0, soll - ist)
    if deficit > 0:
        fig.add_trace(go.Bar(
            x=[deficit], y=[""], base=ist, orientation="h",
            marker=dict(color=GREY_SOLL),
            hoverinfo="skip", showlegend=False
        ))
    fig.update_layout(
        barmode="overlay", height=70,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(visible=False, range=[0, total]),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig


# Donut-Diagramm (ECTS-Gesamtfortschritt)
def donut_ects(ist, total, soll):
    ist = max(0, min(ist, total))
    soll = max(0, min(soll, total))
    gap_soll = max(0, soll - ist)
    gap_rest = max(0, total - soll)
    ist_color = GREEN if ist >= soll else RED

    fig = go.Figure(go.Pie(
        values=[ist, gap_soll, gap_rest],
        hole=0.70, sort=False, direction="clockwise",
        marker=dict(colors=[ist_color, GREY_SOLL, WHITE_REST]),
        textinfo="none", hoverinfo="skip", showlegend=False
    ))

    fig.update_layout(
        height=240, margin=dict(l=0, r=0, t=0, b=0),
        annotations=[dict(
            text=f"<b>{ist}/{total}</b><br>ECTS",
            showarrow=False, font_size=18
        )],
        showlegend=False
    )
    return fig


# Halbkreisdiagramm (Notenübersicht)
def grade_semi(avg: float | None, ziel: float | None = None):
    def to_pct(note: float) -> float:
        return max(0.0, min(1.0, (5.0 - note) / 4.0))

    arc = 0.75
    gap = 1 - arc
    ziel_fill = 0.0 if ziel is None else to_pct(ziel) * arc
    ist_fill = 0.0 if avg is None else to_pct(float(avg)) * arc

    if avg is None:
        ist_color = "#9CA3AF"
        center = "–<br>Ø-Note"
    else:
        ist_color = GREEN if avg <= 1.7 else (AMBER if avg <= 2.0 else RED)
        center = f"<b>{format_note(avg)}</b><br>Ø-Note"

    base = go.Pie(
        values=[ziel_fill, max(0.0, arc - ziel_fill), gap],
        hole=0.70, rotation=225, sort=False, direction="clockwise",
        marker=dict(colors=[GREY_SOLL, WHITE_REST, "rgba(0,0,0,0)"]),
        textinfo="none", hoverinfo="skip", showlegend=False
    )

    overlay = go.Pie(
        values=[min(ist_fill, arc), max(0.0, arc - ist_fill), gap],
        hole=0.70, rotation=225, sort=False, direction="clockwise",
        marker=dict(colors=[ist_color, "rgba(0,0,0,0)", "rgba(0,0,0,0)"]),
        textinfo="none", hoverinfo="skip", showlegend=False
    )

    fig = go.Figure([base, overlay])
    fig.update_layout(
        height=240, margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=center, showarrow=False, font_size=18)],
        showlegend=False
    )
    return fig