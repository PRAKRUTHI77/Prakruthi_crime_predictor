"""utils/theme.py  —  CrimeScope terminal-cyan aesthetic."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;600;700;900&family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

/* ── VARIABLES ────────────────────────────────────────────────── */
:root {
  --bg:        #080d1a;
  --bg2:       #0d1424;
  --bg3:       #111929;
  --border:    #1a2840;
  --border2:   #1e3050;
  --cyan:      #00d4ff;
  --cyan-dim:  #0099bb;
  --cyan-glow: rgba(0,212,255,0.15);
  --red:       #ff3366;
  --amber:     #ffaa00;
  --green:     #00ff9d;
  --purple:    #9d4edd;
  --text:      #c8d8e8;
  --text-dim:  #5a7a9a;
  --text-bright: #e8f4ff;
}

/* ── GLOBAL ───────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'IBM Plex Mono', monospace !important;
}

/* ── SIDEBAR ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background-color: var(--bg2) !important;
  border-right: 1px solid var(--border2) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  font-family: 'Orbitron', monospace !important;
  color: var(--cyan) !important;
}

/* ── SIDEBAR COLLAPSE BUTTON — ALWAYS VISIBLE ON DESKTOP ──────── */
[data-testid="collapsedControl"] {
  display:          flex !important;
  visibility:       visible !important;
  opacity:          1 !important;
  position:         fixed !important;
  top:              50% !important;
  left:             0px !important;
  transform:        translateY(-50%) !important;
  z-index:          999999 !important;
  background:       #0d1424 !important;
  border:           1px solid #00d4ff !important;
  border-left:      none !important;
  border-radius:    0 8px 8px 0 !important;
  width:            28px !important;
  height:           52px !important;
  min-width:        28px !important;
  min-height:       52px !important;
  cursor:           pointer !important;
  box-shadow:       2px 0 12px rgba(0,212,255,0.3) !important;
}
[data-testid="collapsedControl"]:hover {
  background:  rgba(0,212,255,0.2) !important;
  box-shadow:  2px 0 20px rgba(0,212,255,0.6) !important;
}
[data-testid="collapsedControl"] svg {
  color: #00d4ff !important;
  fill:  #00d4ff !important;
}
/* Hide the toggle button only when sidebar is open (avoid duplication) */
[data-testid="stSidebar"][aria-expanded="true"] ~ * [data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
  display: none !important;
}

/* ── INPUTS ───────────────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
  background-color: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  border-radius: 4px !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 1px var(--cyan) !important;
}

/* slider */
.stSlider > div > div > div { background: var(--cyan) !important; }
.stSlider > div > div > div > div { background: var(--cyan) !important; }

/* ── BUTTONS ──────────────────────────────────────────────────── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--cyan) !important;
  color: var(--cyan) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  border-radius: 3px !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  background: var(--cyan-glow) !important;
  box-shadow: 0 0 12px var(--cyan) !important;
}

/* ── METRICS ──────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 6px !important;
  padding: 1.1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-dim) !important;
  font-size: 0.65rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricValue"] {
  color: var(--cyan) !important;
  font-family: 'Orbitron', monospace !important;
  font-weight: 700 !important;
  font-size: 1.6rem !important;
}
[data-testid="stMetricDelta"] { font-family: 'IBM Plex Mono', monospace !important; }

/* ── HEADINGS ─────────────────────────────────────────────────── */
h1, h2, h3 { font-family: 'Orbitron', monospace !important; color: var(--text-bright) !important; }

/* ── TABS ─────────────────────────────────────────────────────── */
[data-testid="stTabs"] button {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--text-dim) !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom: 2px solid var(--cyan) !important;
  background: transparent !important;
}

/* ── DIVIDER ──────────────────────────────────────────────────── */
hr { border-color: var(--border2) !important; }

/* ── DATAFRAME ─────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid var(--border2) !important; }

/* ── ALERTS ───────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  background: var(--bg3) !important;
  border-left: 3px solid var(--cyan) !important;
  color: var(--text) !important;
}

/* ── CUSTOM COMPONENTS ────────────────────────────────────────── */
.cs-header {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-top: 2px solid var(--cyan);
  border-radius: 6px;
  padding: 1.5rem 2rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.cs-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at top left, rgba(0,212,255,0.04), transparent 60%);
  pointer-events: none;
}
.cs-title {
  font-family: 'Orbitron', monospace;
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--cyan);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin: 0;
  line-height: 1.2;
}
.cs-subtitle {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  color: var(--text-dim);
  margin-top: 0.4rem;
  letter-spacing: 0.03em;
}
.cs-badge {
  display: inline-block;
  border: 1px solid var(--cyan);
  color: var(--cyan);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.6rem;
  padding: 2px 10px;
  border-radius: 20px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin: 0.4rem 0.2rem 0 0;
}

.cs-section {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.62rem;
  color: var(--cyan);
  text-transform: uppercase;
  letter-spacing: 0.2em;
  margin-bottom: 0.6rem;
  padding-left: 0.7rem;
  border-left: 2px solid var(--cyan);
}

.cs-kpi {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 6px;
  padding: 1.2rem 1.4rem;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.cs-kpi:hover { border-color: var(--cyan-dim); }
.cs-kpi::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  opacity: 0.4;
}
.cs-kpi-label {
  font-size: 0.6rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 0.4rem;
}
.cs-kpi-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--cyan);
  line-height: 1;
}
.cs-kpi-sub {
  font-size: 0.62rem;
  color: var(--text-dim);
  margin-top: 0.35rem;
}
.cs-kpi-live {
  font-size: 0.58rem;
  color: var(--green);
}

.cs-insight {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--cyan);
  border-radius: 4px;
  padding: 0.8rem 1rem;
  margin: 0.5rem 0;
  font-size: 0.72rem;
  color: var(--text);
  line-height: 1.6;
}

.cs-risk-badge {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 3px;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.cs-sidebar-label {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.6rem;
  color: var(--cyan);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  padding: 0.5rem 0 0.2rem 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.cs-sidebar-label::before {
  content: '▸';
  color: var(--cyan);
}

.cs-logo {
  font-family: 'Orbitron', monospace;
  font-size: 1.1rem;
  font-weight: 900;
  color: var(--cyan);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.cs-logo-sub {
  font-size: 0.55rem;
  color: var(--text-dim);
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

/* ── HIDE STREAMLIT CHROME ────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 100% !important; }

/* ── SCROLLBAR ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan-dim); }

/* ── EXPANDER ─────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 6px !important;
}
[data-testid="stExpander"] summary {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.75rem !important;
  color: var(--cyan) !important;
}

/* scan-line overlay on sidebar */
[data-testid="stSidebar"]::after {
  content: '';
  position: fixed;
  top: 0; left: 0; bottom: 0;
  width: 240px;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,212,255,0.015) 2px,
    rgba(0,212,255,0.015) 4px
  );
  pointer-events: none;
  z-index: 1000;
}
</style>
"""

