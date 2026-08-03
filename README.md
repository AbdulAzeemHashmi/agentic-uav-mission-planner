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

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=00C6FF&center=true&vCenter=true&width=720&lines=Natural+Language+Mission+Planning;5+AI+Agents+Working+Together;7+Safety+Rules+Checked;Live+Map+and+Export+Ready;Stable+Sidebar+Branding+on+Streamlit" alt="Typing SVG"/>

<br/>

> 🛸 A smart mission planning app for UAV flights with AI guidance, live map views, safety checks, and export ready reports.
>
> 🔒 This project is a software simulation only. No real drone hardware is involved.

</div>

---

## 🚀 Project Overview

This project lets a user describe a UAV mission in plain language and then turns it into a structured flight plan. The app uses several AI agents to understand the request, generate route waypoints, verify airspace safety rules, suggest corrections, and create a report.

### ✨ What the app does

- 🧠 Understands mission intent from natural language
- 📍 Builds safe waypoint routes for square, grid, circle, and perimeter patterns
- 🛡 Checks seven airspace safety rules before a mission is accepted
- 🔧 Suggests fixes for any failed rule
- 🗺 Shows the route on an interactive map
- 📥 Exports mission data as JSON, CSV, and PDF

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

The application uses five specialized AI agents in one pipeline.

| Step | Agent | Purpose |
|---|---|---|
| 1 | 🧠 Mission Understanding Agent | Converts natural language into mission parameters |
| 2 | 📍 Waypoint Planner Agent | Generates takeoff, route, altitude, and RTL points |
| 3 | 🛡 Safety Compliance Agent | Validates seven airspace safety rules |
| 4 | 🔧 Correction Agent | Produces fix suggestions for failed checks |
| 5 | 📄 Report Agent | Builds mission summaries and downloadable reports |

### 💬 Example mission prompt

```text
Plan a surveillance mission around the campus for 20 minutes.
Keep altitude below 80 meters, avoid restricted airspace,
and return to launch after completion.
```

---

## 🌟 Key Features

- 🛸 Natural language mission input with Google Gemini AI
- 📍 Auto generation of mission waypoints
- 🗺 Live interactive map with route and no fly zone overlays
- 🛡 Seven rule safety validation engine
- 🔧 Actionable correction suggestions
- 📊 Mission summary reports and PDF export
- 💾 SQLite storage for mission history
- 🎨 Dark and light display modes
- ☰ Stable sidebar toggle and persistent branding header

---

## 🛡 Safety Rules

The safety checker evaluates seven rules for every generated mission.

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

| Pattern | Best use |
|---|---|
| 🟦 Square | Campus and building perimeter scanning |
| ⚡ Grid | Field coverage and mapping |
| ⭕ Circle | Point of interest inspection |
| 🔷 Perimeter | Large area boundary patrol |

All routes include a takeoff point, altitude assignment, sequence numbers, and an RTL point.

---

## 🧰 Technology Stack

| Component | Tool |
|---|---|
| Language | Python 3.12 |
| UI | Streamlit |
| AI | Google Gemini AI |
| Maps | Folium and streamlit folium |
| Data | Pandas |
| Geometry | Shapely |
| Database | SQLite |
| Reports | ReportLab |
| Environment | python dotenv |

---

## 📁 Project Structure

```text
agentic-uav-mission-planner/
├── app.py
├── requirements.txt
├── README.md
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
├── data/
├── database/
├── docs/
└── reports/
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

Create a file named .env in the project root and add:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Get your key here: https://aistudio.google.com/app/apikey

### 5. Launch the app

```bash
streamlit run app.py
```

Open the browser at http://localhost:8501

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
| 📥 Export | Download JSON, CSV, and PDF outputs |

---

## 🛠 UI Fix Note

The header issue reported on the live app is now handled by keeping a persistent branding card visible above the main content. This makes the title and supporting text remain visible even after the sidebar is collapsed or expanded.

---

## 📬 Contact

- 👤 Author: Abdul Azeem Hashmi
- 🐙 GitHub: https://github.com/AbdulAzeemHashmi
- 🌐 Live app: https://agentic-uav-mission-planner-mdarysdfc32zt2nax2tu5p.streamlit.app/
- 📦 Repository: https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0072ff,100:00c6ff&height=100&section=footer&animation=fadeIn" width="100%"/>

**Built with 🛸 🤖 and 💙 for UAV research and education**

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=AbdulAzeemHashmi.agentic-uav-mission-planner)

</div>
