# SkyGuard AI - Agentic UAV Mission Planner & Safety Compliance Assistant

SkyGuard AI is a software application designed for UAV mission planning, route visualization, and safety compliance checks. It combines natural language inputs parsed by Gemini AI with robust rule-based safety checking and active route corrections.

## 🌟 Key Features

1. **Mission Understanding Agent**: Decodes natural language flight descriptions into structured variables (altitude, duration, patterns, home coordinates) using the Gemini API.
2. **Waypoint Planner Agent**: Generates 3D coordinates based on flight pattern geometry (Square, Circle, Grid, Perimeter, and Manual).
3. **Safety Compliance Agent**: Performs checks to prevent dangerous flight states (e.g. altitude limits, geofences/no-fly zones, battery constraints, leg distances).
4. **Correction Agent**: Recommends parameters and coordinate offsets to turn unsafe flights into compliant routes.
5. **Interactive Mapping**: Powered by Folium to draw takeoff locations, flight lines, and restricted airspace boundaries dynamically.
6. **Persistence**: Saves mission details, flight coordinates, and safety check logs to a local SQLite database.
7. **Multi-Format Exports**: Downloads plans in JSON format, waypoints in CSV format, and summaries as printable PDF briefs.

---

## 🛠️ Project Structure

```
agentic-uav-mission-planner/
├── app.py                     # Streamlit frontend entrypoint
├── requirements.txt           # Dependency definition
├── .env                       # Local secrets (GEMINI_API_KEY)
├── database/
│   └── missions.db            # SQLite mission database
├── data/
│   ├── sample_missions.csv    # Mock mission statistics
│   └── sample_waypoints.csv   # Mock flight coordinates
├── agents/
│   ├── mission_understanding_agent.py  # Gemini API parsing layer
│   ├── waypoint_planner_agent.py       # Geometric coordinate planners
│   ├── safety_compliance_agent.py      # Standard regulatory checks
│   ├── correction_agent.py             # Coordinate/rule auto-corrects
│   └── report_agent.py                 # HTML summary formatter
├── utils/
│   ├── database_utils.py      # SQLite schema CRUD
│   ├── map_utils.py           # Folium map overlays
│   ├── export_utils.py        # PDF, CSV, JSON compilers
│   └── distance_utils.py      # Haversine distance computations
└── tests/
    └── test_planner.py        # Comprehensive test coverage
```

---

## 🚀 Setup & Execution

### 1. Install Dependencies
Run the package installation using the virtual environment:
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file inside the `agentic-uav-mission-planner/` folder and include your Gemini token:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Start Application
Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```

### 4. Run Tests
Verify correct computations by executing:
```bash
python -m unittest tests/test_planner.py
```
