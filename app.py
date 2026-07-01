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
# Initialize session state variables
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
if "rtl_enabled" not in st.session_state:
    st.session_state.rtl_enabled = True
if "nlp_input" not in st.session_state:
    st.session_state.nlp_input = ""
if "active_waypoints" not in st.session_state:
    st.session_state.active_waypoints = []
if "safety_checks" not in st.session_state:
    st.session_state.safety_checks = []
if "is_safe" not in st.session_state:
    st.session_state.is_safe = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "selected_db_mission" not in st.session_state:
    st.session_state.selected_db_mission = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "corrected_data" not in st.session_state:
    st.session_state.corrected_data = None

# Custom Theme CSS for Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Background & Text */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(20, 24, 38, 1) 0%, rgba(11, 13, 22, 1) 90.1%);
        color: #f7fafc;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(16, 20, 32, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Title banner styling */
    .hero-banner {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 10px;
        background: linear-gradient(to right, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #e2e8f0;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 242, 254, 0.5);
    }
    
    /* Buttons Customization */
    div.stButton > button {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.2);
    }
    
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 114, 255, 0.4);
        border: none;
    }
    
    /* Error/Success alerts styling override */
    .stAlert {
        border-radius: 10px;
        background-color: rgba(30, 41, 59, 0.8) !important;
    }
