from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, Polygon
from utils.distance_utils import calculate_haversine_distance

# Preconfigured No-Fly Zone Fences
NO_FLY_ZONES = [
    {
        "name": "Restricted Military Airspace (Zone A)",
        "type": "circle",
        "center": (33.6438, 73.0210),
        "radius_m": 120.0
    },
    {
        "name": "High Voltage Grid Facility (Zone B)",
        "type": "polygon",
        "coords": [
            (33.6410, 73.0255),
            (33.6410, 73.0270),
            (33.6395, 73.0270),
            (33.6395, 73.0255)
        ]
    }
]


def check_geofence_violation(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Checks if a coordinate violates any registered no-fly zone fences.
    """
    p = Point(lat, lon)
    
    for nfz in NO_FLY_ZONES:
        if nfz["type"] == "circle":
            c_lat, c_lon = nfz["center"]
            dist = calculate_haversine_distance(lat, lon, c_lat, c_lon)
            if dist <= nfz["radius_m"]:
                return True, nfz["name"]
        elif nfz["type"] == "polygon":
            poly = Polygon(nfz["coords"])
            if poly.contains(p):
                return True, nfz["name"]
                
    return False, ""


def evaluate_safety_constraints(
    mission_data: Dict[str, Any],
    waypoints: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Executes an array verification across structural rules R1 through R7.
    """
    results = []
    
    # Extract structural profile metadata fields safely
    altitude = float(mission_data.get("altitude", 50.0))
    duration = float(mission_data.get("duration", 15.0))
    rtl_needed = bool(mission_data.get("return_to_launch", True))
    avoid_nfz = bool(mission_data.get("avoid_no_fly_zone", True))

    # --- R1: Absolute Operational Ceiling Bounds ---
    r1_pass = altitude <= 80.0
    results.append({
        "check_name": "R1: Maximum Operational Ceiling",
        "result": "Pass" if r1_pass else "Fail",
        "message": f"Requested flight altitude {altitude}m matches safe operating ceiling rules." if r1_pass else f"Requested flight altitude {altitude}m breaches the strict 80m standard ceiling constraint."
    })

    # --- R2: Initialization Vector Launch Check ---
    r2_pass = len(waypoints) > 0 and waypoints[0].get("action") == "takeoff"
    results.append({
        "check_name": "R2: Initial Takeoff Sequence Verification",
        "result": "Pass" if r2_pass else "Fail",
        "message": "Launch point initialization vector successfully checked." if r2_pass else "Mission sequence array fails validation rules (missing sequence index 0 Takeoff vector)."
    })

    # --- R3: Secure Termination Check ---
    r3_pass = len(waypoints) > 0 and waypoints[-1].get("action") in ["rtl", "land"]
    results.append({
        "check_name": "R3: Terminal Return Recovery Validation",
        "result": "Pass" if r3_pass else "Fail",
        "message": f"Verified recovery protocol action type: '{waypoints[-1].get('action') if waypoints else 'None'}'" if r3_pass else "Mission structure fails safely ending recovery configuration checks."
    })

    # --- R4: No-Fly Zone Boundary Containment Check ---
    violated_zones = set()
    if avoid_nfz:
        for wp in waypoints:
            violation, zone_name = check_geofence_violation(wp["latitude"], wp["longitude"])
            if violation:
                violated_zones.add(zone_name)
                
    r4_pass = len(violated_zones) == 0
    results.append({
        "check_name": "R4: No-Fly Zone Spatial Containment Check",
        "result": "Pass" if r4_pass else "Fail",
        "message": "Spatial routing remains clear of all active hazard polygons." if r4_pass else f"Geofence breached inside: {', '.join(violated_zones)}."
    })

    # --- R5: Inter-Waypoint Distance Cap Check ---
    max_dist = 0.0
    violated_wps = []
    for i in range(len(waypoints) - 1):
        d = calculate_haversine_distance(waypoints[i]["latitude"], waypoints[i]["longitude"], waypoints[i+1]["latitude"], waypoints[i+1]["longitude"])
        if d > max_dist:
            max_dist = d
        if d > 500.0:
            violated_wps.append(f"Seq {waypoints[i]['sequence_no']}->{waypoints[i+1]['sequence_no']}")
            
    r5_pass = len(violated_wps) == 0
    results.append({
        "check_name": "R5: Max Waypoint Distance Limit",
        "result": "Pass" if r5_pass else "Fail",
        "message": f"All leg distances are under 500m (Max leg: {max_dist:.1f}m)." if r5_pass else f"Legs exceed 500m limit: {', '.join(violated_wps)}."
    })

    # --- R6: Safe Duration Window Evaluation ---
    r6_pass = duration <= 30.0
    results.append({
        "check_name": "R6: Mission Duration Limit",
        "result": "Pass" if r6_pass else "Fail",
        "message": f"Mission duration {duration} mins is within the 30-minute safety window." if r6_pass else f"Mission duration {duration} mins exceeds the 30-minute maximum limit."
    })

    # --- R7: Predictive Battery Heuristic Model Check ---
    total_distance = 0.0
    for i in range(len(waypoints) - 1):
        total_distance += calculate_haversine_distance(waypoints[i]["latitude"], waypoints[i]["longitude"], waypoints[i+1]["latitude"], waypoints[i+1]["longitude"])
        
    est_battery_used = (duration * 2.0) + (total_distance * 0.04)
    r7_pass = est_battery_used < 80.0
    results.append({
        "check_name": "R7: Battery Heuristic Drainage Model",
        "result": "Pass" if r7_pass else "Fail",
        "message": f"Calculated drainage load forecast ({est_battery_used:.1f}%) matches power reserve standards." if r7_pass else f"Calculated drainage load profile ({est_battery_used:.1f}%) exceeds the 80% maximum safety threshold limit."
    })

    return results