<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00c6ff,100:0072ff&height=220&section=header&text=Agentic%20UAV%20Mission%20Planner&fontSize=36&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI%20Mission%20Planning%20and%20Airspace%20Auditing&descAlignY=58&descSize=18" width="100%"/>

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

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=00C6FF&center=true&vCenter=true&width=720&lines=Natural+Language+Mission+Planning;5+AI+Agents+Working+Together;7+Safety+Rules+Checked;Live+Map+and+Export+Ready;Interactive+History+Map+Preview;JSON+Batch+Import+and+Export" alt="Typing SVG"/>

<br/>

> 🚁 A smart mission planning app for UAV flights with AI guidance, live map views, safety checks, interactive history preview, and export ready reports.
>
> 🔒 This project is a software simulation only. No real drone hardware is involved.

</div>

---

## 🚀 Project Overview

This project lets a user describe a UAV mission in plain language and turns it into a structured flight plan. The app uses five specialized AI agents to understand the request, generate route waypoints, verify airspace safety rules, suggest corrections, and build complete flight reports.

### ✨ What the app does

- 🧠 **Natural Language Parsing**: Converts plain text prompts into structured mission parameters with Google Gemini AI
- 📍 **Route Generation**: Builds safe waypoint routes for Square, Grid, Circle, and Perimeter flight patterns
- 🛡 **7-Rule Safety Audit Engine**: Enforces strict airspace safety compliance rules before takeoff
- 🔧 **Automated Corrections**: Generates actionable fix suggestions for failed safety checks
- 🗺 **Live GCS Radar Map**: Visualizes flight path, takeoff points, and restricted no-fly zones in real time
- 📂 **Mission History & Database**: Browse, filter, sort, preview on map, import, and manage saved SQLite missions
- 📥 **Multi-Format Export**: Generates QGroundControl (.plan), ArduPilot (.waypoints), Google Earth (.kml), JSON, CSV, and PDF reports

---

## 🖼️ Application Showcase & Screenshots

### 🏠 Ground Control Station Dashboard

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121230.png" width="90%" alt="Ground Control Station Dashboard"/>
  <br/>
  <i>Ground Control Station Overview: Active Airspace Regulations and Mission Workflow</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121248.png" width="90%" alt="Live Airspace Radar"/>
  <br/>
  <i>Live Airspace Radar and Dynamic Mission HUD</i>
</div>

---

### 📝 Mission Input & AI Natural Language Understanding

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121303.png" width="90%" alt="Natural Language Input"/>
  <br/>
  <i>Natural Language Intent Extraction powered by Google Gemini AI</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121318.png" width="90%" alt="Flight Profile Selection"/>
  <br/>
  <i>Manual Flight Parameters and Drone Profile Selection</i>
</div>

---

### ⚙️ Mission Planning & Waypoint Generation

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121332.png" width="90%" alt="Waypoint Sequence Table"/>
  <br/>
  <i>Generated Waypoint Sequence Table with Coordinates and Altitude Profile</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121347.png" width="90%" alt="Pattern Profile Mapping"/>
  <br/>
  <i>Raster Grid and Serpentine Flight Pattern Configuration</i>
</div>

---

### 🗺️ Live GCS Airspace Radar Map & Geofence

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121358.png" width="90%" alt="Live GCS Radar Map"/>
  <br/>
  <i>Interactive Folium GCS Airspace Radar Map with Route Polyline</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121407.png" width="90%" alt="No Fly Zone Polygon Overlay"/>
  <br/>
  <i>No-Fly Zone Polygon Overlay and Takeoff Marker Visualization</i>
</div>

---

### 🛡️ Safety Compliance Audit & AI Corrections

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121425.png" width="90%" alt="Safety Audit Engine"/>
  <br/>
  <i>7-Rule Airspace Safety Compliance Engine Audit Results</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121531.png" width="90%" alt="AI Correction Suggestions"/>
  <br/>
  <i>Automated AI Correction Suggestions for Flight Rule Pass/Fail Violations</i>
</div>

---

### 📤 Multi-Format Mission Export & GCS Plans

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121554.png" width="90%" alt="Multi-Format Export"/>
  <br/>
  <i>Multi-Format Mission Export: QGroundControl (.plan), ArduPilot (.waypoints), Google Earth (.kml), JSON, CSV, PDF</i>
</div>

---

### 📂 Mission History & Database Management

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20121608.png" width="90%" alt="Mission History Search and Filters"/>
  <br/>
  <i>Mission History Search, Status Filters, Sort Controls, and Straight Alignment Layout</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121631.png" width="90%" alt="Interactive Map Preview"/>
  <br/>
  <i>Interactive History Map Preview: Instantly Display Saved Mission Routes on GCS Radar</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20121644.png" width="90%" alt="JSON Mission Import and Detailed Audit Breakdown"/>
  <br/>
  <i>JSON Mission File Import and Detailed Safety Audit Rule Breakdown Table</i>
</div>

---

## 🧩 System Flow

```text
User Input
   │
   ▼
Mission Understanding Agent
   │
   ▼
Waypoint Planner Agent
   │
   ▼
Safety Compliance Agent
   │
   ▼
Correction Agent
   │
   ▼
Report Agent
   │
   ▼
Map View + Database + Export Tools
```

---

## 🤖 Agentic Workflow

The application uses five specialized AI agents operating in one unified pipeline.

