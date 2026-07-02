# PHASE 2 ARCHITECTURE OVERVIEW & REFERENCE

**Project:** Agentic UAV Mission Planning and Safety Compliance Assistant  
**Phase:** 2 - Waypoint Generation & Map Visualization  
**Duration:** 5 Days  
**Target:** 5th Semester Undergraduate  
**Status:** Complete

---

## SYSTEM ARCHITECTURE

```
USER INTERFACE (Streamlit App)
|
+-- Mission Input Page
|   +-- Home Location Input (lat, lon)
|   +-- Altitude Selection
|   +-- Route Pattern Selector (square, grid, perimeter)
|   +-- Mission Parameters
|
+-- Mission Plan Page
|   +-- Waypoint Table (st.dataframe)
|   +-- Mission Summary
|
+-- Map View Page
|   +-- Interactive Folium Map
|   +-- Real-time Visualization
|
+-- Database Integration
|   +-- Save/Load Missions
|
+-- Export Features
    +-- PDF Reports
    +-- CSV/JSON Export

BUSINESS LOGIC LAYER
|
+-- agents/waypoint_planner_agent.py
|   +-- generate_waypoints()           [Main entry point]
|   +-- generate_square_route()        [6 waypoints]
|   +-- generate_grid_route()          [Lawn-mower pattern]
|   +-- generate_perimeter_route()     [Circular boundary]
|
+-- agents/mission_understanding_agent.py
|   +-- Natural Language Processing
|
+-- agents/safety_compliance_agent.py
|   +-- Safety Rule Validation
|   +-- No-Fly Zone Detection
|
+-- agents/correction_agent.py
|   +-- Mission Adjustment Suggestions
|
+-- agents/report_agent.py
    +-- Report Generation

UTILITIES LAYER
|
+-- utils/map_utils.py
|   +-- initialize_mission_map()       [Base map with home marker]
|   +-- add_waypoint_markers()         [Numbered waypoint markers]
|   +-- draw_flight_path()             [Polyline connecting waypoints]
|   +-- add_no_fly_zone()              [Polygon boundaries]
|   +-- create_mission_map()           [Complete visualization]
|
+-- utils/distance_utils.py
|   +-- calculate_haversine_distance()
|   +-- calculate_bearing()
|
+-- utils/database_utils.py
|   +-- Mission persistence
|
+-- utils/export_utils.py
    +-- Export functionality

DATA STRUCTURES
|
+-- Waypoint Dictionary
|   {
|     "sequence_no": 0,
|     "latitude": 33.6425,
|     "longitude": 73.0232,
|     "altitude": 50.0,
|     "action": "takeoff"
|   }
|
+-- No-Fly Zone Dictionary
|   {
|     "name": "Airport Buffer",
|     "bounds": {
|       "north": 33.65,
|       "south": 33.63,
|       "east": 73.03,
|       "west": 73.01
|     },
|     "color": "red"
|   }
|
+-- Mission Dictionary
    {
      "mission_name": "FAST Surveillance",
      "mission_type": "surveillance",
      "home_lat": 33.6425,
      "home_lon": 73.0232,
      "altitude": 50.0,
      "duration": 15.0,
      "route_pattern": "square"
    }
```

---

## DATA FLOW DIAGRAM

```
USER SELECTS ROUTE PATTERN
          |
          v
app.py calls compute_current_mission()
          |
          +-- home_lat, home_lon, altitude, pattern
          |
          v
generate_waypoints() in waypoint_planner_agent.py
          |
          +-- Calls pattern-specific function:
          |   - generate_square_route()
          |   - generate_grid_route()
          |   - generate_perimeter_route()
          |
          v
Returns List[Dict] waypoints
          |
          v
Waypoints stored in st.session_state.active_waypoints
          |
          +-- Used by Mission Plan page (st.dataframe)
          |
          +-- Used by Map View page (create_mission_map)
          |
          v
create_mission_map() in map_utils.py
          |
          +-- initialize_mission_map()      [Blue home marker]
          +-- add_waypoint_markers()        [Green/red markers]
          +-- draw_flight_path()           [Blue polyline]
          +-- add_no_fly_zone()            [Red polygons]
          |
          v
Returns folium.Map object
          |
          v
st_folium() renders map in browser
          |
          v
USER SEES INTERACTIVE MISSION MAP
```

---

## FUNCTION REFERENCE GUIDE

### Waypoint Generation Functions

