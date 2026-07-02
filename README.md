# Agentic UAV Mission Planning and Safety Compliance Assistant

**A two-month software internship project for UAV mission planning, route visualization, safety checking, and agentic workflow development.**

## Project Overview

This is an end-to-end software application for planning UAV missions using an agentic AI-based workflow. The system allows users to enter UAV mission requests in natural language or through a form, converts requests into structured mission plans, generates waypoints, visualizes routes on a map, checks safety rules, identifies issues, suggests corrections, and generates mission reports.

**No physical UAV hardware is required** - this is a software-based simulation project.

## Project Information

- **Student:** Abdul Azeem Hashmi
- **Email:** abdulazeemhashmi29@gmail.com
- **GitHub:** https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner
- **Project Domain:** Unmanned Aerial Vehicles (UAVs), Agentic AI, Safety Compliance
- **Project Type:** End-to-end software application
- **Recommended Duration:** 8 weeks (2 months)
- **Target Student Level:** 5th semester undergraduate
- **Core Technologies:** Python, Streamlit, SQLite, Pandas, Folium, GitHub

## Problem Statement

UAV mission planning requires careful definition of waypoints, altitude limits, mission duration, geofence restrictions, return-to-launch behavior, and safety constraints. Manual planning can lead to mistakes such as:
- Missing landing points
- Unsafe altitude values
- Routes crossing restricted zones
- Incomplete mission instructions

This project proposes a software assistant that helps users create safer, better-structured UAV mission plans using different agents/modules.

## Project Objectives

1. Develop a user-friendly UAV mission planning application
2. Allow users to enter mission requirements in natural language
3. Convert mission instructions into structured mission data
4. Generate UAV waypoints automatically
5. Visualize UAV mission routes on a map
6. Define and check no-fly zones/geofence areas
7. Verify mission safety using rule-based checks
8. Suggest corrections for unsafe or incomplete missions
9. Generate a mission summary report
10. Export mission data in JSON and CSV format

## Scope Covered

### Included in Scope
- Streamlit-based web interface
- Natural language mission input
- Manual mission input form
- Waypoint generation (square, grid, perimeter patterns)
- Mission route visualization with Folium maps
- No-fly zone/geofence definition and visualization
- Rule-based safety checking (7 safety rules)
- Agentic workflow with 5 specialized agents
- Mission correction suggestions
- Mission summary reports
- Mission export in JSON and CSV
- SQLite database for storing missions

### Not Included in Basic Scope
- Real UAV hardware integration
- Real-time UAV control
- Drone autopilot programming
- Live GPS tracking
- PX4/SITL simulation
- Advanced machine learning training
- Computer vision-based detection
- Anomaly detection

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Programming Language | Python 3.8+ |
| Web Framework | Streamlit |
| Data Handling | Pandas |
| Map Visualization | Folium / Streamlit-Folium |
| Database | SQLite |
| Charts | Matplotlib / Plotly |
| Export Formats | JSON, CSV, PDF/text report |
| Agentic Logic | Python functions (LangGraph optional) |
| Version Control | GitHub |
| IDE | VS Code |

## Key Features

1. **Mission Understanding Agent** - Extracts mission type, altitude, duration, route pattern, and safety constraints from natural language input using regex fallback and Google Gemini API
2. **Waypoint Planner Agent** - Generates waypoints for square, grid, and perimeter route patterns with takeoff and RTL points
3. **Safety Compliance Agent** - Implements 7 safety rules for mission validation
4. **Correction Agent** - Suggests corrections for failed safety checks
5. **Report Generation Agent** - Creates mission summary reports
6. **Interactive Map Visualization** - Shows home point, waypoints, flight path, and no-fly zones
7. **SQLite Database** - Stores missions for later retrieval
8. **Export Features** - Download missions as JSON, CSV, or PDF reports
- Waypoint Planner Agent for square, circle, grid, perimeter, and manual routes.
- Safety Compliance Agent for altitude, duration, geofence, distance, takeoff, RTL, and battery checks.
- Correction Agent for recommending safe revisions.
- Interactive map using Folium and Streamlit-Folium.
- SQLite persistence for missions, waypoints, and safety results.
- Data export to JSON, CSV, and PDF report files.

