"""pages/heatmap.py"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.data_loader import (
    build_global_dataframe, get_latest_snapshot,
    get_city_hotspots, safety_index, COUNTRY_META, SOCIO
)
from utils.theme import BG, BG2, BG3, BORD, BORD2, CYAN, CYAN2, RED, AMB, GRN, TEXT, TDIM


def render(filters: dict):
    country  = filters["country"]
    crimes   = filters["crime_type"]
    yr       = filters["year_range"]
    is_glob  = filters["is_global"]

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cs-header">
      <div class="cs-title">🌍 World Crime Heatmap</div>
      <div class="cs-subtitle">Interactive global crime intensity map • Click region in sidebar to drill down</div>
      <span class="cs-badge">UNODC Data</span>
      <span class="cs-badge">World Bank API</span>
      <span class="cs-badge">Live Synthesis</span>
      <span class="cs-badge">17 Countries</span>
    </div>
    """, unsafe_allow_html=True)

    snap = get_latest_snapshot(crimes, year=yr[1])

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    avg_g   = snap["avg_rate"].mean()
    max_row = snap.loc[snap["avg_rate"].idxmax()]
    min_row = snap.loc[snap["avg_rate"].idxmin()]

    kpis = [
        (f"{len(COUNTRY_META)}", "COUNTRIES TRACKED", "• live"),
        (f"{avg_g:.1f}", "AVG RATE (PER 100K)", f"Year {yr[1]}"),
        (f"{len(crimes)}", "CRIME TYPES ACTIVE", "• filtered"),
        (max_row["country"][:12], "HIGHEST RISK", f"{max_row['avg_rate']:.0f}/100k"),
        (min_row["country"][:12], "LOWEST RISK",  f"{min_row['avg_rate']:.1f}/100k"),
    ]
    for col, (val, label, sub) in zip([c1,c2,c3,c4,c5], kpis):
        with col:
            st.markdown(f"""
            <div class="cs-kpi">
              <div class="cs-kpi-label">{label}</div>
              <div class="cs-kpi-value">{val}</div>
              <div class="cs-kpi-sub cs-kpi-live">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Map + Sidebar panel ───────────────────────────────────────────────────
    map_col, panel_col = st.columns([3, 1])

    with map_col:
        st.markdown('<div class="cs-section">GLOBAL CRIME INTENSITY MAP</div>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:0.68rem;color:#5a7a9a;">Bubble size ∝ avg crime rate &nbsp;|&nbsp; Color = intensity &nbsp;|&nbsp; Hover for stats</span>', unsafe_allow_html=True)

        fig = go.Figure()
        # Choropleth
        fig.add_trace(go.Choropleth(
            locations=snap["iso"], z=np.log1p(snap["avg_rate"]),
            text=snap["country"],
            customdata=snap[["country","avg_rate"]],
            colorscale=[
                [0.0, "#050c18"], [0.2, "#0a1f35"],
                [0.45, "#003355"], [0.7, CYAN2], [1.0, CYAN]
            ],
            marker_line_color=BORD2, marker_line_width=0.6,
            colorbar=dict(
                title=dict(text="log(Rate)", font=dict(color=TDIM, size=9)),
                tickfont=dict(color=TDIM, size=8), bgcolor=BG2,
                bordercolor=BORD2, thickness=11, len=0.55, x=1.01,
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>Rate: %{customdata[1]:.1f} / 100k<extra></extra>",
        ))
        # Bubble overlay
        fig.add_trace(go.Scattergeo(
            locations=snap["iso"], mode="markers",
            marker=dict(
                size=np.sqrt(snap["avg_rate"]) * 2.2,
                color=snap["avg_rate"],
                colorscale=[[0,f"rgba(0,255,157,0.5)"],[0.5,f"rgba(255,170,0,0.6)"],[1,f"rgba(255,51,102,0.75)"]],
                line=dict(color="rgba(255,255,255,0.2)", width=0.5),
                showscale=False,
            ),
            customdata=snap[["country","avg_rate"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Rate: %{customdata[1]:.1f}/100k<extra></extra>",
        ))
        # Highlight selected
        if not is_glob and country in COUNTRY_META:
            m = COUNTRY_META[country]
            fig.add_trace(go.Scattergeo(
                lon=[m["lon"]], lat=[m["lat"]], mode="markers+text",
                marker=dict(size=22, color=CYAN, symbol="star",
                            line=dict(color="white", width=1.5)),
                text=[country], textfont=dict(color="white", size=10,
                family="Share Tech Mono, monospace"),
                textposition="top center", hoverinfo="skip",
            ))

        fig.update_geos(
            bgcolor=BG, landcolor="#0a1628", oceancolor="#050c18",
            lakecolor="#050c18", showland=True, showocean=True,
            showlakes=True, showframe=False, showcountries=True,
            countrycolor=BORD2, projection_type="natural earth",
        )
        fig.update_layout(
            paper_bgcolor=BG2, geo=dict(bgcolor=BG),
            margin=dict(l=0,r=0,t=0,b=0), height=490,
            font=dict(family="IBM Plex Mono, monospace", color=TEXT),
        )
        st.plotly_chart(fig, use_container_width=True)

    with panel_col:
        st.markdown('<div class="cs-section">COUNTRY RISK PROFILE</div>', unsafe_allow_html=True)
        if is_glob:
            top5 = snap.nlargest(5, "avg_rate")
            for _, row in top5.iterrows():
                lbl, col = safety_index(row["avg_rate"])
                st.markdown(f"""
                <div class="cs-kpi" style="margin-bottom:0.5rem;">
                  <div class="cs-kpi-label">{row['country']}</div>
                  <div class="cs-kpi-value" style="font-size:1.1rem;color:{col};">{row['avg_rate']:.1f}</div>
                  <div class="cs-kpi-sub" style="color:{col};">{lbl}</div>
                </div>""", unsafe_allow_html=True)
        else:
            sel = snap[snap["country"] == country]
            if not sel.empty:
                rate = sel.iloc[0]["avg_rate"]
                lbl, col = safety_index(rate)
                pct = (snap["avg_rate"] < rate).mean() * 100
                gdp, unemp, urban, gini, police = SOCIO.get(country,(25000,7,65,40,150))
                items = [
                    ("SAFETY STATUS",   lbl,              col),
                    ("CRIME RATE",      f"{rate:.1f}",    CYAN),
                    ("GLOBAL PCTILE",   f"{pct:.0f}th",   AMB if pct>50 else GRN),
                    ("GDP / CAPITA",    f"${gdp:,}",      CYAN),
                    ("UNEMPLOYMENT",    f"{unemp}%",      AMB),
                    ("URBANISATION",    f"{urban}%",      CYAN),
                    ("GINI COEFF",      f"{gini}",        AMB),
                    ("POLICE/100K",     f"{police}",      GRN),
                ]
                for label, val, c in items:
                    st.markdown(f"""
                    <div class="cs-kpi" style="margin-bottom:0.4rem;padding:0.7rem 1rem;">
                      <div class="cs-kpi-label">{label}</div>
                      <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:{c};">{val}</div>
                    </div>""", unsafe_allow_html=True)

    # ── City hotspot map ──────────────────────────────────────────────────────
    if not is_glob:
        st.markdown("---")
        st.markdown(f'<div class="cs-section">CITY-LEVEL HOTSPOTS — {country.upper()}</div>', unsafe_allow_html=True)

        cities = get_city_hotspots(country)
        meta   = COUNTRY_META[country]
        c_left, c_right = st.columns([2,1])

        with c_left:
            fig2 = go.Figure()
            fig2.add_trace(go.Densitymapbox(
                lat=cities["lat"], lon=cities["lon"],
                z=cities["crime_index"], radius=45,
                colorscale=[[0,"rgba(0,212,255,0)"],[0.4,"rgba(255,170,0,0.4)"],[1,"rgba(255,51,102,0.75)"]],
                showscale=False, hoverinfo="skip",
            ))
            fig2.add_trace(go.Scattermapbox(
                lat=cities["lat"], lon=cities["lon"],
                mode="markers+text",
                marker=dict(
                    size=cities["crime_index"]/4.5,
                    color=cities["crime_index"],
                    colorscale=[[0,GRN],[0.5,AMB],[1,RED]],
                    opacity=0.9, showscale=True,
                    colorbar=dict(thickness=9, len=0.5,
                                  tickfont=dict(color=TDIM,size=7),
                                  bgcolor=BG2, bordercolor=BORD2,
                                  title=dict(text="Index",font=dict(color=TDIM,size=8))),
                ),
                text=cities["city"],
                textfont=dict(size=9, color="white", family="Share Tech Mono, monospace"),
                textposition="top center",
                customdata=cities[["city","crime_index"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Crime Index: %{customdata[1]}<extra></extra>",
            ))
            fig2.update_layout(
                mapbox=dict(style="carto-darkmatter",
                            center=dict(lat=meta["lat"], lon=meta["lon"]), zoom=4),
                paper_bgcolor=BG2, margin=dict(l=0,r=0,t=0,b=0), height=380,
                font=dict(family="IBM Plex Mono, monospace", color=TEXT),
            )
            st.plotly_chart(fig2, use_container_width=True)

        with c_right:
            cities_s = cities.sort_values("crime_index", ascending=True)
            fig3 = go.Figure(go.Bar(
                x=cities_s["crime_index"], y=cities_s["city"], orientation="h",
                marker=dict(color=cities_s["crime_index"],
                            colorscale=[[0,GRN],[0.5,AMB],[1,RED]], showscale=False),
                text=cities_s["crime_index"], textposition="outside",
                textfont=dict(color=TEXT, size=9),
            ))
            fig3.update_layout(
                paper_bgcolor=BG2, plot_bgcolor=BG3,
                font=dict(family="IBM Plex Mono, monospace", color=TEXT, size=10),
                xaxis=dict(gridcolor=BORD, color=TDIM, title="Crime Index"),
                yaxis=dict(gridcolor=BORD, color=TEXT),
                margin=dict(l=10,r=50,t=10,b=20), height=380,
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── Regional bar ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="cs-section">REGIONAL CRIME COMPARISON</div>', unsafe_allow_html=True)
    reg_df = snap.groupby("region")["avg_rate"].mean().reset_index().sort_values("avg_rate", ascending=False)
    fig4 = go.Figure(go.Bar(
        x=reg_df["region"], y=reg_df["avg_rate"],
        marker=dict(color=reg_df["avg_rate"],
                    colorscale=[[0,"#0a1f35"],[0.5,CYAN2],[1,RED]], showscale=False),
        text=reg_df["avg_rate"].round(1), textposition="outside",
        textfont=dict(color=TEXT, size=10),
    ))
    fig4.update_layout(
        paper_bgcolor=BG2, plot_bgcolor=BG3,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT),
        xaxis=dict(gridcolor=BORD, color=TEXT),
        yaxis=dict(gridcolor=BORD, color=TDIM, title="Avg Rate / 100k"),
        margin=dict(l=10,r=10,t=10,b=10), height=250,
    )
    st.plotly_chart(fig4, use_container_width=True)
