import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_folium import st_folium

# Configure streamlit page settings (MUST be the first command)
st.set_page_config(
    page_title="Agentic UAV Mission Planner",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports from local modules
from agents.mission_understanding_agent import understand_mission
from agents.waypoint_planner_agent import generate_waypoints
from agents.safety_compliance_agent import perform_safety_checks
from agents.correction_agent import generate_corrections
from utils.map_utils import create_mission_map
from utils.database_utils import save_mission, init_db, search_missions, get_mission_by_id
from utils.export_utils import export_mission_json, export_waypoints_csv, generate_pdf_report
from agents.report_agent import generate_mission_summary_html
from agents.mission_understanding_agent import understand_mission, GENAI_AVAILABLE

# Initialize database
init_db()

# Session state defaults (prevent reload reset)
# Theme persistence: read from query params first, fall back to session state
_qp_theme = st.query_params.get("theme", None)
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" if _qp_theme != "Light" else "Light"
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

if "mission_name" not in st.session_state:
    st.session_state.mission_name = "FAST Surveillance"
if "mission_type" not in st.session_state:
    st.session_state.mission_type = "surveillance"
if "altitude" not in st.session_state:
    st.session_state.altitude = 50.0
if "duration" not in st.session_state:
    st.session_state.duration = 15.0
if "pattern" not in st.session_state:
    st.session_state.pattern = "square"
if "home_lat" not in st.session_state:
    st.session_state.home_lat = 33.6425
if "home_lon" not in st.session_state:
    st.session_state.home_lon = 73.0232
if "generated_waypoints" not in st.session_state:
    st.session_state.generated_waypoints = []
if "safety_checks" not in st.session_state:
    st.session_state.safety_checks = []
if "corrections" not in st.session_state:
    st.session_state.corrections = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "map_bounds" not in st.session_state:
    st.session_state.map_bounds = None
if "nl_extracted" not in st.session_state:
    st.session_state.nl_extracted = None  # stores last NL extraction result for feedback card

# Navigation pages
pages = ["Home", "Mission Input", "Mission Plan", "Map View", "Safety Check", "Suggestions", "Export", "Mission History"]

# Ensure current page is valid
if st.session_state.current_page not in pages:
    st.session_state.current_page = "Home"

# Define Theme Tokens:
# Dark Mode: deep navy page, soft slate boxes, dark map tiles (match page)
# Light Mode: off-white page, white boxes, light map tiles (match page)
is_dark = (st.session_state.theme == "Dark")

page_bg        = "#0D0D14" if is_dark else "#F8FAFC"
page_text      = "#E8EAF0" if is_dark else "#1A1A2E"
box_bg         = "#1C1C2E" if is_dark else "#FFFFFF"
box_text       = "#E8EAF0" if is_dark else "#1A1A2E"
sidebar_bg     = "#080810" if is_dark else "#F1F5F9"
sidebar_border = "#22223A" if is_dark else "#CBD5E1"
sidebar_text   = "#E8EAF0" if is_dark else "#1A1A2E"
btn_bg         = "#13131F" if is_dark else "#F8FAFC"
btn_border     = "#2A2A44" if is_dark else "#CBD5E1"
border_col     = "#2A2A44" if is_dark else "#CBD5E1"
th_bg          = "#252540" if is_dark else "#F1F5F9"
caption_col    = "#8890AA" if is_dark else "#64748B"
# Map tiles MATCH the page theme: dark page → dark map tiles, light page → light map tiles
map_bg_col     = "#0D0D14" if is_dark else "#F8FAFC"
map_badge_text = "CARTO Dark Matter (Dark Map)" if is_dark else "CARTO Positron (Light Map)"
map_badge_bg   = "#1E1E2E" if is_dark else "#F1F5F9"
map_badge_fg   = "#E8EAF0" if is_dark else "#1A1A2E"

# High-Contrast Theme CSS with strict 0.5cm top gap measurement
st.markdown(f"""
    <style>
    * {{
        box-sizing: border-box !important;
    }}
    
    /* Root Page Background & Text Color */
    body, .stApp {{
        background-color: {page_bg} !important;
        color: {page_text} !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    }}

    /* Shrink Streamlit header to zero height but keep it in DOM
       so the native sidebar collapse button still functions */
    header[data-testid="stHeader"], [data-testid="stHeader"], .stAppHeader {{
        height: 0px !important;
        min-height: 0px !important;
        overflow: hidden !important;
        padding: 0px !important;
        margin: 0px !important;
        visibility: hidden !important;
    }}

    /* Hide the native Streamlit sidebar collapse controls so our own toggle remains authoritative */
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"] {{
        display: none !important;
    }}

    /* Persistent app branding panel that stays visible even when the sidebar is collapsed */
    .app-branding-card {{
        background: linear-gradient(135deg, rgba(0, 114, 255, 0.14), rgba(0, 198, 255, 0.08));
        border: 1px solid rgba(0, 114, 255, 0.18);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin: 0.85rem 0 1rem 0;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22);
        animation: fadeInUp 0.42s cubic-bezier(.2,.9,.3,1);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }}
    .app-branding-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 26px 68px rgba(0, 0, 0, 0.28);
    }}
    .app-branding-kicker {{
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #00C6FF;
        margin-bottom: 0.35rem;
    }}
    .app-branding-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {page_text};
        margin-bottom: 0.2rem;
    }}
    .app-branding-subtitle {{
        font-size: 0.95rem;
        color: {page_text};
        opacity: 0.9;
        margin-bottom: 0.2rem;
    }}
    .app-branding-footer {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {page_text};
        opacity: 0.82;
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Our custom sidebar toggle button - fixed top-left */
    .sidebar-toggle-btn {{
        position: fixed !important;
        top: 0.6rem !important;
        left: 0.6rem !important;
        z-index: 99999 !important;
        background: #0072FF !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        width: 44px !important;
        height: 44px !important;
        font-size: 1.1rem !important;
        cursor: pointer !important;
        box-shadow: 0 6px 20px rgba(0,114,255,0.25) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Style the Streamlit-generated button (uses title/help attribute) so residual white square becomes themed
       Position it at the top-right of the branding card area */
    button[title="Toggle navigation panel"],
    button[aria-label="Toggle navigation panel"] {{
        position: fixed !important;
        top: 1.0rem !important;
        right: 1.2rem !important;
        left: auto !important;
        z-index: 99998 !important;
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 8px 28px rgba(0,114,255,0.28) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.05rem !important;
    }}
    button[title="Toggle navigation panel"]:focus, button[aria-label="Toggle navigation panel"]:focus {{
        outline: none !important;
        box-shadow: 0 10px 36px rgba(0,114,255,0.36) !important;
    }}

    /* When sidebar is hidden: slide it off-screen */
    .sidebar-hidden section[data-testid="stSidebar"] {{
        display: none !important;
    }}

    /* Hide Leaflet scale bar & attribution footer below map */
    .leaflet-control-attribution,
    .leaflet-control-scale,
    .leaflet-bottom,
    .leaflet-bottom.leaflet-left,
    .leaflet-bottom.leaflet-right {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        background: transparent !important;
        border: none !important;
    }}

    /* Top Boundary Gap: Strictly set to 0.5cm (in 0.3cm - 0.7cm range) */
    .block-container, [data-testid="stMainBlockContainer"] {{
        padding-top: 0.5cm !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        max-width: 100% !important;
    }}

    .stApp h1, h1 {{
        margin-top: 0rem !important;
        padding-top: 0rem !important;
        color: {page_text} !important;
    }}
    h2, h3, h4, h5, h6 {{
        color: {page_text} !important;
    }}

    /* Sidebar Theme & Top Boundary Gap (0.5cm) */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {sidebar_border} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
    section[data-testid="stSidebar"] header {{
        padding-top: 0.5cm !important;
        padding-bottom: 0rem !important;
        height: auto !important;
        min-height: 0px !important;
    }}
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
        padding-top: 0.5cm !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {{
        color: {sidebar_text} !important;
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }}

    /* Sidebar Navigation Buttons */
    section[data-testid="stSidebar"] div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {sidebar_text} !important;
        border: 1px solid {btn_border} !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 0.9rem !important;
        margin-bottom: 0.25rem !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button:hover {{
        background: #0072FF !important;
        color: #FFFFFF !important;
        border-color: #0072FF !important;
        transform: translateX(3px);
    }}

    /* Form & Input Field Labels Outside Boxes - Matches Page Text */
    label,
    .stWidgetLabel,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    .stTextArea label,
    .stTextInput label,
    .stSelectbox label,
    .stNumberInput label,
    .stSlider label,
    .stMultiSelect label,
    .stRadio label,
    .stCheckbox label {{
        color: {page_text} !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }}

    /* Slider values & min/max numbers readability */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"],
    .stSlider div[data-testid="stMarkdownContainer"] p,
    .stSlider span,
    div[data-testid="stSliderTickBar"] * {{
        color: {page_text} !important;
        font-weight: 500 !important;
    }}

    /* Captions globally across main page and sidebar */
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *, caption, small {{
        color: {caption_col} !important;
        font-weight: 500 !important;
    }}
    /* Sidebar caption text – must be explicitly visible */
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{
        color: {sidebar_text} !important;
        opacity: 0.85 !important;
    }}

    /* Telemetry HUD Metrics Cards - BOX BACKGROUND & BOX TEXT COLOR */
    div[data-testid="stMetric"],
    [data-testid="stMetric"] {{
        background-color: {box_bg} !important;
        border: 1px solid {border_col} !important;
        padding: 0.45rem 0.75rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        overflow: hidden !important;
        min-width: 0 !important;
    }}
    div[data-testid="stMetric"] *,
    [data-testid="stMetric"] *,
    [data-testid="stMetricValue"], 
    [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] div,
    div[data-testid="stMetric"] span,
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] p {{
        color: {box_text} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        line-height: 1.2 !important;
    }}

    /* Streamlit Alert Boxes - BOX BACKGROUND & BOX TEXT COLOR */
    div[data-testid="stAlert"],
    .stAlert,
    div[data-baseweb="notification"],
    div[kind="info"],
    div[kind="warning"] {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid {border_col} !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }}
    div[data-testid="stAlert"] *,
    .stAlert *,
    div[data-baseweb="notification"] *,
    div[kind="info"] *,
    div[kind="warning"] * {{
        color: {box_text} !important;
    }}

    /* Primary Action Buttons */
    div.stButton > button {{
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.55rem 1.25rem !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 16px rgba(0, 198, 255, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div.stButton > button:hover {{
        box-shadow: 0 6px 22px rgba(0, 198, 255, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }}

    /* Download Buttons */
    div.stDownloadButton > button {{
        background: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid #0072FF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div.stDownloadButton > button:hover {{
        background: #0072FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(0, 114, 255, 0.3) !important;
    }}

    /* Form Controls & Input Boxes - BOX BACKGROUND & BOX TEXT COLOR */
    div[data-baseweb="input"], div[data-baseweb="select"], textarea, input {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid {border_col} !important;
        border-radius: 8px !important;
    }}
    textarea:focus, input:focus, div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {{
        border-color: #0072FF !important;
        box-shadow: 0 0 0 2px rgba(0, 114, 255, 0.2) !important;
    }}
    
    /* Select Dropdown Popups - BOX BACKGROUND & BOX TEXT COLOR */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid {border_col} !important;
    }}
    li[role="option"] {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background-color: #F1F5F9 !important;
        color: #0072FF !important;
    }}

    /* Dataframe Container & Table - BOX BACKGROUND & BOX TEXT COLOR */
    .dataframe, [data-testid="stDataFrame"] {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid {border_col} !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
    }}
    .dataframe th, [data-testid="stDataFrame"] th {{
        background-color: {th_bg} !important;
        color: {box_text} !important;
        font-weight: 700 !important;
    }}
    .dataframe td, [data-testid="stDataFrame"] td {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
    }}

    /* Custom Card Containers - BOX BACKGROUND & BOX TEXT COLOR */
    .uav-card {{
        background-color: {box_bg} !important;
        border: 1px solid {border_col} !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        color: {box_text} !important;
    }}
    .uav-card *,
    .uav-card-title,
    .uav-card-title * {{
        color: {box_text} !important;
    }}

    /* Map Background Container & iframe alignment */
    iframe[title="streamlit_folium.st_folium"],
    iframe,
    div[data-testid="stCustomComponentV1"],
    div[data-testid="stElementContainer"] {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}
    .leaflet-container {{
        background-color: {map_bg_col} !important;
        background: {map_bg_col} !important;
        border-radius: 12px !important;
    }}
    /* Hide native collapse arrow */
    button[kind="secondary"][data-testid="base_web_button"] {{
        display: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation Header
st.sidebar.title("🚁 UAV Mission Planner")
st.sidebar.caption("Agentic AI Airspace Planner & Auditor")
st.sidebar.markdown("<hr style='border:1px solid #22223A;margin:0.4rem 0 0.8rem 0'>", unsafe_allow_html=True)

# Mode Toggle Radio Control — persist selection to query params so refresh restores it
theme_mode = st.sidebar.radio(
    "🎨 Display Mode",
    ["Dark Mode", "Light Mode"],
    index=0 if st.session_state.theme == "Dark" else 1,
    key="theme_toggle_radio"
)
new_theme = "Dark" if "Dark" in theme_mode else "Light"
if new_theme != st.session_state.theme:
    st.session_state.theme = new_theme
    st.query_params["theme"] = new_theme
    st.rerun()

# Gemini API availability notice (issue #16)
if not GENAI_AVAILABLE:
    st.sidebar.markdown(
        "<div style='background:#3A1A10;border:1px solid #C05621;border-radius:6px;"
        "padding:6px 10px;font-size:0.75rem;color:#FBD38D;margin-bottom:0.5rem'>"
        "⚠️ <b>Gemini AI unavailable</b> — using regex fallback.</div>",
        unsafe_allow_html=True
    )

st.sidebar.markdown("<hr style='border:1px solid #22223A;margin:0.6rem 0'>", unsafe_allow_html=True)

# Grouped navigation with distinct icons
PLANNING_PAGES = {
    "Home":          "🏠",
    "Mission Input": "📝",
    "Mission Plan":  "⚙️",
    "Map View":      "🗺️",
}
SAFETY_PAGES = {
    "Safety Check":    "🛡️",
    "Suggestions":     "💡",
    "Export":          "📥",
    "Mission History": "📂",
}

st.sidebar.markdown(
    f"<div style='font-size:0.7rem;font-weight:700;letter-spacing:0.08em;"
    f"text-transform:uppercase;color:{caption_col};padding:0 0 4px 4px'>📋 Planning</div>",
    unsafe_allow_html=True
)
for page, icon in PLANNING_PAGES.items():
    is_active = (st.session_state.current_page == page)
    label = f"{icon} ▶  {page}" if is_active else f"{icon}  {page}"
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.current_page = page

st.sidebar.markdown(
    f"<div style='font-size:0.7rem;font-weight:700;letter-spacing:0.08em;"
    f"text-transform:uppercase;color:{caption_col};padding:8px 0 4px 4px'>🛡️ Safety & Export</div>",
    unsafe_allow_html=True
)
for page, icon in SAFETY_PAGES.items():
    is_active = (st.session_state.current_page == page)
    label = f"{icon} ▶  {page}" if is_active else f"{icon}  {page}"
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.current_page = page

st.sidebar.markdown("<hr style='border:1px solid #22223A;margin:1rem 0'>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='font-size:0.78rem;color:{sidebar_text};opacity:1;text-align:center;padding:0.3rem 0;font-weight:600'>💡 Powered by Google Gemini AI</div>", unsafe_allow_html=True)


# Hide or show sidebar via CSS based on session state
if not st.session_state.sidebar_open:
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

col_branding, col_toggle = st.columns([12, 1])
with col_branding:
    st.markdown(f"""
        <div class="app-branding-card">
            <div class="app-branding-kicker">🚁 UAV Mission Planner</div>
            <div class="app-branding-title">Agentic AI Airspace Planner and Auditor</div>
            <div class="app-branding-subtitle">Mission planning, safety validation, and live route auditing in one place</div>
            <div class="app-branding-footer">💡 Powered by Google Gemini AI</div>
        </div>
    """, unsafe_allow_html=True)
with col_toggle:
    if st.button("☰", key="sidebar_toggle_btn", help="Toggle navigation panel", use_container_width=True):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

# Telemetry HUD metrics bar
if st.session_state.safety_checks:
    all_passed_hud = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
    status_text = "🟢 SAFE" if all_passed_hud else "🔴 REJECTED"
else:
    status_text = "⚪ UNCHECKED"

hc1, hc2, hc3, hc4 = st.columns(4)
with hc1:
    st.metric("Target Altitude", f"{st.session_state.altitude} m")
with hc2:
    st.metric("Flight Duration", f"{st.session_state.duration} mins")
with hc3:
    st.metric("Compliance Status", status_text)
with hc4:
    st.metric("Flight Profile", st.session_state.pattern.upper())

st.markdown("<hr style='border:1px solid #888888;margin:0.8rem 0 1.2rem 0'>", unsafe_allow_html=True)

# Create GCS split-screen layout (12:12 balanced split)
col_left, col_right = st.columns([12, 12], gap="large")

with col_left:
    # Page 1: Home
    if st.session_state.current_page == "Home":
        st.subheader("🏠 Ground Control Station Dashboard")
        st.caption("AI-driven mission planning system: generate waypoints, enforce safety rules, and export mission plans.")
        
        st.markdown(f"""
            <div class="uav-card" style="margin-top:0.4rem;margin-bottom:0.6rem;padding:0.85rem 1.1rem">
                <div class="uav-card-title" style="margin-bottom:0.4rem;font-size:0.9rem">🛡️ Active Airspace Safety Regulations</div>
                <ul style="margin-bottom:0;padding-left:1.1rem;font-size:0.82rem;color:{box_text};line-height:1.55">
                    <li><b>R1</b>: Maximum Altitude Ceiling: <b>80 metres</b></li>
                    <li><b>R2</b>: Takeoff Command: Mandatory initial sequence</li>
                    <li><b>R3</b>: Return-to-Launch (RTL) / Landing point required</li>
                    <li><b>R4</b>: No-Fly Zone Clearance: Zero entry into restricted airspace</li>
                    <li><b>R5</b>: Maximum Waypoint Leg Separation: <b>500 metres</b></li>
                    <li><b>R6</b>: Maximum Mission Duration: <b>30 minutes</b></li>
                    <li><b>R7</b>: Battery Consumption Reserve: Under <b>80%</b> capacity</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-top:1rem">
                <div class="uav-card" style="margin-bottom:0;padding:1rem">
                    <div style="color:{box_text};font-weight:700;font-size:0.9rem;margin-bottom:0.4rem">1️⃣ Mission Input</div>
                    <div style="font-size:0.83rem;color:{box_text}">Describe mission in natural language or fill out parameters manually.</div>
                </div>
                <div class="uav-card" style="margin-bottom:0;padding:1rem">
                    <div style="color:{box_text};font-weight:700;font-size:0.9rem;margin-bottom:0.4rem">2️⃣ Mission Plan</div>
                    <div style="font-size:0.83rem;color:{box_text}">Generate 4 flight patterns with automatic takeoff & RTL points.</div>
                </div>
                <div class="uav-card" style="margin-bottom:0;padding:1rem">
                    <div style="color:{box_text};font-weight:700;font-size:0.9rem;margin-bottom:0.4rem">3️⃣ Map & Safety</div>
                    <div style="font-size:0.83rem;color:{box_text}">Audit airspace rules on live map and export JSON/CSV/PDF.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Page 2: Mission Input
    elif st.session_state.current_page == "Mission Input":
        st.subheader("📝 Mission Parameter Input")

        # --- Option A: Natural Language ---
        st.markdown(f"""
            <div class="uav-card">
                <div class="uav-card-title">🤖 Option A: Natural Language Request</div>
                <div style="font-size:0.85rem;color:{box_text};margin-bottom:0.5rem">
                    Enter mission details in plain English and let the AI Agent extract the parameters.
                    {'<span style="color:#FBD38D;font-size:0.8rem">⚠️ Using regex fallback (Gemini unavailable)</span>' if not GENAI_AVAILABLE else '<span style="color:#68D391;font-size:0.8rem">✅ Gemini AI active</span>'}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Example prompt buttons
        EXAMPLE_PROMPTS = [
            "Plan a surveillance mission around FAST campus for 15 minutes at 50 meters altitude using a square pattern.",
            "Grid mapping of an industrial zone for 20 minutes, altitude 60 metres, avoid restricted zones, return to launch.",
            "Search and rescue circular sweep for 25 minutes at 40 metres, RTL enabled.",
        ]
        with st.expander("📖 Show example prompts", expanded=False):
            for i, ex in enumerate(EXAMPLE_PROMPTS, 1):
                st.markdown(f"**Example {i}:** `{ex}`")
                if st.button(f"Use Example {i}", key=f"example_prompt_{i}"):
                    st.session_state["_nl_prompt_prefill"] = ex
                    st.rerun()

        default_prompt = st.session_state.pop("_nl_prompt_prefill", None) or \
            "Plan a surveillance mission around FAST campus for 15 minutes at 50 meters altitude using a square pattern layout."

        prompt = st.text_area(
            "Natural Language Prompt:",
            value=default_prompt,
            height=100,
            help="Describe your UAV mission in plain English. Include altitude (metres), duration (minutes), mission type, and route pattern."
        )

        if st.button("🚀 Process with AI Agent", use_container_width=True):
            with st.spinner("Extracting mission parameters..."):
                extracted = understand_mission(prompt)
                st.session_state.mission_name = extracted.get("mission_name", "FAST Surveillance")
                st.session_state.mission_type = extracted.get("mission_type", "surveillance")
                st.session_state.altitude = float(extracted.get("altitude", 50.0))
                st.session_state.duration = float(extracted.get("duration", 15.0))
                st.session_state.pattern = extracted.get(
                    "route_pattern", extracted.get("pattern", "square")
                )
                st.session_state.nl_extracted = extracted
            st.success("✅ Parameters extracted and applied!")

        # NL extraction feedback card (issue #41)
        if st.session_state.nl_extracted:
            ex = st.session_state.nl_extracted
            st.markdown(f"""
                <div class="uav-card" style="border-left:4px solid #0072FF;margin-top:0.6rem">
                    <div style="font-size:0.8rem;font-weight:700;color:{box_text};margin-bottom:0.5rem">🔍 Extracted Parameters</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 16px;font-size:0.82rem;color:{box_text}">
                        <div><b>Name:</b> {ex.get('mission_name','—')}</div>
                        <div><b>Type:</b> {ex.get('mission_type','—')}</div>
                        <div><b>Altitude:</b> {ex.get('altitude','—')} m</div>
                        <div><b>Duration:</b> {ex.get('duration','—')} min</div>
                        <div><b>Pattern:</b> {ex.get('route_pattern', ex.get('pattern','—'))}</div>
                        <div><b>RTL:</b> {'Yes' if ex.get('return_to_launch', True) else 'No'}</div>
                        <div><b>Avoid NFZ:</b> {'Yes' if ex.get('avoid_no_fly_zone', True) else 'No'}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border:1px solid #2A2A44;margin:1.2rem 0'>", unsafe_allow_html=True)

        # --- Option B: Manual Override ---
        st.markdown("""
            <div class="uav-card">
                <div class="uav-card-title">⚙️ Option B: Manual Parameter Override</div>
            </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.session_state.mission_name = st.text_input(
                "Mission Name", st.session_state.mission_name,
                help="A short descriptive label for this mission (e.g. 'Campus Perimeter Survey')."
            )
            st.session_state.mission_type = st.selectbox(
                "Mission Type",
                ["surveillance", "mapping", "search_rescue", "inspection"],
                index=["surveillance", "mapping", "search_rescue", "inspection"].index(st.session_state.mission_type),
                help="The operational category determines how the mission is logged and reported."
            )
            st.session_state.pattern = st.selectbox(
                "Route Pattern Profile",
                ["square", "grid", "circle", "perimeter"],
                index=["square", "grid", "circle", "perimeter"].index(st.session_state.pattern),
                help="Square: 4-corner patrol | Grid: lawn-mower scan | Circle: radial orbit | Perimeter: boundary trace."
            )
        with col_b:
            st.session_state.altitude = st.slider(
                "Target Altitude (metres)", 10.0, 150.0, st.session_state.altitude,
                help="Maximum cruise altitude. Rule R1 limits this to 80 m for legal compliance."
            )
            st.session_state.duration = st.slider(
                "Target Duration (minutes)", 5.0, 60.0, st.session_state.duration,
                help="Planned total flight time. Rule R6 sets a 30-minute maximum safety window."
            )
        with col_c:
            st.session_state.home_lat = st.number_input(
                "Home Latitude", value=st.session_state.home_lat, format="%.6f",
                help="Latitude of the takeoff / launch point (decimal degrees, e.g. 33.642500)."
            )
            st.session_state.home_lon = st.number_input(
                "Home Longitude", value=st.session_state.home_lon, format="%.6f",
                help="Longitude of the takeoff / launch point (decimal degrees, e.g. 73.023200)."
            )

    # Page 3: Mission Plan
    elif st.session_state.current_page == "Mission Plan":
        st.subheader("⚙️ Mission Route Planner")

        st.markdown(f"""
            <div class="uav-card">
                <div class="uav-card-title">📌 Active Mission Setup</div>
                <div style="font-size:0.9rem;color:{box_text}">
                    <b>Mission:</b> {st.session_state.mission_name} &nbsp;|&nbsp; 
                    <b>Type:</b> {st.session_state.mission_type} &nbsp;|&nbsp; 
                    <b>Pattern:</b> {st.session_state.pattern.upper()} &nbsp;|&nbsp; 
                    <b>Altitude:</b> {st.session_state.altitude} m &nbsp;|&nbsp; 
                    <b>Duration:</b> {st.session_state.duration} mins
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Generate Waypoint Trajectory", use_container_width=True):
            with st.spinner("Computing flight waypoints and running safety checks..."):
                wps = generate_waypoints(
                    st.session_state.home_lat, st.session_state.home_lon,
                    st.session_state.altitude, st.session_state.pattern
                )
                st.session_state.generated_waypoints = wps
                meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
                st.session_state.safety_checks = perform_safety_checks(meta, wps)
                st.session_state.corrections = generate_corrections(st.session_state.safety_checks, meta, wps)
                # Compute and store bounding box for map auto-zoom
                _, bounds = create_mission_map(
                    wps,
                    (st.session_state.home_lat, st.session_state.home_lon),
                    dark_map=is_dark
                )
                st.session_state.map_bounds = bounds
            st.success(f"✅ Generated {len(wps)} waypoints — navigate to **Map View** to see the route.")

        if st.session_state.generated_waypoints:
            st.write(f"**Generated Waypoint Count:** `{len(st.session_state.generated_waypoints)}`")
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True, height=300)

            st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
            st.markdown("### 📄 Mission Summary Report")
            mission_meta_rpt = {
                "mission_name": st.session_state.mission_name,
                "mission_type": st.session_state.mission_type,
                "altitude": st.session_state.altitude,
                "duration": st.session_state.duration,
                "status": "Safe" if (st.session_state.safety_checks and all(c["result"] == "Pass" for c in st.session_state.safety_checks)) else "Needs Revision",
            }
            summary_html = generate_mission_summary_html(
                mission_meta_rpt,
                st.session_state.generated_waypoints,
                st.session_state.safety_checks,
                theme=st.session_state.theme
            )
            st.markdown(summary_html, unsafe_allow_html=True)
        else:
            st.info("Click **Generate Waypoint Trajectory** to compute flight waypoints.")


    # Page 4: Map View
    elif st.session_state.current_page == "Map View":
        st.subheader("🗺️ Telemetry & Coordinates Control")
        
        st.markdown(f"""
            <div class="uav-card">
                <div class="uav-card-title">🛰️ Flight Telemetry Summary</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.88rem;color:{box_text}">
                    <div><b>Mission:</b> {st.session_state.mission_name}</div>
                    <div><b>Profile:</b> {st.session_state.pattern.upper()}</div>
                    <div><b>Home Lat:</b> {st.session_state.home_lat:.6f}</div>
                    <div><b>Home Lon:</b> {st.session_state.home_lon:.6f}</div>
                    <div><b>Altitude Ceiling:</b> {st.session_state.altitude} m</div>
                    <div><b>Target Duration:</b> {st.session_state.duration} mins</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.generated_waypoints:
            st.write(f"**Waypoint Sequence List ({len(st.session_state.generated_waypoints)} Points):**")
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True, height=300)
        else:
            st.info("No waypoints generated yet. Go to **Mission Plan** to generate waypoints first.")

    # Page 5: Safety Check
    elif st.session_state.current_page == "Safety Check":
        st.subheader("🛡️ Safety Compliance Auditor")

        if st.session_state.safety_checks:
            all_passed = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
            status_label = "🟢 MISSION CLEARED & SAFE" if all_passed else "🔴 REJECTED: SAFETY VIOLATION"
            
            st.markdown(f"""
                <div class="uav-card" style="border-left:4px solid {'#10B981' if all_passed else '#EF4444'}">
                    <div style="font-size:1.15rem;font-weight:800;color:{box_text}">{status_label}</div>
                </div>
            """, unsafe_allow_html=True)

            for c in st.session_state.safety_checks:
                icon = "✅" if c["result"] == "Pass" else "❌"
                col_c = "#10B981" if c["result"] == "Pass" else "#EF4444"
                st.markdown(f"""
                    <div style="background:{box_bg};border:1px solid {border_col};padding:0.7rem 1rem;border-radius:8px;margin-bottom:0.4rem;display:flex;align-items:center;justify-content:space-between">
                        <span style="font-weight:700;color:{box_text}">{icon} {c['check_name']}</span>
                        <span style="color:{col_c};font-weight:600;font-size:0.85rem">{c['message']}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            if st.button("💾 Save Mission to Database", use_container_width=True):
                mission_row = {
                    "mission_name": st.session_state.mission_name,
                    "mission_type": st.session_state.mission_type,
                    "altitude": st.session_state.altitude,
                    "duration": st.session_state.duration,
                    "status": "Safe" if all_passed else "Unsafe",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_mission(mission_row, st.session_state.generated_waypoints, st.session_state.safety_checks)
                st.success("✅ Mission record saved to SQLite database successfully!")
        else:
            st.warning("⚠️ No safety checks available. Please generate waypoints on the **Mission Plan** page first.")

    # Page 6: Suggestions
    elif st.session_state.current_page == "Suggestions":
        st.subheader("💡 Correction Suggestions Agent")

        if st.session_state.corrections:
            st.write("The Correction Agent generated the following actionable fixes:")
            for i, corr in enumerate(st.session_state.corrections, 1):
                st.markdown(f"""
                    <div class="uav-card" style="border-left:4px solid #0072FF">
                        <div style="color:#0072FF;font-weight:700;font-size:0.9rem">Correction #{i}</div>
                        <div style="color:{box_text};margin-top:0.3rem">{corr}</div>
                    </div>
                """, unsafe_allow_html=True)
        elif st.session_state.safety_checks:
            st.success("✅ All safety compliance checks passed cleanly. No corrections required!")
        else:
            st.warning("⚠️ No suggestions available. Generate waypoints and run safety checks first.")

    # Page 7: Export
    elif st.session_state.current_page == "Export":
        st.subheader("📥 Export Mission Packages")

        if st.session_state.generated_waypoints:
            mission_meta = {
                "mission_name": st.session_state.mission_name,
                "mission_type": st.session_state.mission_type,
                "altitude": st.session_state.altitude,
                "duration": st.session_state.duration,
                "status": "Unchecked",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if st.session_state.safety_checks:
                all_passed = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
                mission_meta["status"] = "Safe" if all_passed else "Unsafe"

            st.markdown(f"""
                <div class="uav-card">
                    <div style="font-size:0.95rem;color:{box_text}">
                        <b>Mission Package:</b> {mission_meta['mission_name']} &nbsp;|&nbsp; 
                        <b>Status:</b> <span style="color:{'#10B981' if mission_meta['status']=='Safe' else '#EF4444'};font-weight:700">{mission_meta['status']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                json_str = export_mission_json(mission_meta, st.session_state.generated_waypoints, st.session_state.safety_checks)
                st.download_button(
                    "⬇️  Download JSON",
                    data=json_str, file_name="mission.json", mime="application/json",
                    use_container_width=True
                )
            with col_e2:
                csv_str = export_waypoints_csv(st.session_state.generated_waypoints)
                st.download_button(
                    "⬇️  Download CSV",
                    data=csv_str, file_name="waypoints.csv", mime="text/csv",
                    use_container_width=True
                )
            with col_e3:
                pdf_bytes = generate_pdf_report(mission_meta, st.session_state.generated_waypoints, st.session_state.safety_checks)
                st.download_button(
                    "⬇️  Download PDF",
                    data=pdf_bytes, file_name="mission_report.pdf", mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ No waypoints generated yet. Complete Mission Plan before exporting.")

    # Page 8: Mission History
    elif st.session_state.current_page == "Mission History":
        st.subheader("📂 Mission History & Database")
        st.caption("Browse, search, filter, load, and delete saved missions from the local SQLite database.")

        # Search & filter bar
        filt_col1, filt_col2, filt_col3 = st.columns([3, 2, 2])
        with filt_col1:
            name_search = st.text_input("🔍 Search by name", "", placeholder="Type mission name...",
                                        help="Case-insensitive substring search on mission name.")
        with filt_col2:
            status_filter = st.selectbox("Filter by status", ["All", "Safe", "Unsafe", "Needs Revision"],
                                         help="Filter missions by their safety compliance status.")
        with filt_col3:
            type_filter = st.selectbox("Filter by type", ["All", "surveillance", "mapping", "search_rescue", "inspection"],
                                       help="Filter missions by their operational type.")

        missions_list = search_missions(name_search, status_filter, type_filter)

        if not missions_list:
            st.info("No saved missions found. Complete a mission and click **Save Mission to Database** on the Safety Check page.")
        else:
            st.markdown(f"<div style='font-size:0.82rem;color:{caption_col};margin-bottom:0.5rem'>"
                        f"Showing <b>{len(missions_list)}</b> mission(s)</div>", unsafe_allow_html=True)

            for m_row in missions_list:
                mid = m_row["mission_id"]
                m_status = m_row.get("status", "")
                status_color = "#10B981" if m_status == "Safe" else ("#EF4444" if m_status == "Unsafe" else "#F59E0B")

                with st.expander(
                    f"#{mid} — {m_row['mission_name']}  |  {m_row['mission_type'].upper()}  |  "
                    f"{m_row['altitude']}m  |  {m_row['duration']}min  |  "
                    f"{'✅' if m_status == 'Safe' else '❌'} {m_status}  |  {m_row['created_at']}",
                    expanded=False
                ):
                    detail_col1, detail_col2 = st.columns([1, 1])
                    with detail_col1:
                        st.markdown(f"""
                            <div class="uav-card" style="padding:0.7rem 1rem">
                                <div style="font-size:0.8rem;color:{box_text}">
                                    <b>Mission ID:</b> {mid}<br>
                                    <b>Name:</b> {m_row['mission_name']}<br>
                                    <b>Type:</b> {m_row['mission_type']}<br>
                                    <b>Altitude:</b> {m_row['altitude']} m<br>
                                    <b>Duration:</b> {m_row['duration']} min<br>
                                    <b>Status:</b> <span style="color:{status_color};font-weight:700">{m_status}</span><br>
                                    <b>Saved:</b> {m_row['created_at']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with detail_col2:
                        if st.button(f"📥 Load Mission #{mid} into Planner", key=f"load_mission_{mid}",
                                     use_container_width=True,
                                     help="Load this mission's parameters and waypoints into the active session."):
                            try:
                                m_data, m_wps, m_checks = get_mission_by_id(mid)
                                st.session_state.mission_name = m_data["mission_name"]
                                st.session_state.mission_type = m_data["mission_type"]
                                st.session_state.altitude = float(m_data["altitude"])
                                st.session_state.duration = float(m_data["duration"])
                                st.session_state.generated_waypoints = m_wps
                                st.session_state.safety_checks = m_checks
                                st.session_state.corrections = []
                                st.success(f"✅ Mission '**{m_data['mission_name']}**' loaded. Navigate to Map View to see the route.")
                            except Exception as e:
                                st.error(f"Error loading mission: {e}")

                        if st.checkbox(f"🗑️ Delete Mission #{mid}", key=f"del_chk_{mid}"):
                            st.warning(f"This will permanently delete mission **#{mid}** and all its waypoints and safety checks.")
                            if st.button(f"Confirm Delete Mission #{mid}", key=f"confirm_delete_{mid}",
                                         use_container_width=True):
                                from utils.database_utils import delete_mission
                                delete_mission(mid)
                                st.success(f"Mission #{mid} deleted.")
                                st.rerun()

with col_right:
    st.markdown(f"""
        <div style="background-color:{box_bg};border:1px solid {border_col};border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between">
            <span style="font-weight:700;color:{box_text};font-size:1rem">🗺️ Live GCS Mission Radar & Airspace</span>
            <span style="font-size:0.78rem;background:{map_badge_bg};color:{map_badge_fg};padding:3px 8px;border-radius:6px;font-weight:600">{map_badge_text}</span>
        </div>
    """, unsafe_allow_html=True)

    m, map_bounds_live = create_mission_map(
        st.session_state.generated_waypoints,
        (st.session_state.home_lat, st.session_state.home_lon),
        dark_map=is_dark  # Fixed: map theme now matches page theme
    )
    # Use stored bounds (from waypoint generation) for auto-zoom; fall back to live-computed bounds
    active_bounds = st.session_state.map_bounds or map_bounds_live
    if active_bounds:
        min_lat, min_lon, max_lat, max_lon = active_bounds
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    st_folium(
        m,
        use_container_width=True,
        height=620,
        key=f"gcs_map_{len(st.session_state.generated_waypoints)}_{st.session_state.theme}"
    )