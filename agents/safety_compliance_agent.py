from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, Polygon
from utils.distance_utils import calculate_haversine_distance

# Define No-Fly Zones (NFZs)
# Format: {"name": str, "type": "circle"|"polygon", "center": (lat, lon), "radius_m": float, "coords": [(lat, lon), ...]}
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
    Checks if a coordinate violates any no-fly zone.
    Returns (is_violated, zone_name).
    """
    for nfz in NO_FLY_ZONES:
        if nfz["type"] == "circle":
            c_lat, c_lon = nfz["center"]
            dist = calculate_haversine_distance(lat, lon, c_lat, c_lon)
            if dist <= nfz["radius_m"]:
                return True, nfz["name"]
        elif nfz["type"] == "polygon":
            poly = Polygon(nfz["coords"])
            # In shapely, x is longitude, y is latitude or we can just use them as coordinates in order.
            # coords is lat, lon. Point is lat, lon. That works if Polygon and Point use the same ordering.
            pt = Point(lat, lon)
            if poly.contains(pt):
                return True, nfz["name"]
    return False, ""

def perform_safety_checks(
    mission_data: Dict[str, Any],
    waypoints: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Runs all rule-based safety compliance checks on the generated mission plan.
    Returns a list of check result details.
    """
    results = []
    
    # Extract params
    altitude = float(mission_data.get("altitude", 50.0))
    duration = float(mission_data.get("duration", 15.0))
    
    # --- R1: Maximum Altitude Check ---
    r1_pass = altitude <= 80.0
    results.append({
        "check_name": "R1: Max Altitude Limit",
        "result": "Pass" if r1_pass else "Fail",
        "message": f"Requested altitude {altitude}m is {'within' if r1_pass else 'above'} the 80m limit."
    })
    
    # --- R2: Takeoff Point Check ---
    r2_pass = len(waypoints) > 0 and waypoints[0]["action"] == "takeoff"
    results.append({
        "check_name": "R2: Takeoff Point",
        "result": "Pass" if r2_pass else "Fail",
        "message": "Mission starts with a takeoff waypoint." if r2_pass else "Mission is missing a takeoff point."
    })
    
    # --- R3: RTL or Landing Point Check ---
    r3_pass = len(waypoints) > 0 and waypoints[-1]["action"] in ["rtl", "land"]
    results.append({
        "check_name": "R3: Landing/RTL Action",
        "result": "Pass" if r3_pass else "Fail",
        "message": f"Mission terminates with {waypoints[-1]['action'].upper()} action." if r3_pass else "Mission does not end with land or RTL action."
    })
    
    # --- R4: No-Fly Zone (Geofence) Check ---
    r4_pass = True
    violated_zones = []
    for idx, wp in enumerate(waypoints):
        violated, zone_name = check_geofence_violation(wp["latitude"], wp["longitude"])
        if violated:
            r4_pass = False
            violated_zones.append(f"Waypoint {idx} in {zone_name}")
            
    results.append({
        "check_name": "R4: No-Fly Zone / Geofence Check",
        "result": "Pass" if r4_pass else "Fail",
        "message": "All waypoints avoid restricted airspaces." if r4_pass else f"Violations detected: {', '.join(violated_zones)}."
    })
    
    # --- R5: Distance Between Consecutive Waypoints ---
    r5_pass = True
    max_dist = 0.0
    violated_wps = []
    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i+1]
        dist = calculate_haversine_distance(wp1["latitude"], wp1["longitude"], wp2["latitude"], wp2["longitude"])
        if dist > max_dist:
            max_dist = dist
        if dist > 500.0:
            r5_pass = False
            violated_wps.append(f"Wp {i}->{i+1} ({dist:.1f}m)")
            
    results.append({
        "check_name": "R5: Max Waypoint Distance Limit",
        "result": "Pass" if r5_pass else "Fail",
        "message": f"All leg distances are under 500m (Max leg: {max_dist:.1f}m)." if r5_pass else f"Legs exceed 500m limit: {', '.join(violated_wps)}."
    })
    
    # --- R6: Mission Duration Check ---
    r6_pass = duration <= 30.0
    results.append({
        "check_name": "R6: Mission Duration Limit",
        "result": "Pass" if r6_pass else "Fail",
        "message": f"Mission duration {duration} mins is within the 30-minute safety window." if r6_pass else f"Mission duration {duration} mins exceeds the 30-minute maximum limit."
    })
    
    # --- R7: Battery Usage Heuristic ---
    # Heuristic: 2.0% battery per minute of hover/flight, plus 0.04% per meter of travel
    total_distance = 0.0
    for i in range(len(waypoints) - 1):
        total_distance += calculate_haversine_distance(waypoints[i]["latitude"], waypoints[i]["longitude"], waypoints[i+1]["latitude"], waypoints[i+1]["longitude"])
        
    est_battery_used = (duration * 2.0) + (total_distance * 0.04)
    r7_pass = est_battery_used < 80.0
    
    results.append({
        "check_name": "R7: Battery Capacity Margin",
        "result": "Pass" if r7_pass else "Fail",
        "message": f"Estimated battery consumption is {est_battery_used:.1f}% (limit is 80%)." if r7_pass else f"Estimated battery consumption of {est_battery_used:.1f}% exceeds safe margin (80% max)."
    })
    
    return results