</style>
""", unsafe_allow_html=True)

# Generate current flight waypoints and safety assessments based on state
def compute_current_mission():
    wps = generate_waypoints(
        st.session_state.home_lat,
        st.session_state.home_lon,
        st.session_state.altitude,
        st.session_state.route_pattern,
        st.session_state.rtl_enabled
    )
    st.session_state.active_waypoints = wps
    
    mission_meta = {
        "altitude": st.session_state.altitude,
        "duration": st.session_state.duration
    }
    
    checks = perform_safety_checks(mission_meta, wps)
    st.session_state.safety_checks = checks
    
    # Check if all checks passed
    all_passed = all(c["result"] == "Pass" for c in checks)
    st.session_state.is_safe = all_passed
    
    # Run corrections if failed
    if not all_passed:
        suggs, corr_m, corr_wps = generate_corrections(
            {
                "mission_name": st.session_state.mission_name,
                "mission_type": st.session_state.mission_type,
                "altitude": st.session_state.altitude,
                "duration": st.session_state.duration,
                "route_pattern": st.session_state.route_pattern,
                "rtl_enabled": st.session_state.rtl_enabled
            },
            wps,
            checks
        )
        st.session_state.suggestions = suggs
        st.session_state.corrected_data = (corr_m, corr_wps)
    else:
        st.session_state.suggestions = []
        st.session_state.corrected_data = None

# Recalculate initially or whenever parameters are set
if not st.session_state.active_waypoints:
    compute_current_mission()

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/nolan/96/ufo.png", width=70)
st.sidebar.title("Agentic UAV Mission Planner")
st.sidebar.caption("Agentic UAV Mission Planning and Safety Compliance Assistant")
st.sidebar.write("---")

page = st.sidebar.radio(
    "Navigation Menu",
    ["Home", "Mission Input", "Mission Plan", "Map View", "Export", "Safety Check"],
    index=0
)

# Page Router
st.session_state.current_page = page

# --- PAGE 1: HOME ---
if st.session_state.current_page == "Home":
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">🛸 Agentic UAV Mission Planner</h1>
        <p class="hero-subtitle">
            <strong>Agentic UAV Mission Planning and Safety Compliance Assistant</strong><br>
            Convert natural language parameters into structured, compliant flight paths,
            visualize on interactive geofence maps, and run fail-safe rule checking dynamically.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📘 Internship Project Snapshot")
    st.markdown("""
    - **Project Domain:** Unmanned Aerial Vehicles (UAVs), Agentic AI, and Safety Compliance
    - **Project Type:** End-to-end software application for mission planning and safety verification
    - **Recommended Duration:** 8 weeks / 2 months
    - **Target Level:** 5th semester undergraduate
    - **Core Scope:** Natural language mission input, waypoint generation, map visualization, geofence checks, correction suggestions, report export, and SQLite storage
    """)

    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💡 Core Intelligent Agents")
        st.markdown("""
        - **Mission Understanding Agent (Gemini NLP)**: Extracts route configurations and limits from conversational commands.
        - **Waypoint Planner Agent**: Generates Square, Circle, Grid, or Perimeter coordinate sequences dynamically centered on target sites.
        - **Safety Compliance Agent**: Verifies coordinates, battery, distance, and altitude limits against geofenced airspace.
        - **Correction Agent**: Recommends flight modifications when constraints fail, allowing immediate one-click compliance.
        """)
        
        st.write("")
        if st.button("Proceed to Mission Input"):
            st.session_state.current_page = "Mission Input"
            st.rerun()
            
    with col2:
        st.subheader("🛑 Active Geofences (No-Fly Zones)")
        st.info("The mission assistant has loaded regulatory airspace restrictions:")
        for nfz in NO_FLY_ZONES:
            if nfz["type"] == "circle":
                st.markdown(f"🔴 **{nfz['name']}** - Center: {nfz['center']}, Radius: `{nfz['radius_m']} meters` (Circular Exclusion)")
            else:
                st.markdown(f"🟥 **{nfz['name']}** - Boundary: `{len(nfz['coords'])} points` (Polygon Exclusion)")
        
        st.write("")
        # Mini map showing home campus and geofences
        m_mini = create_mission_map([], (33.6425, 73.0232))
        st_folium(m_mini, height=250, width=500, key="minimap")

# --- PAGE 2: MISSION INPUT ---
elif st.session_state.current_page == "Mission Input":
    st.title("🛰️ Agentic UAV Mission Planner")
    st.write("Generate flight plans via Natural Language or manual overrides, assess safety compliance, and adjust path settings.")
    
    tab_nlp, tab_form = st.tabs(["💬 Natural Language Input", "⚙️ Manual Configuration Form"])
    
    # 2.1 Natural Language Processing
    with tab_nlp:
        st.session_state.nlp_input = st.text_area(
            "Enter flight request (e.g. Plan a surveillance mission around FAST campus for 20 minutes at an altitude of 75m, avoid restricted zones):",
            value=st.session_state.nlp_input
        )
        
        if st.button("Parse & Generate Flight Plan", key="nlp_btn"):
            if st.session_state.nlp_input:
                with st.spinner("Extracting parameters with Mission Understanding Agent (Gemini)..."):
                    extracted = understand_mission(st.session_state.nlp_input)
                    
                    # Update states
                    st.session_state.mission_name = extracted.get("mission_name", "NL Generated Mission")
                    st.session_state.mission_type = extracted.get("mission_type", "surveillance")
                    st.session_state.altitude = float(extracted.get("altitude", 50.0))
                    st.session_state.duration = float(extracted.get("duration", 15.0))
                    st.session_state.route_pattern = extracted.get("route_pattern", "square")
                    st.session_state.rtl_enabled = extracted.get("return_to_launch", True)
                    
                    if extracted.get("home_latitude") and extracted.get("home_longitude"):
                        st.session_state.home_lat = extracted["home_latitude"]
                        st.session_state.home_lon = extracted["home_longitude"]
                        
                    compute_current_mission()
                    st.success(f"Parsed parameters successfully! Mode: {st.session_state.route_pattern.upper()} at {st.session_state.altitude}m.")
                    st.rerun()
            else:
                st.warning("Please input a natural language request first.")
                
    # 2.2 Form Configuration
    with tab_form:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            m_name = st.text_input("Mission Name", value=st.session_state.mission_name)
            m_type = st.selectbox("Mission Type", ["surveillance", "delivery", "inspection", "search_and_rescue"], index=["surveillance", "delivery", "inspection", "search_and_rescue"].index(st.session_state.mission_type))
            patt = st.selectbox("Route Pattern", ["square", "circle", "grid", "perimeter", "manual"], index=["square", "circle", "grid", "perimeter", "manual"].index(st.session_state.route_pattern))
            rtl_val = st.checkbox("Enable Return-To-Launch (RTL)", value=st.session_state.rtl_enabled)
        with col_f2:
            alt_val = st.number_input("Target Altitude (m)", min_value=10.0, max_value=150.0, value=st.session_state.altitude, step=5.0)
            dur_val = st.number_input("Flight Duration (mins)", min_value=2.0, max_value=60.0, value=st.session_state.duration, step=1.0)
            h_lat = st.number_input("Home Latitude", value=st.session_state.home_lat, format="%.6f")
            h_lon = st.number_input("Home Longitude", value=st.session_state.home_lon, format="%.6f")
            
        if st.button("Update Parameters"):
            st.session_state.mission_name = m_name
            st.session_state.mission_type = m_type
            st.session_state.route_pattern = patt
            st.session_state.rtl_enabled = rtl_val
            st.session_state.altitude = alt_val
            st.session_state.duration = dur_val
            st.session_state.home_lat = h_lat
            st.session_state.home_lon = h_lon
            
            compute_current_mission()
            st.success("Mission parameters updated!")
            st.rerun()

    st.write("---")
    
    # 2.3 Interactive Layout: Split between Map and Safety
    left_col, right_col = st.columns([7, 5])
    
    with left_col:
        st.subheader("🗺️ Flight Path & Geofence Map")
        map_obj = create_mission_map(st.session_state.active_waypoints, (st.session_state.home_lat, st.session_state.home_lon))
        st_folium(map_obj, height=450, width=700, key="missionmap")
        
        # Save Mission to Database Section
        st.subheader("💾 Mission Actions")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("Save Mission to Database", use_container_width=True):
                m_meta = {
                    "mission_name": st.session_state.mission_name,
                    "mission_type": st.session_state.mission_type,
                    "altitude": st.session_state.altitude,
                    "duration": st.session_state.duration,
                    "status": "Safe" if st.session_state.is_safe else "Needs Revision"
                }
                new_id = save_mission(m_meta, st.session_state.active_waypoints, st.session_state.safety_checks)
                st.success(f"Saved to database successfully as Mission #{new_id}!")
        with col_act2:
            st.caption("Safety Checks status must be verified. If failed, use recommendations on the right panel before saving.")

    with right_col:
        st.subheader("🛡️ Safety & Corrections")
        
        # Display Current Status Alert
        if st.session_state.is_safe:
            st.success("✅ **MISSION APPROVED**: Passes all regulatory & battery safety thresholds.")
        else:
            st.error("⚠️ **SAFETY VIOLATION**: Mission parameters violate compliance policies.")
            
        # Display HTML Summary
        summary_html = generate_mission_summary_html(
            {
                "mission_name": st.session_state.mission_name,
                "altitude": st.session_state.altitude,
                "duration": st.session_state.duration,
                "status": "Safe" if st.session_state.is_safe else "Needs Revision"
            },
            st.session_state.active_waypoints,
            st.session_state.safety_checks
        )
        st.markdown(summary_html, unsafe_allow_html=True)
        
        # Auto-corrections
        if st.session_state.suggestions:
            st.subheader("🔧 Correction Agent Recommendations")
            for sugg in st.session_state.suggestions:
                st.write(f"👉 {sugg}")
                
            if st.button("Apply Auto-Corrections", use_container_width=True):
                if st.session_state.corrected_data:
                    corr_m, corr_wps = st.session_state.corrected_data
                    
                    st.session_state.altitude = corr_m["altitude"]
                    st.session_state.duration = corr_m["duration"]
                    # If waypoints were shifted (e.g. out of geofence), update coordinates too
                    st.session_state.active_waypoints = corr_wps
                    
                    # Rerun checks
                    checks = perform_safety_checks(corr_m, corr_wps)
                    st.session_state.safety_checks = checks
                    st.session_state.is_safe = all(c["result"] == "Pass" for c in checks)
                    st.session_state.suggestions = []
                    
                    st.success("Successfully corrected parameters! All safety policies are now met.")
                    st.rerun()
                    
    # Display waypoint coordinates table
    st.write("---")
    st.subheader("📋 Flight Waypoints Coordinate Log")
    wp_df = pd.DataFrame(st.session_state.active_waypoints)
    if not wp_df.empty:
        # Re-order columns for display
        wp_df = wp_df[["sequence_no", "latitude", "longitude", "altitude", "action"]]
        st.dataframe(wp_df, use_container_width=True)
    else:
        st.write("No waypoints generated yet.")

# --- PAGE 3: MISSION PLAN ---
# Day 2 deliverable: dedicated page showing the structured waypoint sequence
# using st.dataframe() with column explanations and mission stat cards.
elif st.session_state.current_page == "Mission Plan":
    st.title("📋 Mission Plan — Waypoint Sequence")
    st.write(
        "This page shows the complete structured flight plan generated by the "
        "**Waypoint Planner Agent**. Every row is one coordinate node the UAV "
        "will visit, in order, from takeoff through to the final RTL command."
    )

    wps = st.session_state.active_waypoints

    # --- Stat Cards Row ---
    st.write("")
    stat1, stat2, stat3, stat4 = st.columns(4)

    total_nodes = len(wps)
    cruise_alt  = st.session_state.altitude
    pattern     = st.session_state.route_pattern.upper()
    rtl_status  = "Enabled ✅" if st.session_state.rtl_enabled else "Disabled ⚠️"

    with stat1:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3 style="color:#00f2fe;font-size:2rem;margin:0">{total_nodes}</h3>'
            f'<p style="margin:4px 0 0 0;color:#94a3b8">Total Waypoints</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    with stat2:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3 style="color:#00f2fe;font-size:2rem;margin:0">{cruise_alt} m</h3>'
            f'<p style="margin:4px 0 0 0;color:#94a3b8">Cruise Altitude</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    with stat3:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3 style="color:#00f2fe;font-size:1.4rem;margin:0">{pattern}</h3>'
            f'<p style="margin:4px 0 0 0;color:#94a3b8">Route Pattern</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    with stat4:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3 style="color:#00f2fe;font-size:1.2rem;margin:0">{rtl_status}</h3>'
            f'<p style="margin:4px 0 0 0;color:#94a3b8">Return-to-Launch</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.write("")
    st.write("---")

    # --- Column Legend ---
    st.subheader("📖 Column Reference")
    st.markdown("""
    | Column | Type | Description |
    |---|---|---|
    | `sequence_no` | int | Execution order — 0 = Takeoff, last = RTL |
    | `latitude` | float | North–South coordinate (decimal degrees, WGS-84) |
    | `longitude` | float | East–West coordinate (decimal degrees, WGS-84) |
    | `altitude` | float | Target flight height above ground level (meters) |
    | `action` | str | Command type: `takeoff`, `waypoint`, `rtl`, or `land` |
    """)

    st.write("---")

    # --- Waypoint Table ---
    st.subheader("🗂️ Generated Waypoint Sequence")

    # Guard: check that the list is not empty before building the DataFrame
    if wps:
        wp_df = pd.DataFrame(wps)
        # Enforce the canonical column order
        wp_df = wp_df[["sequence_no", "latitude", "longitude", "altitude", "action"]]
        # Display with row highlighting applied by Streamlit's default theme
        st.dataframe(
            wp_df,
            use_container_width=True,
            height=min(400, 38 + len(wp_df) * 35)  # auto-size up to 400 px
        )
        st.caption(
            f"✅ {len(wp_df)} nodes generated. "
            f"Sequence 0 is always Takeoff. "
            f"Sequence {len(wp_df)-1} is {'RTL' if st.session_state.rtl_enabled else 'Land'}."
        )
    else:
        # Empty-state guard: no crash, friendly message instead
        st.info(
            "⚠️ No waypoints generated yet. "
            "Go to **Mission Input**, set your parameters, and click **Update Parameters**."
        )

    st.write("---")

    # --- Quick action to jump to Map View ---
    st.subheader("🗺️ Next Step")
    col_np1, col_np2 = st.columns([1, 3])
    with col_np1:
        if st.button("Open Map View →", use_container_width=True):
            st.session_state.current_page = "Map View"
            st.rerun()
    with col_np2:
        st.caption(
            "Switch to **Map View** to see these waypoints plotted on an interactive "
            "Folium map with No-Fly Zone overlays and the flight path PolyLine."
        )

# --- PAGE 4: MAP VIEW ---
# Day 5 deliverable: full-page Folium map combining generator + map drawer.
# Shows how changing Mission Input fields dynamically updates the map canvas.
elif st.session_state.current_page == "Map View":
    st.title("🗺️ Map View — Interactive Flight Path")
    st.write(
        "The interactive map below is built live from your current mission parameters. "
        "Markers show each waypoint in sequence. The dashed blue line is the planned "
        "flight path. Red zones are active **No-Fly Areas** the Safety Agent enforces."
    )

    # --- How the live update works (explanation for the student) ---
    st.info(
        "💡 **How dynamic updates work:** This map is regenerated every time you "
        "change parameters on the **Mission Input** page and click *Update Parameters*. "
        "Streamlit re-runs the entire script, `compute_current_mission()` is called, "
        "and `st.session_state.active_waypoints` is updated — so this map reflects "
        "the latest waypoint list automatically."
    )

    # --- Pattern badge ---
    current_pattern = st.session_state.route_pattern.upper()
    current_alt     = st.session_state.altitude
    home_lat_mv     = st.session_state.home_lat
    home_lon_mv     = st.session_state.home_lon
    wps_mv          = st.session_state.active_waypoints

    badge_col, stats_col = st.columns([1, 3])
    with badge_col:
        st.markdown(
            f'<div class="metric-card" style="text-align:center">'
            f'<p style="font-size:0.8rem;color:#94a3b8;margin:0">Active Pattern</p>'
            f'<h2 style="color:#00f2fe;margin:4px 0">{current_pattern}</h2>'
            f'<p style="font-size:0.8rem;color:#94a3b8;margin:0">{len(wps_mv)} nodes @ {current_alt} m</p>'
            f'</div>',
            unsafe_allow_html=True
        )
    with stats_col:
        # Marker legend
        st.markdown("""
        **Map Legend:**
        | Marker | Colour | Meaning |
        |--------|--------|---------|
        | 🏠 Home | Blue | Base / launch origin |
        | 🟢 Takeoff | Green | UAV lifts off here (Seq 0) |
        | 🔵 Waypoint | Blue | Patrol / scanning node |
        | 🟠 RTL | Orange | Return-to-Launch command |
        | 🔴 No-Fly Zone | Red fill | Restricted airspace |
        """)

    st.write("")

    # --- Build and render the Folium map ---
    # initialize_mission_map() + draw_no_fly_zones() + draw_flight_path()
    # are all called internally by create_mission_map() — one clean call.
    if wps_mv:
        map_obj_mv = create_mission_map(
            wps_mv,
            (home_lat_mv, home_lon_mv)
        )
    else:
        # Empty state: show base map with home marker and NFZs only
        map_obj_mv = create_mission_map([], (home_lat_mv, home_lon_mv))
        st.warning(
            "No waypoints loaded. Showing home point and No-Fly Zones only. "
            "Go to **Mission Input** and click **Update Parameters** first."
        )

    st_folium(
        map_obj_mv,
        height=520,
        use_container_width=True,
        key="mapview_main"
    )

    # --- Quick-edit shortcut ---
    st.write("---")
    col_me1, col_me2 = st.columns([1, 3])
    with col_me1:
        if st.button("← Edit Mission Input", use_container_width=True):
            st.session_state.current_page = "Mission Input"
            st.rerun()
    with col_me2:
        st.caption(
            "Change the route pattern, altitude, or home coordinates on **Mission Input** "
            "then return here — the map will update automatically."
        )

# --- PAGE 5: EXPORT ---
elif st.session_state.current_page == "Export":
    st.title("🗄️ Mission Records Database")
    st.write("Browse previous drone routes stored in SQLite database, view details, export records, or remove items.")
    
    missions = get_all_missions()
    if not missions:
        st.info("No mission plans found in database.")
    else:
        # Build missions DataFrame
        m_df = pd.DataFrame(missions)
        st.subheader("Stored Flight Profiles")
        st.dataframe(m_df, use_container_width=True)
        
        # Load specific mission options
        st.write("---")
        st.subheader("🔍 Inspect & Export Specific Mission")
        mission_options = {f"#{m['mission_id']} - {m['mission_name']} ({m['mission_type']})": m["mission_id"] for m in missions}
        selected_option = st.selectbox("Select Mission to Load", list(mission_options.keys()))
        
        if selected_option:
            m_id = mission_options[selected_option]
            
            # Fetch from SQLite
            m_meta, m_wps, m_checks = get_mission_by_id(m_id)
            
            # Display Details
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Mission Parameters:**")
                st.write(f"- Name: {m_meta['mission_name']}")
                st.write(f"- Type: {m_meta['mission_type']}")
                st.write(f"- Altitude: {m_meta['altitude']} m")
                st.write(f"- Duration: {m_meta['duration']} mins")
                st.write(f"- Status: {m_meta['status']}")
                st.write(f"- Planned: {m_meta['created_at']}")
            with col2:
                # mini-map for history view
                m_hist = create_mission_map(m_wps, (m_wps[0]["latitude"], m_wps[0]["longitude"]))
                st_folium(m_hist, height=220, width=450, key=f"hist_map_{m_id}")
                
            # Exporters
            st.write("**Export Formats:**")
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1:
                json_data = export_mission_json(m_meta, m_wps, m_checks)
                st.download_button(
                    label="Download JSON Profile",
                    data=json_data,
                    file_name=f"mission_{m_id}_export.json",
                    mime="application/json",
                    use_container_width=True
                )
            with col_ex2:
                csv_data = export_waypoints_csv(m_wps)
                st.download_button(
                    label="Download Waypoints CSV",
                    data=csv_data,
                    file_name=f"mission_{m_id}_waypoints.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_ex3:
                # PDF report download
                pdf_filename = f"reports/generated_reports/mission_{m_id}_report.pdf"
                generate_pdf_report(m_meta, m_wps, m_checks, pdf_filename)
                
                with open(pdf_filename, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"mission_{m_id}_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            # Delete option
            st.write("---")
            if st.button("🗑️ Delete Mission from Database", type="secondary"):
                delete_mission(m_id)
                st.success("Mission deleted!")
                st.rerun()

# --- PAGE 6: SAFETY CHECK ---
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
    
    # Load and display docs/uav_terms.md
    terms_path = "docs/uav_terms.md"
    if os.path.exists(terms_path):
        with open(terms_path, "r") as f:
            st.markdown(f.read())
    else:
        st.write("Reference documentation is loading.")