#### generate_waypoints()
```python
SIGNATURE:
  generate_waypoints(
    home_lat: float,
    home_lon: float,
    altitude: float,
    pattern: str = "square",
    rtl_enabled: bool = True
  ) -> List[Dict[str, Any]]

LOCATION: agents/waypoint_planner_agent.py

PURPOSE: Main entry point for waypoint generation

PARAMETERS:
  - home_lat: Home latitude (decimal degrees)
  - home_lon: Home longitude (decimal degrees)
  - altitude: Flight altitude in meters
  - pattern: Route pattern type ("square", "grid", "perimeter", "circle", "manual")
  - rtl_enabled: Whether to include Return-to-Launch (default True)

RETURNS:
  List of waypoint dictionaries with structure:
  {
    "sequence_no": int,        # 0, 1, 2, ...
    "latitude": float,         # Decimal degrees
    "longitude": float,        # Decimal degrees
    "altitude": float,         # Meters
    "action": str             # "takeoff", "waypoint", "rtl", "land"
  }

EXAMPLE:
  wps = generate_waypoints(33.6425, 73.0232, 50.0, "square")
  # Returns 6 waypoints for square pattern
```

#### generate_square_route()
```python
SIGNATURE:
  generate_square_route(
    home_lat: float,
    home_lon: float,
    altitude: float,
    side_length_meters: float = 100.0
  ) -> List[Dict[str, Any]]

PURPOSE: Generate square patrol route with 4 corners

WAYPOINT COUNT: 6 (takeoff, 4 corners, rtl)

PATTERN:
         NW --- NE
         |       |
  Home --+------- +-- East
         |       |
         SW --- SE

COORDINATE CONVERSION:
  - Uses 111,000 meters per degree latitude
  - Scales longitude by cos(latitude)
  - Accurate for areas < 50 km

EXAMPLE:
  square_wps = generate_square_route(33.6425, 73.0232, 50.0, 100.0)
  # 100 meter square centered on home location
```

#### generate_grid_route()
```python
SIGNATURE:
  generate_grid_route(
    home_lat: float,
    home_lon: float,
    altitude: float,
    bounds: Optional[dict] = None
  ) -> List[Dict[str, Any]]

PURPOSE: Generate grid (lawn-mower) pattern for area scanning

WAYPOINT COUNT: ~13 (varies with grid_size)

PATTERN (3x3 grid):
  Row 1: [>] [>] [>]
  Row 2: [<] [<] [<]
  Row 3: [>] [>] [>]
  (Arrows show direction - lawn-mower alternation)

USE CASES:
  - Area surveillance
  - Orthophotography mapping
  - Crop inspection
  - Search and rescue

EXAMPLE:
  grid_wps = generate_grid_route(33.6425, 73.0232, 50.0)
```

#### generate_perimeter_route()
```python
SIGNATURE:
  generate_perimeter_route(
    home_lat: float,
    home_lon: float,
    altitude: float,
    bounds: Optional[dict] = None
  ) -> List[Dict[str, Any]]

PURPOSE: Generate circular boundary patrol route

WAYPOINT COUNT: ~11 (8 perimeter points + takeoff + rtl)

PATTERN:
           N
           |
       NW  |  NE
         \ | /
    W ----HOME---- E
         / | \
       SW  |  SE
           |
           S

USE CASES:
  - Border patrol
  - Perimeter monitoring
  - Airspace boundary verification
  - Area boundary check before grid

EXAMPLE:
  perim_wps = generate_perimeter_route(33.6425, 73.0232, 50.0)
```

---

### Map Visualization Functions

#### initialize_mission_map()
```python
SIGNATURE:
  initialize_mission_map(
    home_lat: float,
    home_lon: float,
    zoom_start: int = 16
  ) -> folium.Map

PURPOSE: Create base map centered at home location

TILE LAYER: OpenStreetMap (default Folium tiles)

ZOOM LEVELS:
  - 12-14: Regional view (1-5 km across)
  - 15-16: Neighborhood view (200-800 m across)
  - 17-19: Street view (50-200 m across)

MARKER: Blue "Home" marker at (home_lat, home_lon)

EXAMPLE:
  base_map = initialize_mission_map(33.6425, 73.0232)
  # Map centered at coordinates, zoomed to street level
```

