"""
CrimeScope — Urban Crime Intelligence Platform
Run: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="CrimeScope | Urban Crime Intelligence",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import GLOBAL_CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Persistent sidebar toggle button (JS injection) ───────────────────────────
st.markdown("""
<style>
/* Always show the native collapse arrow */
[data-testid="collapsedControl"] {
    display:       flex !important;
    visibility:    visible !important;
    opacity:       1 !important;
    z-index:       9999 !important;
}

/* Floating custom toggle button */
#sidebar-toggle-btn {
    position:      fixed;
    top:           50%;
    left:          0px;
    transform:     translateY(-50%);
    z-index:       9999;
    background:    #0d1424;
    color:         #00d4ff;
    border:        1px solid #00d4ff;
    border-left:   none;
    border-radius: 0 6px 6px 0;
    padding:       12px 6px;
    cursor:        pointer;
    font-size:     16px;
    line-height:   1;
    transition:    background 0.2s, box-shadow 0.2s;
}
#sidebar-toggle-btn:hover {
    background:  rgba(0,212,255,0.15);
    box-shadow:  0 0 12px #00d4ff66;
}
</style>

<button id="sidebar-toggle-btn" title="Toggle Sidebar">&#9776;</button>

<script>
(function() {
    function toggleSidebar() {
        // Try all known Streamlit sidebar button selectors across versions
        var selectors = [
            '[data-testid="collapsedControl"] button',
            '[data-testid="collapsedControl"]',
            'button[kind="header"]',
            '[data-testid="baseButton-header"]',
            'section[data-testid="stSidebar"] button',
        ];
        for (var i = 0; i < selectors.length; i++) {
            var btn = window.parent.document.querySelector(selectors[i]);
            if (btn) {
                btn.click();
                return;
            }
        }
        // Fallback: toggle sidebar width directly
        var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            var current = sidebar.style.width;
            sidebar.style.width = (current === '0px' || current === '') ? '21rem' : '0px';
            sidebar.style.overflow = 'hidden';
        }
    }

    // Wait for DOM then attach
    function init() {
        var btn = document.getElementById('sidebar-toggle-btn');
        if (btn) {
            btn.addEventListener('click', toggleSidebar);
        } else {
            setTimeout(init, 300);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
""", unsafe_allow_html=True)

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
if   "Heatmap"   in page: from pages.heatmap   import render; render(filters)
elif "Analytics" in page: from pages.analytics import render; render(filters)
elif "Predictor" in page: from pages.predictor import render; render(filters)
elif "Anomaly"   in page: from pages.anomaly   import render; render(filters)
elif "Explorer"  in page: from pages.explorer  import render; render(filters)
else:                      from pages.about    import render; render()
