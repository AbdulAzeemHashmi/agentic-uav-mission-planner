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

# Custom styling to reduce top spacing / margin and customize HUD elements
st.markdown("""
    <style>
    /* Hide top header bar (Deploy, hamburger menu etc) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0px;
    }
    
    /* Set default padding from main content block to 1rem (~0.4cm) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Set top padding from sidebar to 1rem (~0.4cm) */
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
    }
    
    /* Reset spacing above titles and headers */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
        color: #FAFAFA !important;
    }

    /* Custom styles for HUD metrics */
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] {
        color: #1E90FF !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #FAFAFA !important;
        font-size: 0.9rem !important;
    }

    /* Style the sidebar buttons */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #1E1E1E;
        color: #FAFAFA;
        border: 1px solid #333333;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        border-color: #1E90FF;
        color: #1E90FF;
    }
    
    /* Style main buttons to look professional blue */
    div.stButton > button {
        background-color: #1E90FF;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #00BFFF;
        color: white;
    }

    /* Style dataframes for dark theme contrast */
    .dataframe {
        background-color: #1E1E1E !important;
        color: #FAFAFA !important;
        border: 1px solid #333333 !important;
    }
    .dataframe th {
        background-color: #2D2D2D !important;
        color: #1E90FF !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom Imports from local modules
from agents.mission_understanding_agent import understand_mission
from agents.waypoint_planner_agent import generate_waypoints
from agents.safety_compliance_agent import perform_safety_checks, NO_FLY_ZONES
from agents.correction_agent import generate_corrections
from agents.report_agent import generate_mission_summary_html
from utils.map_utils import create_mission_map
from utils.database_utils import save_mission, get_all_missions, get_mission_by_id, delete_mission, init_db
from utils.export_utils import export_mission_json, export_waypoints_csv, generate_text_report, generate_pdf_report, export_qgc_plan

# Initialize database
init_db()

# --- PREVENT RELOAD RESET ---
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

# --- SIDEBAR INTERFACE NAVIGATOR ---
st.sidebar.title("🛸 Agentic UAV Mission Planner")
pages = ["Home", "Mission Input", "Mission Plan", "Safety Check", "Suggestions", "History", "Export"]

# Ensure current page is valid after page-list update
if "current_page" not in st.session_state or st.session_state.current_page not in pages:
    if st.session_state.get("current_page") == "Database History":
        st.session_state.current_page = "History"
    else:
        st.session_state.current_page = "Home"

for page in pages:
    label = f"▶️ {page}" if st.session_state.current_page == page else page
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.current_page = page

st.sidebar.write("---")
st.sidebar.info("🚀 AI-Driven Mission Planner & Compliance Auditor")

# --- HEADER TITLE & TELEMETRY DASHBOARD ---
st.title("🛸 Agentic UAV Mission Planner")

# Calculate safety compliance status
if st.session_state.safety_checks:
    all_passed = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
    status_text = "🟢 SAFE" if all_passed else "🔴 REJECTED"
else:
    status_text = "⚪ UNCHECKED"

header_col1, header_col2, header_col3, header_col4 = st.columns(4)
with header_col1:
    st.metric("Target Altitude", f"{st.session_state.altitude} m")
with header_col2:
    st.metric("Flight Duration", f"{st.session_state.duration} mins")
with header_col3:
    st.metric("Compliance Status", status_text)
with header_col4:
    st.metric("Flight Profile", st.session_state.pattern.upper())

st.markdown("---")

# --- MAIN CONTENT LAYOUT ---
col_left, col_right = st.columns([5, 7])

with col_left:
    # --- PAGE 1: HOME PANEL ---
    if st.session_state.current_page == "Home":
        st.subheader("🏠 Mission Overview")
        st.write("Welcome to the **Agentic UAV Mission Planner**. This application uses an agentic AI workflow to parse natural language mission goals, construct optimized flight paths, and audit paths against airspace compliance rules.")
        
        st.markdown("""
            <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 8px; border: 1px solid #333333; margin-top: 1rem; margin-bottom: 1rem;">
                <h4 style="margin-top: 0; color: #1E90FF;">Safety Regulations & Scope</h4>
                <ul style="margin-bottom: 0;">
                    <li><b>Max Regulated Ceiling:</b> 80 meters</li>
                    <li><b>Max Operation Range:</b> 500 meters</li>
                    <li><b>Max Flight Window:</b> 30 minutes</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # --- PAGE 2: MISSION INPUT ---
    elif st.session_state.current_page == "Mission Input":
        st.subheader("📝 Design a Flight Mission")
        
        prompt = st.text_area("Enter your mission profile objective in plain natural language:", 
                              value="Plan a surveillance mission around FAST campus for 15 minutes at 50 meters altitude using a square pattern layout.")
        
        if st.button("Process Command via Gemini Agent"):
            with st.spinner("Extracting parameters..."):
                extracted = understand_mission(prompt)
                st.session_state.mission_name = extracted.get("mission_name", "FAST Surveillance")
                st.session_state.mission_type = extracted.get("mission_type", "surveillance")
                st.session_state.altitude = float(extracted.get("altitude", 50.0))
                st.session_state.duration = float(extracted.get("duration", 15.0))
                st.session_state.pattern = extracted.get("pattern", "square")
                st.success("Parameters successfully mapped!")
                
        st.write("---")
        st.subheader("Configured Flight Options")
        st.session_state.mission_name = st.text_input("Mission Name Reference", st.session_state.mission_name)
        st.session_state.mission_type = st.selectbox("Mission Profile", ["surveillance", "mapping", "search_rescue", "inspection"], index=0)
        st.session_state.altitude = st.slider("Target Flight Altitude Ceiling (meters)", 10.0, 150.0, st.session_state.altitude)
        st.session_state.duration = st.slider("Target Operation Window (minutes)", 5.0, 60.0, st.session_state.duration)
        st.session_state.pattern = st.selectbox("Geometric Flight Profile Layout", ["square", "grid", "circle", "perimeter"], index=["square", "grid", "circle", "perimeter"].index(st.session_state.pattern))

    # --- PAGE 3: MISSION PLAN ---
    elif st.session_state.current_page == "Mission Plan":
        st.subheader("⚙️ Route Plan Strategy Matrix")
        
        if st.button("Calculate Trajectory Waypoints"):
            wps = generate_waypoints(st.session_state.home_lat, st.session_state.home_lon, st.session_state.altitude, st.session_state.pattern)
            st.session_state.generated_waypoints = wps
            
            meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
            st.session_state.safety_checks = perform_safety_checks(meta, wps)
            st.session_state.corrections = generate_corrections(st.session_state.safety_checks, meta, wps)
            st.success(f"Successfully generated {len(wps)} flight nodes.")
            
        if st.session_state.generated_waypoints:
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True)

    # --- PAGE 4: SAFETY CHECK ---
    elif st.session_state.current_page == "Safety Check":
        st.subheader("📜 UAV Flight Safety Standards Audit")
        
        if st.session_state.safety_checks:
            all_passed = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
            st.write(f"**Overall Audit Status:** {'🟢 SAFE' if all_passed else '🔴 REJECTED COMPLIANCE'}")
            
            for c in st.session_state.safety_checks:
                icon = "✅" if c["result"] == "Pass" else "❌"
                st.markdown(f"**{icon} {c['check_name']}**: {c['message']}")
                
            if st.button("Save Current Mission Logs to Database"):
                mission_row = {
                    "mission_name": st.session_state.mission_name,
                    "mission_type": st.session_state.mission_type,
                    "altitude": st.session_state.altitude,
                    "duration": st.session_state.duration,
                    "status": "Safe" if all_passed else "Unsafe",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_mission(mission_row, st.session_state.generated_waypoints, st.session_state.safety_checks)
                st.success("Successfully logged all flight records to database records history!")
        else:
            st.warning("No compliance checks exist. Please trigger flight path nodes first.")

    # --- PAGE 5: SUGGESTIONS ---
    elif st.session_state.current_page == "Suggestions":
        st.subheader("🤖 Intelligent Agent Auto-Correction Recommendations")
        
        if st.session_state.corrections:
            for corr in st.session_state.corrections:
                st.info(f"💡 {corr}")
        else:
            st.success("Perfect alignment! No correction suggestions required for this route.")

    # --- PAGE 6: DATABASE HISTORY ---
    elif st.session_state.current_page == "History":
        st.subheader("🗄️ Database Historical Records")
        
        records = get_all_missions()
        if records:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True)
            
            st.write("---")
            del_id = st.number_input("Enter Mission ID to delete reference record:", min_value=1, step=1)
            if st.button("Delete Target Record"):
                delete_mission(del_id)
                st.success("Mission deleted!")
                st.rerun()
        else:
            st.write("No historical mission tracking records found.")

    # --- PAGE 7: EXPORT ---
    elif st.session_state.current_page == "Export":
        st.subheader("📥 Export Options & Reports")
        
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
                
            # JSON Export Button Connection
            json_str = export_mission_json(mission_meta, st.session_state.generated_waypoints, st.session_state.safety_checks)
            st.download_button("Download System JSON Dataset", data=json_str, file_name="flight_plan.json", mime="application/json")
            
            # CSV Export Button Connection
            csv_str = export_waypoints_csv(st.session_state.generated_waypoints)
            st.download_button("Download Waypoints CSV Array Table", data=csv_str, file_name="waypoints.csv", mime="text/csv")
            
            # PDF Report Button Connection
            pdf_bytes = generate_pdf_report(mission_meta, st.session_state.generated_waypoints, st.session_state.safety_checks)
            st.download_button("Download Formal PDF Summary Audit Brief", data=pdf_bytes, file_name="mission_report.pdf", mime="application/pdf")
            
            # QGroundControl .plan Export Button Connection
            qgc_plan_str = export_qgc_plan(mission_meta, st.session_state.generated_waypoints)
            st.download_button("Download QGroundControl .plan File", data=qgc_plan_str, file_name="mission.plan", mime="application/json")
        else:
            st.warning("No mission telemetries generated. Generate path waypoints before executing exports.")

with col_right:
    st.subheader("🛰️ Live Geospatial View")
    # Render map persistently using st_folium
    m = create_mission_map(st.session_state.generated_waypoints, (st.session_state.home_lat, st.session_state.home_lon))
    st_folium(m, use_container_width=True, height=600)