"""pages/about.py"""
import streamlit as st
from utils.theme import CYAN, BG2, BG3, BORD, BORD2, TEXT, TDIM, GRN, AMB, RED


def render():
    st.markdown("""
    <div class="cs-header">
      <div class="cs-title">ℹ️ About CrimeScope</div>
      <div class="cs-subtitle">Urban Crime Intelligence Platform — v1.0</div>
      <span class="cs-badge">Open Source</span>
      <span class="cs-badge">Streamlit</span>
      <span class="cs-badge">Python ML</span>
      <span class="cs-badge">GitHub Ready</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        <div class="cs-section">PLATFORM OVERVIEW</div>
        <div class="cs-insight">
          <b style="color:{CYAN};">CrimeScope</b> is a full-stack urban crime intelligence dashboard
          built with Python + Streamlit. It synthesises UNODC-modelled crime statistics with
          socioeconomic indicators to provide interactive analysis, ML predictions, and
          anomaly detection across 17 countries and 7 crime categories from 2010–2023.
        </div>

        <br><div class="cs-section">PAGES</div>
        <div class="cs-insight">
          🌍 <b>World Heatmap</b> — Choropleth + bubble world map, city-level hotspot density map<br><br>
          📊 <b>Analytics Dashboard</b> — Trends, radar, heatmap matrix, correlations, treemap, animated scatter<br><br>
          🤖 <b>Crime Predictor</b> — RF / Gradient Boost / Ridge ensemble, 95% CI, scenario analysis, 2040 forecast<br><br>
          🔬 <b>Anomaly Radar</b> — Isolation Forest + Z-Score detection, anomaly timeline<br><br>
          📋 <b>Data Explorer</b> — Filterable table, CSV export, socioeconomic panel, scatter matrix
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="cs-section">TECH STACK</div>
        """, unsafe_allow_html=True)

        stack = [
            ("Streamlit",       "Web framework + deployment", CYAN),
            ("Plotly",          "Interactive charts & maps",  GRN),
            ("scikit-learn",    "Random Forest, Gradient Boost, Ridge, Isolation Forest", AMB),
            ("Pandas / NumPy",  "Data wrangling & synthesis", CYAN),
            ("UNODC Reference", "Homicide rate base values",  GRN),
            ("World Bank API",  "GDP, urbanisation indicators",AMB),
        ]
        for name, desc, color in stack:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:0.8rem;
                        padding:0.6rem 0;border-bottom:1px solid {BORD};font-size:0.72rem;">
              <span style="color:{color};min-width:130px;font-weight:600;">{name}</span>
              <span style="color:{TDIM};">{desc}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <br><div class="cs-section">DATA SOURCES</div>
        <div class="cs-insight">
          • <b>UNODC</b> — dataunodc.un.org (homicide base rates)<br>
          • <b>World Bank</b> — data.worldbank.org (GDP, urban, employment)<br>
          • <b>Global Peace Index</b> — visionofhumanity.org<br>
          • <b>Numbeo</b> — numbeo.com/crime (city crime index)<br>
          • <b>FBI UCR / NIBRS</b> — ucr.fbi.gov (US-specific)
        </div>
        <br><div class="cs-section">DEPLOYMENT</div>
        <div class="cs-insight">
          1. Push this repo to <b>GitHub</b><br>
          2. Visit <b>share.streamlit.io</b> → Connect repo<br>
          3. Set Main file: <code>app.py</code><br>
          4. Click Deploy — live in ~60 seconds!<br><br>
          Or locally: <code>pip install -r requirements.txt && streamlit run app.py</code>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:{TDIM};padding:1rem 0;">
      CrimeScope v1.0 &nbsp;|&nbsp; Built with Streamlit &nbsp;|&nbsp;
      <span style="color:{CYAN};">github.com/your-username/urban-crime-heatmap</span>
    </div>
    """, unsafe_allow_html=True)
