# UAV Mission Planning and Safety Terms Reference

This document provides a short reference guide explaining core terms and safety concepts relevant to Unmanned Aerial Vehicles (UAVs) and mission planning.

---

## 1. Core Terminology

### Waypoint
A **waypoint** is a specific 3D geographical coordinate (Latitude, Longitude, and Altitude) that a UAV must fly to during its mission. A series of waypoints forms the UAV's flight route. Each waypoint is typically associated with a flight action (e.g., hover, photograph, takeoff, land).

### RTL (Return-To-Launch)
**Return-to-Launch** (or Return-to-Home/RTH) is a crucial safety fail-safe mechanism. When triggered, the UAV aborts its current course and flies directly back to the takeoff point (home coordinates). RTL can be triggered manually by the operator or automatically under certain conditions (such as low battery, communication signal loss, or sensor failure).

### Geofence
A **geofence** is a virtual geographic boundary defined by GPS coordinates. It acts as a digital fence. The autopilot software uses geofences to restrict the UAV's flight area:
- **Inclusion Geofence**: Keeps the UAV *inside* a safe zone. If the UAV tries to fly out, it triggers a warning or fail-safe (like hovering or returning to home).
- **Exclusion Geofence (No-Fly Zone)**: Keeps the UAV *out* of restricted zones. The UAV is prohibited from crossing into this boundary.

### No-Fly Zone (NFZ)
A **no-fly zone** is a restricted airspace where drone operations are prohibited or heavily restricted by civil aviation authorities (e.g., FAA or CAA). Common examples include airspaces around commercial airports, military facilities, power plants, crowded stadiums, and national parks.

---

## 2. Importance of Mission Safety Checking

Planning a mission route without safety verification poses severe risks:
1. **Collisions & Liability**: Drone flight path intersections with trees, power structures, or buildings due to low altitude settings.
2. **Flyaways**: Missions where the waypoints exceed transmitter range or battery capacity, leading to lost aircraft.
3. **Legal Violations**: Accidental intrusion into restricted military airspace or airport boundaries, resulting in massive fines or prosecution.
4. **Airspace Congestion**: Ensuring the drone stays below local regulatory ceilings (e.g., 80m or 120m depending on the region) to avoid commercial aviation conflicts.

By integrating automated agents to check safety constraints before execution, operators ensure that flight parameters comply with civil aviation guidelines, physical battery capabilities, and geographical restrictions.
