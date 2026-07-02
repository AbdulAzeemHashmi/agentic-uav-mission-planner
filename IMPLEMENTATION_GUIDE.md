# AGENTIC UAV MISSION PLANNER: 5-DAY IMPLEMENTATION GUIDE

**Student:** Abdul Azeem Hashmi  
**GitHub:** AbdulAzeemHashmi  
**Email:** abdulazeemhashmi29@gmail.com  
**Local Path:** C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner  
**Branch:** main

---

## PHASE OVERVIEW

This comprehensive guide takes you through building waypoint generation and map visualization features for your UAV mission planner application. Each day builds upon the previous day, combining Streamlit UI integration with Folium mapping.

**Learning Outcomes:**
- Generate dynamic waypoints for multiple flight patterns
- Visualize routes on interactive maps
- Handle no-fly zone restrictions
- Build modular, maintainable code

---

## DAY 1: WAYPOINT PLANNER MODULE AND SQUARE ROUTE GENERATION

### STATUS
The waypoint_planner_agent.py already exists in your repository with square route generation implemented. Your task is to verify it works correctly and commit any verification tests.

### VERIFICATION CHECKLIST

**Step 1.1:** Verify the module imports without errors:

```powershell
cd C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner
python -c "from agents.waypoint_planner_agent import generate_waypoints; print('Success!')"
```

**Step 1.2:** Test the square route generation:

```powershell
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
for wp in wps:
    print(f'Seq {wp[\"sequence_no\"]}: ({wp[\"latitude\"]:.4f}, {wp[\"longitude\"]:.4f}) Alt={wp[\"altitude\"]}m')
"
```

Expected output: 6 waypoints (takeoff, 4 corners, rtl)

**Step 1.3:** Commit the verification:

```powershell
git status
git add -A
git commit -m "Day 1: Verify waypoint planner with square route generation

- Confirmed generate_waypoints() generates correct square pattern
- Takeoff at seq 0, RTL at final sequence
- All waypoints include required fields: sequence_no, latitude, longitude, altitude, action"

git push origin main
```

---

## DAY 2: ROUTE TRAJECTORY ENHANCEMENTS (TAKEOFF, RTL, AND GRID/PERIMETER PATTERNS)

### OVERVIEW
The waypoint planner already includes all three patterns (square, grid, perimeter). Today you will:
1. Verify all patterns work correctly
2. Update app.py to add pattern selection UI
3. Display waypoints in a data table on the Mission Plan page

### STEP 2.1: Verify All Route Patterns

Test each pattern in PowerShell:

```powershell
python -c "
from agents.waypoint_planner_agent import generate_waypoints

print('=== SQUARE PATTERN ===')
square_wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
print(f'Generated {len(square_wps)} waypoints')

print('\n=== GRID PATTERN ===')
grid_wps = generate_waypoints(33.6425, 73.0232, 50.0, 'grid')
print(f'Generated {len(grid_wps)} waypoints')

print('\n=== PERIMETER PATTERN ===')
perim_wps = generate_waypoints(33.6425, 73.0232, 50.0, 'perimeter')
print(f'Generated {len(perim_wps)} waypoints')
"
```

### STEP 2.2: Check app.py Structure

Read the existing navigation code to understand how pages work:

The app.py already includes:
- Session state initialization for route_pattern
- compute_current_mission() function that calls generate_waypoints()
- Pattern selection via st.session_state.route_pattern

### STEP 2.3: Verify Pattern Selection Works

In Streamlit UI (run app.py and test):
1. Go to "Mission Input" page
2. Look for route pattern selectbox
3. Select "square", "grid", or "perimeter"
4. Check if active_waypoints are generated in session state

### STEP 2.4: Git Commit for Day 2

```powershell
git status
git add -A
git commit -m "Day 2: Verify all route patterns and app integration

- Tested generate_square_route() with 6 waypoints output
- Tested generate_grid_route() with grid pattern waypoints
- Tested generate_perimeter_route() with circular boundary
- Confirmed app.py calls compute_current_mission() on pattern selection
- All patterns include Takeoff (seq 0) and RTL (final sequence)"

git push origin main
```

