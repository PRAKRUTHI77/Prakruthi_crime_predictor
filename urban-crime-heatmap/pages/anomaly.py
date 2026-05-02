"""pages/anomaly.py — Anomaly detection on crime data using Isolation Forest + Z-score"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import build_global_dataframe, COUNTRY_META, CRIME_TYPES, get_latest_snapshot
from utils.theme import BG, BG2, BG3, BORD, BORD2, CYAN, CYAN2, RED, AMB, GRN, TEXT, TDIM, PALETTE


@st.cache_data(show_spinner=False)
def detect_anomalies(crime_types, year_range):
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    df  = build_global_dataframe()
    sub = df[(df["crime_type"].isin(crime_types)) & (df["year"].between(*year_range))]
    agg = sub.groupby(["country","year"])["rate_per_100k"].mean().reset_index()

    # Z-score per country
    agg["z_score"] = agg.groupby("country")["rate_per_100k"].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-9))

    # Isolation Forest
    X = agg[["rate_per_100k","year"]].copy()
    X["country_id"] = pd.factorize(agg["country"])[0]
    sc  = StandardScaler()
    Xs  = sc.fit_transform(X)
    iso = IsolationForest(contamination=0.08, random_state=42)
    agg["anomaly"] = iso.fit_predict(Xs)   # -1 = anomaly
    agg["anomaly_score"] = -iso.score_samples(Xs)

    return agg


def render(filters):
    crimes = filters["crime_type"]
    yr     = filters["year_range"]
    country= filters["country"]
    is_glob= filters["is_global"]

    st.markdown("""
    <div class="cs-header">
      <div class="cs-title">🔬 Anomaly Radar</div>
      <div class="cs-subtitle">Isolation Forest + Z-Score anomaly detection on crime time series</div>
      <span class="cs-badge">Isolation Forest</span>
      <span class="cs-badge">Z-Score</span>
      <span class="cs-badge">Statistical Outliers</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Running anomaly detection..."):
        agg = detect_anomalies(tuple(crimes), yr)

    anomalies   = agg[agg["anomaly"] == -1]
    normal      = agg[agg["anomaly"] == 1]
    n_anomalies = len(anomalies)
    max_z       = agg["z_score"].abs().max()
    worst       = agg.loc[agg["anomaly_score"].idxmax()]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    for col,(v,l,s,c) in zip([c1,c2,c3,c4],[
        (str(n_anomalies),          "ANOMALIES DETECTED", "8% contamination", RED),
        (f"{max_z:.2f}",            "MAX Z-SCORE",        "std devs from mean", AMB),
        (worst["country"][:12],     "WORST OUTLIER",      f"Year {int(worst['year'])}", RED),
        (f"{worst['rate_per_100k']:.1f}", "PEAK ANOMALY RATE", "per 100k", RED),
    ]):
        with col:
            st.markdown(f"""
            <div class="cs-kpi">
              <div class="cs-kpi-label">{l}</div>
              <div class="cs-kpi-value" style="color:{c};">{v}</div>
              <div class="cs-kpi-sub">{s}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Scatter: anomalies vs normal ─────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="cs-section">ANOMALY SCATTER — YEAR vs RATE</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=normal["year"], y=normal["rate_per_100k"],
            mode="markers", name="Normal",
            marker=dict(size=5, color=CYAN, opacity=0.5),
            customdata=normal[["country","year","rate_per_100k"]],
            hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>Rate: %{customdata[2]:.1f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=anomalies["year"], y=anomalies["rate_per_100k"],
            mode="markers", name="Anomaly",
            marker=dict(size=9, color=RED, symbol="x", line=dict(color="white",width=0.5)),
            customdata=anomalies[["country","year","rate_per_100k"]],
            hovertemplate="⚠️ <b>%{customdata[0]}</b> (%{customdata[1]})<br>Rate: %{customdata[2]:.1f}<extra></extra>",
        ))
        fig.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                          font=dict(family="IBM Plex Mono, monospace",color=TEXT),
                          xaxis=dict(gridcolor=BORD,color=TDIM,title="Year"),
                          yaxis=dict(gridcolor=BORD,color=TDIM,title="Rate/100k"),
                          legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=10,color=TEXT)),
                          margin=dict(l=40,r=10,t=30,b=40), height=360,
                          title=dict(text="Anomaly Detection — All Countries",
                                     font=dict(size=12,color=CYAN),x=0.01))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="cs-section">Z-SCORE HEATMAP BY COUNTRY & YEAR</div>', unsafe_allow_html=True)
        pivot_z = agg.pivot_table(index="country", columns="year", values="z_score")
        fig_z = go.Figure(go.Heatmap(
            z=pivot_z.values,
            x=[str(y) for y in pivot_z.columns],
            y=pivot_z.index.tolist(),
            colorscale=[[0,GRN],[0.5,BG3],[1,RED]],
            zmid=0, showscale=True,
            colorbar=dict(thickness=10,len=0.7,tickfont=dict(color=TDIM,size=8),
                          bgcolor=BG2,bordercolor=BORD2,
                          title=dict(text="Z-Score",font=dict(color=TDIM,size=8))),
            hovertemplate="<b>%{y}</b> (%{x})<br>Z-Score: %{z:.2f}<extra></extra>",
        ))
        fig_z.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                            font=dict(family="IBM Plex Mono, monospace",color=TEXT,size=9),
                            xaxis=dict(color=TEXT,title="Year"),
                            yaxis=dict(color=TEXT),
                            margin=dict(l=10,r=10,t=30,b=30), height=360,
                            title=dict(text="Z-Score by Country & Year",
                                       font=dict(size=12,color=CYAN),x=0.01))
        st.plotly_chart(fig_z, use_container_width=True)

    # ── Top anomalies table ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="cs-section">TOP ANOMALY EVENTS — RANKED BY SCORE</div>', unsafe_allow_html=True)

    top_anom = anomalies.nlargest(15, "anomaly_score")[
        ["country","year","rate_per_100k","anomaly_score","z_score"]
    ].reset_index(drop=True)
    top_anom.columns = ["Country","Year","Rate/100k","Anomaly Score","Z-Score"]
    top_anom = top_anom.round(2)

    # colour rows
    rows_html = ""
    for _, row in top_anom.iterrows():
        intensity = min(1.0, row["Anomaly Score"])
        color = f"rgba(255,51,102,{intensity*0.3})"
        rows_html += f"""<tr style="background:{color};">
          <td>{row['Country']}</td>
          <td>{int(row['Year'])}</td>
          <td style="color:{RED};font-weight:600;">{row['Rate/100k']:.1f}</td>
          <td style="color:{AMB};">{row['Anomaly Score']:.3f}</td>
          <td style="color:{AMB if abs(row['Z-Score'])>2 else CYAN};">{row['Z-Score']:.2f}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;font-size:0.72rem;font-family:'IBM Plex Mono',monospace;">
      <thead>
        <tr style="border-bottom:1px solid {CYAN};color:{CYAN};">
          <th style="text-align:left;padding:6px 10px;">Country</th>
          <th style="text-align:left;padding:6px 10px;">Year</th>
          <th style="text-align:left;padding:6px 10px;">Rate/100k</th>
          <th style="text-align:left;padding:6px 10px;">Anomaly Score</th>
          <th style="text-align:left;padding:6px 10px;">Z-Score</th>
        </tr>
      </thead>
      <tbody style="color:{TEXT};">{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    # ── Country-level anomaly timeline ────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="cs-section">COUNTRY ANOMALY TIMELINE</div>', unsafe_allow_html=True)
    sel_c = country if not is_glob else "Brazil"
    c_data = agg[agg["country"] == sel_c]

    if not c_data.empty:
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=c_data["year"], y=c_data["rate_per_100k"],
            mode="lines+markers", name="Rate",
            line=dict(color=CYAN, width=2), marker=dict(size=5),
        ))
        c_anom = c_data[c_data["anomaly"]==-1]
        if not c_anom.empty:
            fig_t.add_trace(go.Scatter(
                x=c_anom["year"], y=c_anom["rate_per_100k"],
                mode="markers", name="Anomaly",
                marker=dict(size=12, color=RED, symbol="x",
                            line=dict(color="white",width=1)),
            ))
        fig_t.update_layout(
            paper_bgcolor=BG2, plot_bgcolor=BG3,
            font=dict(family="IBM Plex Mono, monospace",color=TEXT),
            xaxis=dict(gridcolor=BORD,color=TDIM,title="Year"),
            yaxis=dict(gridcolor=BORD,color=TDIM,title="Avg Rate/100k"),
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=10,color=TEXT)),
            margin=dict(l=40,r=20,t=30,b=40), height=300,
            title=dict(text=f"Anomaly Timeline — {sel_c}",
                       font=dict(size=12,color=CYAN),x=0.01))
        st.plotly_chart(fig_t, use_container_width=True)

    st.markdown(f"""
    <div class="cs-insight">
      ⚠️ Anomalies detected using Isolation Forest (contamination=8%) + Z-Score thresholding.
      Red ✕ markers indicate statistically unusual spikes or drops in crime rates.
      High Z-scores (>2.0) suggest events outside normal variance for that country.
    </div>""", unsafe_allow_html=True)
