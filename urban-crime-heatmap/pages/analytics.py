"""pages/analytics.py"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.data_loader import (
    build_global_dataframe, get_country_data, get_timeseries,
    get_latest_snapshot, safety_index, COUNTRY_META, CRIME_TYPES
)
from utils import charts as C
from utils.theme import BG, BG2, BG3, BORD, BORD2, CYAN, CYAN2, RED, AMB, GRN, TEXT, TDIM, PALETTE


def render(filters: dict):
    country  = filters["country"]
    crimes   = filters["crime_type"]
    yr       = filters["year_range"]
    is_glob  = filters["is_global"]
    label    = "Global Overview" if is_glob else country

    st.markdown(f"""
    <div class="cs-header">
      <div class="cs-title">📊 Analytics Dashboard</div>
      <div class="cs-subtitle">Deep-dive crime statistics &nbsp;|&nbsp; Region: <span style="color:{CYAN};">{label}</span></div>
      <span class="cs-badge">ML Insights</span>
      <span class="cs-badge">Radiance Trends</span>
      <span class="cs-badge">Correlation Lab</span>
    </div>
    """, unsafe_allow_html=True)

    df_all = build_global_dataframe()
    snap   = get_latest_snapshot(crimes, year=yr[1])

    if is_glob:
        cdf = df_all[(df_all["crime_type"].isin(crimes)) & (df_all["year"].between(*yr))]
    else:
        cdf = get_country_data(country, crimes, yr)
        if cdf.empty:
            st.warning("No data for selection."); return

    # ── TABS ─────────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5 = st.tabs([
        "📈 Radiance Trends",
        "🕸 Crime Profile",
        "🔥 Heatmap Matrix",
        "📦 Distribution",
        "🌐 Country Rankings",
    ])

    # TAB 1 – Trends
    with t1:
        st.markdown('<div class="cs-section">CRIME RATE TRENDS OVER TIME</div>', unsafe_allow_html=True)
        if is_glob:
            ts = cdf.groupby(["year","crime_type"])["rate_per_100k"].mean().reset_index()
        else:
            ts = get_timeseries(country, crimes, yr)

        col_ts, col_yoy = st.columns([3,1])
        with col_ts:
            fig = C.area_chart(ts, "year", "rate_per_100k", "crime_type",
                               title=f"Crime Rate Trends (per 100k) — {label}", height=340)
            st.plotly_chart(fig, use_container_width=True)

        with col_yoy:
            st.markdown('<div class="cs-section">YOY CHANGE</div>', unsafe_allow_html=True)
            pivot = ts.pivot(index="year", columns="crime_type", values="rate_per_100k")
            if len(pivot) >= 2:
                yoy = ((pivot.iloc[-1] - pivot.iloc[-2]) / pivot.iloc[-2] * 100).dropna()
                for crime, pct in yoy.items():
                    arr = "▲" if pct>0 else "▼"
                    col = RED if pct>0 else GRN
                    st.markdown(f"""
                    <div class="cs-kpi" style="margin-bottom:0.4rem;padding:0.7rem 1rem;">
                      <div class="cs-kpi-label">{crime[:14]}</div>
                      <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:{col};">{arr} {abs(pct):.1f}%</div>
                    </div>""", unsafe_allow_html=True)

        # Animated bubble
        st.markdown('<div class="cs-section">ANIMATED CRIME EVOLUTION</div>', unsafe_allow_html=True)
        anim = df_all[df_all["crime_type"].isin(crimes)].groupby(
            ["country","year","region"])["rate_per_100k"].mean().reset_index()
        fig_a = px.scatter(anim, x="region", y="rate_per_100k",
                           size="rate_per_100k", color="country",
                           animation_frame="year", hover_name="country",
                           color_discrete_sequence=px.colors.qualitative.Bold,
                           size_max=55)
        fig_a.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                            font=dict(family="IBM Plex Mono, monospace", color=TEXT),
                            xaxis=dict(gridcolor=BORD,color=TEXT),
                            yaxis=dict(gridcolor=BORD,color=TDIM),
                            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9,color=TEXT)),
                            margin=dict(l=10,r=10,t=20,b=10), height=380)
        st.plotly_chart(fig_a, use_container_width=True)

    # TAB 2 – Radar + Box
    with t2:
        col_r, col_b = st.columns(2)
        with col_r:
            st.markdown('<div class="cs-section">CRIME TYPE RADAR PROFILE</div>', unsafe_allow_html=True)
            yr_data = cdf[cdf["year"]==yr[1]].groupby("crime_type")["rate_per_100k"].mean()
            cats = [c for c in CRIME_TYPES if c in yr_data.index]
            vals = [yr_data.get(c,0) for c in cats]
            mx   = max(vals) if max(vals)>0 else 1
            fig  = C.radar_chart(cats, [v/mx for v in vals], name=label,
                                 title=f"Profile — {label} ({yr[1]})", height=380)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            <div class="cs-insight">
              ℹ️ Radar shows normalised crime intensity across all types.
              Larger area = broader crime problem. Spikes indicate dominant crime categories.
            </div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="cs-section">RATE DISTRIBUTION</div>', unsafe_allow_html=True)
            fig = C.box_plot(cdf, "crime_type", "rate_per_100k",
                             title="Box Plot — Crime Rate Distribution", height=380)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"""
            <div class="cs-insight">
              ℹ️ Box plot shows median, IQR, and outliers per crime type.
              Wide boxes indicate high year-to-year variability.
            </div>""", unsafe_allow_html=True)

        # Treemap
        st.markdown('<div class="cs-section">CRIME COMPOSITION TREEMAP</div>', unsafe_allow_html=True)
        tree = cdf.groupby(["crime_type"])["rate_per_100k"].mean().reset_index()
        tree["region"] = label
        fig_tree = C.treemap(tree, path=["region","crime_type"], values="rate_per_100k",
                             title="Crime Composition by Type", height=340)
        st.plotly_chart(fig_tree, use_container_width=True)

    # TAB 3 – Heatmap
    with t3:
        col_h, col_c = st.columns(2)
        with col_h:
            st.markdown('<div class="cs-section">YEAR × CRIME TYPE HEATMAP</div>', unsafe_allow_html=True)
            pivot_hm = cdf.groupby(["year","crime_type"])["rate_per_100k"].mean().unstack(fill_value=0)
            fig = C.heatmap_chart(z=pivot_hm.values,
                                  x=pivot_hm.columns.tolist(),
                                  y=[str(y) for y in pivot_hm.index.tolist()],
                                  title="Crime Intensity Heatmap", height=380)
            st.plotly_chart(fig, use_container_width=True)

        with col_c:
            st.markdown('<div class="cs-section">CORRELATION MATRIX</div>', unsafe_allow_html=True)
            if is_glob:
                cp = df_all[df_all["year"].between(*yr)].pivot_table(
                    index=["country","year"], columns="crime_type",
                    values="rate_per_100k").dropna()
            else:
                cp = cdf.pivot_table(index="year", columns="crime_type",
                                     values="rate_per_100k").dropna()
            if cp.shape[0] > 2:
                corr = cp.corr()
                fig_corr = go.Figure(go.Heatmap(
                    z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
                    colorscale=[[0,"#0a1f35"],[0.5,CYAN2],[1,CYAN]],
                    zmin=-1, zmax=1,
                    text=corr.round(2).values, texttemplate="%{text}",
                    textfont=dict(size=9, color=TEXT), showscale=True,
                    colorbar=dict(thickness=10,len=0.7,tickfont=dict(color=TDIM,size=8),
                                  bgcolor=BG2,bordercolor=BORD2),
                ))
                fig_corr.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                    font=dict(family="IBM Plex Mono, monospace",color=TEXT,size=10),
                    xaxis=dict(color=TEXT), yaxis=dict(color=TEXT),
                    margin=dict(l=10,r=10,t=30,b=10), height=380,
                    title=dict(text="Crime Type Correlations",
                               font=dict(size=12,color=CYAN),x=0.01))
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Expand year range for correlation data.")

        # Waterfall YOY
        st.markdown('<div class="cs-section">YEAR-OVER-YEAR RATE CHANGE BY CRIME</div>', unsafe_allow_html=True)
        ts2 = cdf.groupby(["year","crime_type"])["rate_per_100k"].mean().reset_index()
        pvt = ts2.pivot(index="year",columns="crime_type",values="rate_per_100k")
        if len(pvt) >= 2:
            cats = pvt.columns.tolist()
            vals = ((pvt.iloc[-1] - pvt.iloc[-2]) / pvt.iloc[-2] * 100).tolist()
            fig_wf = C.waterfall_chart(cats, vals,
                                       title=f"YoY % Change ({yr[1]-1}→{yr[1]})", height=300)
            st.plotly_chart(fig_wf, use_container_width=True)

    # TAB 4 – Distribution
    with t4:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="cs-section">RATE HISTOGRAM</div>', unsafe_allow_html=True)
            fig = C.histogram(cdf, x="rate_per_100k", color="crime_type",
                              title="Crime Rate Frequency Distribution", height=340)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="cs-section">SCATTER — GDP vs CRIME RATE</div>', unsafe_allow_html=True)
            from utils.data_loader import SOCIO
            sc_rows = []
            for c, m in COUNTRY_META.items():
                s = snap[snap["country"]==c]
                if not s.empty and c in SOCIO:
                    sc_rows.append({"country":c,"region":m["region"],
                                    "avg_rate":s.iloc[0]["avg_rate"],
                                    "gdp":SOCIO[c][0],"unemp":SOCIO[c][1]})
            import pandas as pd
            sc_df = pd.DataFrame(sc_rows)
            if not sc_df.empty:
                fig_sc = C.scatter_bubble(sc_df, x="gdp", y="avg_rate",
                    size="avg_rate", color_col="avg_rate",
                    hover="country",
                    title="GDP per Capita vs Avg Crime Rate", height=340)
                st.plotly_chart(fig_sc, use_container_width=True)
                st.markdown("""
                <div class="cs-insight">
                  ℹ️ Generally negative correlation between GDP and crime rate.
                  Exceptions (high-GDP, high-crime) often driven by wealth inequality (Gini).
                </div>""", unsafe_allow_html=True)

        # Bar breakdown latest year
        st.markdown('<div class="cs-section">CRIME BREAKDOWN — LATEST YEAR</div>', unsafe_allow_html=True)
        bar_df = cdf[cdf["year"]==yr[1]]
        if is_glob:
            bar_df = bar_df.groupby("crime_type")["rate_per_100k"].mean().reset_index()
            fig_b  = C.bar_chart(bar_df, x="crime_type", y="rate_per_100k",
                                 title=f"Global Avg Crime Rate by Type ({yr[1]})", height=290)
        else:
            fig_b = C.bar_chart(bar_df, x="crime_type", y="rate_per_100k",
                                title=f"{country} Crime Breakdown ({yr[1]})", height=290)
        st.plotly_chart(fig_b, use_container_width=True)

    # TAB 5 – Rankings
    with t5:
        st.markdown('<div class="cs-section">COUNTRY CRIME RANKINGS — LATEST YEAR</div>', unsafe_allow_html=True)
        rank = snap.sort_values("avg_rate", ascending=False).reset_index(drop=True)
        rank["rank"] = rank.index + 1

        col_rank, col_meta = st.columns([2,1])
        with col_rank:
            fig_rank = go.Figure(go.Bar(
                x=rank["avg_rate"], y=rank["country"], orientation="h",
                marker=dict(color=rank["avg_rate"],
                            colorscale=[[0,GRN],[0.4,AMB],[1,RED]], showscale=False),
                text=rank["avg_rate"].round(1), textposition="outside",
                textfont=dict(color=TEXT, size=9),
            ))
            fig_rank.update_layout(
                paper_bgcolor=BG2, plot_bgcolor=BG3,
                font=dict(family="IBM Plex Mono, monospace", color=TEXT, size=10),
                xaxis=dict(gridcolor=BORD,color=TDIM,title="Avg Rate / 100k"),
                yaxis=dict(gridcolor=BORD,color=TEXT,autorange="reversed"),
                margin=dict(l=10,r=60,t=20,b=30), height=500,
            )
            st.plotly_chart(fig_rank, use_container_width=True)

        with col_meta:
            st.markdown('<div class="cs-section">RISK CATEGORIES</div>', unsafe_allow_html=True)
            for _, row in rank.iterrows():
                lbl, clr = safety_index(row["avg_rate"])
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:0.35rem 0;border-bottom:1px solid {BORD};font-size:0.7rem;">
                  <span style="color:{TEXT};">#{row['rank']} {row['country'][:15]}</span>
                  <span style="color:{clr};font-weight:600;font-size:0.6rem;">{lbl}</span>
                </div>""", unsafe_allow_html=True)
