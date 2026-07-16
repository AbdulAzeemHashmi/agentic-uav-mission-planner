<div align="center">

# 🛸 Agentic UAV Mission Planner

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Folium](https://img.shields.io/badge/Folium-Map-77B829?style=for-the-badge)](https://python-visualization.github.io/folium/)
[![License](https://img.shields.io/badge/License-Academic-green?style=for-the-badge)](LICENSE)

<br/>

> **An end-to-end software application for planning UAV missions through an agentic AI workflow.**  
> Accepts natural language mission requests, generates waypoints, validates airspace safety rules,  
> suggests corrections, and produces exportable flight plans and compliance reports.

> 🔒 **No physical UAV hardware required.**  
> This is a fully software-based simulation project.

</div>

---

## 📋 Table of Contents

- [🎯 Problem Statement](#-problem-statement)
- [🏗️ System Architecture](#%EF%B8%8F-system-architecture)
- [🤖 Agentic Workflow](#-agentic-workflow)
- [✨ Key Features](#-key-features)
- [🛡️ Safety Rules](#%EF%B8%8F-safety-rules)
- [🗺️ Waypoint Patterns](#%EF%B8%8F-waypoint-generation-patterns)
- [📦 Technology Stack](#-technology-stack)
- [📁 Project Structure](#-project-structure)
- [⚙️ Setup and Run](#%EF%B8%8F-setup-and-run)
- [🖥️ Application Pages](#%EF%B8%8F-application-pages)
- [🗄️ Database Schema](#%EF%B8%8F-database-schema)
- [📅 8-Week Internship Plan](#-8-week-internship-plan)
- [🔮 Future Enhancements](#-future-enhancements)

---

## 🎯 Problem Statement

UAV mission planning requires careful definition of waypoints, altitude limits, mission duration, geofence restrictions, return-to-launch behaviour, and safety constraints. Manual planning can lead to mistakes such as:

| Problem | Impact |
|---|---|
| 🔴 Missing landing points | UAV never returns home |
| 🔴 Unsafe altitude values | Airspace regulation violation |
| 🔴 Routes crossing restricted zones | Collision or legal penalty |
| 🔴 Incomplete mission instructions | Mission abort mid-flight |

This project proposes a software assistant that helps users create safer and better-structured UAV mission plans through an agentic workflow.

---

## 🏗️ System Architecture

```
User Input (Natural Language / Form)
         |
         v
Streamlit Interface
         |
         v
Mission Understanding Agent
         |
         v
Waypoint Planner Agent
         |
         v
Safety Compliance Agent
         |
         v
Correction Agent
         |
         v
Report Generation Agent
         |
         v
Mission Export / Database / Map Visualization
```

---

## 🤖 Agentic Workflow

The system uses **5 specialized agents**, initially implemented as Python modules. An LLM API (Google Gemini) is used for natural language parsing with a regex fallback.

| Agent | File | Purpose |
|---|---|---|
| 🧠 **Mission Understanding** | `agents/mission_understanding_agent.py` | Parses natural language via Gemini API (regex fallback), extracts mission type, altitude, duration, route pattern, and safety constraints |
| 📍 **Waypoint Planner** | `agents/waypoint_planner_agent.py` | Generates takeoff, route waypoints, altitude values, sequence numbers, and RTL point for 4 flight patterns |
| 🛡️ **Safety Compliance** | `agents/safety_compliance_agent.py` | Enforces 7 airspace rules - altitude, RTL, geofence, waypoint distance, duration, and battery estimate |
| 🔧 **Correction** | `agents/correction_agent.py` | Suggests corrections for failed safety checks: altitude clipping, waypoint relocation outside no-fly zones, duration reduction |
| 📄 **Report Generation** | `agents/report_agent.py` | Generates HTML mission summary with safety checklist, flight metrics, and approval status |

### Example Natural Language Input

```
Plan a surveillance mission around FAST campus for 20 minutes.
Keep altitude below 80 meters, avoid restricted zones,
and return to launch after completion.
```

### Example Extracted Output (Mission Understanding Agent)

```json
{
  "mission_type": "surveillance",
  "altitude": 60,
  "duration": 20,
  "return_to_launch": true,
  "avoid_no_fly_zone": true,
  "route_pattern": "square"
}
```

---

## ✨ Key Features

- 🗣️ **Natural language mission input** - parsed by Google Gemini API with regex fallback
- 📝 **Manual input form** - mission name, type, altitude, duration, route pattern, home coordinates
- 📍 **Waypoint generation** - square, grid, circle, and perimeter route patterns
- 🗺️ **Interactive map view** - home point, waypoint markers, flight path, no-fly zone overlays (Folium)
- 🛡️ **7-rule safety checker** - altitude, RTL, takeoff, geofence, leg distance, duration, battery
- 💡 **Correction suggestions** - actionable fixes for every failed safety rule
- 📄 **Mission summary report** - inline HTML report with checklist and approval status
- 💾 **SQLite database** - stores missions, waypoints, and safety check results
- 📥 **Export** - Mission JSON, Waypoints CSV, PDF report

---

## 🛡️ Safety Rules

| Rule | Description | Threshold |
|---|---|---|
| **R1** | Maximum altitude limit | ≤ 80 m |
| **R2** | Mission must include takeoff point | Required |
| **R3** | Mission must include RTL or landing point | Required |
| **R4** | Waypoints must not enter no-fly zones | All zones clear |
| **R5** | Max distance between consecutive waypoints | ≤ 500 m |
| **R6** | Mission duration limit | ≤ 30 min |
| **R7** | Estimated battery usage | < 80% |

---

## 🗺️ Waypoint Generation Patterns

| Pattern | Description |
|---|---|
| **Square** | 4-corner patrol route centered on home point |
| **Grid** | Lawn-mower scan pattern for area mapping |
| **Circle** | 8-point orbital path around home point |
| **Perimeter** | 4-point perimeter boundary patrol |

All patterns automatically include a **Takeoff** point at start and **RTL** at end.

---

## 📦 Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web App Framework | Streamlit |
| Data Handling | Pandas |
| Map Visualization | Folium / Streamlit-Folium |
| Database | SQLite |
| Charts | Matplotlib / Plotly |
| Geospatial Checks | Shapely |
| Export | JSON, CSV, PDF (ReportLab) |
| Agentic Logic | Python functions + Google Gemini API |
| Version Control | GitHub |
| IDE | VS Code |

---

## 📁 Project Structure

```
agentic-uav-mission-planner/
|
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
|
├── database/
|   └── missions.db                 # SQLite database file
|
├── data/
|   ├── sample_missions.csv         # Sample mission data
|   └── sample_waypoints.csv        # Sample waypoint data
|
├── agents/
|   ├── mission_understanding_agent.py   # NL → structured mission data
|   ├── waypoint_planner_agent.py        # Route waypoint generator
|   ├── safety_compliance_agent.py       # 7-rule safety checker
|   ├── correction_agent.py              # Correction suggestions
|   └── report_agent.py                  # Mission summary HTML report
|
├── utils/
|   ├── database_utils.py           # SQLite CRUD operations
|   ├── map_utils.py                # Folium map builder
|   ├── export_utils.py             # JSON, CSV, PDF exporters
|   └── distance_utils.py           # Haversine & bearing math
|
├── reports/
|   └── generated_reports/          # Saved PDF reports
|
└── docs/
    ├── uav_terms.md                # UAV terminology reference
    ├── project_report.docx         # Final project report
    ├── user_manual.pdf             # User manual
    └── presentation.pptx           # Presentation slides
```

---

## ⚙️ Setup and Run

### 1. Clone the repository

```bash
git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git
cd agentic-uav-mission-planner
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# or
source .venv/bin/activate     # Linux/macOS
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key (optional)

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

> If no API key is provided, the Mission Understanding Agent automatically falls back to regex-based parsing.

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🖥️ Application Pages

| Page | Content |
|---|---|
| **Home** | Project title, short description, safety rules summary |
| **Mission Input** | Natural language input + manual form (name, type, altitude, duration, pattern, coordinates) |
| **Mission Plan** | Extracted mission details, generated waypoint table, mission summary report |
| **Map View** | Home point, UAV waypoints with markers, route path line, no-fly zone polygons |
| **Safety Check** | Safety checklist (R1-R7), pass/fail per rule, final mission status, save to DB |
| **Suggestions** | Issues found and recommended corrections |
| **Export** | Download Mission JSON, Waypoints CSV, PDF Report |

---

## 🗄️ Database Schema

### Missions Table

| Field | Type | Description |
|---|---|---|
| `mission_id` | INTEGER | Primary key (auto) |
| `mission_name` | TEXT | Name of mission |
| `mission_type` | TEXT | surveillance, delivery, inspection, etc. |
| `altitude` | REAL | Mission altitude in metres |
| `duration` | REAL | Mission duration in minutes |
| `status` | TEXT | Safe / Needs Revision |
| `created_at` | TEXT | Date and time |

### Waypoints Table

| Field | Type | Description |
|---|---|---|
| `waypoint_id` | INTEGER | Primary key (auto) |
| `mission_id` | INTEGER | Related mission (foreign key) |
| `sequence_no` | INTEGER | Waypoint order |
| `latitude` | REAL | Latitude |
| `longitude` | REAL | Longitude |
| `altitude` | REAL | Altitude in metres |
| `action` | TEXT | takeoff, waypoint, rtl, land |

### Safety Checks Table

| Field | Type | Description |
|---|---|---|
| `check_id` | INTEGER | Primary key (auto) |
| `mission_id` | INTEGER | Related mission (foreign key) |
| `check_name` | TEXT | Name of safety check (e.g. R1: Altitude) |
| `result` | TEXT | Pass / Fail |
| `message` | TEXT | Explanation |

---

## 📅 8-Week Internship Plan

| Week | Focus | Main Tasks | Deliverable |
|---|---|---|---|
| Week 1 | Project Setup and UAV Basics | Install tools, create basic Streamlit app, learn UAV terms | GitHub repo, basic app, `docs/uav_terms.md` |
| Week 2 | Mission Data Model and Manual Input | Create mission fields, waypoint structure, mission summary display | Mission input form and sample mission file |
| Week 3 | Waypoint Generation | Generate square/grid/perimeter routes with takeoff and RTL points | Waypoint planner module and waypoint table |
| Week 4 | Map Visualization | Use Folium to show home point, waypoints, route line, and no-fly zone | Interactive mission map |
| Week 5 | Safety Compliance Checker | Implement altitude, duration, takeoff/RTL, no-fly zone, distance, and battery checks | Safety checker module and results page |
| Week 6 | Agentic Layer | Add mission understanding, correction, and report agents; connect workflow | Agentic workflow and natural language input |
| Week 7 | Database and Export | Save missions in SQLite; export mission JSON, waypoint CSV, and report | Database integration and export features |
| Week 8 | Testing, Documentation, and Submission | Test full system, fix bugs, improve UI, prepare report and demo | Final app, report, slides, demo video, GitHub |

---

## 🔮 Future Enhancements

1. QGroundControl `.plan` file export
2. PX4 SITL simulation
3. Multi-UAV mission planning
4. Real drone integration
5. Battery consumption model (detailed physics)
6. Weather-aware mission planning
7. Voice-based mission input
8. LLM-based mission understanding (LangGraph)
9. Human approval workflow
10. Formal verification of UAV mission constraints

---

## 📬 Contact

**Abdul Azeem Hashmi**  
GitHub: [@AbdulAzeemHashmi](https://github.com/AbdulAzeemHashmi)  
Repository: [agentic-uav-mission-planner](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner)