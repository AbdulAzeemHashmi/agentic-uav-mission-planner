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

# Custom Imports from local modules
from agents.mission_understanding_agent import understand_mission
from agents.waypoint_planner_agent import generate_waypoints
from agents.safety_compliance_agent import perform_safety_checks, NO_FLY_ZONES
from agents.correction_agent import generate_corrections
from agents.report_agent import generate_mission_summary_html
from utils.map_utils import create_mission_map
from utils.database_utils import save_mission, get_all_missions, get_mission_by_id, delete_mission, init_db
from utils.export_utils import export_mission_json, export_waypoints_csv, generate_text_report, generate_pdf_report

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
st.sidebar.title("🛸 SkyGuard AI Control Panel")
pages = ["Home", "Mission Input", "Mission Plan", "Map View", "Safety Check", "Suggestions", "Database History", "Export"]

for page in pages:
    if st.sidebar.button(page, use_container_width=True):
        st.session_state.current_page = page

st.sidebar.write("---")
st.sidebar.info("🚀 AI-Driven Mission Planner & Compliance Auditor")

# --- PAGE 1: HOME PANEL ---
if st.session_state.current_page == "Home":
    st.title("🛸 Agentic UAV Mission Planner & Safety Auditor")
    st.write("Welcome to SkyGuard AI. This application uses an agentic AI workflow to parse natural language mission goals, construct optimized flight paths, and audit paths against airspace compliance rules.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max Regulated Ceiling", "80 meters")
    with col2:
        st.metric("Max Operation Range", "500 meters")
    with col3:
        st.metric("Max Flight Window", "30 minutes")

# --- PAGE 2: MISSION INPUT ---
elif st.session_state.current_page == "Mission Input":
    st.title("📝 Design a Flight Mission")
    
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
    st.title("⚙️ Route Plan Strategy Matrix")
    
    if st.button("Calculate Trajectory Waypoints"):
        wps = generate_waypoints(st.session_state.home_lat, st.session_state.home_lon, st.session_state.altitude, st.session_state.pattern)
        st.session_state.generated_waypoints = wps
        
        meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
        st.session_state.safety_checks = perform_safety_checks(meta, wps)
        st.session_state.corrections = generate_corrections(st.session_state.safety_checks, meta, wps)
        st.success(f"Successfully generated {len(wps)} flight nodes.")
        
    if st.session_state.generated_waypoints:
        st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True)

# --- PAGE 4: MAP VIEW ---
elif st.session_state.current_page == "Map View":
    st.title("🗺️ Interactive Geospatial Map Display")
    
    if st.session_state.generated_waypoints:
        m = create_mission_map(st.session_state.home_lat, st.session_state.home_lon, st.session_state.generated_waypoints, NO_FLY_ZONES)
        st_folium(m, width=1100, height=550)
    else:
        st.warning("Generate trajectory waypoints on the Mission Plan page first to display the path map.")

# --- PAGE 5: SAFETY CHECK ---
elif st.session_state.current_page == "Safety Check":
    st.title("📜 UAV Flight Safety Standards Audit")
    
    if st.session_state.safety_checks:
        all_passed = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
        st.subheader(f"Overall Audit Status: {'SAFE' if all_passed else 'REJECTED COMPLIANCE'}")
        
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

# --- PAGE 6: SUGGESTIONS ---
elif st.session_state.current_page == "Suggestions":
    st.title("🤖 Intelligent Agent Auto-Correction Recommendations")
    
    if st.session_state.corrections:
        for corr in st.session_state.corrections:
            st.info(f"💡 {corr}")
    else:
        st.success("Perfect alignment! No correction suggestions required for this route.")

# --- PAGE 7: DATABASE HISTORY ---
elif st.session_state.current_page == "Database History":
    st.title("🗄️ Relational Database Historical Records Log")
    
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

# --- PAGE 8: EXPORT ---
elif st.session_state.current_page == "Export":
    st.title("📥 Export Options & Download Reports")
    
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
    else:
        st.warning("No mission telemetries generated. Generate path waypoints before executing exports.")