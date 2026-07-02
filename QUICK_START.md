# 5-DAY QUICK START GUIDE: Exact Commands and Code

**Student:** Abdul Azeem Hashmi  
**Email:** abdulazeemhashmi29@gmail.com  
**GitHub:** https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner  
**Local Path:** C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner

---

## PREREQUISITES CHECK

Before starting, verify you have:

```powershell
# Check Python version (3.8 or higher required)
python --version

# Check Git is installed
git --version

# Navigate to workspace
cd C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner

# Verify virtual environment is activated (you should see (.venv) in prompt)
# If not activated, run:
.\.venv\Scripts\Activate.ps1

# Verify dependencies installed
pip list | Select-String "streamlit\|folium\|pandas"
```

---

## DAY 1: VERIFY WAYPOINT PLANNER

### 1.1 Test Waypoint Generation

```powershell
# Navigate to workspace
cd C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner

# Test imports
python -c "from agents.waypoint_planner_agent import generate_waypoints; print('Waypoint module imported successfully!')"

# Test square route generation
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
print(f'Generated {len(wps)} waypoints for square pattern')
for wp in wps:
    print(f'  Seq {wp[\"sequence_no\"]}: ({wp[\"latitude\"]:.4f}, {wp[\"longitude\"]:.4f}) - {wp[\"action\"]}')
"
```

**Expected Output:**
```
Generated 6 waypoints for square pattern
  Seq 0: (33.6425, 73.0232) - takeoff
  Seq 1: (33.6430, 73.0237) - waypoint
  Seq 2: (33.6430, 73.0227) - waypoint
  Seq 3: (33.6420, 73.0227) - waypoint
  Seq 4: (33.6420, 73.0237) - waypoint
  Seq 5: (33.6425, 73.0232) - rtl
```

### 1.2 Commit to Git

```powershell
# Check status
git status

# See all changes
git diff

# Stage all changes
git add agents/waypoint_planner_agent.py

# Commit
git commit -m "Day 1: Verify waypoint planner with square route generation

- Confirmed generate_waypoints() function works correctly
- Square pattern generates 6 waypoints as expected
- Takeoff at seq 0, RTL at final sequence
- All waypoints include: sequence_no, latitude, longitude, altitude, action"

# Push to main branch
git push origin main

# Verify push
git log --oneline -3
```

---

## DAY 2: TEST ALL ROUTE PATTERNS

### 2.1 Test Grid and Perimeter Patterns

```powershell
# Test all three patterns
python -c "
from agents.waypoint_planner_agent import generate_waypoints

print('=== SQUARE PATTERN ===')
square_wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
print(f'Generated {len(square_wps)} waypoints')
print(f'First: {square_wps[0][\"action\"]}, Last: {square_wps[-1][\"action\"]}')

print('\n=== GRID PATTERN ===')
grid_wps = generate_waypoints(33.6425, 73.0232, 50.0, 'grid')
print(f'Generated {len(grid_wps)} waypoints')
print(f'First: {grid_wps[0][\"action\"]}, Last: {grid_wps[-1][\"action\"]}')

print('\n=== PERIMETER PATTERN ===')
perim_wps = generate_waypoints(33.6425, 73.0232, 50.0, 'perimeter')
print(f'Generated {len(perim_wps)} waypoints')
print(f'First: {perim_wps[0][\"action\"]}, Last: {perim_wps[-1][\"action\"]}')
"
```

**Expected Output:**
```
=== SQUARE PATTERN ===
Generated 6 waypoints
First: takeoff, Last: rtl

=== GRID PATTERN ===
Generated 13 waypoints
First: takeoff, Last: rtl

=== PERIMETER PATTERN ===
Generated 11 waypoints
First: takeoff, Last: rtl
```

### 2.2 Test in Streamlit App

```powershell
# Start the Streamlit app
streamlit run app.py

# In browser:
# 1. Go to "Mission Input" page
# 2. Find Route Pattern selectbox
# 3. Select "square" - verify 6 waypoints shown
# 4. Select "grid" - verify grid waypoints shown
# 5. Select "perimeter" - verify perimeter waypoints shown
# 6. Check that app.py session state updates active_waypoints
```

### 2.3 Commit to Git

```powershell
git status
git add -A
git commit -m "Day 2: Verify all route patterns and app integration

- Tested generate_square_route() generates 6 waypoints
- Tested generate_grid_route() generates lawn-mower pattern
- Tested generate_perimeter_route() generates circular boundary
- All patterns include Takeoff (seq 0) and RTL (final sequence)
- Verified app.py integration with route pattern selectbox
- Confirmed real-time waypoint updates on pattern selection"

git push origin main
```

