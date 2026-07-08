<div align="center">

# 🛸 SkyGuard AI
### Agentic UAV Mission Planning and Safety Compliance Assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-Academic-green?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-9%2F9%20Passing-brightgreen?style=for-the-badge&logo=checkmarx)](tests/)

<br/>

[![Open App](https://img.shields.io/badge/🚀%20Launch%20App-Streamlit-FF4B4B?style=for-the-badge)](http://localhost:8501)
[![View Repo](https://img.shields.io/badge/📁%20View%20Repo-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner)
[![Report Bug](https://img.shields.io/badge/🐛%20Report%20Bug-Issues-orange?style=for-the-badge)](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner/issues)

<br/>

> **An end-to-end software application for planning UAV missions through an agentic AI workflow.**
> Accepts natural language mission requests, generates waypoints, validates airspace safety rules,
> applies physics-based corrections, and produces exportable flight plans and compliance reports.

> 🔒 **No physical UAV hardware required** — this is a fully software-based simulation project.

</div>

---

## 📋 Table of Contents

- [🎯 Problem Statement](#-problem-statement)
- [🏗️ System Architecture](#-system-architecture)
- [✨ Key Features](#-key-features)
- [🛡️ Safety Rules](#-safety-rules-7-rules)
- [🗺️ Waypoint Patterns](#-waypoint-generation-patterns)
- [📦 Technology Stack](#-technology-stack)
- [📁 Project Structure](#-project-structure)
- [⚙️ Setup and Run](#-setup-and-run)
- [🖥️ Application Pages](#-application-pages)
- [🗄️ Database Schema](#-database-schema)
- [🧪 Testing](#-testing)
- [📅 8-Week Internship Plan](#-8-week-internship-plan)
- [🔮 Future Enhancements](#-future-enhancements)
- [📬 Contact](#-contact)

---

## 🎯 Problem Statement

UAV mission planning requires careful definition of waypoints, altitude limits, mission duration, geofence restrictions, return-to-launch behaviour, and safety constraints. Manual planning can lead to mistakes such as:

| Problem | Impact |
|---|---|
| 🔴 Missing landing points | UAV never returns home |
| 🔴 Unsafe altitude values | Airspace regulation violation |
| 🔴 Routes crossing restricted zones | Collision or legal penalty |
| 🔴 Incomplete mission instructions | Mission abort mid-flight |

SkyGuard AI solves these problems through a modular, AI-driven agentic pipeline that validates every mission before export.

---

## 🏗️ System Architecture

The system uses **5 specialized agents** working in a sequential pipeline:

```
🗣️  User Input (Natural Language / Form)
        |
        v
🧠  Mission Understanding Agent   -->  Structured JSON Plan
        |
        v
📍  Waypoint Planner Agent        -->  Waypoint List + Route
        |
        v
🛡️  Safety Compliance Agent       -->  Violations Found?
        |
        +--- YES -->  🔧 Correction Agent  -->  Fixed Waypoints
        |
        +--- NO  -->  📄 Report Agent      -->  Final Report
        |
        v
💾  Export + Database Storage
```

### 🤖 Agent Details

| Agent | File | Purpose |
|---|---|---|
| 🧠 **Mission Understanding** | `agents/mission_understanding_agent.py` | Parses natural language via Google Gemini API and regex fallback, extracts mission type, altitude, duration, route pattern, and safety constraints |
| 📍 **Waypoint Planner** | `agents/waypoint_planner_agent.py` | Generates takeoff, route waypoints, altitude values, sequence numbers, and RTL point for 5 flight patterns |
| 🛡️ **Safety Compliance** | `agents/safety_compliance_agent.py` | Enforces 7 airspace rules using Shapely line-segment geofence checks and a physics-based battery energy model |
| 🔧 **Correction** | `agents/correction_agent.py` | Applies Shapely boundary normal-vector projection to move waypoints exactly 15 m outside restricted zones |
| 📄 **Report Generation** | `agents/report_generation_agent.py` | Creates PDF compliance reports, CSV waypoint logs, and QGroundControl `.plan` files |

---

## ✨ Key Features

- 🗣️ **Natural Language Mission Input** — describe your mission in plain text; Gemini AI parses it
- 📝 **Manual Form Input** — structured form for precise parameter entry
- 🗺️ **Interactive Map View** — Folium-powered map with waypoints, flight path, and no-fly zones
- 🛡️ **7-Rule Safety Validation** — altitude, geofence, battery, duration, leg distance, takeoff, RTL
- 🔧 **Smart Auto-Correction** — normal-vector Shapely projection moves waypoints to safe positions
- 🔋 **Physics-Based Battery Model** — climb / cruise / descent / hover energy stages (replaces heuristics)
- 📐 **Metric Geofence Checks** — `latlon_to_meters()` projection eliminates degree distortion
- 💾 **SQLite Persistence** — all missions, waypoints, and safety results stored locally
- 📤 **Multi-Format Export** — JSON mission plan, CSV waypoints, PDF report, QGC `.plan` file
- ✅ **9/9 Unit Tests Passing** — full test coverage for all core modules

---

## 🛡️ Safety Rules (7 Rules)

| Rule | Standard | Limit | Example Failure |
|---|---|---|---|
| **R1** | Altitude ceiling | Max 80 m AGL | Altitude 120 m = Fail |
| **R2** | Takeoff waypoint | Must be present | Missing takeoff = Fail |
| **R3** | Landing / RTL waypoint | Must be present | Missing RTL = Fail |
| **R4** | Geofence clearance | No path segment crosses no-fly zone | Waypoint inside restricted area = Fail |
| **R5** | Leg distance | Max 500 m between waypoints | Distance 600 m = Fail |
| **R6** | Mission duration | Max 30 minutes | Duration 45 min = Fail |
| **R7** | Battery usage | Below 80% of 90 Wh capacity | Estimated usage 95% = Fail |

> **R7 Physics Model:** Climb (215 W at 4 m/s) + Cruise (120 W at 10 m/s) + Descent (115 W at 2 m/s) + Hover (130 W)

---

## 🗺️ Waypoint Generation Patterns

| Pattern | Description | Waypoints |
|---|---|---|
| **Square** | Square perimeter around home point | 6 waypoints |
| **Grid** | Lawn-mower scan for area mapping | 13+ waypoints |
| **Perimeter** | Circular boundary patrol route | 11 waypoints |
| **Circle Orbit** | Circular orbit around home location | 12 waypoints |
| **Manual** | User-defined coordinate list | Variable |

---

## 📦 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| 🐍 Language | Python 3.8+ | Core application |
| 🌐 Web UI | Streamlit | Interactive dashboard |
| 🧠 AI / NLP | Google Gemini API | Natural language parsing |
| 🗺️ Maps | Folium + Streamlit-Folium | Route visualization |
| 📐 Geometry | Shapely | Geofence and correction math |
| 📊 Data | Pandas | Waypoint table handling |
| 💾 Database | SQLite | Mission persistence |
| 📈 Charts | Matplotlib / Plotly | Analytics charts |
| 📄 PDF | ReportLab | Compliance report generation |
| 🛩️ Export | python-pptx / python-docx | Office document generation |
| 🧪 Testing | Python unittest | Automated test suite |
| 🔁 Version Control | Git + GitHub | Source control |

---

## 📁 Project Structure

```text
agentic-uav-mission-planner/
|
+-- app.py                          # Main Streamlit application
+-- requirements.txt                # Python dependencies
+-- README.md                       # This file
|
+-- agents/
|   +-- mission_understanding_agent.py   # NLP parsing (Gemini + regex)
|   +-- waypoint_planner_agent.py        # Route generation (5 patterns)
|   +-- safety_compliance_agent.py       # 7-rule safety validation
|   +-- correction_agent.py             # Shapely normal-vector correction
|   +-- report_agent.py                 # PDF / CSV / QGC export
|
+-- utils/
|   +-- map_utils.py                # Folium map visualization
|   +-- database_utils.py           # SQLite CRUD operations
|   +-- export_utils.py             # JSON / CSV / QGC .plan export
|   +-- distance_utils.py           # Haversine + metric projection
|
+-- docs/
|   +-- uav_terms.md                # UAV terminology reference
|   +-- user_manual.pdf             # Full user manual (ReportLab)
|   +-- project_report.docx      # Academic project report
|   +-- presentation.pptx           # 7-slide presentation deck
|
+-- data/
|   +-- no_fly_zones.json           # Default no-fly zone definitions
|
+-- database/
|   +-- missions.db                 # SQLite database (auto-created)
|
+-- reports/
|   +-- generated_reports/          # Auto-generated PDF mission reports
|
+-- tests/
|    +-- test_planner.py             # Unit tests (9 tests, all passing)
```

---

## ⚙️ Setup and Run

### 📋 Prerequisites

- Python 3.8 or higher
- `pip` and `virtualenv`
- Git
- Google Gemini API key (optional, for NLP features)

### 🚀 Quick Start

**Step 1 - Clone the repository**

```bash
git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git
cd agentic-uav-mission-planner
```

**Step 2 - Create and activate a virtual environment**

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate

# Linux / Mac
python -m venv .venv
source .venv/bin/activate
```

**Step 3 - Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 - Configure Gemini API (optional)**

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

**Step 5 - Launch the app**

```bash
streamlit run app.py
```

**Step 6 - Open in browser**

```
http://localhost:8501
```

---

## 🖥️ Application Pages

| Page | Icon | Content |
|---|---|---|
| **Home** | 🏠 | Project title, description, and navigation |
| **Mission Input** | 📝 | Mission name, type, NLP input, home location, altitude, duration, route pattern |
| **Mission Plan** | 📋 | Extracted mission details, waypoint table, generated route parameters |
| **Map View** | 🗺️ | Home marker, waypoint markers, flight path polyline, no-fly zone polygons |
| **Safety Check** | 🛡️ | Safety checklist, passed checks, failed checks, final safety status |
| **Suggestions** | 💡 | Issues found, recommended corrections, revised mission values |
| **History** | 🗄️ | All saved missions, filter by status, download PDF reports |
| **Export** | 📤 | Download mission JSON, waypoint CSV, text report, QGC .plan file |

---

## 🗄️ Database Schema

### 📋 Missions Table

| Column | Type | Notes |
|---|---|---|
| `mission_id` | INTEGER | Primary Key, auto-increment |
| `mission_name` | TEXT | User-defined name |
| `mission_type` | TEXT | surveillance, delivery, inspection, search_and_rescue |
| `altitude` | REAL | Target altitude in metres |
| `duration` | REAL | Estimated duration in minutes |
| `status` | TEXT | Safe / Needs Revision |
| `created_at` | TEXT | ISO timestamp |

### 📍 Waypoints Table

| Column | Type | Notes |
|---|---|---|
| `waypoint_id` | INTEGER | Primary Key |
| `mission_id` | INTEGER | Foreign Key to Missions |
| `sequence_no` | INTEGER | Order in flight path |
| `latitude` | REAL | Decimal degrees |
| `longitude` | REAL | Decimal degrees |
| `altitude` | REAL | Metres above ground |
| `action` | TEXT | takeoff, waypoint, rtl, land |

### 🛡️ Safety Checks Table

| Column | Type | Notes |
|---|---|---|
| `check_id` | INTEGER | Primary Key |
| `mission_id` | INTEGER | Foreign Key to Missions |
| `check_name` | TEXT | R1 through R7 |
| `result` | TEXT | Pass / Fail |
| `message` | TEXT | Detail of violation or confirmation |

---

## 🧪 Testing

Run the full unit test suite:

```bash
python -m unittest tests/test_planner.py -v
```

| Test | Coverage | Result |
|---|---|---|
| `test_haversine` | Haversine distance accuracy | ✅ PASS |
| `test_waypoint_square` | Square pattern generation | ✅ PASS |
| `test_waypoint_grid` | Grid pattern generation | ✅ PASS |
| `test_waypoint_circle` | Circle orbit generation | ✅ PASS |
| `test_waypoint_perimeter` | Perimeter pattern generation | ✅ PASS |
| `test_geofence_segment` | Shapely line-segment intersection | ✅ PASS |
| `test_battery_model` | Physics battery estimation | ✅ PASS |
| `test_correction_agent` | Normal-vector boundary projection | ✅ PASS |
| `test_qgc_export` | QGC .plan file structure | ✅ PASS |

**9 / 9 tests passing**

---

## 📅 8-Week Internship Plan

| Week | Focus | Tasks | Deliverable |
|---|---|---|---|
| **1** | Project Setup | Install tools, create app, learn UAV terms | GitHub repo, basic Streamlit app |
| **2** | Mission Data Model | Create mission form, waypoint structure | Mission input form, sample data |
| **3** | Waypoint Generation | Implement square / grid / perimeter routes | Waypoint planner module |
| **4** | Map Visualization | Folium integration, home / waypoints / routes | Interactive mission map |
| **5** | Safety Checking | Implement 7 safety rules | Safety checker module |
| **6** | Agentic Layer | Connect all agents, NLP integration | Agentic workflow |
| **7** | Database and Export | SQLite setup, JSON / CSV / PDF export | Database integration |
| **8** | Testing and Docs | Full system testing, final report | Complete application |

---

## 📝 Usage Example

**User types:**

> "Plan a surveillance mission around campus for 20 minutes. Keep altitude below 80 metres, avoid restricted zones, and return to launch after completion."

**System pipeline:**

```
Step 1  [Mission Understanding]  mission_type=surveillance, altitude=50m,
                                  duration=20m, route_pattern=square, rtl=true

Step 2  [Waypoint Planner]       6 waypoints generated with takeoff and RTL

Step 3  [Safety Compliance]      All 7 rules pass (R1 through R7)

Step 4  [Report Agent]           Interactive map + compliance report created

Step 5  [Export]                 Mission JSON, waypoint CSV, PDF report, QGC .plan
```

---

## 🔮 Future Enhancements

| Priority | Enhancement | Status |
|---|---|---|
| 🟡 Planned | QGroundControl `.plan` file export | ✅ Completed |
| 🟡 Planned | Physics-based battery model | ✅ Completed |
| 🟡 Planned | Shapely line-segment geofence checks | ✅ Completed |
| 🔵 Future | Multi-UAV coordinated mission planning | Pending |
| 🔵 Future | PX4 / SITL simulation integration (Gazebo) | Pending |
| 🔵 Future | Voice-based mission input (Whisper ASR) | Pending |
| 🔵 Future | Weather-aware planning (wind / rain APIs) | Pending |
| 🔵 Future | Terrain-following altitude profiles (SRTM) | Pending |
| 🔵 Future | REST API mode for third-party GCS integration | Pending |
| 🔵 Future | Human approval workflow before execution | Pending |

---

## 📚 Documentation

| Document | Location | Description |
|---|---|---|
| 📖 User Manual | `docs/user_manual.pdf` | Full system usage guide |
| 📄 Project Report | `docs/project_report_v2.docx` | Academic internship report |
| 🎤 Presentation | `docs/presentation.pptx` | 7-slide project deck |
| 📚 UAV Glossary | `docs/uav_terms.md` | Key UAV terminology definitions |
| ✅ Delivery Checklist | `DELIVERY_CHECKLIST.md` | Project completion verification |

---

## 📬 Contact

<div align="center">

| Field | Value |
|---|---|
| 👤 **Student** | Abdul Azeem Hashmi |
| 📧 **Email** | abdulazeemhashmi29@gmail.com |
| 🐙 **GitHub** | [AbdulAzeemHashmi](https://github.com/AbdulAzeemHashmi) |
| 📁 **Project Repo** | [agentic-uav-mission-planner](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner) |
| 🎓 **Level** | 5th Semester Undergraduate |
| 🏢 **Domain** | UAVs, Agentic AI, Safety Compliance |

<br/>

[![Email](https://img.shields.io/badge/📧%20Email-abdulazeemhashmi29%40gmail.com-blue?style=for-the-badge)](mailto:abdulazeemhashmi29@gmail.com)
[![GitHub](https://img.shields.io/badge/🐙%20GitHub-AbdulAzeemHashmi-181717?style=for-the-badge&logo=github)](https://github.com/AbdulAzeemHashmi)

</div>

---

<div align="center">

**Built with 🧠 Agentic AI + 🛸 UAV Safety Engineering**

*Developed as part of an internship program for educational and academic demonstration purposes.*

[![Star on GitHub](https://img.shields.io/github/stars/AbdulAzeemHashmi/agentic-uav-mission-planner?style=social)](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner)

</div>