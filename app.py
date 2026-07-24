import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_folium import st_folium

# Configure streamlit page settings (MUST be the first command)
st.set_page_config(
    page_title="Agentic UAV Mission Planner",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Contrast Theme CSS (Black Page Background, White Page Text, White Boxes, Black Box Text, White Map)
st.markdown("""
    <style>
    /* Reset & Box Sizing */
    * {
        box-sizing: border-box !important;
    }
    
    /* Root Page Background - Pure Black & White Default Page Text */
    body, .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
    }

    /* Hide Header Toolbar & eliminate top gap */
    header[data-testid="stHeader"], [data-testid="stHeader"], .stAppHeader {
        display: none !important;
        height: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    /* Page Bounding Container - Minimized top gap */
    .block-container, [data-testid="stMainBlockContainer"] {
        padding-top: 0.4rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        max-width: 100% !important;
    }

    /* Top Title Spacing */
    .stApp h1, h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }

    /* Sidebar - Black Background & White Navigation Labels with zero top gap */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #222222 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
    section[data-testid="stSidebar"] header {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        height: auto !important;
        min-height: 0px !important;
    }
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: #FFFFFF !important;
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }

    /* Form & Input Field Labels - Crisp White Text for Max Visibility */
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
    .stCheckbox label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Slider values & min/max numbers readability */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"],
    .stSlider div[data-testid="stMarkdownContainer"] p,
    .stSlider span,
    div[data-testid="stSliderTickBar"] * {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }

    /* Captions globally across main page and sidebar - Crisp Light Gray Text */
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *, section[data-testid="stSidebar"] caption, caption, small {
        color: #E2E8F0 !important;
        font-weight: 500 !important;
    }

    /* Sidebar Navigation Buttons */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #0F0F0F !important;
        color: #FFFFFF !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.55rem 0.9rem !important;
        margin-bottom: 0.25rem !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: #1A1A1A !important;
        border-color: #0072FF !important;
        color: #0072FF !important;
        transform: translateX(3px);
    }

    /* Global Typography Outside Boxes - Crisp White Text */
    .stApp > div h1, .stApp > div h2, .stApp > div h3, .stApp > div h4, .stApp > div h5, .stApp > div h6 {
        color: #FFFFFF !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
    }

    /* Telemetry HUD Metrics Cards - WHITE BOX BACKGROUND & BLACK TEXT, COMPACT SIZE */
    div[data-testid="stMetric"],
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        padding: 0.45rem 0.75rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        overflow: hidden !important;
        min-width: 0 !important;
    }
    div[data-testid="stMetric"] *,
    [data-testid="stMetric"] *,
    [data-testid="stMetricValue"], 
    [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] div,
    div[data-testid="stMetric"] span,
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] p {
        color: #000000 !important;
    }
    /* Shrink HUD metric value font size */
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        line-height: 1.2 !important;
    }

    /* Streamlit Alert Boxes (st.info, st.warning, st.error, st.success, st.sidebar.info) - WHITE BOX BACKGROUND & BLACK TEXT */
    div[data-testid="stAlert"],
    .stAlert,
    div[data-baseweb="notification"],
    div[kind="info"],
    div[kind="warning"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stAlert"] *,
    .stAlert *,
    div[data-baseweb="notification"] *,
    div[kind="info"] *,
    div[kind="warning"] * {
        color: #000000 !important;
    }

    /* Primary Action Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.55rem 1.25rem !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 16px rgba(0, 198, 255, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 6px 22px rgba(0, 198, 255, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }

    /* Download Buttons */
    div.stDownloadButton > button {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #0072FF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stDownloadButton > button:hover {
        background: #0072FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(0, 114, 255, 0.3) !important;
    }

    /* Form Controls & Input Boxes - WHITE BOX BACKGROUND & BLACK TEXT */
    div[data-baseweb="input"], div[data-baseweb="select"], textarea, input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    textarea:focus, input:focus, div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #0072FF !important;
        box-shadow: 0 0 0 2px rgba(0, 114, 255, 0.2) !important;
    }
    
    /* Select Dropdown Popups - WHITE BOX BACKGROUND & BLACK TEXT */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CBD5E1 !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #F1F5F9 !important;
        color: #0072FF !important;
    }

    /* Dataframe Container & Table - WHITE BOX BACKGROUND & BLACK TEXT */
    .dataframe, [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
    }
    .dataframe th, [data-testid="stDataFrame"] th {
        background-color: #F8FAFC !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    .dataframe td, [data-testid="stDataFrame"] td {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Slider Styling */
    .stSlider label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Custom Card Containers - WHITE BOX BACKGROUND & BLACK TEXT */
    .uav-card {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        color: #000000 !important;
    }
    .uav-card *,
    .uav-card-title,
    .uav-card-title * {
        color: #000000 !important;
    }

    /* Map Background Container - WHITE BACKGROUND */
    .leaflet-container {
        background-color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Imports from local modules
from agents.mission_understanding_agent import understand_mission
from agents.waypoint_planner_agent import generate_waypoints
from agents.safety_compliance_agent import perform_safety_checks
from agents.correction_agent import generate_corrections
from utils.map_utils import create_mission_map
from utils.database_utils import save_mission, init_db
from utils.export_utils import export_mission_json, export_waypoints_csv, generate_pdf_report
from agents.report_agent import generate_mission_summary_html

# Initialize database
init_db()

# Session state defaults (prevent reload reset)
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

# Navigation pages (matches brief Section 14)
pages = ["Home", "Mission Input", "Mission Plan", "Map View", "Safety Check", "Suggestions", "Export"]

# Ensure current page is valid
if st.session_state.current_page not in pages:
    st.session_state.current_page = "Home"

# Sidebar navigation
st.sidebar.title("🛸 UAV Mission Planner")
st.sidebar.caption("Agentic AI Airspace Planner & Auditor")
st.sidebar.markdown("<hr style='border:1px solid #E2E8F0;margin:0.5rem 0 1rem 0'>", unsafe_allow_html=True)

for page in pages:
    is_active = (st.session_state.current_page == page)
    label = f"▶️ {page}" if is_active else f"   {page}"
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.current_page = page

st.sidebar.markdown("<hr style='border:1px solid #E2E8F0;margin:1rem 0'>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size:0.78rem;color:#AAAAAA;text-align:center;padding:0.3rem 0'>💡 Powered by Google Gemini AI</div>", unsafe_allow_html=True)

# Global header
st.title("🛸 Agentic UAV Mission Planner")

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

st.markdown("<hr style='border:1px solid #E2E8F0;margin:0.8rem 0 1.2rem 0'>", unsafe_allow_html=True)

# Create GCS split-screen layout (12:12 balanced split)
col_left, col_right = st.columns([12, 12], gap="large")

with col_left:
    # Page 1: Home
    if st.session_state.current_page == "Home":
        st.subheader("🏠 Ground Control Station Dashboard")
        st.caption("AI-driven mission planning system: generate waypoints, enforce safety rules, and export mission plans.")
        
        st.markdown("""
            <div class="uav-card" style="margin-top:0.4rem;margin-bottom:0.6rem;padding:0.85rem 1.1rem">
                <div class="uav-card-title" style="margin-bottom:0.4rem;font-size:0.9rem">🛡️ Active Airspace Safety Regulations</div>
                <ul style="margin-bottom:0;padding-left:1.1rem;font-size:0.82rem;color:#000000;line-height:1.55">
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

        st.markdown("""
            <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-top:1rem">
                <div class="uav-card" style="margin-bottom:0;padding:1rem">
                    <div style="color:#000000;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem">1️⃣ Mission Input</div>
                    <div style="font-size:0.83rem;color:#000000">Describe mission in natural language or fill out parameters manually.</div>
                </div>
                <div class="uav-card" style="margin-bottom:0;padding:1rem">
                    <div style="color:#000000;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem">2️⃣ Mission Plan</div>
                    <div style="font-size:0.83rem;color:#000000">Generate 4 flight patterns with automatic takeoff & RTL points.</div>
                </div>
                <div class="uav-card" style="margin-bottom:0;padding:1rem">
                    <div style="color:#000000;font-weight:700;font-size:0.9rem;margin-bottom:0.4rem">3️⃣ Map & Safety</div>
                    <div style="font-size:0.83rem;color:#000000">Audit airspace rules on live dark map and export JSON/CSV/PDF.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Page 2: Mission Input
    elif st.session_state.current_page == "Mission Input":
        st.subheader("📝 Mission Parameter Input")

        st.markdown("""
            <div class="uav-card">
                <div class="uav-card-title">🤖 Option A: Natural Language Request</div>
                <div style="font-size:0.85rem;color:#000000;margin-bottom:0.5rem">Enter mission details in plain English and let the Gemini AI Agent extract coordinates and parameters.</div>
            </div>
        """, unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Natural Language Prompt:",
            value="Plan a surveillance mission around FAST campus for 15 minutes at 50 meters altitude using a square pattern layout.",
            height=100
        )
        
        if st.button("🚀 Process with Gemini AI Agent", use_container_width=True):
            with st.spinner("Extracting mission parameters with Gemini..."):
                extracted = understand_mission(prompt)
                st.session_state.mission_name = extracted.get("mission_name", "FAST Surveillance")
                st.session_state.mission_type = extracted.get("mission_type", "surveillance")
                st.session_state.altitude = float(extracted.get("altitude", 50.0))
                st.session_state.duration = float(extracted.get("duration", 15.0))
                st.session_state.pattern = extracted.get("pattern", "square")
                st.success("✅ Parameters successfully extracted and applied!")

        st.markdown("<hr style='border:1px solid #E2E8F0;margin:1.2rem 0'>", unsafe_allow_html=True)

        st.markdown("""
            <div class="uav-card">
                <div class="uav-card-title">⚙️ Option B: Manual Parameter Override</div>
            </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.session_state.mission_name = st.text_input("Mission Name", st.session_state.mission_name)
            st.session_state.mission_type = st.selectbox(
                "Mission Type",
                ["surveillance", "mapping", "search_rescue", "inspection"],
                index=["surveillance", "mapping", "search_rescue", "inspection"].index(st.session_state.mission_type)
            )
            st.session_state.pattern = st.selectbox(
                "Route Pattern Profile",
                ["square", "grid", "circle", "perimeter"],
                index=["square", "grid", "circle", "perimeter"].index(st.session_state.pattern)
            )
        with col_b:
            st.session_state.altitude = st.slider("Target Altitude (metres)", 10.0, 150.0, st.session_state.altitude)
            st.session_state.duration = st.slider("Target Duration (minutes)", 5.0, 60.0, st.session_state.duration)
        with col_c:
            st.session_state.home_lat = st.number_input("Home Latitude", value=st.session_state.home_lat, format="%.6f")
            st.session_state.home_lon = st.number_input("Home Longitude", value=st.session_state.home_lon, format="%.6f")

    # Page 3: Mission Plan
    elif st.session_state.current_page == "Mission Plan":
        st.subheader("⚙️ Mission Route Planner")

        st.markdown(f"""
            <div class="uav-card">
                <div class="uav-card-title">📌 Active Mission Setup</div>
                <div style="font-size:0.9rem;color:#000000">
                    <b>Mission:</b> {st.session_state.mission_name} &nbsp;|&nbsp; 
                    <b>Type:</b> {st.session_state.mission_type} &nbsp;|&nbsp; 
                    <b>Pattern:</b> {st.session_state.pattern.upper()} &nbsp;|&nbsp; 
                    <b>Altitude:</b> {st.session_state.altitude} m &nbsp;|&nbsp; 
                    <b>Duration:</b> {st.session_state.duration} mins
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Generate Waypoint Trajectory", use_container_width=True):
            wps = generate_waypoints(
                st.session_state.home_lat, st.session_state.home_lon,
                st.session_state.altitude, st.session_state.pattern
            )
            st.session_state.generated_waypoints = wps
            meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
            st.session_state.safety_checks = perform_safety_checks(meta, wps)
            st.session_state.corrections = generate_corrections(st.session_state.safety_checks, meta, wps)
            st.success(f"✅ Generated {len(wps)} waypoints successfully!")

        if st.session_state.generated_waypoints:
            st.write(f"**Generated Waypoint Count:** `{len(st.session_state.generated_waypoints)}`")
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True)

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
                st.session_state.safety_checks
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
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.88rem;color:#000000">
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
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True)
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
                    <div style="font-size:1.15rem;font-weight:800;color:#000000">{status_label}</div>
                </div>
            """, unsafe_allow_html=True)

            for c in st.session_state.safety_checks:
                icon = "✅" if c["result"] == "Pass" else "❌"
                col_c = "#10B981" if c["result"] == "Pass" else "#EF4444"
                st.markdown(f"""
                    <div style="background:#FFFFFF;border:1px solid #E2E8F0;padding:0.7rem 1rem;border-radius:8px;margin-bottom:0.4rem;display:flex;align-items:center;justify-content:space-between">
                        <span style="font-weight:700;color:#000000">{icon} {c['check_name']}</span>
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
                        <div style="color:#000000;margin-top:0.3rem">{corr}</div>
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
                    <div style="font-size:0.95rem;color:#000000">
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

with col_right:
    st.markdown("""
        <div style="background-color:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between">
            <span style="font-weight:700;color:#000000;font-size:1rem">🗺️ Live GCS Mission Radar & Airspace</span>
            <span style="font-size:0.78rem;background:#F1F5F9;color:#000000;padding:3px 8px;border-radius:6px;font-weight:600">CARTO Positron (Light)</span>
        </div>
    """, unsafe_allow_html=True)

    m = create_mission_map(
        st.session_state.generated_waypoints,
        (st.session_state.home_lat, st.session_state.home_lon)
    )
    st_folium(m, use_container_width=True, height=620, key=f"gcs_map_{st.session_state.current_page}_{len(st.session_state.generated_waypoints)}")