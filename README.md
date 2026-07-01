# SkyGuard AI - Agentic UAV Mission Planner and Safety Compliance Assistant

SkyGuard AI is a Streamlit-based web application for intelligent UAV mission planning, interactive route visualization, and automated safety compliance checking. It combines natural language parsing powered by the Gemini API with robust rule-based safety logic, geofence-aware route generation, and one-click auto-correction to help operators plan safe drone flights quickly and confidently.

---

## Key Features

1. **Mission Understanding Agent** - Parses natural language flight descriptions into structured mission parameters (altitude, duration, pattern, home coordinates) using the Gemini 1.5 Flash API. Falls back to a regex-based parser when the API is unavailable.
2. **Waypoint Planner Agent** - Generates sequential 3D flight coordinates (latitude, longitude, altitude) for five route patterns: Square, Circle, Grid, Perimeter, and Manual.
3. **Safety Compliance Agent** - Enforces seven regulatory rules covering altitude limits, geofence boundaries, takeoff/landing sequences, leg distances, mission duration, and estimated battery consumption.
4. **Correction Agent** - Automatically recommends and applies parameter fixes and coordinate nudges when safety checks fail, turning non-compliant missions into approved flight plans.
5. **Interactive Map** - Folium-powered live map renders waypoint markers, flight path polylines, and restricted airspace overlays in the browser.
6. **Mission Database** - SQLite persistence stores complete mission records (metadata, waypoints, and safety logs) for historical review and audit trails.
7. **Multi-Format Export** - Download flight plans as JSON, waypoints as CSV, and full mission summaries as PDF reports.

---

## Project Structure

```
agentic-uav-mission-planner/
|-- app.py                              # Streamlit frontend entry point
|-- requirements.txt                   # Python dependency list
|-- .env                               # Local secrets file (GEMINI_API_KEY)
|-- .gitignore                         # Git ignore rules
|
|-- agents/
|   |-- __init__.py
|   |-- mission_understanding_agent.py # Gemini NLP parsing layer
|   |-- waypoint_planner_agent.py      # Geometric coordinate generator
|   |-- safety_compliance_agent.py     # Rule-based safety checker
|   |-- correction_agent.py            # Auto-correction engine
|   |-- report_agent.py                # HTML summary formatter
|
|-- utils/
|   |-- __init__.py
|   |-- database_utils.py              # SQLite schema and CRUD operations
|   |-- map_utils.py                   # Folium map builder
|   |-- export_utils.py                # PDF, CSV, and JSON exporters
|   |-- distance_utils.py              # Haversine and bearing calculations
|
|-- data/
|   |-- sample_missions.csv            # Sample mission statistics
|   |-- sample_waypoints.csv           # Sample flight coordinates
|
|-- docs/
|   |-- uav_terms.md                   # UAV terminology reference guide
|
|-- tests/
|   |-- test_planner.py                # Unit tests covering all core modules
|
|-- reports/
|   |-- generated_reports/             # Auto-generated PDF output directory
```

---

## Safety Compliance Rules

SkyGuard AI enforces the following seven rules on every mission plan before approval:

| Rule | Description | Limit |
|------|-------------|-------|
| R1 | Maximum altitude | 80 m |
| R2 | Mission must begin with a takeoff waypoint | Required |
| R3 | Mission must end with RTL or land action | Required |
| R4 | No waypoint may enter a no-fly zone or geofence | Zero violations |
| R5 | Maximum distance between consecutive waypoints | 500 m |
| R6 | Maximum planned flight duration | 30 minutes |
| R7 | Estimated battery consumption (2% per min + 0.04% per meter) | Below 80% |

---

## Active No-Fly Zones

The application ships with two pre-configured restricted airspace zones centered near FAST-NUCES Islamabad:

- **Zone A (Circular)** - Restricted Military Airspace at (33.6438, 73.0210), radius 120 m
- **Zone B (Polygon)** - High Voltage Grid Facility bounding box near (33.6410, 73.0255)

---

## Setup and Execution

### Step 1 - Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2 - Configure Gemini API Key

Create a `.env` file in the project root directory and add your Gemini API token:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

If no valid key is provided, the application automatically uses the built-in regex fallback parser for natural language input processing.

### Step 3 - Launch the Application

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

### Step 4 - Run Unit Tests

```bash
python -m unittest tests/test_planner.py
```

---

## Agentic Workflow

```
User Input (NL or Form)
        |
        v
Mission Understanding Agent  <-- Gemini 1.5 Flash / Regex fallback
        |
        v
Waypoint Planner Agent       <-- Square / Circle / Grid / Perimeter / Manual
        |
        v
Safety Compliance Agent      <-- 7 Rule checks (R1 to R7)
        |
       / \
      /   \
  Pass    Fail
    |       |
    |       v
    |  Correction Agent  <-- Auto-fix altitude, duration, geofence offsets
    |       |
    v       v
Report Agent + Map + Export  <-- HTML summary, Folium map, PDF/CSV/JSON
        |
        v
SQLite Database              <-- Persist mission, waypoints, safety logs
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit 1.32 |
| NLP Agent | Google Gemini 1.5 Flash (google-generativeai 0.4.1) |
| Map Rendering | Folium 0.16 + streamlit-folium 0.18 |
| Geofence Checks | Shapely 2.0.3 |
| Data Handling | Pandas 2.2.1 |
| Database | SQLite3 (built-in Python) |
| PDF Export | ReportLab 4.1 |
| Charts | Matplotlib 3.8.3 |
| Distance Math | Haversine formula (custom implementation) |

---

## Usage Guide

### Natural Language Planning

Type a plain English flight request in the Natural Language Input tab, for example:

```
Plan a 20-minute surveillance mission over FAST campus at 70 meters altitude using a circular orbit pattern. Enable return-to-launch and avoid all restricted zones.
```

The Mission Understanding Agent extracts all parameters and the system generates a full flight plan instantly.

### Manual Configuration

Use the Manual Configuration Form tab to set mission name, type, altitude, duration, home coordinates, and route pattern using form controls.

### Reviewing Safety Results

The right-hand panel on the Mission Planner page shows a live safety checklist. Red rows indicate failing rules. Click **Apply Auto-Corrections** to resolve violations automatically.

### Saving and Exporting

Click **Save Mission to Database** to persist the plan. Navigate to the **History and Database** page to load past missions and download them as JSON, CSV, or PDF.

---

## Repository Information

- **GitHub**: [https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner)
- **Branch**: main
- **Author**: Abdul Azeem Hashmi
- **Email**: abdulazeemhashmi29@gmail.com

---

## License

This project is developed as part of an internship program. All rights reserved by the author.
