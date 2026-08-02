<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00c6ff,100:0072ff&height=220&section=header&text=Agentic%20UAV%20Mission%20Planner&fontSize=36&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI-Driven%20Airspace%20Planner%20and%20Safety%20Auditor&descAlignY=58&descSize=18" width="100%"/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini AI](https://img.shields.io/badge/Google%20Gemini-AI%20Agent-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Folium](https://img.shields.io/badge/Folium-Live%20Map-77B829?style=for-the-badge)](https://python-visualization.github.io/folium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<img src="https://img.shields.io/github/stars/AbdulAzeemHashmi/agentic-uav-mission-planner?style=social" alt="stars"/>
<img src="https://img.shields.io/github/forks/AbdulAzeemHashmi/agentic-uav-mission-planner?style=social" alt="forks"/>
<img src="https://img.shields.io/github/last-commit/AbdulAzeemHashmi/agentic-uav-mission-planner?color=00c6ff" alt="last commit"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=00C6FF&center=true&vCenter=true&width=680&lines=Natural+Language+UAV+Mission+Planning;5+Specialized+AI+Agents+Working+Together;7+Rule+Airspace+Safety+Validation;Dual+Display+Modes+(Dark+and+Light);Exportable+Flight+Plans+and+Reports" alt="Typing SVG"/>

<br/>

> 🛸 **An end-to-end AI application for planning, validating, and auditing UAV flight missions through an agentic workflow.**
> Accepts natural language requests, generates waypoint trajectories, validates 7 airspace safety rules, suggests corrections, and exports mission packages (JSON, CSV, PDF).

> 🔒 **Fully Software Simulation Project.** No physical UAV hardware required.

</div>

---

## 📋 Table of Contents

