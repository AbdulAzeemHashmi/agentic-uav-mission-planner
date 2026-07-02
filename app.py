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
if "route_pattern" not in st.session_state:
    st.session_state.route_pattern = "square"
if "home_lat" not in st.session_state:
    st.session_state.home_lat = 33.6425
if "home_lon" not in st.session_state:
    st.session_state.home_lon = 73.0232
if "waypoints" not in st.session_state:
    st.session_state.waypoints = []
if "safety_checks" not in st.session_state:
    st.session_state.safety_checks = []
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🛸 SkyGuard AI")
st.sidebar.markdown("*UAV Flight Mission Control Center*")
st.sidebar.write("---")

pages = ["Dashboard", "Mission Planner", "Saved Missions", "Safety Check"]
for page in pages:
    if st.sidebar.button(page, use_container_width=True):
        st.session_state.current_page = page

st.sidebar.write("---")
st.sidebar.info("💡 **Tip:** Use the Mission Planner to generate routes via AI or structural entry patterns.")

# --- PAGE 1: DASHBOARD ---
if st.session_state.current_page == "Dashboard":
    st.title("📊 Mission Dashboard")
    st.write("Welcome to the Agentic UAV Mission Planner panel.")
    
    col1, col2, col3 = st.columns(3)
    missions = get_all_missions()
    
    with col1:
        st.metric("Total Planned Missions", len(missions))
    with col2:
        safe_count = sum(1 for m in missions if m.get("status") == "Safe")
        st.metric("Safe Approved Missions", safe_count)
    with col3:
        unsafe_count = sum(1 for m in missions if m.get("status") == "Needs Revision")
        st.metric("Missions Requiring Revision", unsafe_count)

# --- PAGE 2: MISSION PLANNER ---
elif st.session_state.current_page == "Mission Planner":
    st.title("🎯 UAV Mission Configuration & Route Planner")
    
    # NLP Input Prompt Panel
    st.subheader("🤖 Natural Language Mission Parser")
    user_prompt = st.text_area("Describe your mission objectives in natural language:", 
                               placeholder="e.g., Run a surveillance mission centered at FAST University campus at an altitude of 60 meters with a square pattern.")
    
    if st.button("Parse Request with AI Agent", type="primary"):
        if user_prompt.strip():
            with st.spinner("Processing request..."):
                parsed_data = understand_mission(user_prompt)
                if parsed_data:
                    st.session_state.mission_name = parsed_data.get("mission_name", st.session_state.mission_name)
                    st.session_state.mission_type = parsed_data.get("mission_type", st.session_state.mission_type)
                    st.session_state.altitude = float(parsed_data.get("altitude", st.session_state.altitude))
                    st.session_state.duration = float(parsed_data.get("duration", st.session_state.duration))
                    st.session_state.route_pattern = parsed_data.get("route_pattern", st.session_state.route_pattern)
                    st.success("AI extraction completed! Review updated parameters below.")
        else:
            st.warning("Please specify a valid mission description.")

    st.write("---")
    
    # Manual Override Parameters
    st.subheader("⚙️ Mission Control Parameters")
    with st.form("mission_form"):
        col1, col2 = st.columns(2)
        with col1:
            m_name = st.text_input("Mission Title", value=st.session_state.mission_name)
            m_type = st.selectbox("Application Domain", ["surveillance", "delivery", "inspection", "search_and_rescue"], index=["surveillance", "delivery", "inspection", "search_and_rescue"].index(st.session_state.mission_type))
            m_alt = st.number_input("Target Cruising Altitude (meters)", value=st.session_state.altitude, min_value=10.0, max_value=150.0)
        with col2:
            m_dur = st.number_input("Target Target Flight Duration (mins)", value=st.session_state.duration, min_value=1.0, max_value=60.0)
            m_pattern = st.selectbox("Geometric Path Pattern", ["square", "grid", "perimeter"], index=["square", "grid", "perimeter"].index(st.session_state.route_pattern))
            
            c1, c2 = st.columns(2)
            with c1:
                h_lat = st.number_input("Home Latitude", value=st.session_state.home_lat, format="%.6f")
            with c2:
                h_lon = st.number_input("Home Longitude", value=st.session_state.home_lon, format="%.6f")
                
        submit_btn = st.form_submit_with_clicks = st.form_submit_button("Generate Flight Plan & Waypoints", type="primary")

    if submit_btn:
        st.session_state.mission_name = m_name
        st.session_state.mission_type = m_type
        st.session_state.altitude = m_alt
        st.session_state.duration = m_dur
        st.session_state.route_pattern = m_pattern
        st.session_state.home_lat = h_lat
        st.session_state.home_lon = h_lon
        
        # Build coordinates
        st.session_state.waypoints = generate_waypoints(h_lat, h_lon, m_alt, m_pattern, rtl_enabled=True)
        
        # Run Verification Checks
        mission_meta = {"altitude": m_alt, "duration": m_dur, "mission_name": m_name, "mission_type": m_type}
        st.session_state.safety_checks = perform_safety_checks(mission_meta, st.session_state.waypoints)
        
        # Process Correction Adjustments if needed
        sug, _, _ = generate_corrections(mission_meta, st.session_state.waypoints, st.session_state.safety_checks)
        st.session_state.suggestions = sug

    # Display flight routing map and tables if tracking exists
    if st.session_state.waypoints:
        st.write("---")
        st.subheader("🗺️ Mission Flight Path Map")
        
        # Build Folium layer
        m_map = create_mission_map(st.session_state.waypoints, (st.session_state.home_lat, st.session_state.home_lon))
        st_folium(m_map, width=1100, height=500, returned_objects=[])
        
        # Show Metrics Summary and Adjustments Panel
        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.subheader("📋 Detailed Waypoint Sequences")
            df_wps = pd.DataFrame(st.session_state.waypoints)
            st.dataframe(df_wps, use_container_width=True, hide_index=True)
        with col_right:
            st.subheader("🛡️ Safety Compliance Summary")
            has_fails = False
            for chk in st.session_state.safety_checks:
                if chk["result"] == "Pass":
                    st.success(f"**{chk['check_name']}**: {chk['message']}")
                else:
                    st.error(f"**{chk['check_name']}**: {chk['message']}")
                    has_fails = True
            
            status_final = "Needs Revision" if has_fails else "Safe"
            
            if has_fails and st.session_state.suggestions:
                st.warning("⚠️ **Correction Agent Suggestions:**")
                for s in st.session_state.suggestions:
                    st.write(f"- {s}")
                    
            if st.button("Save Mission Configuration to Database", use_container_width=True):
                mission_save_data = {
                    "mission_name": st.session_state.mission_name,
                    "mission_type": st.session_state.mission_type,
                    "altitude": st.session_state.altitude,
                    "duration": st.session_state.duration,
                    "status": status_final
                }
                save_mission(mission_save_data, st.session_state.waypoints, st.session_state.safety_checks)
                st.success("🎉 Flight plan saved successfully!")

