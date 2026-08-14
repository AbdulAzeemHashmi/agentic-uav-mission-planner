<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00c6ff,100:0072ff&height=220&section=header&text=Agentic%20UAV%20Mission%20Planner&fontSize=36&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI%20Mission%20Planning%20and%20Airspace%20Auditing&descAlignY=58&descSize=18" width="100%"/>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini AI](https://img.shields.io/badge/Google%20Gemini-AI%20Agent-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Folium](https://img.shields.io/badge/Folium-Live%20Map-77B829?style=for-the-badge)](https://python-visualization.github.io/folium/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

<img src="https://img.shields.io/github/stars/AbdulAzeemHashmi/agentic-uav-mission-planner?style=social" alt="stars"/>
<img src="https://img.shields.io/github/forks/AbdulAzeemHashmi/agentic-uav-mission-planner?style=social" alt="forks"/>
<img src="https://img.shields.io/github/last-commit/AbdulAzeemHashmi/agentic-uav-mission-planner?color=00c6ff" alt="last commit"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=00C6FF&center=true&vCenter=true&width=720&lines=Natural+Language+Mission+Planning;5+AI+Agents+Working+Together;7+Safety+Rules+Checked;Live+Airspace+Radar+Map;Mission+History+and+Export;Interactive+Demo+Screenshots" alt="Typing SVG"/>

<br/>

> 🛩️ Agentic UAV Mission Planner converts natural language mission goals into validated UAV flight plans with AI planning, safety checks, and export ready files.
>
> 🔒 This repository is a software simulation only. No actual drone hardware is controlled.

</div>

---

## 🚀 What This Project Does

Agentic UAV Mission Planner is a Streamlit app that turns text based mission requests into complete UAV flight plans. It uses a chain of five AI agents to:

- 🧠 Convert plain language into structured mission details
- 📍 Generate mission waypoints for multiple flight patterns
- 🛡 Check airspace safety rules and no fly zones
- 🔧 Suggest corrections for mission issues
- 📤 Export mission plans in multiple ground control formats

---

## 🖼 Demo Gallery

### 🛩️ Control Station View

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20220852.png" width="90%" alt="Control Station Dashboard"/>
  <br/>
  <i>Mission dashboard showing route status and planning controls.</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20220921.png" width="90%" alt="Airspace Radar"/>
  <br/>
  <i>Live airspace radar view with no fly zone highlights.</i>
</div>

---

### ✍️ Mission Input and AI Understanding

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20222349.png" width="90%" alt="Mission Prompt Input"/>
  <br/>
  <i>Plain language mission prompt converted to mission data.</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20222405.png" width="90%" alt="Drone Profile Selection"/>
  <br/>
  <i>Vehicle profile selection and flight settings.</i>
</div>

---

### 🧭 Waypoint Planning and Pattern Generation

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20222446.png" width="90%" alt="Waypoint Table"/>
  <br/>
  <i>Waypoint table with coordinates, altitude, and sequence order.</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20222458.png" width="90%" alt="Flight Pattern Settings"/>
  <br/>
  <i>Pattern selection for grid, square, circle, and perimeter missions.</i>
</div>

---

### 🛡 Safety Audit and Correction Suggestions

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20222644.png" width="90%" alt="Safety Audit"/>
  <br/>
  <i>Mission safety audit displaying rule pass and fail states.</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20222703.png" width="90%" alt="AI Corrections"/>
  <br/>
  <i>AI generated mission corrections for safety violations.</i>
</div>

---

### 📂 Mission History and Exports

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20222829.png" width="90%" alt="Mission History"/>
  <br/>
  <i>Mission history, filtering, and quick preview controls.</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20222855.png" width="90%" alt="History Map Preview"/>
  <br/>
  <i>Saved mission preview on the map before export.</i>
</div>

---

## 🧠 How the Agent Chain Works

The app processes user input with a set of AI agents that each add structure, validation, or export readiness.

```text
User prompt
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
Report Agent
  |
  v
Map view, history, and export files
```

---

## 🤖 Agent Roles

| Step | Agent | Role |
|---|---|---|
| 1 | 🧠 Mission Understanding Agent | Parse mission goals from natural language |
| 2 | 📍 Waypoint Planner Agent | Build route waypoints and flight legs |
| 3 | 🛡 Safety Compliance Agent | Validate no fly zones and mission rules |
| 4 | 🔧 Correction Agent | Suggest fixes for mission failures |
| 5 | 📄 Report Agent | Create summary reports and export packages |

### 💬 Example mission prompt

```text
Plan a surveillance mission around the campus for 20 minutes.
Keep altitude below 80 meters, avoid restricted airspace,
and return to launch after completion.
```