---

## DAY 3: MAP UTILITIES AND HOME LOCATION PINNING

### OVERVIEW
Create map utilities to display the home location on an interactive Folium map.

### STEP 3.1: Verify Folium and Streamlit-Folium Installation

```powershell
python -c "import folium; import streamlit_folium; print('Success!')"
```

If you get an error, install:

```powershell
pip install folium streamlit-folium
pip freeze > requirements.txt
```

### STEP 3.2: Create utils/map_utils.py

```powershell
cd C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner
```

Create the file with this code:

```python
# File: utils/map_utils.py
"""
Map Utilities Module

Provides functions to create and manipulate Folium map objects for mission visualization.
Includes home location pinning, waypoint markers, flight path drawing, and no-fly zone fencing.
"""

import folium
from folium import plugins
from typing import List, Dict, Any, Tuple, Optional
import math


def initialize_mission_map(
    home_lat: float,
    home_lon: float,
    zoom_start: int = 17
) -> folium.Map:
    """
    Creates and returns a Folium map object centered at the home location.
    
    Args:
        home_lat: Home latitude coordinate (decimal degrees)
        home_lon: Home longitude coordinate (decimal degrees)
        zoom_start: Initial map zoom level (default 17 for street level detail)
    
    Returns:
        folium.Map object ready for further customization
    
    Example:
        map_obj = initialize_mission_map(33.6425, 73.0232)
        # Map is now centered at home location with zoom level 17
    """
    
    # Create base map centered on home location
    mission_map = folium.Map(
        location=[home_lat, home_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap"
    )
    
    # Add home location marker (distinctive color: blue)
    folium.Marker(
        location=[home_lat, home_lon],
        popup="Home / Takeoff Point",
        tooltip="Click for details: Home Location",
        icon=folium.Icon(
            color="blue",
            icon="home",
            prefix="fa"
        )
    ).add_to(mission_map)
    
    return mission_map


def add_waypoint_markers(
    mission_map: folium.Map,
    waypoints: List[Dict[str, Any]]
) -> folium.Map:
    """
    Adds numbered markers for each waypoint on the map.
    Each marker is labeled with its sequence number for easy identification.
    
    Args:
        mission_map: Folium map object to add markers to
        waypoints: List of waypoint dictionaries from generate_waypoints()
    
    Returns:
        Updated folium.Map object with waypoint markers
    
    Example:
        map_obj = add_waypoint_markers(map_obj, waypoints)
        # Map now shows markers numbered 0, 1, 2, etc.
    """
    
    if not waypoints:
        return mission_map
    
    for waypoint in waypoints:
        seq = waypoint["sequence_no"]
        lat = waypoint["latitude"]
        lon = waypoint["longitude"]
        action = waypoint["action"]
        
        # Skip the home location (already marked above)
        if action == "takeoff":
            continue
        
        # Assign colors based on action type
        if action == "rtl":
            color = "red"
            icon_char = "arrow-down"
        elif action == "waypoint":
            color = "green"
            icon_char = "circle"
        else:
            color = "gray"
            icon_char = "circle"
        
        # Create marker with sequence number
        folium.Marker(
            location=[lat, lon],
            popup=f"Waypoint {seq}: {action.upper()}",
            tooltip=f"Sequence {seq}",
            icon=folium.Icon(
                color=color,
                icon=icon_char,
                prefix="fa"
            )
        ).add_to(mission_map)
    
    return mission_map


def draw_flight_path(
    mission_map: folium.Map,
    waypoints: List[Dict[str, Any]]
) -> folium.Map:
    """
    Draws a continuous flight path line connecting all waypoints in sequence.
    Uses a PolyLine to visualize the planned route.
    
    Args:
        mission_map: Folium map object to draw path on
        waypoints: List of waypoint dictionaries from generate_waypoints()
    
    Returns:
        Updated folium.Map object with flight path
    
    Example:
        map_obj = draw_flight_path(map_obj, waypoints)
        # Map now shows a blue line connecting all waypoints
    """
    
    if not waypoints or len(waypoints) < 2:
        return mission_map
    
    # Extract coordinates from waypoints in sequence order
    coordinates = [
        [wp["latitude"], wp["longitude"]]
        for wp in sorted(waypoints, key=lambda w: w["sequence_no"])
    ]
    
    # Draw the flight path as a polyline
    folium.PolyLine(
        locations=coordinates,
        color="blue",
        weight=2,
        opacity=0.8,
        popup="Flight Path"
    ).add_to(mission_map)
    
    return mission_map


def add_no_fly_zone(
    mission_map: folium.Map,
    zone_name: str,
    zone_bounds: Dict[str, float],
    color: str = "red",
    fill_opacity: float = 0.3
) -> folium.Map:
    """
    Adds a no-fly zone polygon to the map using zone boundary coordinates.
    
    Args:
        mission_map: Folium map object to add zone to
        zone_name: Name of the no-fly zone (e.g., "Airport Buffer")
        zone_bounds: Dictionary with keys "north", "south", "east", "west" (decimal degrees)
        color: Border color for the polygon (default "red")
        fill_opacity: Transparency of the filled area (0.0 to 1.0)
    
    Returns:
        Updated folium.Map object with no-fly zone polygon
    
    Example:
        bounds = {"north": 33.65, "south": 33.64, "east": 73.03, "west": 73.02}
        map_obj = add_no_fly_zone(map_obj, "Airport Buffer", bounds)
    """
    
    # Extract boundary coordinates
    north = zone_bounds["north"]
    south = zone_bounds["south"]
    east = zone_bounds["east"]
    west = zone_bounds["west"]
    
    # Create polygon points (counterclockwise from NW corner)
    polygon_coords = [
        [north, west],   # NW corner
        [north, east],   # NE corner
        [south, east],   # SE corner
        [south, west],   # SW corner
        [north, west]    # Close the polygon
    ]
    
    # Draw the polygon on the map
    folium.Polygon(
        locations=polygon_coords,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=fill_opacity,
        popup=f"No-Fly Zone: {zone_name}",
        tooltip=zone_name
    ).add_to(mission_map)
    
    return mission_map


def create_mission_map(
    home_lat: float,
    home_lon: float,
    waypoints: List[Dict[str, Any]],
    no_fly_zones: Optional[List[Dict[str, Any]]] = None
) -> folium.Map:
    """
    Comprehensive map creation function that combines all elements.
    This is the main function to call for creating a complete mission map.
    
    Args:
        home_lat: Home latitude coordinate
        home_lon: Home longitude coordinate
        waypoints: List of waypoint dictionaries from generate_waypoints()
        no_fly_zones: Optional list of no-fly zone dictionaries
    
    Returns:
        Complete folium.Map object with all visualization elements
    
    Example:
        map_obj = create_mission_map(33.6425, 73.0232, waypoints, no_fly_zones)
        st_folium(map_obj, width=1000, height=600)
    """
    
    # Initialize base map with home location
    mission_map = initialize_mission_map(home_lat, home_lon)
    
    # Add waypoint markers (if any)
    if waypoints:
        mission_map = add_waypoint_markers(mission_map, waypoints)
        mission_map = draw_flight_path(mission_map, waypoints)
    
    # Add no-fly zones (if any)
    if no_fly_zones:
        for zone in no_fly_zones:
            mission_map = add_no_fly_zone(
                mission_map,
                zone_name=zone.get("name", "Unknown Zone"),
                zone_bounds=zone.get("bounds", {}),
                color=zone.get("color", "red")
            )
    
    return mission_map
```

