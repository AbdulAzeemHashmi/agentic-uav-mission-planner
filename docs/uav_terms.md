# UAV Mission Planning Terminology

This document provides a reference for core terminology and concepts in Unmanned Aerial Vehicle (UAV) mission planning, route visualization, and safety compliance checks.

## Key UAV Flight Terms

### 1. Waypoint
A **waypoint** is a set of coordinates (latitude, longitude, and usually altitude) that defines a physical point along a planned flight path. During a mission, the UAV's autopilot system navigates sequentially through these waypoints. Waypoints can also have associated actions, such as hovering, taking photos, performing payload release, or initiating land sequences.

### 2. Return-To-Launch (RTL)
**Return-to-Launch** (or RTL/RTH - Return-to-Home) is a safety and convenience command. When triggered, the UAV aborts its current mission task and flies directly (or via a preset altitude path) back to its takeoff coordinates (home point) and lands automatically. RTL is commonly used as a terminal step in planned missions or triggered automatically as a fail-safe during low battery or signal loss events.

### 3. Geofence
A **geofence** is a virtual geographic boundary or perimeter. It is defined using GPS coordinates to enclose a specific 2D or 3D airspace. The geofence serves as a spatial limit:
*   **Inclusion Geofences**: Contain the drone. If the drone attempts to fly outside the geofence, the autopilot restricts movement or triggers a fail-safe (such as hovering or RTL).
*   **Exclusion Geofences**: Keep the drone out of specific zones (e.g., restricted zones, property boundaries).

### 4. No-Fly Zone (NFZ)
A **No-Fly Zone** is a specific type of exclusion geofence. These are areas where drone flight is restricted or completely prohibited due to regulations, safety, or security concerns. Examples include:
*   Military bases and government complexes
*   Airports, heliports, and flight paths of commercial aircraft
*   High-voltage electricity grids and nuclear facilities
*   Crowded public venues or sporting events

---

## Importance of Mission Safety Checking

Autonomous UAV operations rely heavily on pre-planned coordinates. Because human planners can make errors, automated **mission safety checking** (or compliance auditing) is crucial before a drone takes off. 

### Why Automated Compliance is Critical:
1.  **Preventing Collisions and Airspace Violations**: An automated checker verifies that the planned flight path does not enter restricted airspaces or no-fly zones (like Zone A and Zone B), protecting public safety and avoiding legal penalties.
2.  **Equipment and Battery Safety**: Calculating the expected battery drainage based on path length and wind prevents the UAV from running out of power mid-flight, which would cause an uncontrolled crash.
3.  **Regulatory Compliance**: Enforcing local aviation rules (such as maintaining flight altitude below legal thresholds like 80 meters) keeps operations compliant with regional civil aviation authorities (e.g., FAA or local equivalents).
4.  **Fail-safe Assurance**: Verifying that a takeoff command starts the sequence and a terminal landing/RTL command finishes the path ensures the drone does not hover indefinitely or fail to land safely after completing its tasks.