---

## 🛡 Safety Compliance Rules

Every generated mission passes through a seven rule safety audit before it is marked as approved.

| Rule | Description | Limit |
|---|---|---|
| R1 | Maximum altitude ceiling | 80 meters |
| R2 | Mission must include a takeoff command | Required |
| R3 | Mission must include RTL or a landing point | Required |
| R4 | No waypoint may enter a no fly zone | Zero tolerance |
| R5 | Maximum distance between route points | 500 meters |
| R6 | Maximum mission duration | 30 minutes |
| R7 | Battery reserve must stay below 80 percent usage | Required |

---

## 🗺 Route Profiles

| Pattern | Best use case |
|---|---|
| 🟦 Square | Campus and building perimeter scanning |
| ⚡ Grid | Field coverage and agricultural mapping |
| ⭕ Circle | Point of interest inspection |
| 🔷 Perimeter | Large area boundary patrol |

All routes include a takeoff command, altitude assignment, sequence numbers, and return to launch behavior.

---

## 🌟 Features

- 🛩️ Natural language mission creation
- 📍 Automatic waypoint route generation for four flight patterns
- 🗺 Live airspace map with route overlay and no fly zone rendering
- 🛡 Seven rule mission safety audit engine
- 🔧 AI correction recommendations for failed checks
- 📂 SQLite mission history with search, filter, and pagination
- 📤 Export to plan, waypoint, kml, json, csv, and pdf formats
- 🧾 Report generation with full audit summaries
- 🎨 Dark and light display modes with responsive layout
- 🐳 Docker ready for one command deployment

---

## 🛠 Technology Stack

| Component | Tool |
|---|---|
| Language | Python 3.12 |
| Framework | Streamlit |
| AI Engine | Google Gemini AI |
| Interactive Maps | Folium |
| Data Processing | Pandas |
| Spatial Geometry | Shapely |
| Database | SQLite |
| PDF Export | ReportLab |
| Containerization | Docker |

---

## 📁 Repository Layout

```text
agentic-uav-mission-planner/
├── agents/                  AI agent modules for the mission pipeline
├── config/                  App settings and no fly zone definitions
├── data/                    Sample missions and waypoint data
├── docs/                    Project report and technical documentation
├── reports/
│   └── generated_reports/   Exported mission reports
├── screenshots/             Demo images referenced in this README
├── tests/                   Automated test cases
├── utils/                   Helper utilities for maps, exports, and database
├── .dockerignore
├── .gitignore
├── app.py                   Main Streamlit application
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

1. Clone the repository:

```bash
git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git
cd agentic-uav-mission-planner
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS and Linux
source .venv/bin/activate

pip install -r requirements.txt
```

3. Add your Gemini API key in a `.env` file:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Get your key here: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

4. Run the app:

```bash
streamlit run app.py
```

5. Open the local Streamlit URL shown in your terminal, typically `http://localhost:8501`.

---

## 🐳 Running with Docker

### Option A, Docker Compose (recommended)

```bash
docker compose up --build
```

### Option B, Docker CLI

```bash
docker build -t agentic-uav-mission-planner .
docker run -d -p 8501:8501 --env-file .env --name uav-planner agentic-uav-mission-planner
```

Then open `http://localhost:8501` in your browser.

---

## 🖥 Application Pages

| Page | Purpose |
|---|---|
| 🏠 Home | Mission overview and quick start dashboard |
| 📝 Mission Input | Natural language prompt or manual parameter entry |
| ⚙ Mission Plan | Waypoint generation and mission report view |
| 🗺 Map View | Interactive route and no fly zone map |
| 🛡 Safety Check | Rule by rule compliance audit |
| 💡 Suggestions | Correction recommendations |
| 📥 Export | Download plan, waypoints, kml, json, csv, and pdf |
| 📂 Mission History | Database search, history map preview, import and export |

---

## 💡 Notes

- This project is a software only mission planning demo.
- It is not a live drone autopilot or flight controller.
- Always validate exported mission files in a dedicated ground station before real world use.

---

## 📬 Contact

- 👤 Author: Abdul Azeem Hashmi
- 🐙 GitHub: [github.com/AbdulAzeemHashmi](https://github.com/AbdulAzeemHashmi)
- 📦 Repository: [agentic-uav-mission-planner](https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for full details.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0072ff,100:00c6ff&height=100&section=footer&animation=fadeIn" width="100%"/>

**Built with 🛩️ 🤖 and 💙 for UAV research and education**

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=AbdulAzeemHashmi.agentic-uav-mission-planner)

</div>