### STEP 3.3: Test the Map Utilities

Create a quick test:

```powershell
python -c "
from utils.map_utils import initialize_mission_map, add_waypoint_markers
from agents.waypoint_planner_agent import generate_waypoints

home_lat, home_lon = 33.6425, 73.0232
map_obj = initialize_mission_map(home_lat, home_lon)
waypoints = generate_waypoints(home_lat, home_lon, 50.0, 'square')
map_obj = add_waypoint_markers(map_obj, waypoints)

print('Map created successfully!')
print(f'Map center: ({map_obj.location[0]}, {map_obj.location[1]})')
"
```

### STEP 3.4: Git Commit for Day 3

```powershell
git status
git add utils/map_utils.py
git commit -m "Day 3: Create map utilities and home location pinning

- Added utils/map_utils.py with comprehensive mapping functions
- initialize_mission_map() creates base map centered at home location
- add_waypoint_markers() displays numbered markers for each waypoint
- draw_flight_path() connects waypoints with PolyLine
- add_no_fly_zone() draws restricted airspace boundaries as polygons
- create_mission_map() is the main entry point for complete visualization"

git push origin main
```

---

## DAY 4: DRAWING FLIGHT VECTORS AND WAYPOINT LABELS

### OVERVIEW
Your map utilities from Day 3 already include:
- Waypoint markers with numbers
- Flight path polylines
- No-fly zone polygons

