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

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=00C6FF&center=true&vCenter=true&width=720&lines=Natural+Language+Mission+Planning;5+AI+Agents+Working+Together;7+Safety+Rules+Checked;Live+Map+Preview;Mission+History+and+Export;Interactive+Screenshots" alt="Typing SVG"/>

<br/>

> 🚁 Agentic UAV Mission Planner converts natural language mission goals into validated UAV flight plans with AI planning, safety checks, and export-ready files.
>
> 🔒 This repository is a software simulation only. No actual drone hardware is controlled.

</div>

---

## 🚀 What This Project Does

Agentic UAV Mission Planner is a Streamlit app that turns text-based mission requests into complete UAV flight plans. It uses a chain of AI agents to:

- Convert plain language into mission details
- Generate mission waypoints and patterns
- Check airspace safety rules and no-fly zones
- Suggest corrections for mission issues
- Export mission plans in multiple formats

---

## 🖼 Demo Gallery

### 🚁 Control Station View

<div align="center">
  <img src="./screenshots/Screenshot%202026-08-10%20220852.png" width="90%" alt="Control Station Dashboard"/>
  <br/>
  <i>Mission dashboard showing route status and planning controls.</i>
  <br/><br/>
  <img src="./screenshots/Screenshot%202026-08-10%20220921.png" width="90%" alt="Airspace Radar"/>
  <br/>
  <i>Live airspace radar view with no-fly zone highlights.</i>
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
  <i>AI-generated mission corrections for safety violations.</i>
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

The app processes user input with a set of AI agents that each add structure, validation, or export readiness:

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
| 1 | Mission Understanding Agent | Parse mission goals from natural language |
| 2 | Waypoint Planner Agent | Build route waypoints and flight legs |
| 3 | Safety Compliance Agent | Validate no-fly zones and mission rules |
| 4 | Correction Agent | Suggest fixes for mission failures |
| 5 | Report Agent | Create summary reports and export packages |

---

## 🌟 Features

- 🚁 Natural language mission creation
- 📍 Automatic waypoint route generation
- 🗺 Live airspace map with route overlay
- 🛡 Seven-rule mission safety audit
- 🔧 AI correction recommendations
- 📂 SQLite mission history and search
- 📤 Export to plan, waypoint, kml, json, csv, pdf
- 🧾 Report generation with audit summaries

---

## 🛠 Technology Stack

- Python 3.12
- Streamlit UI
- Folium map rendering
- SQLite mission storage
- Google Gemini AI parsing
- ReportLab PDF generation
- Pandas data handling

---

## 🚀 Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run app.py
```

3. Open the local Streamlit URL shown in your terminal.

---

## 📁 Repository Layout

- `app.py` - main Streamlit application
- `agents/` - mission planning, safety, correction, report logic
- `config/` - settings and no-fly zone data
- `data/` - sample missions and waypoint data
- `database/` - SQLite mission storage
- `reports/` - generated export output
- `screenshots/` - demo image files referenced here
- `tests/` - automated test cases
- `utils/` - helper utilities for maps and exports

---

## 💡 Notes

- This project is a software-only mission planning demo.
- It is not a live drone autopilot or flight controller.
- Always validate exported mission files in a dedicated ground station.

---

## 📄 License

MIT License