#### add_waypoint_markers()
```python
SIGNATURE:
  add_waypoint_markers(
    mission_map: folium.Map,
    waypoints: List[Dict[str, Any]]
  ) -> folium.Map

PURPOSE: Add numbered markers for each waypoint

MARKER COLORS:
  - Green: Takeoff
  - Blue: Waypoint (cruise)
  - Red: RTL (Return-to-Launch)
  - Gray: Other actions

MARKER INFORMATION:
  - Popup: Shows full waypoint details
  - Tooltip: Shows sequence number on hover
  - Icon: Font Awesome icon for action type

EXAMPLE:
  mission_map = add_waypoint_markers(mission_map, waypoints)
  # Map now shows 0, 1, 2, 3, 4, 5 markers
```

#### draw_flight_path()
```python
SIGNATURE:
  draw_flight_path(
    mission_map: folium.Map,
    waypoints: List[Dict[str, Any]]
  ) -> folium.Map

PURPOSE: Draw polyline connecting waypoints in sequence

LINE STYLE:
  - Color: Blue (#1E90FF)
  - Weight: 4 pixels
  - Opacity: 0.85 (slightly transparent)
  - Pattern: Dashed (8px dash, 6px gap)

PURPOSE OF DASHED STYLE:
  - Indicates "planned" path (not yet executed)
  - Standard convention in UAV GCS software
  - Distinguishes from actual flight path

EXAMPLE:
  mission_map = draw_flight_path(mission_map, waypoints)
  # Map shows blue dashed line: 0 -> 1 -> 2 -> 3 -> 4 -> 5
```

#### add_no_fly_zone()
```python
SIGNATURE:
  add_no_fly_zone(
    mission_map: folium.Map,
    zone_name: str,
    zone_bounds: Dict[str, float],
    color: str = "red",
    fill_opacity: float = 0.3
  ) -> folium.Map

PURPOSE: Draw no-fly zone polygon on map

ZONE BOUNDS STRUCTURE:
  {
    "north": 33.65,   # Northern latitude boundary
    "south": 33.63,   # Southern latitude boundary
    "east": 73.03,    # Eastern longitude boundary
    "west": 73.01     # Western longitude boundary
  }

POLYGON STYLE:
  - Border: Solid line in specified color
  - Fill: Transparent fill in same color
  - Opacity: 0.3 (30%) to not obscure map

INFORMATION:
  - Popup: Zone name and type
  - Tooltip: Zone name on hover

EXAMPLE:
  bounds = {"north": 33.65, "south": 33.63, "east": 73.03, "west": 73.01}
  mission_map = add_no_fly_zone(mission_map, "Airport Buffer", bounds)
  # Red polygon displayed on map
```

#### create_mission_map()
```python
SIGNATURE:
  create_mission_map(
    home_lat: float,
    home_lon: float,
    waypoints: List[Dict[str, Any]],
    no_fly_zones: Optional[List[Dict[str, Any]]] = None
  ) -> folium.Map

PURPOSE: Main entry point - create complete mission visualization

CALLS IN SEQUENCE:
  1. initialize_mission_map()    -> Base map with home marker
  2. add_waypoint_markers()      -> All waypoint markers
  3. draw_flight_path()         -> Connecting polyline
  4. add_no_fly_zone()          -> Each no-fly zone polygon

EXAMPLE:
  mission_map = create_mission_map(
    home_lat=33.6425,
    home_lon=73.0232,
    waypoints=waypoint_list,
    no_fly_zones=nfz_list
  )
  st_folium(mission_map, width=1000, height=600)
```

---

## COORDINATE SYSTEM REFERENCE

### Coordinate Conversion Formulas

**Problem:** Maps use latitude/longitude (degrees), but we need to place waypoints at specific distances (meters) from home.

**Solution:** Convert meters to degrees offset

```
meters_per_degree_latitude = 111,000 m/degree  (constant)

For longitude:
  meters_per_degree_longitude = 111,000 * cos(latitude_radians)
  
This is because longitude lines converge toward poles.

EXAMPLE:
  Home: 33.6425 N, 73.0232 E
  Target: 100 meters east
  
  1. Convert latitude to radians:
     lat_rad = 33.6425 * pi / 180 = 0.5870 radians
  
  2. Calculate meters per degree:
     m_per_deg_lat = 111,000
     m_per_deg_lon = 111,000 * cos(0.5870) = 111,000 * 0.8355 = 92,740
  
  3. Calculate degree offset:
     lat_offset = 0 / 111,000 = 0.0000 degrees
     lon_offset = 100 / 92,740 = 0.001077 degrees
  
  4. Calculate final coordinates:
     new_lat = 33.6425 + 0.0000 = 33.6425
     new_lon = 73.0232 + 0.001077 = 73.0243
```