Today you will verify these features work in the Streamlit app.

### STEP 4.1: Check that app.py has Map View Page

Verify that the map view page code exists in app.py. Look for a page that calls st_folium() with the map object.

### STEP 4.2: Integrate Map Utilities into Streamlit

You need to ensure the app.py calls create_mission_map() when rendering the Map View page.

Check if app.py has this import at the top:

```python
from utils.map_utils import create_mission_map
```

If it does, verify the Map View page calls:

```python
mission_map = create_mission_map(
    home_lat=st.session_state.home_lat,
    home_lon=st.session_state.home_lon,
    waypoints=st.session_state.active_waypoints,
    no_fly_zones=st.session_state.get("no_fly_zones", [])
)
st_folium(mission_map, width=1000, height=600)
```

### STEP 4.3: Test in Streamlit UI

```powershell
streamlit run app.py
```

1. Navigate to "Mission Input" page
2. Set home location (latitude, longitude, altitude)
3. Select a route pattern (square, grid, or perimeter)
4. Go to "Map View" page
5. Verify:
   - Blue marker at home location labeled "Home / Takeoff Point"
   - Green markers at each waypoint numbered 0, 1, 2, etc.
   - Blue line connecting all waypoints in sequence
   - Red marker at final RTL waypoint

### STEP 4.4: Update No-Fly Zones in Session State

In app.py, add these sample no-fly zones to session state initialization:

```python
if "no_fly_zones" not in st.session_state:
    st.session_state.no_fly_zones = [
        {
            "name": "Airport Buffer Zone",
            "bounds": {
                "north": 33.65,
                "south": 33.63,
                "east": 73.04,
                "west": 73.01
            },
            "color": "red"
        },
        {
            "name": "Restricted Military Area",
            "bounds": {
                "north": 33.70,
                "south": 33.68,
                "east": 73.10,
                "west": 73.08
            },
            "color": "darkred"
        }
    ]
```

### STEP 4.5: Git Commit for Day 4

```powershell
git status
git add -A
git commit -m "Day 4: Integrate flight vectors and waypoint visualization

- Verified add_waypoint_markers() displays all waypoints with sequence numbers
- Verified draw_flight_path() connects waypoints with PolyLine
- Added sample no-fly zones to session state
- Tested map rendering in Streamlit with all visualization elements
- Map shows home location (blue), waypoints (green), path (blue line), RTL (red)"

git push origin main
```

---

## DAY 5: NO-FLY ZONE FENCING AND STAGING VERIFICATION

### OVERVIEW
Finalize no-fly zone visualization and prepare for delivery.

### STEP 5.1: Verify No-Fly Zone Display on Map

In Streamlit UI:
1. Navigate to Map View page
2. Check that no-fly zone polygons are visible as red/darkred regions
3. Verify the polygons do not interfere with waypoint markers
4. Check that multiple zones can be displayed simultaneously

