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
from agents.mission_understanding_agent import understand_mission, GENAI_AVAILABLE
from agents.waypoint_planner_agent import generate_waypoints
from agents.safety_compliance_agent import perform_safety_checks
from agents.correction_agent import generate_corrections
from utils.map_utils import create_mission_map
from utils.database_utils import (
    save_mission, init_db, search_missions, get_mission_by_id,
    get_mission_waypoint_count, clone_mission,
    export_filtered_missions_batch_json, import_mission_from_json
)
from utils.export_utils import (
    export_mission_json, export_waypoints_csv, generate_pdf_report,
    export_qgroundcontrol_plan, export_ardupilot_waypoints, export_kml_format
)
from agents.report_agent import generate_mission_summary_html
from config.settings import DRONE_PROFILES
from agents.safety_compliance_agent import perform_safety_checks, add_custom_no_fly_zone

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
    st.session_state.nl_extracted = None
if "drone_profile_key" not in st.session_state:
    st.session_state.drone_profile_key = "quadcopter_inspection"
if "history_preview_id" not in st.session_state:
    st.session_state.history_preview_id = None
if "history_preview_name" not in st.session_state:
    st.session_state.history_preview_name = ""
if "history_preview_waypoints" not in st.session_state:
    st.session_state.history_preview_waypoints = []



if "square_side" not in st.session_state:
    st.session_state.square_side = 100.0
if "grid_step" not in st.session_state:
    st.session_state.grid_step = 40.0
if "perim_offset" not in st.session_state:
    st.session_state.perim_offset = 60.0
if "circle_radius" not in st.session_state:
    st.session_state.circle_radius = 50.0

# Navigation pages
pages = ["Home", "Mission Input", "Mission Plan", "Map View", "Safety Check", "Suggestions", "Export", "Mission History"]

# Ensure current page is valid
if st.session_state.current_page not in pages:
    st.session_state.current_page = "Home"

# ================================================================
# DEFINE THEME TOKENS - ENHANCED VISUAL HIERARCHY
# ================================================================
# The key fix: Page background, sidebar, and boxes now have DIFFERENT colors
# This creates depth and visual separation between UI layers

is_dark = (st.session_state.theme == "Dark")

# DARK MODE: Page is dark, sidebar is darker, boxes are lighter
# LIGHT MODE: Page is light gray, sidebar is lighter gray, boxes are white
page_bg        = "#0A0A12" if is_dark else "#EBEEF2"      # Darkest / Lightest gray
sidebar_bg     = "#06060E" if is_dark else "#E8ECF0"      # Darker than page / Lighter than page
box_bg         = "#181828" if is_dark else "#FFFFFF"      # Lighter than page / Pure white

page_text      = "#E8EAF0" if is_dark else "#1A1A2E"
box_text       = "#E8EAF0" if is_dark else "#1A1A2E"
sidebar_border = "#1E1E2E" if is_dark else "#CBD5E1"
sidebar_text   = "#E8EAF0" if is_dark else "#1A1A2E"
btn_bg         = "#13131F" if is_dark else "#F8FAFC"
btn_border     = "#2A2A44" if is_dark else "#CBD5E1"
border_col     = "#2A2A44" if is_dark else "#CBD5E1"
th_bg          = "#252540" if is_dark else "#F1F5F9"
caption_col    = "#A0AEC0" if is_dark else "#4A5568"
map_bg_col     = "#0A0A12" if is_dark else "#EBEEF2"
map_badge_text = "CARTO Dark Matter (Dark Map)" if is_dark else "CARTO Positron (Light Map)"
map_badge_bg   = "#1E1E2E" if is_dark else "#F1F5F9"
map_badge_fg   = "#E8EAF0" if is_dark else "#1A1A2E"