### Session State Coordinates

**Islamabad International Airport (Reference):**
```
Latitude:  33.6425 N
Longitude: 73.0232 E
Elevation: 507 m
```

**Default Test Area:**
```
Home Position: 33.6425, 73.0232
Square Size: 100 meters
Grid Size: 3x3 (default)
Perimeter Radius: 150 meters
```

---

## SESSION STATE VARIABLES

```python
# Location & Route Parameters
st.session_state.home_lat = 33.6425           # Home latitude
st.session_state.home_lon = 73.0232           # Home longitude
st.session_state.altitude = 50.0              # Flight altitude in meters
st.session_state.route_pattern = "square"     # Pattern type

# Generated Data
st.session_state.active_waypoints = []        # List of waypoint dicts
st.session_state.no_fly_zones = []            # List of zone dicts

# Safety & Compliance
st.session_state.safety_checks = []           # Safety check results
st.session_state.is_safe = False              # Overall safety status

# Mission Info
st.session_state.mission_name = ""
st.session_state.mission_type = ""
st.session_state.duration = 15.0              # Estimated flight time

# UI Navigation
st.session_state.current_page = "Home"
st.session_state.selected_db_mission = None
```

---

## TESTING QUICK REFERENCE

### Unit Tests

```bash
# Test 1: Import verification
python -c "from agents.waypoint_planner_agent import generate_waypoints; print('OK')"

# Test 2: Square pattern
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
assert len(wps) == 6
print('Square: OK')"

# Test 3: Grid pattern
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'grid')
assert len(wps) > 6
print('Grid: OK')"

# Test 4: Perimeter pattern
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'perimeter')
assert len(wps) > 3
print('Perimeter: OK')"

# Test 5: Map creation
python -c "
from utils.map_utils import create_mission_map
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
m = create_mission_map(33.6425, 73.0232, wps)
print('Map: OK')"
```

### Integration Tests (Streamlit)

```bash
# Start app
streamlit run app.py

# Then in browser:
# 1. Test route pattern selector updates map
# 2. Test home location change updates map center
# 3. Test altitude change updates waypoints
# 4. Test no-fly zone visibility
# 5. Test map interactivity (zoom, pan, click)
```

---

## GIT WORKFLOW SUMMARY

```bash
# Day 1-5 workflow
git status                          # Check status
git add <files>                     # Stage changes
git commit -m "Day N: Description" # Commit with message
git push origin main               # Push to GitHub
git log --oneline -5               # Verify commits

# Example commits:
# Day 1: Verify waypoint planner with square route generation
# Day 2: Verify all route patterns and app integration
# Day 3: Create map utilities and home location pinning
# Day 4: Integrate flight vectors and waypoint visualization
# Day 5: Complete no-fly zone visualization and verification
```

---

## COMMON ERRORS & SOLUTIONS

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: folium` | folium not installed | `pip install folium` |
| `No attribute 'st_folium'` | streamlit-folium not installed | `pip install streamlit-folium` |
| Map not displaying | st_folium not imported/called | Add `from streamlit_folium import st_folium` and call it |
| Waypoints at wrong location | Lat/lon swapped | Check function call uses (lat, lon) order |
| No-fly zones hidden | Behind waypoints | Check z-order or reduce zone opacity |
| Map update lag | Too many markers | Limit marker count or simplify zones |

---

## NEXT STEPS AFTER PHASE 2

1. **Phase 3:** Safety Compliance & Correction Agents
   - Validate missions against no-fly zones
   - Suggest corrections for unsafe routes
   - Implement rule-based checking

2. **Phase 4:** Mission Reporting & Export
   - Generate PDF mission plans
   - Export CSV waypoints
   - Generate JSON mission data

3. **Phase 5:** Database Integration
   - Save missions to SQLite
   - Load previous missions
   - Mission history and versioning

---

## REFERENCES

- **Folium Docs:** https://folium.readthedocs.io/
- **Streamlit Docs:** https://docs.streamlit.io/
- **Project GitHub:** https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner
- **Coordinate Systems:** https://en.wikipedia.org/wiki/Decimal_degrees

---

**Document Version:** 1.0  
**Prepared for:** Abdul Azeem Hashmi  
**5th Semester Undergraduate - Internship Project**  
**Date:** 2026-07-02