## Project Structure

```text
agentic-uav-mission-planner/
├── app.py
├── requirements.txt
├── README.md
├── agents/
├── utils/
├── data/
├── docs/
├── reports/
└── tests/
```

## Setup and Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a local `.env` file if you want to use Gemini-based NLP:
   ```env
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
   ```
3. Launch the app:
   ```bash
   streamlit run app.py
   ```
4. Run the tests:
   ```bash
   python -m unittest tests/test_planner.py
   ```

## Agentic Workflow Architecture

The system uses a modular agentic workflow with 5 specialized agents:

### Agent/Module Details

| Agent | Purpose |
|-------|---------|
| **Mission Understanding Agent** | Extracts mission type, altitude, duration, route pattern, and safety constraints from natural language using regex and Gemini API |
| **Waypoint Planner Agent** | Generates takeoff point, route waypoints, altitude values, sequence numbers, and return-to-launch point |
| **Safety Compliance Agent** | Checks altitude, duration, geofence/no-fly zone, waypoint distance, mission completeness, and battery usage |
| **Correction Agent** | Suggests corrections for failed safety checks (e.g., reduce altitude, move waypoints, adjust duration) |
| **Report Generation Agent** | Creates mission summary, waypoint table, safety checklist, final status, and exportable reports |

### Data Flow

```
User Input (Text/Form)
     |
     v
Mission Understanding Agent -> Structured Mission Data
     |
     v
Waypoint Planner Agent -> Waypoint List + Route
     |
     v
Safety Compliance Agent -> Safety Violations Found?
     |
     +-- YES --> Correction Agent -> Suggestions
     |
     +-- NO --> Report Agent -> Final Report
     |
     v
Export + Database Storage
```

## Safety Rules Enforced (7 Rules)

| Rule | Requirement | Example Failure |
|------|-------------|-----------------|
| **R1** | Maximum altitude must not exceed 80m | Altitude 120m = Fail |
| **R2** | Mission must include takeoff point | Missing takeoff = Fail |
| **R3** | Mission must include RTL or landing point | Missing RTL = Fail |
| **R4** | Waypoints must not enter no-fly zones | Waypoint inside restricted area = Fail |
| **R5** | Distance between consecutive waypoints max 500m | Distance 600m = Fail |
| **R6** | Mission duration must not exceed 30 minutes | Duration 45 minutes = Fail |
| **R7** | Estimated battery usage must stay below 80% | Estimated usage 95% = Fail |

## Waypoint Generation Patterns

1. **Square Route**: 6 waypoints forming a square perimeter around home
2. **Grid Route**: Lawn-mower pattern for area scanning and mapping (13+ waypoints)
3. **Perimeter Route**: Circular boundary patrol route (11 waypoints)
4. **Circle Route**: Circular orbit around home location
5. **Manual Route**: User-defined waypoint coordinates

## Application Pages

| Page | Content |
|------|---------|
| **Home** | Project title, description, and navigation |
| **Mission Input** | Mission name, type, NLP input, home location, altitude, duration, route pattern |
| **Mission Plan** | Extracted mission details, waypoint table, generated route parameters |
| **Map View** | Home marker, waypoint markers, flight path polyline, no-fly zone polygons |
| **Safety Check** | Safety checklist, passed checks, failed checks, final safety status |
| **Suggestions** | Issues found, recommended corrections, revised mission values |
| **Export** | Download mission JSON, waypoint CSV, text report |

## Database Schema

### Missions Table
- mission_id (INTEGER, Primary Key)
- mission_name (TEXT)
- mission_type (TEXT) - surveillance, delivery, inspection, search_and_rescue
- altitude (REAL)
- duration (REAL)
- status (TEXT) - Safe / Needs Revision
- created_at (TEXT)