### STEP 5.2: Add No-Fly Zone Management UI

Add this to the "Mission Input" page in app.py to allow users to define no-fly zones:

```python
st.subheader("No-Fly Zone Configuration")
add_nfz = st.checkbox("Add Custom No-Fly Zone")
if add_nfz:
    nfz_name = st.text_input("Zone Name", "Custom No-Fly Zone")
    col1, col2 = st.columns(2)
    with col1:
        nfz_north = st.number_input("North Boundary (Lat)", 33.6425, step=0.001)
        nfz_east = st.number_input("East Boundary (Lon)", 73.0232, step=0.001)
    with col2:
        nfz_south = st.number_input("South Boundary (Lat)", 33.6425 - 0.01, step=0.001)
        nfz_west = st.number_input("West Boundary (Lon)", 73.0232 - 0.01, step=0.001)
    
    if st.button("Add No-Fly Zone"):
        new_zone = {
            "name": nfz_name,
            "bounds": {
                "north": nfz_north,
                "south": nfz_south,
                "east": nfz_east,
                "west": nfz_west
            },
            "color": "red"
        }
        st.session_state.no_fly_zones.append(new_zone)
        st.success(f"Added no-fly zone: {nfz_name}")
```

### STEP 5.3: Add Verification Checklist

Create a new file: docs/DELIVERY_CHECKLIST.md

```markdown
# Phase Delivery Checklist

## Waypoint Generation & Map Visualization Phase

### Code Files
- [ ] agents/waypoint_planner_agent.py exists and exports generate_waypoints()
- [ ] utils/map_utils.py exists with all mapping functions
- [ ] app.py imports generate_waypoints() and create_mission_map()
- [ ] requirements.txt includes folium and streamlit-folium

### Functional Requirements
- [ ] Square route pattern generates 6 waypoints (takeoff, 4 corners, RTL)
- [ ] Grid pattern generates multiple waypoints in lawn-mower arrangement
- [ ] Perimeter pattern generates circular boundary waypoints
- [ ] Each waypoint includes: sequence_no, latitude, longitude, altitude, action
- [ ] Takeoff waypoint always at seq=0 at home location
- [ ] RTL waypoint at final sequence returning to home location

### Map Visualization
- [ ] Home location displays as blue marker with "Home / Takeoff Point" label
- [ ] Waypoints display as numbered green markers
- [ ] RTL waypoint displays as red marker
- [ ] Flight path shows as blue polyline connecting all waypoints
- [ ] No-fly zones display as colored polygons (red/darkred)
- [ ] Multiple no-fly zones can be displayed simultaneously
- [ ] Map is interactive and zoomable

### UI Integration
- [ ] Mission Input page allows route pattern selection
- [ ] Route pattern selection triggers waypoint regeneration
- [ ] Mission Plan page displays waypoint data table (via st.dataframe())
- [ ] Map View page displays complete mission map

### Testing
- [ ] Manual test: Square pattern generates correct waypoints
- [ ] Manual test: Grid pattern generates lawn-mower layout
- [ ] Manual test: Perimeter pattern generates circular boundary
- [ ] Streamlit test: Route pattern selection updates map in real-time
- [ ] Streamlit test: No-fly zones display correctly on map
- [ ] No errors in terminal or browser console during testing

### Git Repository
- [ ] All code committed to main branch
- [ ] Commit messages follow convention: "Day N: Description"
- [ ] All commits pushed to origin main
- [ ] GitHub repository reflects latest changes
```

### STEP 5.4: Final Testing Checklist

