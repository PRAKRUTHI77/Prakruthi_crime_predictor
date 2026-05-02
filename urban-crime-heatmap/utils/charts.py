"""utils/charts.py — Plotly chart helpers for the cyan terminal theme."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.theme import (BG, BG2, BG3, BORD, BORD2, CYAN, CYAN2,
                          RED, AMB, GRN, PURP, TEXT, TDIM, PALETTE, BASE_LAYOUT)


def _apply(fig: go.Figure, title="", height=360) -> go.Figure:
    kw = dict(BASE_LAYOUT)
    kw["height"] = height
    if title:
        kw["title"] = dict(text=title, font=dict(size=12, color=CYAN,
                           family="IBM Plex Mono, monospace"), x=0.01, y=0.97)
    fig.update_layout(**kw)
    return fig


def line_chart(df, x, y, color, title="", height=360):
    fig = px.line(df, x=x, y=y, color=color,
                  color_discrete_sequence=PALETTE, markers=True)
    fig.update_traces(line=dict(width=2), marker=dict(size=5))
    return _apply(fig, title, height)


def area_chart(df, x, y, color, title="", height=360):
    fig = px.area(df, x=x, y=y, color=color,
                  color_discrete_sequence=PALETTE)
    fig.update_traces(line=dict(width=1.5))
    return _apply(fig, title, height)


def bar_chart(df, x, y, color=None, title="", height=320, orientation="v"):
    if color:
        fig = px.bar(df, x=x, y=y, color=color,
                     color_discrete_sequence=PALETTE,
                     orientation=orientation, barmode="group")
    else:
        fig = px.bar(df, x=x, y=y, orientation=orientation,
                     color_discrete_sequence=[CYAN])
        fig.update_traces(marker_color=CYAN, marker_opacity=0.85)
    return _apply(fig, title, height)


def heatmap_chart(z, x, y, title="", height=340):
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y,
        colorscale=[[0, BG3], [0.25, "#003355"], [0.6, CYAN2], [1, CYAN]],
        showscale=True,
        colorbar=dict(thickness=10, len=0.8,
                      tickfont=dict(color=TDIM, size=8),
                      bgcolor=BG2, bordercolor=BORD2),
    ))
    return _apply(fig, title, height)


def radar_chart(categories, values, name="Profile", title="", height=340):
    cats = categories + [categories[0]]
    vals = values + [values[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself", name=name,
        fillcolor=f"rgba(0,212,255,0.15)",
        line=dict(color=CYAN, width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=BG3,
            radialaxis=dict(visible=True, gridcolor=BORD, color=TDIM, tickfont=dict(size=8)),
            angularaxis=dict(gridcolor=BORD, color=TEXT, tickfont=dict(size=9)),
        ),
        paper_bgcolor=BG2, plot_bgcolor=BG3,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT),
        showlegend=False, height=height,
        margin=dict(l=55, r=55, t=50, b=40),
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=12, color=CYAN,
                          family="IBM Plex Mono, monospace"), x=0.01))
    return fig


def box_plot(df, x, y, title="", height=340):
    fig = px.box(df, x=x, y=y, color=x,
                 color_discrete_sequence=PALETTE)
    fig.update_traces(marker_size=3)
    return _apply(fig, title, height)


def scatter_bubble(df, x, y, size, color_col, hover, title="", height=380):
    fig = px.scatter(
        df, x=x, y=y, size=size, color=color_col,
        hover_name=hover,
        color_continuous_scale=[[0, GRN], [0.5, AMB], [1, RED]],
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color=BG), opacity=0.85))
    fig.update_coloraxes(colorbar=dict(thickness=10, tickfont=dict(color=TDIM, size=8),
                                       bgcolor=BG2, bordercolor=BORD2))
    return _apply(fig, title, height)


def gauge(value: float, title="", ref=None, height=220):
    steps = [
        dict(range=[0, 5],  color="#0d2a1a"),
        dict(range=[5, 15], color="#2a2000"),
        dict(range=[15, 40],color="#2a0a00"),
        dict(range=[40, 100],color="#2a0010"),
    ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta=dict(reference=ref, valueformat=".1f") if ref else None,
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=TDIM, tickfont=dict(color=TDIM, size=8)),
            bar=dict(color=CYAN, thickness=0.25),
            bgcolor=BG3, bordercolor=BORD2,
            steps=steps,
            threshold=dict(line=dict(color=RED, width=2), thickness=0.8, value=40),
        ),
        number=dict(font=dict(color=CYAN, family="Orbitron, monospace", size=28), suffix="/100k"),
        title=dict(text=title, font=dict(color=TEXT, size=11, family="IBM Plex Mono, monospace")),
    ))
    fig.update_layout(paper_bgcolor=BG2, font=dict(color=TEXT), height=height,
                      margin=dict(l=25, r=25, t=35, b=15))
    return fig


def waterfall_chart(categories, values, title="", height=320):
    colors = [CYAN if v < 0 else RED for v in values]
    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=colors,
        text=[f"{v:+.1f}" for v in values],
        textposition="outside",
        textfont=dict(color=TEXT, size=9),
    ))
    fig.add_hline(y=0, line_color=BORD2, line_width=1)
    return _apply(fig, title, height)


def histogram(df, x, color=None, title="", height=300, nbins=20):
    fig = px.histogram(df, x=x, color=color, nbins=nbins,
                       color_discrete_sequence=PALETTE)
    fig.update_traces(marker_line_color=BG, marker_line_width=0.5)
    return _apply(fig, title, height)


def treemap(df, path, values, title="", height=380):
    fig = px.treemap(df, path=path, values=values,
                     color=values,
                     color_continuous_scale=[[0, BG3], [0.5, CYAN2], [1, CYAN]])
    fig.update_traces(textfont=dict(family="IBM Plex Mono, monospace", color=TEXT))
    fig.update_layout(paper_bgcolor=BG2, height=height,
                      margin=dict(l=5, r=5, t=40, b=5),
                      font=dict(family="IBM Plex Mono, monospace", color=TEXT))
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=12, color=CYAN), x=0.01))
    return fig
