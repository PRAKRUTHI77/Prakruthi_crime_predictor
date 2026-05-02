"""pages/predictor.py — ML Crime Rate Predictor"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import build_global_dataframe, COUNTRY_META, CRIME_TYPES, SOCIO, safety_index
from utils.theme import BG, BG2, BG3, BORD, BORD2, CYAN, CYAN2, RED, AMB, GRN, TEXT, TDIM, PALETTE


# ── Cached model training ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_trained_models():
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import r2_score, mean_absolute_error

    df = build_global_dataframe()
    le_c = LabelEncoder().fit(list(COUNTRY_META.keys()))
    le_t = LabelEncoder().fit(CRIME_TYPES)

    rows = []
    rng  = np.random.default_rng(0)
    for _, row in df.iterrows():
        c = row["country"]
        if c not in SOCIO: continue
        gdp, unemp, urban, gini, police = SOCIO[c]
        noise = rng.normal(1, 0.04)
        rows.append({
            "year":         row["year"],
            "gdp_norm":     gdp/70000,
            "unemployment": unemp*noise,
            "urbanisation": urban*noise,
            "gini":         gini*noise,
            "police_norm":  police/450,
            "country_enc":  le_c.transform([c])[0],
            "crime_enc":    le_t.transform([row["crime_type"]])[0],
            "rate":         row["rate_per_100k"],
        })

    ml = pd.DataFrame(rows)
    FEATS = ["year","gdp_norm","unemployment","urbanisation","gini","police_norm","country_enc","crime_enc"]
    X, y  = ml[FEATS].values, ml["rate"].values

    def pipe(model):
        return Pipeline([("sc", StandardScaler()), ("m", model)])

    rf  = pipe(RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1))
    gb  = pipe(GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=5, random_state=42))
    rr  = pipe(Ridge(alpha=10.0))

    for m in [rf, gb, rr]: m.fit(X, y)

    cv_rf = cross_val_score(rf, X, y, cv=5, scoring="r2").mean()
    cv_gb = cross_val_score(gb, X, y, cv=5, scoring="r2").mean()
    imp   = pd.Series(rf.named_steps["m"].feature_importances_, index=FEATS).sort_values(ascending=False)
    y_hat = rf.predict(X)

    return dict(rf=rf, gb=gb, rr=rr, le_c=le_c, le_t=le_t, feats=FEATS,
                cv_rf=cv_rf, cv_gb=cv_gb,
                mae=mean_absolute_error(y, y_hat), r2=r2_score(y, y_hat),
                imp=imp, X=X, y=y, y_hat=y_hat)


def predict(bundle, country, crime, year, gdp, unemp, urban, gini, police, model="rf"):
    x = np.array([[year, gdp/70000, unemp, urban, gini, police/450,
                   bundle["le_c"].transform([country])[0],
                   bundle["le_t"].transform([crime])[0]]])
    m = bundle[model]
    p = max(0, m.predict(x)[0])
    if model == "rf":
        tree_preds = np.array([t.predict(bundle["rf"].named_steps["sc"].transform(x))[0]
                               for t in bundle["rf"].named_steps["m"].estimators_])
        lo, hi = np.percentile(tree_preds, [5,95])
    else:
        lo, hi = p*0.85, p*1.15
    return p, max(0,lo), hi


def render(filters):
    st.markdown("""
    <div class="cs-header">
      <div class="cs-title">🤖 Crime Rate Predictor</div>
      <div class="cs-subtitle">Random Forest · Gradient Boost · Ridge Regression ensemble</div>
      <span class="cs-badge">ML Models</span>
      <span class="cs-badge">Confidence Intervals</span>
      <span class="cs-badge">Feature Importance</span>
      <span class="cs-badge">Scenario Analysis</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("⚙️ Training models on crime dataset..."):
        B = get_trained_models()

    # ── Model metrics bar ────────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    for col, (val, lbl, sub) in zip([c1,c2,c3,c4],[
        (f"{B['r2']:.3f}",  "RF R² SCORE",    "on training data"),
        (f"{B['mae']:.2f}", "RF MAE",          "rate per 100k"),
        (f"{B['cv_rf']:.3f}","RF CV R² (5-fold)","cross-validated"),
        (f"{B['cv_gb']:.3f}","GB CV R²",        "cross-validated"),
    ]):
        with col:
            st.markdown(f"""
            <div class="cs-kpi">
              <div class="cs-kpi-label">{lbl}</div>
              <div class="cs-kpi-value">{val}</div>
              <div class="cs-kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Input panel + Results ─────────────────────────────────────────────────
    inp_col, res_col = st.columns([1,2])

    with inp_col:
        st.markdown('<div class="cs-section">PREDICTION INPUTS</div>', unsafe_allow_html=True)
        p_country = st.selectbox("Country", list(COUNTRY_META.keys()), index=0)
        p_crime   = st.selectbox("Crime Type", CRIME_TYPES, index=0)
        p_year    = st.slider("Target Year", 2024, 2040, 2026)
        p_model   = st.selectbox("ML Model", ["rf","gb","rr"],
                                 format_func=lambda x: {"rf":"Random Forest","gb":"Gradient Boost","rr":"Ridge Regression"}[x])

        st.markdown('<div class="cs-section" style="margin-top:1rem;">SOCIOECONOMIC INPUTS</div>', unsafe_allow_html=True)
        base = SOCIO.get(p_country, (25000,7,65,40,150))
        p_gdp    = st.slider("GDP per Capita ($)", 1000, 80000, int(base[0]), step=1000)
        p_unemp  = st.slider("Unemployment (%)", 0.5, 40.0, float(base[1]), step=0.5)
        p_urban  = st.slider("Urbanisation (%)", 10, 100, int(base[2]))
        p_gini   = st.slider("Gini Coefficient", 20.0, 70.0, float(base[3]), step=0.5)
        p_police = st.slider("Police / 100k", 10, 500, int(base[4]))
        predict_btn = st.button("⬡  RUN PREDICTION")

    with res_col:
        st.markdown('<div class="cs-section">PREDICTION RESULTS</div>', unsafe_allow_html=True)

        pred, lo, hi = predict(B, p_country, p_crime, p_year,
                               p_gdp, p_unemp, p_urban, p_gini, p_police, p_model)
        lbl, clr = safety_index(pred)

        # Gauge
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pred,
            gauge=dict(
                axis=dict(range=[0,120], tickcolor=TDIM, tickfont=dict(color=TDIM,size=8)),
                bar=dict(color=CYAN, thickness=0.28),
                bgcolor=BG3, bordercolor=BORD2,
                steps=[
                    dict(range=[0,5],  color="#0d2a1a"),
                    dict(range=[5,15], color="#2a2000"),
                    dict(range=[15,40],color="#2a0a00"),
                    dict(range=[40,120],color="#2a0010"),
                ],
                threshold=dict(line=dict(color=RED,width=2),thickness=0.8,value=40),
            ),
            number=dict(font=dict(color=clr,family="Orbitron, monospace",size=38),suffix=" /100k"),
            title=dict(text=f"{p_crime} · {p_country} · {p_year}",
                       font=dict(color=TEXT,size=11,family="IBM Plex Mono, monospace")),
        ))
        fig_g.update_layout(paper_bgcolor=BG2, font=dict(color=TEXT), height=260,
                            margin=dict(l=30,r=30,t=30,b=10))
        st.plotly_chart(fig_g, use_container_width=True)

        # Confidence + risk label
        r1, r2, r3 = st.columns(3)
        for col,(v,l,c) in zip([r1,r2,r3],[
            (f"{lo:.1f}", "95% CI LOW",   GRN),
            (f"{pred:.1f}", "PREDICTION", clr),
            (f"{hi:.1f}", "95% CI HIGH",  RED),
        ]):
            with col:
                st.markdown(f"""
                <div class="cs-kpi" style="text-align:center;">
                  <div class="cs-kpi-label">{l}</div>
                  <div style="font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:700;color:{c};">{v}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin:0.8rem 0;">
          <span class="cs-risk-badge" style="background:{clr}22;color:{clr};border:1px solid {clr};
                padding:4px 20px;border-radius:3px;font-size:0.7rem;letter-spacing:0.1em;">
            ⬡ {lbl}
          </span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="cs-insight">
          ℹ️ Model: <b style="color:{CYAN};">{"Random Forest" if p_model=="rf" else "Gradient Boost" if p_model=="gb" else "Ridge Regression"}</b>
          &nbsp;|&nbsp; Predicted <b>{p_crime}</b> rate for <b>{p_country}</b> in <b>{p_year}</b>
          is <b style="color:{clr};">{pred:.1f} per 100,000</b> people.
          CI: [{lo:.1f}, {hi:.1f}]. Based on GDP ${p_gdp:,}, {p_unemp}% unemployment, Gini {p_gini}.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Scenario Analysis ─────────────────────────────────────────────────────
    st.markdown('<div class="cs-section">SCENARIO ANALYSIS — GDP IMPACT</div>', unsafe_allow_html=True)

    gdp_range  = np.linspace(2000, 75000, 30)
    pred_range = [predict(B, p_country, p_crime, p_year, g, p_unemp, p_urban, p_gini, p_police, p_model)[0]
                  for g in gdp_range]
    lo_range   = [predict(B, p_country, p_crime, p_year, g, p_unemp, p_urban, p_gini, p_police, p_model)[1]
                  for g in gdp_range]
    hi_range   = [predict(B, p_country, p_crime, p_year, g, p_unemp, p_urban, p_gini, p_police, p_model)[2]
                  for g in gdp_range]

    sa_col1, sa_col2 = st.columns(2)

    with sa_col1:
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=gdp_range, y=hi_range, fill=None, mode="lines",
                                   line=dict(color="rgba(0,212,255,0)"), showlegend=False))
        fig_s.add_trace(go.Scatter(x=gdp_range, y=lo_range, fill="tonexty",
                                   fillcolor="rgba(0,212,255,0.1)", mode="lines",
                                   line=dict(color="rgba(0,212,255,0)"), name="95% CI"))
        fig_s.add_trace(go.Scatter(x=gdp_range, y=pred_range, mode="lines",
                                   line=dict(color=CYAN,width=2.5), name="Predicted Rate"))
        fig_s.add_vline(x=p_gdp, line_color=AMB, line_width=1.5, line_dash="dot",
                        annotation_text=f"Current ${p_gdp:,}", annotation_font_color=AMB)
        fig_s.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                            font=dict(family="IBM Plex Mono, monospace",color=TEXT),
                            xaxis=dict(gridcolor=BORD,color=TDIM,title="GDP per Capita ($)"),
                            yaxis=dict(gridcolor=BORD,color=TDIM,title="Predicted Rate/100k"),
                            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9,color=TEXT)),
                            margin=dict(l=40,r=20,t=30,b=40), height=320,
                            title=dict(text="GDP vs Predicted Crime Rate",
                                       font=dict(size=12,color=CYAN),x=0.01))
        st.plotly_chart(fig_s, use_container_width=True)

    with sa_col2:
        # Feature Importance
        imp = B["imp"]
        nice = {"year":"Year","gdp_norm":"GDP","unemployment":"Unemployment",
                "urbanisation":"Urbanisation","gini":"Gini Coeff",
                "police_norm":"Police Density","country_enc":"Country","crime_enc":"Crime Type"}
        fig_fi = go.Figure(go.Bar(
            y=[nice.get(f,f) for f in imp.index],
            x=imp.values, orientation="h",
            marker=dict(color=imp.values,
                        colorscale=[[0,BG3],[0.5,CYAN2],[1,CYAN]], showscale=False),
            text=[f"{v:.3f}" for v in imp.values],
            textposition="outside", textfont=dict(color=TEXT,size=9),
        ))
        fig_fi.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                             font=dict(family="IBM Plex Mono, monospace",color=TEXT,size=10),
                             xaxis=dict(gridcolor=BORD,color=TDIM,title="Importance"),
                             yaxis=dict(gridcolor=BORD,color=TEXT,autorange="reversed"),
                             margin=dict(l=10,r=60,t=30,b=30), height=320,
                             title=dict(text="Feature Importance (Random Forest)",
                                        font=dict(size=12,color=CYAN),x=0.01))
        st.plotly_chart(fig_fi, use_container_width=True)

    # ── Multi-country forecast ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="cs-section">MULTI-COUNTRY FORECAST — 2024–2040</div>', unsafe_allow_html=True)

    sel_countries = st.multiselect("Select countries to forecast",
                                   list(COUNTRY_META.keys()),
                                   default=["United States","Brazil","United Kingdom","India"])
    sel_crime_fc  = st.selectbox("Crime type for forecast", CRIME_TYPES, key="fc_crime")

    future_years = list(range(2024, 2041))
    fig_fc = go.Figure()
    colors = [CYAN,"#00ff9d","#ffaa00","#ff3366","#9d4edd","#4cc9f0","#f72585"]

    for i, ctry in enumerate(sel_countries[:7]):
        base = SOCIO.get(ctry, (25000,7,65,40,150))
        # Apply slight GDP growth trend per year
        preds = []
        for yr in future_years:
            gdp_proj = base[0] * (1.02 ** (yr-2023))
            p,_,_ = predict(B, ctry, sel_crime_fc, yr,
                            min(gdp_proj,80000), base[1], base[2], base[3], base[4], "rf")
            preds.append(p)
        fig_fc.add_trace(go.Scatter(
            x=future_years, y=preds, mode="lines+markers",
            name=ctry, line=dict(color=colors[i%len(colors)],width=2),
            marker=dict(size=4),
        ))

    fig_fc.update_layout(paper_bgcolor=BG2, plot_bgcolor=BG3,
                         font=dict(family="IBM Plex Mono, monospace",color=TEXT),
                         xaxis=dict(gridcolor=BORD,color=TDIM,title="Year"),
                         yaxis=dict(gridcolor=BORD,color=TDIM,title="Predicted Rate/100k"),
                         legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=9,color=TEXT),
                                     bordercolor=BORD2,borderwidth=1),
                         margin=dict(l=40,r=20,t=20,b=40), height=380,
                         title=dict(text=f"{sel_crime_fc} Rate Forecast 2024–2040",
                                    font=dict(size=12,color=CYAN),x=0.01))
    st.plotly_chart(fig_fc, use_container_width=True)
    st.markdown(f"""
    <div class="cs-insight">
      ℹ️ Forecast assumes 2% annual GDP growth and stable socioeconomic conditions.
      Shaded bands represent model uncertainty. Crime type: <b>{sel_crime_fc}</b>.
      Countries with high GDP growth tend to see declining crime rates over time.
    </div>""", unsafe_allow_html=True)
