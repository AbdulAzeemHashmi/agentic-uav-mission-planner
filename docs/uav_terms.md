# UAV Mission Planning and Safety Concepts Reference

This document provides a comprehensive reference guide for UAV (Unmanned Aerial Vehicle) mission planning concepts, terminology, and safety principles essential for understanding the Agentic UAV Mission Planner project.

---

## 1. Core UAV Terminology

### Waypoint
A **waypoint** is a specific geographic location defined by three coordinates:
- **Latitude** (decimal degrees, N/S)
- **Longitude** (decimal degrees, E/W)
- **Altitude** (meters above ground level or sea level)

During a mission, the UAV flies from one waypoint to another in sequential order. Each waypoint can have an associated action (hover, photograph, investigate, etc.). The series of waypoints creates the complete flight path/route.

**Example:** A surveillance mission might include:
- Waypoint 0: (33.6425, 73.0232, 0m) - Takeoff
- Waypoint 1: (33.6430, 73.0237, 50m) - Fly to scan area
- Waypoint 2: (33.6435, 73.0242, 50m) - Move to next scan position
- Waypoint 3: (33.6425, 73.0232, 0m) - Return and land

### Takeoff Point / Home Location
The **home location** (or **takeoff point**) is the geographic coordinate where the UAV physically sits on the ground before launching. This is always the first waypoint (sequence 0) and also the final RTL destination. It's crucial for safety because if the UAV loses connection or faces an emergency, it automatically returns to this safe location.

### Altitude
**Altitude** is the vertical distance of the UAV above ground level (AGL) or mean sea level (MSL). Different regions have different altitude restrictions:
- **Standard limit:** 80-120 meters AGL
- **City areas:** 50 meters or less
- **Open rural areas:** May allow up to 400 meters
- **Military/protected zones:** Restricted or prohibited

In this project, we enforce a maximum altitude of 80 meters for safety.

### RTL (Return-to-Launch) / Return-to-Home (RTH)
**Return-to-Launch** is a critical UAV safety feature. When RTL is triggered:
1. The UAV immediately stops its current mission
2. It navigates directly back to the home location
3. It lands or hovers at the home point

RTL can be triggered by:
- Pilot manual command
- Low battery warning
- Loss of communication signal
- UAV system failure
- Operator timeout

**Why it matters:** RTL prevents lost aircraft and ensures the UAV can always find its way home.

### Landing Point
The **landing point** is where the UAV will descend and shut down. Usually this is the same as the home location, but advanced missions might land at a different location. Landing transitions the UAV from flight (altitude > 0m) to ground (altitude 0m).

---

## 2. Geographic Restrictions and Airspace Concepts

### Geofence / Geofencing
A **geofence** is a virtual geographic boundary drawn on a map using GPS coordinates. UAV autopilot software uses geofences to restrict where the aircraft can fly:

**Inclusion Geofence:**
- Keeps the UAV INSIDE a safe zone
- If the UAV tries to fly outside, it triggers actions like hovering or RTL
- Used for "keep-in" safety boundaries

**Exclusion Geofence (No-Fly Zone):**
- Keeps the UAV OUT of restricted zones
- The UAV is prohibited from crossing this boundary
- Used around dangerous or restricted areas

**Geofence Structure:**
A geofence is defined by coordinates that form a polygon or circle:
```
Polygon Example (4 corner waypoints):
NW -------- NE
|            |
|  SAFE ZONE |
|            |
SW -------- SE
```

### No-Fly Zone (NFZ)
A **no-fly zone** is officially restricted airspace where drone operations are prohibited or heavily regulated by civil aviation authorities. Common no-fly zones include:

- **Airports and runway corridors** - Commercial and military aircraft operations
- **Military facilities** - National defense areas
- **Power plants and electrical grid** - Critical infrastructure protection
- **Government buildings** - Security and privacy
- **Crowded stadiums/events** - Public safety
- **Hospitals** - Privacy and emergency operations
- **National parks** - Environmental protection
- **Urban residential areas** - Privacy and safety

**Enforcement:**
- Violating airspace can result in fines up to $27,500 (USA)
- Criminal prosecution in severe cases
- Aircraft confiscation
- Permanent operating license revocation

**In this project:** The Safety Compliance Agent checks all waypoints against predefined no-fly zones and prevents missions from entering restricted areas.

---

## 3. Mission Planning Concepts

### Mission
A **mission** is a complete flight plan that includes:
- Mission name and description
- Mission type (surveillance, delivery, inspection, search-and-rescue)
- Home/takeoff location
- Flight altitude
- Route waypoints
- Return-to-launch behavior
- Flight duration estimate
- Safety constraints

### Route Pattern
A **route pattern** is the geometric shape the UAV will follow:

1. **Square Pattern**: UAV flies a square perimeter around home
   - Use case: Quick surveillance, border patrol
   - Waypoint count: 4-6

2. **Grid/Lawnmower Pattern**: UAV flies parallel rows like mowing a lawn
   - Use case: Area mapping, crop monitoring, search
   - Waypoint count: 9-30+ depending on area size

3. **Perimeter/Circular Pattern**: UAV flies a circle around home
   - Use case: Boundary verification, circular patrol
   - Waypoint count: 8-16 (octagon approximation)

