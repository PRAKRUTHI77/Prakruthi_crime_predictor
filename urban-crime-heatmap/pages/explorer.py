"""pages/explorer.py — Interactive data table + download"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import build_global_dataframe, COUNTRY_META, CRIME_TYPES, SOCIO
from utils.theme import BG, BG2, BG3, BORD, BORD2, CYAN, CYAN2, RED, AMB, GRN, TEXT, TDIM


def render(filters):
    crimes   = filters["crime_type"]
    yr       = filters["year_range"]
    country  = filters["country"]
    is_glob  = filters["is_global"]

    st.markdown("""
    <div class="cs-header">
      <div class="cs-title">📋 Data Explorer</div>
      <div class="cs-subtitle">Browse, filter, and export the full crime dataset</div>
      <span class="cs-badge">Raw Data</span>
      <span class="cs-badge">CSV Export</span>
      <span class="cs-badge">Socioeconomic Panel</span>
    </div>
    """, unsafe_allow_html=True)

    df = build_global_dataframe()

    # ── Filter controls ───────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        f_countries = st.multiselect("Filter Countries",
                                     list(COUNTRY_META.keys()),
                                     default=[] if is_glob else [country])
    with fc2:
        f_crimes = st.multiselect("Filter Crime Types", CRIME_TYPES, default=crimes)
    with fc3:
        f_years = st.slider("Year Range", 2010, 2023, yr)

    # Apply
    mask = df["year"].between(*f_years)
    if f_countries: mask &= df["country"].isin(f_countries)
    if f_crimes:    mask &= df["crime_type"].isin(f_crimes)
    fdf = df[mask].round(2)

    # ── Summary stats ─────────────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    for col,(v,l) in zip([c1,c2,c3,c4],[
        (f"{len(fdf):,}",              "RECORDS"),
        (f"{fdf['rate_per_100k'].mean():.2f}", "AVG RATE"),
        (f"{fdf['rate_per_100k'].max():.1f}",  "MAX RATE"),
        (f"{fdf['rate_per_100k'].min():.2f}",  "MIN RATE"),
    ]):
        with col:
            st.markdown(f"""
            <div class="cs-kpi" style="padding:0.8rem 1rem;">
              <div class="cs-kpi-label">{l}</div>
              <div class="cs-kpi-value" style="font-size:1.3rem;">{v}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Data table ────────────────────────────────────────────────────────────
    st.markdown('<div class="cs-section">CRIME DATASET</div>', unsafe_allow_html=True)
    display_df = fdf[["country","region","year","crime_type","rate_per_100k"]].rename(columns={
        "country":"Country","region":"Region","year":"Year",
        "crime_type":"Crime Type","rate_per_100k":"Rate per 100k"
    })
    st.dataframe(display_df, use_container_width=True, height=320)

    # ── Download ──────────────────────────────────────────────────────────────
    csv = display_df.to_csv(index=False).encode()
    st.download_button("⬡ Download CSV", csv, "crimescope_data.csv", "text/csv")

    st.markdown("---")

    # ── Pivot table (rendered as Plotly heatmap — no matplotlib needed) ───────
    st.markdown('<div class="cs-section">PIVOT TABLE — AVG RATE BY COUNTRY × CRIME TYPE</div>', unsafe_allow_html=True)
    pivot = fdf.groupby(["country","crime_type"])["rate_per_100k"].mean().unstack(fill_value=0).round(1)
    fig_pivot = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, BG3], [0.35, "#003355"], [0.7, CYAN2], [1, CYAN]],
        text=pivot.values,
        texttemplate="%{text:.1f}",
        textfont=dict(size=9, color=TEXT),
        showscale=True,
        colorbar=dict(thickness=10, len=0.9,
                      tickfont=dict(color=TDIM, size=8),
                      bgcolor=BG2, bordercolor=BORD2),
        hovertemplate="<b>%{y}</b> — %{x}<br>Rate: %{z:.1f} / 100k<extra></extra>",
    ))
    fig_pivot.update_layout(
        paper_bgcolor=BG2, plot_bgcolor=BG3,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT, size=9),
        xaxis=dict(color=TEXT, side="bottom"),
        yaxis=dict(color=TEXT, autorange="reversed"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=420,
    )
    st.plotly_chart(fig_pivot, use_container_width=True)

    st.markdown("---")

    # ── Socioeconomic panel ───────────────────────────────────────────────────
    st.markdown('<div class="cs-section">SOCIOECONOMIC REFERENCE PANEL</div>', unsafe_allow_html=True)
    socio_rows = []
    for c, (gdp, unemp, urban, gini, police) in SOCIO.items():
        snap_c = df[(df["country"]==c) & (df["year"]==2022)]["rate_per_100k"].mean()
        socio_rows.append({
            "Country": c,
            "Region":  COUNTRY_META[c]["region"],
            "GDP/Cap ($)": gdp,
            "Unemployment (%)": unemp,
            "Urbanisation (%)": urban,
            "Gini Coeff": gini,
            "Police/100k": police,
            "Avg Crime Rate (2022)": round(snap_c, 1),
        })
    sdf = pd.DataFrame(socio_rows).sort_values("Avg Crime Rate (2022)", ascending=False)
    st.dataframe(sdf, use_container_width=True, height=340)

    # Scatter matrix
    st.markdown('<div class="cs-section">SOCIOECONOMIC SCATTER MATRIX</div>', unsafe_allow_html=True)
    import plotly.express as px
    sdf_num = sdf.copy()
    fig_sm = px.scatter_matrix(
        sdf_num,
        dimensions=["GDP/Cap ($)","Unemployment (%)","Gini Coeff","Police/100k","Avg Crime Rate (2022)"],
        color="Region",
        hover_name="Country",
        color_discrete_sequence=["#00d4ff","#00ff9d","#ffaa00","#ff3366","#9d4edd","#4cc9f0"],
    )
    fig_sm.update_traces(diagonal_visible=False, showupperhalf=False,
                         marker=dict(size=5, opacity=0.8))
    fig_sm.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                         font=dict(family="IBM Plex Mono, monospace",color=TEXT,size=9),
                         margin=dict(l=10,r=10,t=20,b=10), height=520,
                         legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9,color=TEXT)))
    st.plotly_chart(fig_sm, use_container_width=True)