---

## DAY 3: CREATE MAP UTILITIES

### 3.1 Verify Folium Installation

```powershell
# Check if folium is installed
python -c "import folium; print(f'Folium version: {folium.__version__}')"

# If error, install:
pip install folium==0.16.0 streamlit-folium==0.18.0

# Update requirements.txt
pip freeze > requirements.txt
```

### 3.2 Test Map Utilities

```powershell
# Test map creation
python -c "
from utils.map_utils import initialize_mission_map, add_waypoint_markers, draw_flight_path
from agents.waypoint_planner_agent import generate_waypoints

home_lat, home_lon = 33.6425, 73.0232
altitude = 50.0

print('Creating base map...')
map_obj = initialize_mission_map(home_lat, home_lon)
print(f'Map center: ({map_obj.location[0]}, {map_obj.location[1]})')

print('Generating waypoints...')
waypoints = generate_waypoints(home_lat, home_lon, altitude, 'square')
print(f'Generated {len(waypoints)} waypoints')

print('Adding markers...')
map_obj = add_waypoint_markers(map_obj, waypoints)
print('Markers added')

print('Drawing flight path...')
map_obj = draw_flight_path(map_obj, waypoints)
print('Flight path drawn')

print('SUCCESS: Map utilities working correctly!')
"
```

**Expected Output:**
```
Creating base map...
Map center: (33.6425, 73.0232)
Generating waypoints...
Generated 6 waypoints
Adding markers...
Markers added
Drawing flight path...
Flight path drawn
SUCCESS: Map utilities working correctly!
```

### 3.3 Commit to Git

```powershell
git status
git add utils/map_utils.py
git commit -m "Day 3: Create map utilities and home location pinning

- Added utils/map_utils.py with comprehensive mapping functions
- initialize_mission_map() creates base Folium map at home location
- add_waypoint_markers() displays numbered markers for each waypoint
- draw_flight_path() connects waypoints with PolyLine (dashed)
- create_mission_map() combines all elements into complete visualization
- All functions tested and working correctly"

git push origin main
```

---

## DAY 4: INTEGRATE MAPS INTO STREAMLIT

### 4.1 Test Map Display in Streamlit

```powershell
# Start Streamlit app
streamlit run app.py

# In browser, perform these tests:
# 1. Navigate to Map View page
# 2. Look for:
#    - Blue marker at home location (labeled "Home / Takeoff Point")
#    - Green/blue markers for each waypoint (numbered)
#    - Red marker for RTL waypoint
#    - Blue dashed line connecting all waypoints
# 3. Test interactions:
#    - Click on markers - popups should show
#    - Hover over markers - tooltips should show
#    - Zoom in/out - map should respond
#    - Pan left/right - map should respond
# 4. Change route pattern on Mission Input page
#    - Verify map updates automatically
#    - No manual refresh needed
```

### 4.2 Add No-Fly Zone Test

```powershell
# Check that no-fly zones display (if already in app)
# In Streamlit:
# 1. Go to Map View page
# 2. Look for red polygons (no-fly zones)
# 3. Verify they don't obscure waypoints
# 4. Hover over zones to see names
```

### 4.3 Commit to Git

```powershell
git status
git add -A
git commit -m "Day 4: Integrate flight vectors and waypoint visualization

- Verified waypoint markers display on map with correct colors
- Verified flight path polyline connects all waypoints in sequence
- Verified home location pinning with distinctive blue marker
- Tested real-time map updates on route pattern changes
- Tested interactive map features (zoom, pan, click, hover)
- All map visualizations working correctly in Streamlit"

git push origin main
```

---

## DAY 5: FINAL VERIFICATION & COMPLETION

### 5.1 Run Complete Test Suite

```powershell
# Test 1: All imports work
python -c "
from agents.waypoint_planner_agent import generate_waypoints
from utils.map_utils import create_mission_map
from agents.mission_understanding_agent import understand_mission
from agents.safety_compliance_agent import perform_safety_checks
from utils.database_utils import init_db
print('All imports successful!')
"

# Test 2: Waypoint generation for all patterns
python -c "
from agents.waypoint_planner_agent import generate_waypoints

patterns = ['square', 'grid', 'perimeter']
for pattern in patterns:
    wps = generate_waypoints(33.6425, 73.0232, 50.0, pattern)
    print(f'{pattern.upper()}: {len(wps)} waypoints (first={wps[0][\"action\"]}, last={wps[-1][\"action\"]})')
"

# Test 3: Map creation with no-fly zones
python -c "
from utils.map_utils import create_mission_map
from agents.waypoint_planner_agent import generate_waypoints

wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
no_fly_zones = [
    {
        'name': 'Test Zone',
        'bounds': {'north': 33.65, 'south': 33.63, 'east': 73.03, 'west': 73.01},
        'color': 'red'
    }
]
map_obj = create_mission_map(33.6425, 73.0232, wps, no_fly_zones)
print('Map with no-fly zones created successfully!')
"

# Test 4: Streamlit app
echo 'Starting Streamlit app for manual testing...'
streamlit run app.py
```

