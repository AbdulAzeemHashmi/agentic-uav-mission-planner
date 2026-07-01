# Agentic UAV Mission Planning and Safety Compliance Assistant

This repository contains a Streamlit-based application for UAV mission planning, route visualization, safety checking, and agentic workflow development. It was built to match the internship project brief for an 8-week software project focused on agentic planning and compliance assistance.

## Internship Project Brief

- **Project Domain:** Unmanned Aerial Vehicles (UAVs), Agentic AI, Safety Compliance
- **Project Type:** End-to-end software application
- **Recommended Duration:** 8 weeks / 2 months
- **Recommended Student Level:** 5th semester undergraduate
- **Hardware Requirement:** No physical UAV required
- **Core Tools:** Python, Streamlit, SQLite, Pandas, Folium, GitHub

## Project Objectives

1. Develop a beginner-friendly UAV mission planning application.
2. Allow mission requests through natural language or manual form input.
3. Convert mission instructions into structured mission data.
4. Generate waypoints automatically for different route patterns.
5. Visualize the route on an interactive map.
6. Apply rule-based safety checks for altitude, duration, geofences, and RTL requirements.
7. Suggest corrections for unsafe or incomplete missions.
8. Generate a mission summary report and export mission data.

## Scope Covered

### Included in Scope
- Streamlit-based web interface
- Natural language mission input
- Manual mission input form
- Waypoint generation
- Mission route visualization
- No-fly zone / geofence definition
- Rule-based safety checking
- Agentic workflow modules
- Mission correction suggestions
- Mission summary reports
- Mission export in JSON and CSV
- SQLite database storage

### Not Included in the Basic Scope
- Real UAV hardware integration
- Real-time UAV control
- Autopilot programming
- Live GPS tracking
- Advanced machine learning training

## Key Features

- Mission Understanding Agent for extracting mission parameters from natural language.
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

## Agentic Workflow

```text
User input -> Mission Understanding Agent -> Waypoint Planner Agent -> Safety Compliance Agent -> Correction Agent -> Report + Export + Database
```

## Safety Rules Enforced

- Maximum altitude must stay within 80 m.
- Mission must include a takeoff point.
- Mission must include RTL or landing behavior.
- Waypoints must avoid no-fly zones.
- Consecutive waypoint distance must stay within 500 m.
- Duration must remain within 30 minutes.
- Estimated battery usage must remain below 80%.

## GitHub Details

- **GitHub Username:** AbdulAzeemHashmi
- **Email:** abdulazeemhashmi29@gmail.com
- **Profile URL:** https://github.com/AbdulAzeemHashmi
- **Repository URL:** https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner
- **Primary Branch:** main
- **Workspace Path:** C:\Users\ABC\.gemini\antigravity-ide\scratch\agentic-uav-mission-planner

## Internship Deliverables Checklist

- Working Streamlit application
- Source code and modular agent design
- Sample mission and waypoint data
- SQLite mission database
- Mission export and report generation
- README and documentation
- Final presentation/demo materials

## Daily Progress Template

```text
Date:
Today's Completed Tasks:
1.
2.
3.
Problems Faced:
1.
2.
How I Solved Them:
1.
2.
Pending Tasks:
1.
2.
GitHub Commit Link:
```

## License

This project is developed as part of an internship program and is intended for academic demonstration and learning.