# ================================================================
# UPDATED CSS WITH VISUAL HIERARCHY - DIFFERENT BACKGROUNDS FOR EACH LAYER
# ================================================================
st.markdown(f"""
    <style>
    :root {{
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 10px;
        --radius-xl: 12px;
        --radius-xxl: 16px;
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 0.75rem;
        --spacing-lg: 1rem;
        --spacing-xl: 1.25rem;
        --spacing-2xl: 1.5rem;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
        --shadow-md: 0 8px 32px rgba(0,0,0,0.12);
        --shadow-lg: 0 16px 48px rgba(0,0,0,0.18);
        --accent-start: #00C6FF;
        --accent-end: #0072FF;
    }}

    * {{
        box-sizing: border-box !important;
    }}

    /* ================================================================
       PAGE BACKGROUND - Darkest in Dark Mode, Lightest gray in Light Mode
       ================================================================ */

    body, .stApp {{
        background-color: {page_bg} !important;
        color: {page_text} !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        min-height: 100vh !important;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(0,114,255,0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0,198,255,0.02) 0%, transparent 50%) !important;
        background-attachment: fixed !important;
    }}

    /* ================================================================
       HEADER HIDE
       ================================================================ */

    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    .stAppHeader {{
        height: 0px !important;
        min-height: 0px !important;
        overflow: hidden !important;
        padding: 0px !important;
        margin: 0px !important;
        visibility: hidden !important;
    }}

    /* COMPLETELY HIDE the native sidebar collapse controls */
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"],
    button[kind="secondary"][data-testid="base_web_button"],
    button[title="Toggle navigation panel"],
    button[aria-label="Toggle navigation panel"],
    section[data-testid="stSidebar"] button:has(svg),
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"],
    button[kind="header"],
    [data-testid="stSidebarHeader"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -9999px !important;
    }}

    /* ================================================================
       SIDEBAR - Darker than page in Dark Mode, Lighter in Light Mode
       ================================================================ */

    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {sidebar_border} !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.12) !important;
        position: relative !important;
        z-index: 100 !important;
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 0.5cm !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: {sidebar_text} !important;
    }}

    /* Sidebar Navigation Buttons */
    section[data-testid="stSidebar"] div.stButton > button {{
        background-color: {btn_bg} !important;
        color: {sidebar_text} !important;
        border: 1px solid {btn_border} !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: var(--spacing-sm) var(--spacing-md) !important;
        margin-bottom: 0.25rem !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button:hover {{
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: #FFFFFF !important;
        border-color: #0072FF !important;
        transform: translateX(3px);
        box-shadow: 0 4px 12px rgba(0,114,255,0.25) !important;
    }}

    /* Sidebar Section Headers */
    .sidebar-section-label {{
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {caption_col};
        padding: 0.5rem 0 0.25rem 0.25rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 0.5rem;
    }}

    /* ================================================================
       BRANDING CARD - Enhanced with gradient and glow
       ================================================================ */

    .app-branding-card {{
        background: linear-gradient(135deg, 
            rgba(0,114,255,0.10) 0%, 
            rgba(0,198,255,0.05) 100%
        );
        border: 1px solid rgba(0,114,255,{0.25 if is_dark else 0.12});
        border-radius: var(--radius-xl);
        padding: var(--spacing-lg) var(--spacing-xl);
        margin: 0.85rem 0 1rem 0;
        box-shadow: 0 18px 40px rgba(0,0,0,0.12);
        animation: fadeInUp 0.42s cubic-bezier(.2,.9,.3,1);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        position: relative;
        overflow: hidden;
    }}
    .app-branding-card::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 70% 30%, rgba(0,198,255,0.04), transparent 60%);
        pointer-events: none;
    }}
    .app-branding-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 26px 68px rgba(0,0,0,0.18);
    }}
    .app-branding-kicker {{
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #00C6FF;
        margin-bottom: 0.35rem;
        position: relative;
        z-index: 1;
    }}
    .app-branding-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {page_text};
        margin-bottom: 0.2rem;
        position: relative;
        z-index: 1;
    }}
    .app-branding-subtitle {{
        font-size: 0.95rem;
        color: {page_text};
        opacity: 0.9;
        margin-bottom: 0.2rem;
        position: relative;
        z-index: 1;
    }}
    .app-branding-footer {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {page_text};
        opacity: 0.82;
        position: relative;
        z-index: 1;
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ================================================================
       METRICS CARDS - With gradient accent bar
       ================================================================ */

    div[data-testid="stMetric"],
    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, 
            {box_bg} 0%, 
            {'rgba(0,114,255,0.02)' if is_dark else '#F8FAFC'} 100%
        ) !important;
        border: 1px solid rgba(0,114,255,0.08) !important;
        padding: 0.75rem 1rem !important;
        border-radius: var(--radius-md) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
        overflow: hidden !important;
        min-width: 0 !important;
        position: relative !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.14) !important;
    }}
    /* Accent bar on top of metrics */
    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 3px !important;
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%) !important;
        border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
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
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        line-height: 1.3 !important;
        letter-spacing: -0.01em !important;
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        opacity: 0.8 !important;
    }}

    /* ================================================================
       CARDS - Lighter than page, with shadows and hover effects
       ================================================================ */

    .uav-card {{
        background: linear-gradient(145deg, 
            {box_bg} 0%, 
            {'rgba(0,114,255,0.01)' if is_dark else '#F8FAFC'} 100%
        ) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: var(--radius-xl) !important;
        padding: var(--spacing-lg) var(--spacing-xl);
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08) !important;
        color: {box_text} !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
        box-sizing: border-box !important;
        max-width: 100% !important;
        position: relative !important;
    }}
    .uav-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 16px 48px rgba(0,0,0,0.14) !important;
    }}
    .uav-card *,
    .uav-card-title,
    .uav-card-title * {{
        color: {box_text} !important;
    }}

    /* Card with accent border */
    .uav-card-accent {{
        border-left: 4px solid #0072FF !important;
    }}

    /* Card with gradient top border */
    .uav-card-gradient-top {{
        border-top: 3px solid transparent !important;
        border-image: linear-gradient(90deg, #00C6FF, #0072FF) 1 !important;
    }}

    /* ================================================================
       ALERT BOXES
       ================================================================ */

    div[data-testid="stAlert"],
    .stAlert,
    div[data-baseweb="notification"],
    div[kind="info"],
    div[kind="warning"] {{
        background: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid rgba(0,114,255,0.10) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--spacing-md) var(--spacing-lg) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }}
    div[data-testid="stAlert"] *,
    .stAlert *,
    div[data-baseweb="notification"] *,
    div[kind="info"] *,
    div[kind="warning"] * {{
        color: {box_text} !important;
    }}

    /* Success alert - green accent */
    div[kind="success"] {{
        border-left: 4px solid #10B981 !important;
    }}
    /* Error alert - red accent */
    div[kind="error"] {{
        border-left: 4px solid #EF4444 !important;
    }}
    /* Warning alert - orange accent */
    div[kind="warning"] {{
        border-left: 4px solid #F59E0B !important;
    }}
    /* Info alert - blue accent */
    div[kind="info"] {{
        border-left: 4px solid #3B82F6 !important;
    }}

    /* ================================================================
       BUTTONS
       ================================================================ */

    /* Primary Action Buttons */
    div.stButton > button {{
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 16px rgba(0,198,255,0.25) !important;
        transition: all 0.25s ease-in-out !important;
        min-height: 44px !important;
    }}
    div.stButton > button:hover {{
        box-shadow: 0 6px 28px rgba(0,198,255,0.4) !important;
        transform: translateY(-2px);
        background: linear-gradient(135deg, #00D4FF 0%, #0084FF 100%) !important;
    }}

    /* Secondary Buttons */
    div.stButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {{
        background: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid {border_col} !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
        min-height: 38px !important;
    }}
    div.stButton > button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {{
        background: rgba(0,114,255,0.08) !important;
        border-color: #0072FF !important;
        color: #0072FF !important;
        box-shadow: 0 4px 12px rgba(0,114,255,0.12) !important;
    }}

    /* Download Buttons */
    div.stDownloadButton > button,
    [data-testid="stDownloadButton"] > button {{
        background: {box_bg} !important;
        color: {box_text} !important;
        border: 2px solid #0072FF !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.25s ease-in-out !important;
        min-height: 44px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }}
    div.stDownloadButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover {{
        background: linear-gradient(135deg, #0072FF 0%, #0052CC 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(0,114,255,0.3) !important;
        transform: translateY(-2px);
        border-color: #0072FF !important;
    }}

    /* ================================================================
       FORM CONTROLS
       ================================================================ */

    div[data-baseweb="input"],
    div[data-baseweb="select"],
    textarea,
    input {{
        background: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: var(--radius-sm) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.04) !important;
    }}
    input::placeholder,
    textarea::placeholder,
    [data-baseweb="input"] input::placeholder {{
        color: {caption_col} !important;
        opacity: 0.6 !important;
    }}
    textarea:focus,
    input:focus,
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {{
        border-color: #0072FF !important;
        box-shadow: 0 0 0 3px rgba(0,114,255,0.15), inset 0 1px 3px rgba(0,0,0,0.04) !important;
    }}

    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="select"] > div {{
        min-height: 42px !important;
        height: 42px !important;
        display: flex !important;
        align-items: center !important;
    }}
    div[data-baseweb="input"] input {{
        height: 100% !important;
        color: {box_text} !important;
        -webkit-text-fill-color: {box_text} !important;
    }}

    /* ================================================================
       DATA FRAME
       ================================================================ */

    .dataframe,
    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {{
        background: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.88rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }}
    .dataframe th,
    [data-testid="stDataFrame"] th,
    [data-testid="stDataEditor"] th {{
        background: rgba(255,255,255,0.04) !important;
        color: {box_text} !important;
        font-weight: 700 !important;
        padding: 0.5rem 0.6rem !important;
        border-bottom: 2px solid rgba(0,114,255,0.12) !important;
    }}
    .dataframe td,
    [data-testid="stDataFrame"] td,
    [data-testid="stDataEditor"] td {{
        padding: 0.4rem 0.6rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    }}
    .dataframe tr:hover,
    [data-testid="stDataFrame"] tr:hover {{
        background: rgba(0,114,255,0.04) !important;
    }}

    /* ================================================================
       MAP
       ================================================================ */

    iframe[title="streamlit_folium.st_folium"],
    div[data-testid="stCustomComponentV1"] {{
        background-color: {map_bg_col} !important;
        border: 1px solid rgba(0,114,255,0.08) !important;
        border-radius: var(--radius-xl) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.10) !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        line-height: 0 !important;
        overflow: hidden !important;
    }}
    div[data-testid="stCustomComponentV1"] > div,
    div[data-testid="stCustomComponentV1"] iframe,
    [data-testid="stIFrame"],
    [data-testid="stIFrame"] > iframe {{
        background-color: {map_bg_col} !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        display: block !important;
        line-height: 0 !important;
        vertical-align: bottom !important;
        border-radius: var(--radius-xl) !important;
    }}
    .leaflet-container,
    .folium-map {{
        background-color: {map_bg_col} !important;
        background: {map_bg_col} !important;
        border-radius: var(--radius-xl) !important;
    }}

    /* ================================================================
       TOP BOUNDARY GAP
       ================================================================ */

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

    /* ================================================================
       CAPTIONS
       ================================================================ */

    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *, caption, small {{
        color: {caption_col} !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }}
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{
        color: {sidebar_text} !important;
        opacity: 0.85 !important;
    }}

    /* ================================================================
       LABELS
       ================================================================ */

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

    /* ================================================================
       SLIDER VALUES
       ================================================================ */

    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"],
    .stSlider div[data-testid="stMarkdownContainer"] p,
    .stSlider span,
    div[data-testid="stSliderTickBar"] * {{
        color: {page_text} !important;
        font-weight: 500 !important;
    }}

    /* ================================================================
       SELECT DROPDOWN
       ================================================================ */

    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
        border: 1px solid {border_col} !important;
        box-shadow: var(--shadow-md) !important;
        border-radius: var(--radius-sm) !important;
    }}
    li[role="option"] {{
        background-color: {box_bg} !important;
        color: {box_text} !important;
        padding: 0.5rem 0.75rem !important;
        transition: background 0.15s ease !important;
    }}
    li[role="option"]:hover, li[aria-selected="true"] {{
        background: rgba(0,114,255,0.12) !important;
        color: #0072FF !important;
    }}

    /* ================================================================
       RADIO BUTTONS
       ================================================================ */

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] span {{
        color: {box_text} !important;
        -webkit-text-fill-color: {box_text} !important;
        font-weight: 600 !important;
    }}

    /* ================================================================
       EXPANDER
       ================================================================ */

    details {{
        background: transparent !important;
        border: none !important;
    }}
    details summary {{
        color: {page_text} !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.25rem 0 !important;
    }}
    details summary:hover {{
        color: #00C6FF !important;
    }}

    /* ================================================================
       RESPONSIVE DESIGN
       ================================================================ */

    @media screen and (max-width: 768px) {{
        .stColumns {{
            flex-direction: column !important;
        }}
        .block-container, [data-testid="stMainBlockContainer"] {{
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }}
        div[data-testid="stMetric"] {{
            padding: 0.4rem 0.6rem !important;
            margin-bottom: 0.5rem !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1rem !important;
        }}
        .app-branding-title {{
            font-size: 1rem !important;
        }}
        .app-branding-subtitle {{
            font-size: 0.8rem !important;
        }}
        div.stButton > button,
        div.stDownloadButton > button {{
            padding: 0.4rem 0.8rem !important;
            font-size: 0.8rem !important;
            min-height: 36px !important;
        }}
        .uav-card {{
            padding: var(--spacing-md) var(--spacing-lg) !important;
        }}
    }}

    @media screen and (max-width: 480px) {{
        .app-branding-card {{
            padding: var(--spacing-md) var(--spacing-lg) !important;
        }}
        .app-branding-title {{
            font-size: 0.9rem !important;
        }}
        .app-branding-subtitle {{
            font-size: 0.7rem !important;
        }}
        div[data-testid="stMetric"] {{
            padding: 0.3rem 0.4rem !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 0.9rem !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.6rem !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation Header
st.sidebar.title("🚁 UAV Mission Planner")
st.sidebar.caption("Agentic AI Airspace Planner & Auditor")
st.sidebar.markdown("<hr style='border:1px solid #22223A;margin:0.4rem 0 0.8rem 0'>", unsafe_allow_html=True)

# Mode Toggle Radio Control
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

# Gemini API availability notice
if not GENAI_AVAILABLE:
    st.sidebar.markdown(
        "<div style='background:#3A1A10;border:1px solid #C05621;border-radius:6px;"
        "padding:6px 10px;font-size:0.75rem;color:#FBD38D;margin-bottom:0.5rem'>"
        "⚠️ <b>Gemini AI unavailable</b> - using regex fallback.</div>",
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
    f"<div class='sidebar-section-label'>📋 Planning</div>",
    unsafe_allow_html=True
)
for page, icon in PLANNING_PAGES.items():
    is_active = (st.session_state.current_page == page)
    label = f"{icon} ▶  {page}" if is_active else f"{icon}  {page}"
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.current_page = page

st.sidebar.markdown(
    f"<div class='sidebar-section-label'>🛡️ Safety & Export</div>",
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
            <div class="uav-card uav-card-gradient-top" style="margin-top:0.4rem;margin-bottom:0.6rem;padding:0.85rem 1.1rem">
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

        # JSON Mission File Import Block
        with st.expander("📥 Import Saved Mission Package (JSON)", expanded=False):
            uploaded_file = st.file_uploader("Upload exported mission.json file:", type=["json"])
            if uploaded_file is not None:
                try:
                    imported_data = json.load(uploaded_file)
                    mission_info = imported_data.get("mission", imported_data)
                    wps_info = imported_data.get("waypoints", [])
                    checks_info = imported_data.get("safety_checks", [])

                    st.session_state.mission_name = mission_info.get("mission_name", st.session_state.mission_name)
                    st.session_state.mission_type = mission_info.get("mission_type", st.session_state.mission_type)
                    st.session_state.altitude = float(mission_info.get("altitude", st.session_state.altitude))
                    st.session_state.duration = float(mission_info.get("duration", st.session_state.duration))
                    if wps_info:
                        st.session_state.generated_waypoints = wps_info
                    if checks_info:
                        st.session_state.safety_checks = checks_info
                    st.success(f"✅ Imported mission package '**{st.session_state.mission_name}**' successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to parse mission JSON: {e}")

        st.markdown(f"""
            <div class="uav-card uav-card-accent">
                <div class="uav-card-title">🤖 Option A: Natural Language Request</div>
                <div style="font-size:0.85rem;color:{box_text};margin-bottom:0.5rem">
                    Enter mission details in plain English and let the AI Agent extract the parameters.
                    {'<span style="color:#FBD38D;font-size:0.8rem">⚠️ Using regex fallback (Gemini unavailable)</span>' if not GENAI_AVAILABLE else '<span style="color:#68D391;font-size:0.8rem">✅ Gemini AI active</span>'}
                </div>
            </div>
        """, unsafe_allow_html=True)

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
            with st.status("🤖 Extracting mission parameters with AI Agent...", expanded=True) as status_box:
                status_box.update(label="Parsing prompt string & identifying entities...")
                extracted = understand_mission(prompt)
                
                status_box.update(label="Applying extracted telemetry parameters...")
                st.session_state.mission_name = extracted.get("mission_name", "FAST Surveillance")
                st.session_state.mission_type = extracted.get("mission_type", "surveillance")
                st.session_state.altitude = float(extracted.get("altitude", 50.0))
                st.session_state.duration = float(extracted.get("duration", 15.0))
                st.session_state.pattern = extracted.get(
                    "route_pattern", extracted.get("pattern", "square")
                )
                st.session_state.nl_extracted = extracted
                
                status_box.update(label="✅ Extraction complete!", state="complete")
            st.success("✅ Parameters extracted and applied!")

        if st.session_state.nl_extracted:
            ex = st.session_state.nl_extracted
            st.markdown(f"""
                <div class="uav-card uav-card-accent" style="margin-top:0.6rem">
                    <div style="font-size:0.8rem;font-weight:700;color:{box_text};margin-bottom:0.5rem">🔍 Extracted Parameters</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 16px;font-size:0.82rem;color:{box_text}">
                        <div><b>Name:</b> {ex.get('mission_name', 'N/A')}</div>
                        <div><b>Type:</b> {ex.get('mission_type', 'N/A')}</div>
                        <div><b>Altitude:</b> {ex.get('altitude', 'N/A')} m</div>
                        <div><b>Duration:</b> {ex.get('duration', 'N/A')} min</div>
                        <div><b>Pattern:</b> {ex.get('route_pattern', ex.get('pattern', 'N/A'))}</div>
                        <div><b>RTL:</b> {'Yes' if ex.get('return_to_launch', True) else 'No'} <span style="font-size:0.72rem;color:{caption_col}">(Return to Launch)</span></div>
                        <div><b>Avoid NFZ:</b> {'Yes' if ex.get('avoid_no_fly_zone', True) else 'No'} <span style="font-size:0.72rem;color:{caption_col}">(No-Fly Zone)</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("✖ Clear AI Extraction", key="clear_nl_extracted", type="secondary", help="Dismiss the extracted parameters card and use manual values only."):
                st.session_state.nl_extracted = None
                st.rerun()

        st.markdown("<hr style='border:1px solid #2A2A44;margin:1.2rem 0'>", unsafe_allow_html=True)

        st.markdown("""
            <div class="uav-card uav-card-gradient-top">
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
            lat_val = st.number_input(
                "Home Latitude", value=st.session_state.home_lat, format="%.6f",
                help="Latitude of the takeoff / launch point (decimal degrees, e.g. 33.642500)."
            )
            if lat_val < -90 or lat_val > 90:
                st.error("❌ Latitude must be between -90 and 90 degrees.")
            else:
                st.session_state.home_lat = lat_val

            lon_val = st.number_input(
                "Home Longitude", value=st.session_state.home_lon, format="%.6f",
                help="Longitude of the takeoff / launch point (decimal degrees, e.g. 73.023200)."
            )
            if lon_val < -180 or lon_val > 180:
                st.error("❌ Longitude must be between -180 and 180 degrees.")
            else:
                st.session_state.home_lon = lon_val

        # Reset button
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            from config.settings import MISSION_DEFAULTS
            st.session_state.mission_name = MISSION_DEFAULTS["name"]
            st.session_state.mission_type = MISSION_DEFAULTS["type"]
            st.session_state.altitude = MISSION_DEFAULTS["altitude"]
            st.session_state.duration = MISSION_DEFAULTS["duration"]
            st.session_state.pattern = MISSION_DEFAULTS["pattern"]
            st.session_state.home_lat = MISSION_DEFAULTS["home_lat"]
            st.session_state.home_lon = MISSION_DEFAULTS["home_lon"]
            st.session_state.generated_waypoints = []
            st.session_state.safety_checks = []
            st.session_state.corrections = []
            st.session_state.nl_extracted = None
            st.success("✅ All parameters reset to defaults.")
            st.rerun()

    # Page 3: Mission Plan
    elif st.session_state.current_page == "Mission Plan":
        st.subheader("⚙️ Mission Route Planner")

        st.markdown(f"""
            <div class="uav-card uav-card-gradient-top">
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

        with st.expander("📐 Route Pattern Dimensions & Geometry Options", expanded=False):
            dim_col1, dim_col2 = st.columns(2)
            with dim_col1:
                st.session_state.square_side = st.slider(
                    "Square Side Length (m)", 20.0, 500.0, st.session_state.square_side,
                    help="Side length for Square patrol geometry."
                )
                st.session_state.grid_step = st.slider(
                    "Grid Scan Step Spacing (m)", 10.0, 200.0, st.session_state.grid_step,
                    help="Step spacing distance for Grid lawn-mower mapping scan."
                )
            with dim_col2:
                st.session_state.perim_offset = st.slider(
                    "Perimeter Boundary Offset (m)", 10.0, 300.0, st.session_state.perim_offset,
                    help="Offset distance for Perimeter boundary trace."
                )
                st.session_state.circle_radius = st.slider(
                    "Circle Orbit Radius (m)", 10.0, 300.0, st.session_state.circle_radius,
                    help="Radial distance for Circle orbit pattern."
                )

        if st.button("⚡ Generate Waypoint Trajectory", use_container_width=True):
            # Auto-generate a unique timestamped name if default name is used
            if st.session_state.mission_name == "FAST Surveillance":
                stamp = datetime.now().strftime("%Y%m%d_%H%M")
                st.session_state.mission_name = f"Surveillance_{st.session_state.pattern.upper()}_{stamp}"

            with st.status("⚙️ Generating Flight Trajectory & Auditing Airspace Safety...", expanded=True) as status_box:
                status_box.update(label="Computing pattern coordinates & geometry...")
                dims = {
                    "square_side": st.session_state.square_side,
                    "grid_step": st.session_state.grid_step,
                    "perim_offset": st.session_state.perim_offset,
                    "circle_radius": st.session_state.circle_radius,
                }
                wps = generate_waypoints(
                    st.session_state.home_lat, st.session_state.home_lon,
                    st.session_state.altitude, st.session_state.pattern,
                    dimensions=dims
                )
                
                status_box.update(label="Auditing 7 airspace safety compliance regulations...")
                meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
                safety_checks = perform_safety_checks(meta, wps)
                
                status_box.update(label="Applying compliance correction heuristics...")
                suggestions, corrected_meta, corrected_wps = generate_corrections(
                    safety_checks, meta, wps
                )
                
                status_box.update(label="Updating session state and map boundary vectors...")
                st.session_state.generated_waypoints = corrected_wps
                st.session_state.safety_checks = safety_checks
                st.session_state.corrections = suggestions
                
                st.session_state.altitude = corrected_meta.get("altitude", st.session_state.altitude)
                st.session_state.duration = corrected_meta.get("duration", st.session_state.duration)
                
                _, bounds = create_mission_map(
                    corrected_wps,
                    (st.session_state.home_lat, st.session_state.home_lon),
                    dark_map=is_dark
                )
                st.session_state.map_bounds = bounds
                status_box.update(label="✅ Trajectory and safety audit complete!", state="complete")

            st.success(f"✅ Generated {len(corrected_wps)} waypoints - navigate to Map View to see the route.")

        if st.session_state.generated_waypoints:
            st.markdown(f"### 📍 Interactive Waypoint Editor (`{len(st.session_state.generated_waypoints)}` Points)")
            st.caption("You can edit waypoint values directly in the table below and re-audit safety compliance.")
            
            df_wp = pd.DataFrame(st.session_state.generated_waypoints)
            edited_df = st.data_editor(
                df_wp,
                use_container_width=True,
                height=min(320, 42 + len(df_wp) * 35),
                key="waypoint_table_editor",
                column_config={
                    "sequence_no": st.column_config.NumberColumn("Seq #",     format="%d",    width="small"),
                    "latitude":    st.column_config.NumberColumn("Latitude",  format="%.6f"),
                    "longitude":   st.column_config.NumberColumn("Longitude", format="%.6f"),
                    "altitude":    st.column_config.NumberColumn("Alt (m)",   format="%.1f",  width="small"),
                    "action":      st.column_config.SelectboxColumn("Action", width="small",
                                       options=["takeoff", "waypoint", "rtl", "land"]),
                }
            )

            if st.button("✏️ Apply Waypoint Edits & Re-Audit Safety", use_container_width=True):
                updated_wps = edited_df.to_dict('records')
                # Ensure correct types for updated waypoints
                for wp in updated_wps:
                    wp["sequence_no"] = int(wp.get("sequence_no", 0))
                    wp["latitude"] = float(wp.get("latitude", st.session_state.home_lat))
                    wp["longitude"] = float(wp.get("longitude", st.session_state.home_lon))
                    wp["altitude"] = float(wp.get("altitude", st.session_state.altitude))
                    wp["action"] = str(wp.get("action", "waypoint"))

                meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
                safety_checks = perform_safety_checks(meta, updated_wps)
                suggestions, corrected_meta, corrected_wps = generate_corrections(
                    safety_checks, meta, updated_wps
                )

                st.session_state.generated_waypoints = corrected_wps
                st.session_state.safety_checks = safety_checks
                st.session_state.corrections = suggestions
                
                _, bounds = create_mission_map(
                    corrected_wps,
                    (st.session_state.home_lat, st.session_state.home_lon),
                    dark_map=is_dark
                )
                st.session_state.map_bounds = bounds
                st.success("✅ Waypoint modifications saved and safety checks updated!")
                st.rerun()

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
            <div class="uav-card uav-card-accent">
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
            st.markdown(f"<div style='font-weight:700;color:{box_text};font-size:0.95rem;margin-bottom:0.4rem'>Waypoint Sequence List ({len(st.session_state.generated_waypoints)} Points):</div>", unsafe_allow_html=True)
            df_map = pd.DataFrame(st.session_state.generated_waypoints)
            st.dataframe(
                df_map,
                use_container_width=True,
                height=min(350, 38 + len(df_map) * 35),
                column_config={
                    "sequence_no": st.column_config.NumberColumn("Seq #", format="%d", width="small"),
                    "latitude":    st.column_config.NumberColumn("Latitude",  format="%.6f"),
                    "longitude":   st.column_config.NumberColumn("Longitude", format="%.6f"),
                    "altitude":    st.column_config.NumberColumn("Alt (m)",   format="%.1f", width="small"),
                    "action":      st.column_config.TextColumn("Action", width="small"),
                }
            )
        else:
            st.info("No waypoints generated yet. Go to Mission Plan to generate waypoints first.")

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
                st.rerun()
        else:
            st.warning("⚠️ No safety checks available. Please generate waypoints on the **Mission Plan** page first.")

    # Page 6: Suggestions
    elif st.session_state.current_page == "Suggestions":
        st.subheader("💡 Correction Suggestions Agent")

        if st.session_state.corrections:
            st.write("The Correction Agent generated the following actionable fixes:")
            for i, corr in enumerate(st.session_state.corrections, 1):
                st.markdown(f"""
                    <div class="uav-card uav-card-accent">
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
                <div class="uav-card uav-card-gradient-top">
                    <div style="font-size:0.95rem;color:{box_text}">
                        <b>Mission Package:</b> {mission_meta['mission_name']} &nbsp;|&nbsp; 
                        <b>Status:</b> <span style="color:{'#10B981' if mission_meta['status']=='Safe' else '#EF4444'};font-weight:700">{mission_meta['status']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='font-size:0.9rem;font-weight:700;margin-top:0.8rem;margin-bottom:0.4rem'>📄 Standard Mission Reports & Telemetry:</div>", unsafe_allow_html=True)
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
                    "⬇️  Download PDF Report",
                    data=pdf_bytes, file_name="mission_report.pdf", mime="application/pdf",
                    use_container_width=True
                )

            st.markdown("<div style='font-size:0.9rem;font-weight:700;margin-top:1.2rem;margin-bottom:0.4rem'>🚁 Industry GCS & GIS Mission Package Exports:</div>", unsafe_allow_html=True)
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                qgc_str = export_qgroundcontrol_plan(mission_meta, st.session_state.generated_waypoints)
                st.download_button(
                    "🛸 QGroundControl (.plan)",
                    data=qgc_str, file_name="mission.plan", mime="application/json",
                    use_container_width=True,
                    help="Native QGroundControl mission plan format for PX4/ArduPilot."
                )
            with col_g2:
                ardupilot_str = export_ardupilot_waypoints(st.session_state.generated_waypoints)
                st.download_button(
                    "✈️ ArduPilot (.waypoints)",
                    data=ardupilot_str, file_name="mission.waypoints", mime="text/plain",
                    use_container_width=True,
                    help="Mission Planner QGC WPL 110 waypoints file for ArduPilot flight controllers."
                )
            with col_g3:
                kml_str = export_kml_format(mission_meta, st.session_state.generated_waypoints)
                st.download_button(
                    "🌍 Google Earth (.kml)",
                    data=kml_str, file_name="mission.kml", mime="application/vnd.google-earth.kml+xml",
                    use_container_width=True,
                    help="3D trajectory vector file for Google Earth GIS visualization."
                )

        else:
            st.warning("⚠️ No waypoints generated yet. Complete Mission Plan before exporting.")

    # Page 8: Mission History
    elif st.session_state.current_page == "Mission History":
        st.subheader("📂 Mission History & Database")
        st.caption("Browse, search, filter, sort, export, clone, and delete saved missions from the local SQLite database.")

        # ── JSON Mission Import Section ─────────────────────────────────────
        with st.expander("📥 Import Saved Mission JSON", expanded=False):
            st.markdown("Upload a single or batch mission JSON file to restore into the database.")
            uploaded_file = st.file_uploader("Choose a mission JSON file", type=["json"], key="import_mission_uploader")
            if uploaded_file is not None:
                if st.button("✅ Import to Database", key="btn_confirm_import", use_container_width=True):
                    try:
                        content = uploaded_file.read().decode("utf-8")
                        imported_ids = import_mission_from_json(content)
                        st.success(f"Successfully imported {len(imported_ids)} mission(s) into database! (IDs: {imported_ids})")
                        st.rerun()
                    except Exception as ie:
                        st.error(f"Import failed: {ie}")

        # ── Filters Wrapper (Scoped CSS) ───────────────────────────────────
        st.markdown('<div class="history-filter-bar">', unsafe_allow_html=True)
        filt_col1, filt_col2, filt_col3 = st.columns([2, 1, 1])
        with filt_col1:
            name_search = st.text_input(
                "🔍 Name", "", placeholder="Type mission name...",
                help="Case-insensitive substring search on mission name."
            )
        with filt_col2:
            status_filter = st.selectbox(
                "🛡️ Status", ["All", "Safe", "Unsafe", "Needs Revision"],
                help="Filter missions by safety compliance status."
            )
        with filt_col3:
            type_filter = st.selectbox(
                "✈️ Type", ["All", "surveillance", "mapping", "search_rescue", "inspection"],
                help="Filter missions by operational type."
            )

        filt_col4, filt_col5, filt_col6, filt_col7 = st.columns([1, 1, 1, 1])
        with filt_col4:
            date_from = st.date_input(
                "📅 From", value=None, help="Show missions on or after this date."
            )
        with filt_col5:
            date_to = st.date_input(
                "📅 To", value=None, help="Show missions on or before this date."
            )
        with filt_col6:
            sort_by = st.selectbox(
                "🔃 Sort",
                ["created_at", "mission_name", "altitude", "duration", "status"],
                index=0,
                help="Column used to sort the results."
            )
        with filt_col7:
            sort_dir_choice = st.selectbox(
                "↕️ Order",
                ["DESC (Newest)", "ASC (Oldest)"],
                index=0,
                help="Newest first (DESC) or oldest first (ASC)."
            )
            sort_dir = "DESC" if "DESC" in sort_dir_choice else "ASC"
        st.markdown('</div>', unsafe_allow_html=True)

        date_from_str = date_from.strftime("%Y-%m-%d") if date_from else ""
        date_to_str   = date_to.strftime("%Y-%m-%d")   if date_to   else ""

        missions_list = search_missions(
            name_search, status_filter, type_filter,
            date_from_str, date_to_str, sort_by, sort_dir
        )

        # ── Batch Export (Optimized 2-query batch function) ─────────────────
        if missions_list:
            batch_json = export_filtered_missions_batch_json(missions_list)
            st.download_button(
                label=f"⬇️ Export All {len(missions_list)} Mission(s) as JSON",
                data=batch_json,
                file_name=f"all_missions_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                help="Download all currently filtered missions as a single JSON file.",
                key="export_all_missions_btn"
            )

        if not missions_list:
            st.info("No saved missions found. Complete a mission and click **Save Mission to Database** on the Safety Check page.")
        else:
            # ── Pagination & Bounds Sanitization ───────────────────────────
            p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
                page_size_val = st.selectbox("Items per page", [10, 20, 50, "All"], index=0, key="hist_page_size")

            total_missions = len(missions_list)
            if page_size_val == "All":
                page_size = max(1, total_missions)
            else:
                page_size = int(page_size_val)

            total_pages = max(1, (total_missions + page_size - 1) // page_size)

            current_p = st.session_state.get("page_number", 1)
            if current_p > total_pages:
                st.session_state["page_number"] = 1
                current_p = 1

            if total_pages > 1:
                with p_col2:
                    page_number = st.selectbox("Page", range(1, total_pages + 1), key="page_number")
                start_idx = (page_number - 1) * page_size
                end_idx = min(start_idx + page_size, total_missions)
                page_missions = missions_list[start_idx:end_idx]
            else:
                page_missions = missions_list

            st.markdown(
                f"<div style='font-size:0.82rem;color:{caption_col};margin-bottom:0.5rem'>"
                f"Showing <b>{len(page_missions)}</b> of <b>{total_missions}</b> mission(s)</div>",
                unsafe_allow_html=True
            )

            # ── Mission Cards ─────────────────────────────────────────────────
            for m_row in page_missions:
                mid       = m_row["mission_id"]
                m_status  = m_row.get("status", "")
                wp_count  = get_mission_waypoint_count(mid)
                status_color    = "#10B981" if m_status == "Safe" else ("#EF4444" if m_status == "Unsafe" else "#F59E0B")
                status_badge_bg = "rgba(16,185,129,0.14)" if m_status == "Safe" else ("rgba(239,68,68,0.14)" if m_status == "Unsafe" else "rgba(245,158,11,0.14)")
                status_icon     = "🟢" if m_status == "Safe" else ("🔴" if m_status == "Unsafe" else "⚠️")

                expander_label = (
                    f"{status_icon} Mission #{mid} : {m_row['mission_name']}  "
                    f"[{m_status.upper()}]  |  {m_row['altitude']}m alt  •  {m_row['duration']}min duration  •  {wp_count} WPs"
                )

                with st.expander(expander_label, expanded=False):
                    detail_col1, detail_col2 = st.columns([3, 2])

                    with detail_col1:
                        # ── Telemetry card ────────────────────────────────
                        st.markdown(f"""
                            <div style="background:{box_bg};border:1px solid {border_col};border-radius:10px;padding:0.85rem 1.1rem;margin-bottom:0.6rem;box-shadow:0 2px 8px rgba(0,0,0,0.06);word-break:break-word;overflow-wrap:anywhere;">
                                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.7rem;padding-bottom:0.4rem;border-bottom:1px solid {border_col}">
                                    <span style="font-weight:800;font-size:0.88rem;color:#00C6FF">📋 Mission #{mid} Telemetry & Specs</span>
                                    <span style="background:{status_badge_bg};color:{status_color};padding:2px 10px;border-radius:12px;font-size:0.75rem;font-weight:800;border:1px solid {status_color}33">
                                        {'✅ SAFE' if m_status == 'Safe' else '🔴 ' + m_status.upper()}
                                    </span>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;font-size:0.82rem;color:{box_text};line-height:1.4">
                                    <div><span style="color:{caption_col};font-weight:600;font-size:0.74rem">🏷️ MISSION NAME</span><br><b style="color:{box_text};font-size:0.88rem">{m_row['mission_name']}</b></div>
                                    <div><span style="color:{caption_col};font-weight:600;font-size:0.74rem">🎯 FLIGHT TYPE</span><br><b style="color:{box_text};font-size:0.88rem">{m_row['mission_type'].title()}</b></div>
                                    <div><span style="color:{caption_col};font-weight:600;font-size:0.74rem">📐 CRUISE ALTITUDE</span><br><b style="color:{box_text};font-size:0.88rem">{m_row['altitude']} m</b></div>
                                    <div><span style="color:{caption_col};font-weight:600;font-size:0.74rem">⏱️ MAX DURATION</span><br><b style="color:{box_text};font-size:0.88rem">{m_row['duration']} min</b></div>
                                    <div><span style="color:{caption_col};font-weight:600;font-size:0.74rem">📍 WAYPOINTS</span><br><b style="color:{box_text};font-size:0.88rem">{wp_count} points</b></div>
                                    <div><span style="color:{caption_col};font-weight:600;font-size:0.74rem">🛡️ SAFETY AUDIT</span><br><b style="color:{status_color};font-size:0.88rem">{m_status}</b></div>
                                    <div style="grid-column:1/-1"><span style="color:{caption_col};font-weight:600;font-size:0.74rem">📅 RECORDED DATE</span><br><b style="color:{box_text};font-size:0.82rem">{m_row['created_at']}</b></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # ── Safety Check Detailed Breakdown Table ────────────────
                        try:
                            _, _, m_checks_detail = get_mission_by_id(mid)
                            if m_checks_detail:
                                with st.expander(f"🛡️ Safety Audit Breakdown ({len(m_checks_detail)} rules evaluated)", expanded=False):
                                    checks_df = pd.DataFrame(m_checks_detail)[["check_name", "result", "message"]]
                                    st.dataframe(
                                        checks_df,
                                        use_container_width=True,
                                        column_config={
                                            "check_name": st.column_config.TextColumn("Rule Name", width="medium"),
                                            "result": st.column_config.TextColumn("Status", width="small"),
                                            "message": st.column_config.TextColumn("Audit Log Details", width="large"),
                                        }
                                    )
                        except Exception:
                            pass

                        # ── Inline Waypoint Table ─────────────────────
                        if wp_count > 0:
                            try:
                                _, m_wps_preview, _ = get_mission_by_id(mid)
                                st.markdown(
                                    f"<div style='font-size:0.8rem;font-weight:700;color:{caption_col};"
                                    f"margin-bottom:0.3rem'>📍 Waypoint Sequence ({wp_count} points):</div>",
                                    unsafe_allow_html=True
                                )
                                df_preview = pd.DataFrame(m_wps_preview)[["sequence_no", "latitude", "longitude", "altitude", "action"]]
                                st.dataframe(
                                    df_preview,
                                    use_container_width=True,
                                    height=min(220, 38 + len(df_preview) * 35),
                                    column_config={
                                        "sequence_no": st.column_config.NumberColumn("Seq #",    format="%d",    width="small"),
                                        "latitude":    st.column_config.NumberColumn("Lat",      format="%.6f"),
                                        "longitude":   st.column_config.NumberColumn("Lon",      format="%.6f"),
                                        "altitude":    st.column_config.NumberColumn("Alt (m)",  format="%.1f", width="small"),
                                        "action":      st.column_config.TextColumn("Action",    width="small"),
                                    }
                                )
                            except Exception as _e:
                                st.caption(f"Could not load waypoints: {_e}")

                    with detail_col2:
                        st.markdown(
                            f"<div style='font-size:0.8rem;font-weight:700;color:{caption_col};margin-bottom:0.4rem'>⚡ Actions & Controls</div>",
                            unsafe_allow_html=True
                        )

                        # ── Map Preview Action Button ──────────────────────
                        is_currently_previewing = (st.session_state.get("history_preview_id") == mid)
                        if is_currently_previewing:
                            if st.button(f"⏹️ Stop Map Preview", key=f"preview_stop_{mid}", use_container_width=True):
                                st.session_state.history_preview_id = None
                                st.session_state.history_preview_name = ""
                                st.session_state.history_preview_waypoints = []
                                st.rerun()
                        else:
                            if st.button(f"👁️ Preview on Map #{mid}", key=f"preview_start_{mid}", use_container_width=True, help="Display this mission route on the right-hand map visualizer."):
                                try:
                                    _, m_wps_prev, _ = get_mission_by_id(mid)
                                    st.session_state.history_preview_id = mid
                                    st.session_state.history_preview_name = m_row['mission_name']
                                    st.session_state.history_preview_waypoints = m_wps_prev
                                    st.rerun()
                                except Exception as pe:
                                    st.error(f"Failed to preview map: {pe}")

                        # ── Load Mission ─────────────────────────────────
                        if st.button(f"📂 Load Mission #{mid}", key=f"load_mission_{mid}",
                                     use_container_width=True,
                                     help="Load this mission into the active planning session."):
                            try:
                                m_data, m_wps, m_checks = get_mission_by_id(mid)
                                st.session_state.mission_name         = m_data["mission_name"]
                                st.session_state.mission_type         = m_data["mission_type"]
                                st.session_state.altitude             = float(m_data["altitude"])
                                st.session_state.duration             = float(m_data["duration"])
                                st.session_state.generated_waypoints  = m_wps
                                st.session_state.safety_checks        = m_checks
                                st.session_state.corrections          = []
                                st.session_state.nl_extracted         = None
                                st.session_state.current_page         = "Mission Plan"
                                st.success(f"Mission '{m_data['mission_name']}' loaded.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error loading mission: {e}")

                        # ── Clone Mission ─────────────────────────────
                        with st.popover(f"🗂️ Clone Mission #{mid}", use_container_width=True):
                            st.markdown(f"**Clone Mission #{mid}**: create a duplicate you can edit independently.")
                            clone_name = st.text_input(
                                "New Mission Name",
                                value=f"{m_row['mission_name']}_Copy",
                                key=f"clone_name_{mid}"
                            )
                            if st.button(f"✅ Create Clone", key=f"confirm_clone_{mid}", use_container_width=True):
                                try:
                                    new_id = clone_mission(mid, clone_name)
                                    st.success(f"✅ Cloned as Mission #{new_id}: '{clone_name}'")
                                    st.rerun()
                                except Exception as ce:
                                    st.error(f"Clone failed: {ce}")

                        # ── Delete Mission ───────────────────────────────
                        with st.popover(f"🗑️ Delete Mission #{mid}", use_container_width=True):
                            st.warning(f"Permanently delete mission #{mid}?")
                            if st.button(f"Yes, Delete #{mid}", key=f"confirm_delete_{mid}", use_container_width=True):
                                from utils.database_utils import delete_mission
                                delete_mission(mid)
                                if st.session_state.get("history_preview_id") == mid:
                                    st.session_state.history_preview_id = None
                                    st.session_state.history_preview_name = ""
                                    st.session_state.history_preview_waypoints = []
                                st.success(f"Mission #{mid} deleted.")
                                st.rerun()

                        # ── Compact Per-Mission Export Popover ─────────────
                        with st.popover(f"📤 Export Mission #{mid}...", use_container_width=True):
                            st.markdown(f"**Export Mission #{mid} Formats:**")
                            try:
                                _md, _mw, _mc = get_mission_by_id(mid)
                                _meta = {
                                    "mission_name": _md["mission_name"],
                                    "mission_type": _md["mission_type"],
                                    "altitude":     _md["altitude"],
                                    "duration":     _md["duration"],
                                    "status":       _md.get("status", "Unknown"),
                                    "created_at":   _md.get("created_at", ""),
                                }
                                _fn = _md["mission_name"].replace(" ", "_")[:40]

                                st.download_button(
                                    "⬇️ JSON Format",
                                    data=export_mission_json(_meta, _mw, _mc),
                                    file_name=f"{_fn}.json", mime="application/json",
                                    use_container_width=True, key=f"exp_json_{mid}"
                                )
                                st.download_button(
                                    "⬇️ CSV Waypoints",
                                    data=export_waypoints_csv(_mw),
                                    file_name=f"{_fn}_waypoints.csv", mime="text/csv",
                                    use_container_width=True, key=f"exp_csv_{mid}"
                                )
                                st.download_button(
                                    "🛸 QGroundControl (.plan)",
                                    data=export_qgroundcontrol_plan(_meta, _mw),
                                    file_name=f"{_fn}.plan", mime="application/json",
                                    use_container_width=True, key=f"exp_plan_{mid}"
                                )
                                st.download_button(
                                    "✈️ ArduPilot (.waypoints)",
                                    data=export_ardupilot_waypoints(_mw),
                                    file_name=f"{_fn}.waypoints", mime="text/plain",
                                    use_container_width=True, key=f"exp_wp_{mid}"
                                )
                                st.download_button(
                                    "🌍 Google Earth (.kml)",
                                    data=export_kml_format(_meta, _mw),
                                    file_name=f"{_fn}.kml",
                                    mime="application/vnd.google-earth.kml+xml",
                                    use_container_width=True, key=f"exp_kml_{mid}"
                                )
                            except Exception as _ex:
                                st.caption(f"Export unavailable: {_ex}")


with col_right:
    is_history_preview = (
        st.session_state.current_page == "Mission History"
        and st.session_state.get("history_preview_id") is not None
        and len(st.session_state.get("history_preview_waypoints", [])) > 0
    )

    if is_history_preview:
        map_waypoints = st.session_state.history_preview_waypoints
        preview_mid = st.session_state.history_preview_id
        preview_name = st.session_state.history_preview_name

        st.markdown(f"""
            <div style="background-color:{box_bg};border:1px solid #00C6FF;border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between">
                <span style="font-weight:700;color:#00C6FF;font-size:0.95rem">🗺️ Map Preview: Mission #{preview_mid} - {preview_name}</span>
                <span style="font-size:0.78rem;background:rgba(0,198,255,0.2);color:#00C6FF;padding:3px 8px;border-radius:6px;font-weight:600">HISTORICAL PREVIEW</span>
            </div>
        """, unsafe_allow_html=True)
        if st.button("⏹️ Reset Map to Active Session", key="clear_map_preview_btn", use_container_width=True):
            st.session_state.history_preview_id = None
            st.session_state.history_preview_name = ""
            st.session_state.history_preview_waypoints = []
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background-color:{box_bg};border:1px solid {border_col};border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between">
                <span style="font-weight:700;color:{box_text};font-size:1rem">🗺️ Live GCS Mission Radar & Airspace</span>
                <span style="font-size:0.78rem;background:{map_badge_bg};color:{map_badge_fg};padding:3px 8px;border-radius:6px;font-weight:600">{map_badge_text}</span>
            </div>
        """, unsafe_allow_html=True)
        map_waypoints = st.session_state.generated_waypoints

    m, map_bounds_live = create_mission_map(
        map_waypoints,
        (st.session_state.home_lat, st.session_state.home_lon),
        dark_map=is_dark
    )
    active_bounds = st.session_state.map_bounds or map_bounds_live
    if active_bounds:
        min_lat, min_lon, max_lat, max_lon = active_bounds
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    st_folium(
        m,
        use_container_width=True,
        height=620,
        key=f"gcs_map_{len(map_waypoints)}_{st.session_state.theme}_{st.session_state.get('history_preview_id', 'active')}"
    )