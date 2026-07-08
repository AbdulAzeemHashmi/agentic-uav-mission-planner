from typing import List, Dict, Any, Tuple
import math
from shapely.geometry import Point, Polygon, LineString
from utils.distance_utils import calculate_haversine_distance, latlon_to_meters

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


def check_segment_geofence_violation(wp1: Dict[str, Any], wp2: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Checks if the flight path segment between wp1 and wp2 violates any registered no-fly zone fences.
    """
    lat1, lon1 = wp1["latitude"], wp1["longitude"]
    lat2, lon2 = wp2["latitude"], wp2["longitude"]
    
    # Create LineString for polygon checks (using latitude, longitude order to match Polygon coords)
    line = LineString([(lat1, lon1), (lat2, lon2)])
    
    for nfz in NO_FLY_ZONES:
        if nfz["type"] == "polygon":
            poly = Polygon(nfz["coords"])
            if poly.intersects(line):
                return True, nfz["name"]
                
        elif nfz["type"] == "circle":
            c_lat, c_lon = nfz["center"]
            radius_m = nfz["radius_m"]
            
            # Convert coordinates to local meters with respect to (lat1, lon1)
            # This completely avoids degree-meter aspect-ratio distortion!
            x1, y1 = 0.0, 0.0
            x2, y2 = latlon_to_meters(lat2, lon2, lat1, lon1)
            xc, yc = latlon_to_meters(c_lat, c_lon, lat1, lon1)
            
            dy = y2 - y1
            dx = x2 - x1
            
            if dx == 0 and dy == 0:
                dist = calculate_haversine_distance(lat1, lon1, c_lat, c_lon)
                if dist <= radius_m:
                    return True, nfz["name"]
                continue
                
            uy = yc - y1
            ux = xc - x1
            
            t = (ux * dx + uy * dy) / (dx * dx + dy * dy)
            t_clamped = max(0.0, min(1.0, t))
            
            closest_x = x1 + t_clamped * dx
            closest_y = y1 + t_clamped * dy
            
            # Calculate exact Euclidean distance in local metric space
            dist = math.sqrt((closest_x - xc)**2 + (closest_y - yc)**2)
            if dist <= radius_m:
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
            
    # Check flight path segments between consecutive waypoints
    for i in range(len(waypoints) - 1):
        violated, zone_name = check_segment_geofence_violation(waypoints[i], waypoints[i+1])
        if violated and zone_name not in violated_zones:
            violated_zones.append(zone_name)
            
    r4_pass = len(violated_zones) == 0
    results.append({
        "check_name": "R4: Geofence Compliance Check",
        "result": "Pass" if r4_pass else "Fail",
        "message": "All waypoints and flight path segments successfully clear registered geofenced zones." if r4_pass else f"Route violates restricted airspace: {', '.join(violated_zones)}."
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
    # Realistic physics-based energy model
    battery_capacity_wh = 90.0  # Wh (standard 4S LiPo drone battery)
    
    # Speed parameters
    v_cruise = 10.0  # m/s
    v_climb = 4.0  # m/s
    v_descend = 2.0  # m/s
    
    # Power consumption constants (Watts)
    p_climb = 215.0
    p_cruise = 120.0
    p_hover = 130.0
    p_descend = 115.0
    
    t_climb = 0.0
    t_cruise_all = 0.0
    t_descend = 0.0
    
    energy_climb = 0.0
    energy_cruise = 0.0
    energy_descend = 0.0
    
    # Iterate over waypoints to compute transition energy
    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i+1]
        action2 = wp2.get("action", "").lower()
        
        dist = calculate_haversine_distance(
            wp1["latitude"], wp1["longitude"],
            wp2["latitude"], wp2["longitude"]
        )
        
        # Calculate horizontal cruise energy
        t_leg = dist / v_cruise
        t_cruise_all += t_leg
        energy_cruise += p_cruise * t_leg / 3600.0
        
        # Handle takeoff vertical ascent
        if wp1.get("action", "").lower() == "takeoff":
            t_asc = altitude / v_climb
            t_climb += t_asc
            energy_climb += p_climb * t_asc / 3600.0
            
        # Handle land/rtl vertical descent
        if action2 in ["rtl", "land"]:
            t_desc = altitude / v_descend
            t_descend += t_desc
            energy_descend += p_descend * t_desc / 3600.0
            
    # Hover time calculation (remaining mission duration)
    fly_time_sec = t_climb + t_cruise_all + t_descend
    planned_time_sec = duration * 60.0
    t_hover = max(0.0, planned_time_sec - fly_time_sec)
    energy_hover = p_hover * t_hover / 3600.0
    
    total_energy_wh = energy_climb + energy_cruise + energy_descend + energy_hover
    est_battery_used = (total_energy_wh / battery_capacity_wh) * 100.0
    
    # Cap battery percentage at 100%
    est_battery_used = min(100.0, est_battery_used)
    
    r7_pass = est_battery_used < 80.0
    results.append({
        "check_name": "R7: Battery Heuristic Drainage Model",
        "result": "Pass" if r7_pass else "Fail",
        "message": f"Estimated battery usage of {est_battery_used:.1f}% is safely under the 80% threshold." if r7_pass else f"Estimated battery consumption ({est_battery_used:.1f}%) exceeds the 80% safety margin safety limit."
    })

    return results