| Step | Agent | Purpose |
|---|---|---|
| 1 | 🧠 Mission Understanding Agent | Converts natural language into structured mission parameters |
| 2 | 📍 Waypoint Planner Agent | Generates takeoff, route, altitude, and RTL points |
| 3 | 🛡 Safety Compliance Agent | Validates seven airspace safety compliance rules |
| 4 | 🔧 Correction Agent | Produces actionable fix suggestions for failed checks |
| 5 | 📄 Report Agent | Builds mission summaries and downloadable PDF reports |

### 💬 Example mission prompt

```text
Plan a surveillance mission around the campus for 20 minutes.
Keep altitude below 80 meters, avoid restricted airspace,
and return to launch after completion.
```

---

## 🌟 Key Features

- 🚁 Natural language mission input powered by Google Gemini AI
- 📍 Automatic generation of mission waypoints for 4 flight patterns
- 🗺 Live interactive GCS map with route lines and no fly zone overlays
- 🛡 Seven rule safety validation audit engine
- 🔧 Actionable AI correction suggestions
- 📊 Detailed mission summary reports and PDF export
- 📂 SQLite database for mission history, search filtering, and page controls
- 👁️ Interactive history map preview without overwriting active session
- 📥 JSON mission file import and 2-query batch export optimization
- 🎨 Dark and light display modes with responsive CSS layout
- ☰ Stable sidebar toggle and persistent branding header

---

## 🛡 Safety Compliance Rules

The safety compliance engine evaluates seven rules for every generated mission.

| Rule | Description | Limit |
|---|---|---|
| R1 | Maximum altitude ceiling | 80 meters |
| R2 | Mission must include a takeoff command | Required |
| R3 | Mission must include RTL or landing point | Required |
| R4 | No waypoint may enter a no fly zone | Zero tolerance |
| R5 | Maximum distance between route points | 500 meters |
| R6 | Maximum mission duration | 30 minutes |
| R7 | Battery reserve must stay below 80 percent | Required |

---

## 🗺 Route Profiles

| Pattern | Best use case |
|---|---|
| 🟦 Square | Campus and building perimeter scanning |
| ⚡ Grid | Field coverage and agricultural mapping |
| ⭕ Circle | Point of interest inspection |
| 🔷 Perimeter | Large area boundary patrol |

All routes include takeoff command, altitude assignment, sequence numbers, and Return to Launch (RTL).

---

## 🧰 Technology Stack

| Component | Tool |
|---|---|
| Language | Python 3.12 |
| Framework | Streamlit |
| AI Engine | Google Gemini AI |
| Interactive Maps | Folium and Streamlit Folium |
| Data Processing | Pandas |
| Spatial Geometry | Shapely |
| Database | SQLite |
| PDF Export | ReportLab |
| Environment | Python Dotenv |

---

## 📁 Project Structure

```text
agentic-uav-mission-planner/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .env
├── agents/
│   ├── mission_understanding_agent.py
│   ├── waypoint_planner_agent.py
│   ├── safety_compliance_agent.py
│   ├── correction_agent.py
│   └── report_agent.py
├── utils/
│   ├── database_utils.py
│   ├── map_utils.py
│   ├── export_utils.py
│   └── distance_utils.py
├── screenshots/
├── data/
├── database/
├── docs/
├── reports/
└── tests/
    ├── test_planner.py
    └── test_history.py
```

---

## ⚙ Setup and Run

### 1. Clone the repository

```bash
git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git
cd agentic-uav-mission-planner
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS and Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Create a file named `.env` in the project root and add:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Get your key here: https://aistudio.google.com/app/apikey

### 5. Launch the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

### 🐳 Running with Docker

You can easily containerize and run this application using Docker or Docker Compose.

#### Option A: Using Docker Compose (Recommended)

1. Ensure Docker Desktop is running and `.env` contains your `GEMINI_API_KEY`.
2. Build and start the containerized application:

```bash
docker compose up --build
```

3. Access the app in your browser at `http://localhost:8501`.

#### Option B: Using Docker CLI

1. Build the Docker image:

```bash
docker build -t agentic-uav-mission-planner .
```

2. Run the container:

```bash
docker run -d -p 8501:8501 --env-file .env --name uav-planner agentic-uav-mission-planner
```

3. Open `http://localhost:8501` in your browser.

---

## 🖥 Application Pages

| Page | Purpose |
|---|---|
| 🏠 Home | Mission overview and quick start dashboard |
| 📝 Mission Input | Manual entry or natural language mission prompt |
| ⚙ Mission Plan | Waypoint generation and mission report view |
| 🗺 Map View | Interactive route and no fly zone map |
| 🛡 Safety Check | Rule by rule compliance audit |
| 💡 Suggestions | Correction recommendations |
| 📥 Export | Download QGroundControl, ArduPilot, KML, JSON, CSV, PDF |
| 📂 Mission History | Database search, history map preview, JSON import/export |

---

## 📬 Contact

- 👤 Author: Abdul Azeem Hashmi
- 🐙 GitHub: https://github.com/AbdulAzeemHashmi
- 📦 Repository: https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0072ff,100:00c6ff&height=100&section=footer&animation=fadeIn" width="100%"/>

**Built with 🚁 🤖 and 💙 for UAV research and education**

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=AbdulAzeemHashmi.agentic-uav-mission-planner)

</div>