```powershell
# Test 1: All imports work
python -c "from agents.waypoint_planner_agent import generate_waypoints; from utils.map_utils import create_mission_map; print('All imports successful')"

# Test 2: Square route
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
assert len(wps) == 6, 'Expected 6 waypoints'
assert wps[0]['action'] == 'takeoff', 'First waypoint must be takeoff'
assert wps[-1]['action'] == 'rtl', 'Last waypoint must be RTL'
print('Square route test PASSED')
"

# Test 3: Grid route
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'grid')
assert len(wps) > 6, 'Grid should have more waypoints than square'
print(f'Grid route test PASSED ({len(wps)} waypoints)')
"

# Test 4: Perimeter route
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'perimeter')
assert len(wps) > 3, 'Perimeter should have multiple waypoints'
print(f'Perimeter route test PASSED ({len(wps)} waypoints)')
"

# Test 5: Map creation
python -c "
from utils.map_utils import create_mission_map
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
map_obj = create_mission_map(33.6425, 73.0232, wps)
print('Map creation test PASSED')
"
```

### STEP 5.5: Git Commit for Day 5

```powershell
git add -A
git commit -m "Day 5: Complete no-fly zone visualization and verification

- Added sample no-fly zones to session state
- Implemented no-fly zone management UI on Mission Input page
- Verified no-fly zone polygons display correctly on map
- All no-fly zones render without interfering with waypoint markers
- Created delivery checklist: docs/DELIVERY_CHECKLIST.md
- Performed comprehensive testing of all route patterns
- Verified map interactive features (zoom, pan, tooltips)"

git push origin main
```

### STEP 5.6: Final Repository State Verification

```powershell
# Verify all required files exist
ls agents/waypoint_planner_agent.py
ls utils/map_utils.py
ls app.py
ls requirements.txt
ls IMPLEMENTATION_GUIDE.md
ls docs/DELIVERY_CHECKLIST.md

# Check Git log
git log --oneline -10

# Verify all changes are on main
git branch -v
git status
```

---

## SUMMARY OF DELIVERABLES

### Code Files Created/Updated
1. **agents/waypoint_planner_agent.py** - Waypoint generation with patterns
2. **utils/map_utils.py** - Map visualization utilities
3. **app.py** - Streamlit UI integration
4. **requirements.txt** - Dependencies (folium, streamlit-folium)
5. **docs/DELIVERY_CHECKLIST.md** - Verification checklist
6. **IMPLEMENTATION_GUIDE.md** - This guide

### Features Implemented
- Square route pattern (6 waypoints)
- Grid route pattern (lawn-mower style)
- Perimeter route pattern (circular boundary)
- Home location pinning on map
- Waypoint markers with sequence numbers
- Flight path visualization with polylines
- No-fly zone polygon boundaries
- Interactive map with zoom and pan
- Real-time map updates on route pattern change

### Testing Performed
- Unit tests for waypoint generation
- Streamlit UI functional tests
- Map rendering verification
- Multi-pattern testing
- No-fly zone visualization testing

---

## TROUBLESHOOTING GUIDE

### Issue: "ModuleNotFoundError: No module named 'folium'"
**Solution:**
```powershell
pip install folium streamlit-folium
pip freeze > requirements.txt
```

### Issue: "Map not displaying in Streamlit"
**Solution:**
1. Ensure st_folium() is imported: `from streamlit_folium import st_folium`
2. Check that map object is being passed: `st_folium(mission_map, width=1000, height=600)`
3. Verify Streamlit version: `pip install --upgrade streamlit`

### Issue: "Waypoints showing at incorrect locations"
**Solution:**
1. Verify coordinate conversion: Test with known coordinates
2. Check that lat/lon are not swapped in function calls
3. Verify degree offsets are being calculated correctly

### Issue: "No-fly zones not displaying"
**Solution:**
1. Check that no_fly_zones session state is initialized
2. Verify bounds dictionary has all four keys: "north", "south", "east", "west"
3. Ensure no_fly_zones are passed to create_mission_map()

---

## NEXT STEPS

After completing this 5-day phase, you can proceed to:
1. **Safety Compliance Agent** - Validate missions against no-fly zones
2. **Mission Correction Agent** - Suggest fixes for unsafe missions
3. **Report Generation** - Export mission plans as PDF/JSON
4. **Database Integration** - Save and load missions from SQLite

Good luck with your internship project!