### 5.2 Manual Testing Checklist

```powershell
# In Streamlit browser window, verify:
# [ ] Mission Input page - route pattern selectbox visible
# [ ] Mission Input page - home location inputs visible
# [ ] Mission Input page - altitude input visible
# [ ] Mission Plan page - waypoint table displays
# [ ] Map View page - home marker visible (blue)
# [ ] Map View page - waypoint markers visible (green/blue)
# [ ] Map View page - RTL marker visible (red)
# [ ] Map View page - flight path line visible (blue dashed)
# [ ] Map View page - no-fly zone polygons visible (red)
# [ ] Map is interactive (zoom, pan work)
# [ ] Markers have popups (click to see)
# [ ] Markers have tooltips (hover to see)
# [ ] Changing pattern updates map in real-time
# [ ] No console errors
# [ ] No lag or freezing
```

### 5.3 Final Git Commit

```powershell
# Verify git status
git status

# Add any remaining files
git add -A

# Final commit
git commit -m "Day 5: Complete no-fly zone visualization and verification

- Verified all route pattern generation functions work correctly
- Verified map utilities create complete visualizations
- Verified Streamlit UI integration for all pages
- Verified interactive map features (zoom, pan, click, hover)
- Verified no-fly zone display without interference
- Verified real-time map updates on parameter changes
- Completed delivery checklist: docs/DELIVERY_CHECKLIST.md
- All tests passed, ready for next phase"

# Push final changes
git push origin main

# Verify push
git log --oneline -10
```

### 5.4 Repository Verification

```powershell
# Verify all files exist
ls agents/waypoint_planner_agent.py
ls utils/map_utils.py
ls app.py
ls requirements.txt
ls IMPLEMENTATION_GUIDE.md
ls docs/DELIVERY_CHECKLIST.md
ls docs/project_progress.md

# Show Git log
git log --oneline -15

# Show current branch
git branch -v

# Show commits on main
git log --oneline --graph main -20
```

---

## FINAL CHECKLIST

- [ ] DAY 1: Waypoint planner verified and committed
- [ ] DAY 2: All route patterns tested and committed
- [ ] DAY 3: Map utilities created and committed
- [ ] DAY 4: Maps integrated and visualized in Streamlit
- [ ] DAY 5: Complete verification, all tests passed

**Final Verification Commands:**

```powershell
# Quick verification
python -c "
from agents.waypoint_planner_agent import generate_waypoints
from utils.map_utils import create_mission_map
wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
map_obj = create_mission_map(33.6425, 73.0232, wps)
print('Phase 2 Complete: All systems verified!')
"

git log --oneline -5
```

---

## TROUBLESHOOTING

### Problem: Import errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Map not showing
```powershell
# Verify imports in app.py
# Ensure st_folium is imported:
from streamlit_folium import st_folium

# Ensure map is being passed to st_folium
st_folium(mission_map, width=1000, height=600)
```

### Problem: Waypoints at wrong locations
```powershell
# Check that latitude/longitude aren't swapped
# Correct: (lat, lon) not (lon, lat)

# Test with known coordinates
python -c "
from agents.waypoint_planner_agent import generate_waypoints
wps = generate_waypoints(0.0, 0.0, 50.0, 'square')
# Should be near 0,0 coordinates
for wp in wps[:2]:
    print(f'{wp[\"latitude\"]}, {wp[\"longitude\"]}')"
```

### Problem: Git push fails
```powershell
# Verify you're on main branch
git branch

# Pull latest changes
git pull origin main

# Try push again
git push origin main

# If still failing, check remote
git remote -v
```

---

## ADDITIONAL RESOURCES

- **GitHub Repository:** https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner
- **Folium Documentation:** https://folium.readthedocs.io/
- **Streamlit Documentation:** https://docs.streamlit.io/
- **Project Progress:** docs/project_progress.md

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-02  
**Prepared for:** Abdul Azeem Hashmi, 5th Semester Undergraduate
