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

# Inline custom CSS for dark HUD theme
st.markdown("""
    <style>
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0px;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
    }
    h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #FAFAFA !important;
    }
    h2 {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: #FAFAFA !important;
    }
    h3 {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #FAFAFA !important;
    }
    h4, h5, h6 {
        font-size: 1.0rem !important;
        font-weight: 600 !important;
        color: #FAFAFA !important;
    }
    .stMarkdown p, .stMarkdown li, p, li, label {
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        padding: 0.6rem 1.0rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] {
        color: #1E90FF !important;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 1.2rem !important;
        white-space: nowrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    [data-testid="stMetricLabel"] {
        color: #FAFAFA !important;
        font-size: 0.8rem !important;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #1E1E1E;
        color: #FAFAFA;
        border: 1px solid #333333;
        font-size: 0.88rem !important;
        padding: 0.3rem 0.6rem !important;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        border-color: #1E90FF;
        color: #1E90FF;
    }
    div.stButton > button {
        background-color: #1E90FF;
        color: white;
        border: none;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9rem !important;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #00BFFF;
        color: white;
    }
    .dataframe {
        background-color: #1E1E1E !important;
        color: #FAFAFA !important;
        border: 1px solid #333333 !important;
        font-size: 0.85rem !important;
    }
    .dataframe th {
        background-color: #2D2D2D !important;
        color: #1E90FF !important;
        font-weight: bold !important;
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
st.sidebar.title("🛸 Agentic UAV Mission Planner")
for page in pages:
    label = f"▶️  {page}" if st.session_state.current_page == page else page
    if st.sidebar.button(label, use_container_width=True, key=f"nav_{page}"):
        st.session_state.current_page = page

st.sidebar.markdown("<hr style='border:1px solid #333;margin:0.5rem 0'>", unsafe_allow_html=True)
st.sidebar.info("🚀 AI-Driven Mission Planner & Compliance Auditor")

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

st.markdown("<hr style='border:1px solid #333;margin:0.5rem 0'>", unsafe_allow_html=True)

# Create GCS split-screen layout
col_left, col_right = st.columns([11, 13], gap="large")

with col_left:
    # Page 1: Home
    if st.session_state.current_page == "Home":
        st.subheader("🏠 Agentic UAV Mission Planner")
        st.caption("AI-driven mission planning - generate waypoints, check airspace rules, and export mission data.")
        st.markdown("""
            <div style="background-color:#1E1E1E;padding:1.2rem 1.5rem;border-radius:8px;border:1px solid #333333;margin-top:0.5rem">
                <h4 style="margin-top:0;color:#1E90FF;font-size:0.95rem">Active Safety Regulations</h4>
                <ul style="margin-bottom:0;padding-left:1.2rem;font-size:0.88rem">
                    <li><b>R1</b> - Max altitude 80 m</li>
                    <li><b>R2</b> - Takeoff point required</li>
                    <li><b>R3</b> - RTL or landing point required</li>
                    <li><b>R4</b> - No entry into no-fly zones</li>
                    <li><b>R5</b> - Max waypoint separation 500 m</li>
                    <li><b>R6</b> - Max flight duration 30 min</li>
                    <li><b>R7</b> - Battery usage below 80%</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="display:flex;gap:12px;align-items:stretch">
                <div style="flex:1;background-color:#1E1E1E;padding:1rem;border-radius:8px;border:1px solid #1E90FF33">
                    <div style="color:#1E90FF;font-weight:700;font-size:0.88rem;margin-bottom:0.4rem">Step 1 - Mission Input</div>
                    <div style="font-size:0.83rem;color:#CCCCCC">Enter a natural language request or fill the manual form.</div>
                </div>
                <div style="flex:1;background-color:#1E1E1E;padding:1rem;border-radius:8px;border:1px solid #1E90FF33">
                    <div style="color:#1E90FF;font-weight:700;font-size:0.88rem;margin-bottom:0.4rem">Step 2 - Mission Plan</div>
                    <div style="font-size:0.83rem;color:#CCCCCC">Generate waypoints and review the mission route table.</div>
                </div>
                <div style="flex:1;background-color:#1E1E1E;padding:1rem;border-radius:8px;border:1px solid #1E90FF33">
                    <div style="color:#1E90FF;font-weight:700;font-size:0.88rem;margin-bottom:0.4rem">Step 3 - Map View</div>
                    <div style="font-size:0.83rem;color:#CCCCCC">Visualize flight path and no-fly zones on the live map.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Page 2: Mission Input
    elif st.session_state.current_page == "Mission Input":
        st.subheader("📝 Mission Input")

        st.write("**Option A - Natural Language Request**")
        prompt = st.text_area(
            "Enter your mission request in plain English:",
            value="Plan a surveillance mission around FAST campus for 15 minutes at 50 meters altitude using a square pattern layout."
        )
        if st.button("Process with Gemini AI Agent"):
            with st.spinner("Extracting mission parameters..."):
                extracted = understand_mission(prompt)
                st.session_state.mission_name = extracted.get("mission_name", "FAST Surveillance")
                st.session_state.mission_type = extracted.get("mission_type", "surveillance")
                st.session_state.altitude = float(extracted.get("altitude", 50.0))
                st.session_state.duration = float(extracted.get("duration", 15.0))
                st.session_state.pattern = extracted.get("pattern", "square")
                st.success("Parameters extracted and applied to the form below!")

        st.markdown("<hr style='border:1px solid #333;margin:1rem 0'>", unsafe_allow_html=True)
        st.write("**Option B - Manual Input Form**")

        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.mission_name = st.text_input("Mission Name", st.session_state.mission_name)
            st.session_state.mission_type = st.selectbox(
                "Mission Type",
                ["surveillance", "mapping", "search_rescue", "inspection"],
                index=["surveillance", "mapping", "search_rescue", "inspection"].index(st.session_state.mission_type)
            )
            st.session_state.pattern = st.selectbox(
                "Route Pattern",
                ["square", "grid", "circle", "perimeter"],
                index=["square", "grid", "circle", "perimeter"].index(st.session_state.pattern)
            )
        with col_b:
            st.session_state.altitude = st.slider("Altitude (metres)", 10.0, 150.0, st.session_state.altitude)
            st.session_state.duration = st.slider("Duration (minutes)", 5.0, 60.0, st.session_state.duration)
            st.session_state.home_lat = st.number_input("Home Latitude", value=st.session_state.home_lat, format="%.6f")
            st.session_state.home_lon = st.number_input("Home Longitude", value=st.session_state.home_lon, format="%.6f")

    # Page 3: Mission Plan
    elif st.session_state.current_page == "Mission Plan":
        st.subheader("⚙️ Mission Plan")

        st.write(f"**Mission:** {st.session_state.mission_name} | **Type:** {st.session_state.mission_type} | **Pattern:** {st.session_state.pattern} | **Altitude:** {st.session_state.altitude} m | **Duration:** {st.session_state.duration} min")

        if st.button("Generate Waypoints"):
            wps = generate_waypoints(
                st.session_state.home_lat, st.session_state.home_lon,
                st.session_state.altitude, st.session_state.pattern
            )
            st.session_state.generated_waypoints = wps
            meta = {"altitude": st.session_state.altitude, "duration": st.session_state.duration}
            st.session_state.safety_checks = perform_safety_checks(meta, wps)
            st.session_state.corrections = generate_corrections(st.session_state.safety_checks, meta, wps)
            st.success(f"Generated {len(wps)} waypoints. Navigate to Map View to see the route.")

        if st.session_state.generated_waypoints:
            st.write(f"**Total Waypoints:** {len(st.session_state.generated_waypoints)}")
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True)

            # Report Agent - mission summary HTML (brief Section 7.5)
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
            st.info("Click **Generate Waypoints** to create the mission route.")

    # Page 4: Map View
    elif st.session_state.current_page == "Map View":
        st.subheader("🗺️ Mission Map View Control")
        st.write("This page shows the active flight parameters and waypoint list for the current mission.")
        
        st.markdown(f"""
            <div style="background-color:#1E1E1E;padding:1.2rem;border-radius:8px;border:1px solid #333333;margin-bottom:1rem">
                <h4 style="margin-top:0;color:#1E90FF">🛰️ Flight Telemetry Overview</h4>
                <ul style="margin-bottom:0;padding-left:1.2rem">
                    <li><b>Mission Name:</b> {st.session_state.mission_name}</li>
                    <li><b>Home Latitude:</b> {st.session_state.home_lat:.6f}</li>
                    <li><b>Home Longitude:</b> {st.session_state.home_lon:.6f}</li>
                    <li><b>Flight Altitude:</b> {st.session_state.altitude} m</li>
                    <li><b>Target Duration:</b> {st.session_state.duration} mins</li>
                    <li><b>Flight Pattern Profile:</b> {st.session_state.pattern.upper()}</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.generated_waypoints:
            st.write(f"**Waypoint Count:** {len(st.session_state.generated_waypoints)}")
            st.dataframe(pd.DataFrame(st.session_state.generated_waypoints), use_container_width=True)
        else:
            st.info("No waypoints generated yet. Go to **Mission Plan** to generate waypoints first.")

    # Page 5: Safety Check
    elif st.session_state.current_page == "Safety Check":
        st.subheader("🛡️ Safety Compliance Check")

        if st.session_state.safety_checks:
            all_passed = all(c["result"] == "Pass" for c in st.session_state.safety_checks)
            status_label = "🟢 MISSION SAFE" if all_passed else "🔴 COMPLIANCE FAILED"
            st.markdown(f"### Overall Status: {status_label}")
            st.markdown("<hr style='border:1px solid #333;margin:0.5rem 0'>", unsafe_allow_html=True)

            for c in st.session_state.safety_checks:
                icon = "✅" if c["result"] == "Pass" else "❌"
                st.markdown(f"**{icon} {c['check_name']}**: {c['message']}")

            st.markdown("<hr style='border:1px solid #333;margin:0.5rem 0'>", unsafe_allow_html=True)
            if st.button("Save Mission to Database"):
                mission_row = {
                    "mission_name": st.session_state.mission_name,
                    "mission_type": st.session_state.mission_type,
                    "altitude": st.session_state.altitude,
                    "duration": st.session_state.duration,
                    "status": "Safe" if all_passed else "Unsafe",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_mission(mission_row, st.session_state.generated_waypoints, st.session_state.safety_checks)
                st.success("Mission saved to database!")
        else:
            st.warning("No safety checks available. Please generate waypoints on the **Mission Plan** page first.")

    # Page 6: Suggestions
    elif st.session_state.current_page == "Suggestions":
        st.subheader("💡 Correction Suggestions")

        if st.session_state.corrections:
            st.write("The following corrections are recommended for this mission:")
            for i, corr in enumerate(st.session_state.corrections, 1):
                st.info(f"**Suggestion {i}:** {corr}")
        elif st.session_state.safety_checks:
            st.success("✅ All safety checks passed. No corrections required!")
        else:
            st.warning("No suggestions available. Generate waypoints and run safety checks first.")

    # Page 7: Export
    elif st.session_state.current_page == "Export":
        st.subheader("📥 Export Mission Data")

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

            st.write(f"**Mission:** {mission_meta['mission_name']} | **Status:** {mission_meta['status']}")
            st.markdown("<hr style='border:1px solid #333;margin:0.5rem 0'>", unsafe_allow_html=True)

            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1:
                json_str = export_mission_json(mission_meta, st.session_state.generated_waypoints, st.session_state.safety_checks)
                st.download_button(
                    "⬇️  Download Mission JSON",
                    data=json_str, file_name="mission.json", mime="application/json",
                    use_container_width=True
                )
            with col_e2:
                csv_str = export_waypoints_csv(st.session_state.generated_waypoints)
                st.download_button(
                    "⬇️  Download Waypoints CSV",
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
        else:
            st.warning("No waypoints generated yet. Complete Mission Plan before exporting.")

with col_right:
    st.subheader("🗺️ Live GCS Mission Map")
    if st.session_state.generated_waypoints:
        st.write(f"Displaying route for **{st.session_state.mission_name}** - {len(st.session_state.generated_waypoints)} waypoints")
    else:
        st.info("No waypoints generated yet. Showing home location and restricted zones.")

    m = create_mission_map(
        st.session_state.generated_waypoints,
        (st.session_state.home_lat, st.session_state.home_lon)
    )
    st_folium(m, use_container_width=True, height=600, key=f"gcs_map_{st.session_state.current_page}_{len(st.session_state.generated_waypoints)}")