4. **Manual Pattern**: User defines custom waypoints
   - Use case: Complex missions, specific areas of interest

### Mission Duration
**Duration** is the estimated time for the complete mission, typically:
- Takeoff: 0.5 - 1 minute
- Flight to waypoints: 1-2 minutes per waypoint (depending on distance)
- Scanning/hovering: 1-5 minutes per waypoint
- Return to home: 1-3 minutes
- Landing: 0.5 - 1 minute

**Safe range:** 15-30 minutes maximum for this project.

### Mission Type
Standard UAV mission classifications:

- **Surveillance**: Monitor area, record video/photos
- **Delivery**: Transport package from point A to point B
- **Inspection**: Close-range visual inspection of infrastructure
- **Search and Rescue**: Find missing persons or objects

---

## 4. Safety and Compliance Concepts

### Mission Safety Checking
**Mission safety checking** is the automated verification process that ensures a planned mission complies with safety rules before execution. This prevents:

1. **Collisions & Damage** - Hitting trees, power lines, buildings due to low altitude
2. **Flyaway Aircraft** - Missions exceeding communication range or battery capacity
3. **Legal Violations** - Operating in restricted airspace, facing fines/prosecution
4. **Airspace Conflicts** - Interfering with manned aircraft or other operations
5. **Battery Depletion** - Running out of power mid-flight, crashing

**Safety rules this project enforces:**
- Maximum altitude limit (80m)
- Takeoff point verification
- RTL/landing point verification
- No-fly zone avoidance
- Waypoint distance limits
- Mission duration limits
- Battery capacity estimates

### Battery and Power Management
UAV batteries determine flight time and range:
- **Flight endurance**: Typically 15-30 minutes with consumer drones
- **Power consumption**: Higher with payload, faster flight, larger drones
- **Reserve requirement**: Always maintain 20-30% reserve for emergencies
- **Estimation formula**: Estimated % = (Duration in minutes × 2) + (Distance in meters × 0.04)

### Correction and Suggestions
When a mission fails safety checks, the system suggests corrections:

**Examples:**
- "Reduce altitude from 120m to 80m" (safety rule violation)
- "Move waypoint 3 outside the military zone" (geofence violation)
- "Reduce mission duration from 45 to 30 minutes" (time limit violation)
- "Reduce flight speed to save battery" (battery usage violation)

---

## 5. Why Mission Safety Checking is Important

### Real-World Consequences

1. **Legal**: Federal fines up to $27,500, criminal charges, license revocation
2. **Safety**: Risk of collision with people, property, manned aircraft
3. **Financial**: Aircraft loss, liability insurance claims, business shutdown
4. **Environmental**: Damage to infrastructure, power outages, property damage

### Best Practices
- Always plan missions with safety tools
- Check local airspace restrictions before every flight
- Maintain 30% battery reserve
- Use geofences for all flights
- Document all missions
- Follow civil aviation authority guidelines

### Regulations Reference
- **USA**: FAA Part 107 (Commercial drone operations)
- **EU**: EASA (European Aviation Safety Agency) regulations
- **UK**: CAA (Civil Aviation Authority) guidelines
- **Pakistan**: CAA (Civil Aviation Authority) Pakistan
- **Canada**: Transport Canada drone regulations

---

## 6. Project-Specific Constraints

### Default Test Location
- **Home Location**: 33.6425°N, 73.0232°E (Islamabad, Pakistan area)
- **Altitude Limit**: 80 meters
- **Duration Limit**: 30 minutes
- **Max Waypoint Distance**: 500 meters between consecutive waypoints
- **Battery Reserve**: 20% minimum

### Seven Safety Rules Enforced

1. **R1**: Altitude ≤ 80m
2. **R2**: Mission must have takeoff point
3. **R3**: Mission must have RTL or landing point
4. **R4**: No waypoints in no-fly zones
5. **R5**: Max 500m between consecutive waypoints
6. **R6**: Duration ≤ 30 minutes
7. **R7**: Estimated battery usage < 80%

---

## 7. Quick Reference Table

| Term | Definition | Example |
|------|-----------|---------|
| **Waypoint** | Single GPS coordinate (lat, lon, alt) | (33.6425, 73.0232, 50) |
| **Takeoff** | First waypoint at home location | Waypoint 0 |
| **Altitude** | Height above ground in meters | 50m, 80m, 120m |
| **RTL** | Automatic return to home | Emergency trigger |
| **Geofence** | Virtual boundary using GPS coords | Airport buffer zone |
| **No-Fly Zone** | Restricted airspace | Military area |
| **Route Pattern** | Flight shape (square, grid, circle) | Grid pattern |
| **Duration** | Estimated mission time | 20 minutes |
| **Battery** | Power reserve percentage | 75% usage |
| **Correction** | Suggested mission fix | Reduce altitude to 80m |

---

## 8. Additional Resources

- **UAV Terminology**: Research FAA Part 107 regulations
- **Geofencing**: Understand exclusion vs. inclusion boundaries
- **Mission Planning**: Review QGroundControl mission planning tutorials
- **Safety Standards**: Consult local aviation authority guidelines

---

**Last Updated:** 2026-07-02  
**Project:** Agentic UAV Mission Planning and Safety Compliance Assistant  
**Student:** Abdul Azeem Hashmi