# --- PAGE 3: SAVED MISSIONS ---
elif st.session_state.current_page == "Saved Missions":
    st.title("📂 Mission Repository History")
    all_m = get_all_missions()
    
    if not all_m:
        st.info("No saved records found in database storage.")
    else:
        for m in all_m:
            with st.expander(f"📋 {m['mission_name']} ({m['created_at']}) — Status: {m['status']}"):
                st.write(f"**Application Domain:** {m['mission_type']} | **Altitude:** {m['altitude']}m | **Duration:** {m['duration']} mins")
                
                # Fetch details
                m_meta, wps, chks = get_mission_by_id(m["mission_id"])
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Waypoints Overview:**")
                    st.dataframe(pd.DataFrame(wps)[["sequence_no", "latitude", "longitude", "altitude", "action"]], hide_index=True)
                with c2:
                    st.markdown("**Safety Record Logs:**")
                    for c in chks:
                        if c["result"] == "Pass":
                            st.caption(f"✅ {c['check_name']}: {c['message']}")
                        else:
                            st.caption(f"❌ {c['check_name']}: {c['message']}")
                            
                st.write("---")
                # Export Tools Layout
                json_str = export_mission_json(m_meta, wps, chks)
                csv_str = export_waypoints_csv(wps)
                md_report = generate_text_report(m_meta, wps, chks)
                pdf_bytes = generate_pdf_report(m_meta, wps, chks)
                
                dl_col1, dl_col2, dl_col3, dl_col4 = st.columns(4)
                dl_col1.download_button("📥 Export Mission JSON", data=json_str, file_name=f"mission_{m['mission_id']}.json", mime="application/json", use_container_width=True)
                dl_col2.download_button("📥 Export CSV Path", data=csv_str, file_name=f"waypoints_{m['mission_id']}.csv", mime="text/csv", use_container_width=True)
                dl_col3.download_button("📥 Download Markdown Report", data=md_report, file_name=f"report_{m['mission_id']}.md", mime="text/markdown", use_container_width=True)
                dl_col4.download_button("📥 Download PDF Report", data=pdf_bytes, file_name=f"flight_report_{m['mission_id']}.pdf", mime="application/pdf", use_container_width=True)
                
                if st.button(f"🗑️ Delete Mission Plan Record", key=f"del_{m['mission_id']}", type="secondary"):
                    delete_mission(m["mission_id"])
                    st.warning("Mission deleted!")
                    st.rerun()

# --- PAGE 4: SAFETY CHECK ---
elif st.session_state.current_page == "Safety Check":
    st.title("📜 UAV Flight Safety Standards")
    st.write("The Agentic UAV Mission Planner enforces strict compliance rules to align with civil airspace regulations:")
    
    st.markdown("""
    ### 🛡️ Safety Verification Rules
    1. **R1: Maximum Altitude Limit**: Flights must not exceed **80 meters** to avoid conflicts with manned aviation.
    2. **R2: Takeoff Verification**: The path sequence must initiate with a dedicated `takeoff` command.
    3. **R3: Landing/RTL Verification**: The path sequence must end with a return-to-launch or landing command.
    4. **R4: Geofence Compliance**: Coordinates must not violate defined airport or military airspaces.
    5. **R5: Maximum Leg Length**: Consecutive waypoints should not exceed **500 meters** to ensure reliable signal telemetry.
    6. **R6: Mission Duration Limit**: Total planned flight duration cannot exceed **30 minutes**.
    7. **R7: Battery Safety Margin**: Estimated battery capacity usage must stay below **80%**.
    """)
    
    st.write("---")
    st.subheader("📚 Airspace Terminology Reference")
    
    terms_path = "docs/uav_terms.md"
    if os.path.exists(terms_path):
        with open(terms_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("Airspace reference text guide is missing from docs path directory.")