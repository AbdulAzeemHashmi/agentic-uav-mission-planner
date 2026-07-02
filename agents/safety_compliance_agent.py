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


def perform_safety_checks(mission_data: Dict[str, Any], waypoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Executes the 7 core safety rule compliance checks against planned mission parameters and waypoints.
    """
    results = []
    altitude = mission_data.get("altitude", 50.0)
    duration = mission_data.get("duration", 15.0)

    # --- R1: Maximum Altitude Limit ---
    r1_pass = altitude <= 80.0
    results.append({
        "check_name": "R1: Maximum Altitude Limit",
        "result": "Pass" if r1_pass else "Fail",
        "message": f"Planned altitude {altitude}m is within the legal 80m limit." if r1_pass else f"Planned altitude {altitude}m exceeds the maximum 80m legal limit."
    })

    # --- R2: Takeoff Verification ---
    r2_pass = len(waypoints) > 0 and waypoints[0].get("action") == "takeoff"
    results.append({
        "check_name": "R2: Takeoff Verification",
        "result": "Pass" if r2_pass else "Fail",
        "message": "Mission sequence initiates with a proper takeoff command." if r2_pass else "Mission is missing a designated takeoff starting sequence."
    })

    # --- R3: Landing/RTL Verification ---
    r3_pass = len(waypoints) > 0 and waypoints[-1].get("action") in ["rtl", "land"]
    results.append({
        "check_name": "R3: Landing/RTL Verification",
        "result": "Pass" if r3_pass else "Fail",
        "message": f"Mission sequence safely terminates with an termination action ({waypoints[-1].get('action') if waypoints else 'None'})." if r3_pass else "Mission sequence lacks a terminal land or return-to-launch (RTL) command."
    })

    # --- R4: Geofence Compliance ---
    violated_zones = []
    for wp in waypoints:
        violated, zone_name = check_geofence_violation(wp["latitude"], wp["longitude"])
        if violated and zone_name not in violated_zones:
            violated_zones.append(zone_name)
            
    r4_pass = len(violated_zones) == 0
    results.append({
        "check_name": "R4: Geofence Compliance Check",
        "result": "Pass" if r4_pass else "Fail",
        "message": "All waypoints successfully clear registered geofenced zones." if r4_pass else f"Route violates restricted airspace: {', '.join(violated_zones)}."
    })

    # --- R5: Maximum Leg Length ---
    max_dist = 0.0
    violated_wps = []
    for i in range(len(waypoints) - 1):
        dist = calculate_haversine_distance(
            waypoints[i]["latitude"], waypoints[i]["longitude"],
            waypoints[i+1]["latitude"], waypoints[i+1]["longitude"]
        )
        if dist > max_dist:
            max_dist = dist
        if dist > 500.0:
            violated_wps.append(f"{waypoints[i]['sequence_no']}->{waypoints[i+1]['sequence_no']}")
            
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
        total_distance += calculate_haversine_distance(
            waypoints[i]["latitude"], waypoints[i]["longitude"],
            waypoints[i+1]["latitude"], waypoints[i+1]["longitude"]
        )
        
    est_battery_used = (duration * 2.0) + (total_distance * 0.04)
    r7_pass = est_battery_used < 80.0
    results.append({
        "check_name": "R7: Battery Heuristic Drainage Model",
        "result": "Pass" if r7_pass else "Fail",
        "message": f"Estimated battery usage of {est_battery_used:.1f}% is safely under the 80% threshold." if r7_pass else f"Estimated battery consumption ({est_battery_used:.1f}%) exceeds the 80% safety margin safety limit."
    })

    return results