### Waypoints Table
- waypoint_id (INTEGER, Primary Key)
- mission_id (INTEGER, Foreign Key)
- sequence_no (INTEGER)
- latitude (REAL)
- longitude (REAL)
- altitude (REAL)
- action (TEXT) - takeoff, waypoint, rtl, land

### Safety Checks Table
- check_id (INTEGER, Primary Key)
- mission_id (INTEGER, Foreign Key)
- check_name (TEXT)
- result (TEXT) - Pass / Fail
- message (TEXT)

## 8-Week Internship Plan

| Week | Focus | Tasks | Deliverable |
|------|-------|-------|-------------|
| 1 | Project Setup & Basics | Install tools, create app, learn UAV terms | GitHub repo, basic Streamlit app |
| 2 | Mission Data Model | Create mission form, waypoint structure | Mission input form, sample data |
| 3 | Waypoint Generation | Implement square/grid/perimeter routes | Waypoint planner module |
| 4 | Map Visualization | Folium integration, home/waypoints/routes | Interactive mission map |
| 5 | Safety Checking | Implement 7 safety rules | Safety checker module |
| 6 | Agentic Layer | Connect all agents, NLP integration | Agentic workflow |
| 7 | Database & Export | SQLite setup, JSON/CSV/PDF export | Database integration |
| 8 | Testing & Documentation | Full system testing, final report | Complete application |

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip and virtualenv
- Git
- Google Gemini API key (optional, for NLP features)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git
   cd agentic-uav-mission-planner
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file (optional for Gemini API):
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

5. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```

6. Access in browser:
   ```
   http://localhost:8501
   ```

## Usage Example

**User Input:**
> "Plan a surveillance mission around campus for 20 minutes. Keep altitude below 80 meters, avoid restricted zones, and return to launch after completion."

**System Output:**
1. Extracts: mission_type=surveillance, altitude=50m, duration=20m, route_pattern=square, rtl=true
2. Generates: 6 waypoints with takeoff and RTL points
3. Checks: All 7 safety rules (all pass)
4. Creates: Interactive map with waypoints and route
5. Exports: Mission JSON, waypoint CSV, mission report PDF

## Key Project Components

### agents/
- `mission_understanding_agent.py` - NLP parsing
- `waypoint_planner_agent.py` - Route generation
- `safety_compliance_agent.py` - Safety validation
- `correction_agent.py` - Correction suggestions
- `report_agent.py` - Report generation

### utils/
- `map_utils.py` - Folium map visualization
- `database_utils.py` - SQLite operations
- `export_utils.py` - JSON/CSV/PDF export
- `distance_utils.py` - Coordinate calculations

### docs/
- `uav_terms.md` - UAV terminology reference
- `project_progress.md` - Weekly progress tracking
- `DELIVERY_CHECKLIST.md` - Verification checklist

## Testing

Run unit tests:
```bash
python -m unittest tests/test_planner.py
```

## Documentation

- See `docs/uav_terms.md` for UAV terminology
- See `docs/project_progress.md` for progress tracking
- See `IMPLEMENTATION_GUIDE.md` for Phase 2 details
- See `DELIVERY_CHECKLIST.md` for completeness verification

## Future Enhancements

1. QGroundControl .plan file export
2. PX4 SITL simulation integration
3. Multi-UAV mission planning
4. Real drone integration
5. Advanced battery consumption modeling
6. Weather-aware mission planning
7. Voice-based mission input
8. LLM-based mission understanding with function calling
9. Human approval workflow
10. Formal verification of UAV constraints

## License

This project is developed as part of an internship program for educational and academic demonstration purposes.

## Contact

- **Student:** Abdul Azeem Hashmi
- **Email:** abdulazeemhashmi29@gmail.com
- **GitHub:** https://github.com/AbdulAzeemHashmi
- **Project:** Agentic UAV Mission Planning and Safety Compliance Assistant
