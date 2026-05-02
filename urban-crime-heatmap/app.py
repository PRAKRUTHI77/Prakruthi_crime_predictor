"""
CrimeScope — Urban Crime Intelligence Platform
Run: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="CrimeScope | Urban Crime Intelligence",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.theme import GLOBAL_CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1.4rem 0; border-bottom:1px solid #1e3050; margin-bottom:1.2rem;">
      <div class="cs-logo">⬡ CrimeScope</div>
      <div class="cs-logo-sub">Urban Crime Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cs-sidebar-label">Navigation</div>', unsafe_allow_html=True)
    page = st.selectbox("", [
        "🌍  World Heatmap",
        "📊  Analytics Dashboard",
        "🤖  Crime Predictor",
        "🔬  Anomaly Radar",
        "📋  Data Explorer",
        "ℹ️   About",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="cs-sidebar-label">Region Filter</div>', unsafe_allow_html=True)
    region = st.selectbox("", [
        "🌐  Global Overview",
        "🇺🇸  United States", "🇬🇧  United Kingdom", "🇩🇪  Germany",
        "🇫🇷  France",        "🇮🇳  India",          "🇧🇷  Brazil",
        "🇲🇽  Mexico",        "🇿🇦  South Africa",   "🇳🇬  Nigeria",
        "🇦🇺  Australia",     "🇨🇦  Canada",         "🇷🇺  Russia",
        "🇨🇳  China",         "🇯🇵  Japan",          "🇰🇷  South Korea",
        "🇸🇦  Saudi Arabia",  "🇦🇷  Argentina",
    ], label_visibility="collapsed")

    st.markdown('<div class="cs-sidebar-label">Crime Types</div>', unsafe_allow_html=True)
    crime_type = st.multiselect("", [
        "Homicide", "Robbery", "Assault",
        "Theft", "Burglary", "Drug Offenses", "Sexual Violence",
    ], default=["Homicide", "Robbery", "Assault"],
       label_visibility="collapsed")

    st.markdown('<div class="cs-sidebar-label">Year Range</div>', unsafe_allow_html=True)
    year_range = st.slider("", 2010, 2023, (2015, 2023), label_visibility="collapsed")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.58rem; color:#5a7a9a; line-height:1.9;">
      <span style="color:#00d4ff;">▸ DATA SOURCES</span><br>
      • UNODC Crime Statistics<br>
      • World Bank Open Data<br>
      • Global Peace Index<br>
      • Numbeo Crime Index<br>
      • FBI UCR / NIBRS
    </div>
    """, unsafe_allow_html=True)

# Strip emoji prefix to get plain country name
country_name = region.split("  ", 1)[-1].strip()
is_global    = "Global" in country_name

filters = dict(region=region, country=country_name,
               is_global=is_global, crime_type=crime_type or ["Homicide"],
               year_range=year_range)

# ── Route ──────────────────────────────────────────────────────────────────────
if   "Heatmap"    in page: from pages.heatmap    import render; render(filters)
elif "Analytics"  in page: from pages.analytics  import render; render(filters)
elif "Predictor"  in page: from pages.predictor  import render; render(filters)
elif "Anomaly"    in page: from pages.anomaly     import render; render(filters)
elif "Explorer"   in page: from pages.explorer    import render; render(filters)
else:                       from pages.about      import render; render()