- [🎯 Problem Statement](#-problem-statement)
- [🏗 System Architecture](#-system-architecture)
- [🤖 Agentic Workflow](#-agentic-workflow)
- [✨ Key Features](#-key-features)
- [🎨 Dual Display Modes](#-dual-display-modes)
- [🛡 Safety Regulations](#-safety-regulations)
- [🗺 Waypoint Route Profiles](#-waypoint-route-profiles)
- [📦 Technology Stack](#-technology-stack)
- [📁 Project Structure](#-project-structure)
- [⚙ Setup and Run](#-setup-and-run)
- [🖥 Application Pages](#-application-pages)
- [🗄 Database Schema](#-database-schema)
- [📅 8-Week Internship Plan](#-8-week-internship-plan)
- [🔮 Future Enhancements](#-future-enhancements)
- [📬 Contact Information](#-contact-information)

---

## 🎯 Problem Statement

UAV mission planning requires careful definition of waypoints, altitude limits, mission duration, geofence restrictions, return-to-launch behaviour, and safety constraints. Manual planning leads to mistakes such as missing landing points, unsafe altitude values, route crossing restricted zones, or incomplete mission instructions.

This project proposes a **software assistant** that helps users create safer and better-structured UAV mission plans through an agentic AI pipeline.

---

## 🏗 System Architecture

```
User Input (Natural Language or Manual Form)
          |
          v
  Streamlit Web Interface
          |
          v
  Mission Understanding Agent   <-- Google Gemini AI
          |
          v
  Waypoint Planner Agent        <-- Route Generation
          |
          v
  Safety Compliance Agent       <-- 7 Rule Engine
          |
          v
  Correction Agent              <-- Auto Fix Suggestions
          |
          v
  Report Generation Agent       <-- Summary + PDF
          |
          v
  Map Visualization + SQLite DB + JSON/CSV/PDF Export
```

---

## 🤖 Agentic Workflow

The application uses **5 specialized AI agents** working in a coordinated pipeline:

| # | Agent | Role |
|---|-------|------|
| 1 | 🧠 **Mission Understanding Agent** | Extracts mission type, altitude, duration, pattern, and safety constraints from natural language input using Google Gemini AI |
| 2 | 📍 **Waypoint Planner Agent** | Generates takeoff point, route waypoints, altitude assignments, sequence numbers, and RTL point |
| 3 | 🛡 **Safety Compliance Agent** | Runs 7 airspace safety rules and flags any violations with Pass or Fail results |
| 4 | 🔧 **Correction Agent** | Produces actionable fix suggestions for all failed safety checks |
| 5 | 📄 **Report Generation Agent** | Builds mission summary, waypoint table, safety checklist, and final status in HTML and PDF |

### 💬 Example Natural Language Input

```
Plan a surveillance mission around FAST campus for 20 minutes.
Keep altitude below 80 meters, avoid restricted zones,
and return to launch after completion.
```

### 📤 Example Extracted Output (Gemini AI)

```json
{
  "mission_type": "surveillance",
  "altitude": 60,
  "duration": 20,
  "pattern": "square",
  "return_to_launch": true,
  "avoid_no_fly_zone": true
}
```

---

## ✨ Key Features

```
🛸  Natural language mission input via Google Gemini AI
📍  Auto waypoint generation (Square, Grid, Circle, Perimeter)
🗺  Live interactive Folium map with home point + route + NFZ overlays
🛡  7-rule real-time airspace safety compliance engine
🔧  Correction agent with actionable fix suggestions
📊  Mission summary HTML report with telemetry table
💾  SQLite database for persistent mission storage
📥  Export to JSON, CSV, and PDF formats
🎨  Dual display mode: Dark (black page, white map) and Light (white page, dark map)
☰  Custom sidebar toggle that works reliably on Streamlit Cloud
```

---

## 🎨 Dual Display Modes

| Mode | Page Background | Map Background | Use Case |
|------|----------------|----------------|----------|
| 🌑 **Dark Mode** | Black (#000000) | White (CARTO Light) | Low-light operations |
| ☀ **Light Mode** | White (#FFFFFF) | Dark (CARTO Dark) | Daylight / presentation |

The map background color **automatically inverts** relative to the page background for maximum contrast in every mode.

---

## 🛡 Safety Regulations

The Safety Compliance Agent enforces **7 airspace rules** on every generated mission:

| Rule | Description | Limit |
|------|-------------|-------|
| R1 | Maximum altitude ceiling | 80 metres |
| R2 | Mission must include a takeoff command | Mandatory |
| R3 | Mission must include RTL or landing point | Mandatory |
| R4 | No waypoint may enter a no-fly zone | Zero tolerance |
| R5 | Max distance between consecutive waypoints | 500 metres |
| R6 | Maximum mission duration | 30 minutes |
| R7 | Estimated battery usage reserve | Below 80% |

---

## 🗺 Waypoint Route Profiles

| Pattern | Shape | Best For |
|---------|-------|----------|
| 🟦 **Square** | 4-corner box | Campus or building perimeter |
| ⚡ **Grid** | Parallel scan lines | Field mapping and coverage |
| ⭕ **Circle** | Circular orbit | Point of interest inspection |
| 🔷 **Perimeter** | 8-point outline | Large area boundary patrol |

All routes automatically include:
- **Takeoff point** at the home location
- **Altitude assignment** for every waypoint
- **Sequence numbers** in flight order
- **RTL (Return-To-Launch)** as the final waypoint

---

## 📦 Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Web Framework | Streamlit 1.32 |
| AI Agent | Google Gemini AI (google-generativeai) |
| Map Visualization | Folium + streamlit-folium |
| Data Handling | Pandas 2.2.1 |
| Geometry | Shapely 2.x |
| Database | SQLite via database_utils.py |
| Charts | Matplotlib + Plotly |
| PDF Export | ReportLab 4.x |
| Environment | python-dotenv |
| Version Control | Git + GitHub |

---

## 📁 Project Structure

```
agentic-uav-mission-planner/
|
+-- app.py                          Main Streamlit application
+-- requirements.txt                Python dependencies
+-- README.md                       Project documentation
+-- .env                            API key environment file
|
+-- agents/
|   +-- mission_understanding_agent.py   Gemini NL parser
|   +-- waypoint_planner_agent.py        Route generator
|   +-- safety_compliance_agent.py       7-rule safety engine
|   +-- correction_agent.py              Fix suggestion generator
|   +-- report_agent.py                  HTML report builder
|
+-- utils/
|   +-- database_utils.py           SQLite read/write helpers
|   +-- map_utils.py                Folium map builder
|   +-- export_utils.py             JSON, CSV, PDF exporters
|   +-- distance_utils.py           Haversine distance calculator
|
+-- database/
|   +-- missions.db                 SQLite database file
|
+-- data/
|   +-- sample_missions.csv         Sample mission records
|   +-- sample_waypoints.csv        Sample waypoint data
|
+-- reports/
|   +-- generated_reports/          Output PDF reports
|
+-- docs/
    +-- uav_terms.md                UAV glossary reference
```

---

## ⚙ Setup and Run

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git
cd agentic-uav-mission-planner
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Get your free API key at: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 5️⃣ Run the Application

```bash
streamlit run app.py
```

Open your browser and navigate to: `http://localhost:8501`

---

## 🖥 Application Pages

| Page | Icon | Description |
|------|------|-------------|
| Home | 🏠 | Dashboard with active safety regulations and quick start guide |
| Mission Input | 📝 | Natural language prompt OR manual parameter form |
| Mission Plan | ⚙ | Waypoint generation, trajectory table, and mission report |
| Map View | 🗺 | Live Folium map with waypoints, route line, and NFZ overlays |
| Safety Check | 🛡 | Rule-by-rule compliance audit with Pass or Fail indicators |
| Suggestions | 💡 | Correction agent output with actionable fix instructions |
| Export | 📥 | Download mission as JSON, waypoints as CSV, and full PDF report |

---

## 🗄 Database Schema

### missions

| Field | Type | Description |
|-------|------|-------------|
| mission_id | INTEGER | Primary key |
| mission_name | TEXT | Mission label |
| mission_type | TEXT | surveillance, delivery, inspection |
| altitude | REAL | Target altitude in metres |
| duration | REAL | Mission duration in minutes |
| status | TEXT | Safe or Needs Revision |
| created_at | TEXT | Timestamp |

### waypoints

| Field | Type | Description |
|-------|------|-------------|
| waypoint_id | INTEGER | Primary key |
| mission_id | INTEGER | Foreign key to missions |
| sequence_no | INTEGER | Waypoint order |
| latitude | REAL | Coordinate latitude |
| longitude | REAL | Coordinate longitude |
| altitude | REAL | Altitude at this point |
| action | TEXT | takeoff, waypoint, rtl, land |

### safety_checks

| Field | Type | Description |
|-------|------|-------------|
| check_id | INTEGER | Primary key |
| mission_id | INTEGER | Foreign key to missions |
| check_name | TEXT | Rule name |
| result | TEXT | Pass or Fail |
| message | TEXT | Detailed explanation |

---

## 📅 8-Week Internship Plan

```
Week 1  Project Setup + UAV Basics
        GitHub repo, basic Streamlit app, UAV terms reference

Week 2  Mission Data Model + Manual Input
        Mission fields, waypoint structure, sample mission display

Week 3  Waypoint Generation
        Square, Grid, Circle, Perimeter routes with Takeoff + RTL

Week 4  Map Visualization
        Folium map with home marker, waypoints, route line, NFZ polygon

Week 5  Safety Compliance Checker
        7-rule engine: altitude, duration, NFZ, battery, takeoff, RTL

Week 6  Agentic Layer
        Mission understanding + correction + report agents connected

Week 7  Database + Export
        SQLite integration, JSON export, CSV export, PDF report

Week 8  Testing + Documentation + Submission
        Bug fixes, UI polish, final report, demo video, slides
```

---

## 🔮 Future Enhancements

| # | Enhancement | Description |
|---|-------------|-------------|
| 1 | 🗂 QGC Export | QGroundControl .plan file export |
| 2 | 🚁 PX4 SITL | Software-in-the-loop simulation integration |
| 3 | 👥 Multi-UAV | Coordinated multi-drone mission planning |
| 4 | 🛰 Live GPS | Real-time drone position tracking |
| 5 | 🔋 Battery Model | Physics-based battery consumption estimation |
| 6 | 🌦 Weather | Weather-aware route planning with wind data |
| 7 | 🎙 Voice Input | Microphone-based natural language entry |
| 8 | 🔍 Human Approval | Operator review step before mission commit |

---

## 📬 Contact Information

<div align="center">

| | |
|-|-|
| 👤 **Author** | Abdul Azeem Hashmi |
| 🐙 **GitHub** | [@AbdulAzeemHashmi](https://github.com/AbdulAzeemHashmi) |
| 🌐 **Live App** | [Streamlit Cloud](https://agentic-uav-mission-planner-mdarysdfc32zt2nax2tu5p.streamlit.app/) |
| 📦 **Repository** | [agentic-uav-mission-planner](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner) |

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0072ff,100:00c6ff&height=100&section=footer&animation=fadeIn" width="100%"/>

**Built with 🛸 + 🤖 + 💙 for UAV research and education**

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=AbdulAzeemHashmi.agentic-uav-mission-planner)

</div>