# Plotly dark theme tokens
BG    = "#080d1a"
BG2   = "#0d1424"
BG3   = "#111929"
BORD  = "#1a2840"
BORD2 = "#1e3050"
CYAN  = "#00d4ff"
CYAN2 = "#0099bb"
RED   = "#ff3366"
AMB   = "#ffaa00"
GRN   = "#00ff9d"
PURP  = "#9d4edd"
TEXT  = "#c8d8e8"
TDIM  = "#5a7a9a"

PALETTE = [CYAN, "#00ff9d", "#ffaa00", "#ff3366", "#9d4edd", "#4cc9f0", "#f72585"]

BASE_LAYOUT = dict(
    paper_bgcolor=BG2,
    plot_bgcolor=BG3,
    font=dict(family="IBM Plex Mono, monospace", color=TEXT, size=11),
    margin=dict(l=45, r=20, t=45, b=40),
    xaxis=dict(gridcolor=BORD, zerolinecolor=BORD, color=TDIM, linecolor=BORD2),
    yaxis=dict(gridcolor=BORD, zerolinecolor=BORD, color=TDIM, linecolor=BORD2),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=TEXT),
                bordercolor=BORD2, borderwidth=1),
    hoverlabel=dict(bgcolor=BG3, bordercolor=BORD2, font_color=TEXT,
                    font_family="IBM Plex Mono, monospace"),
)
