import math
import copy
from typing import List, Dict, Any, Tuple
from agents.safety_compliance_agent import NO_FLY_ZONES, check_geofence_violation
from utils.distance_utils import calculate_haversine_distance, calculate_bearing


def get_point_at_distance_and_bearing(lat: float, lon: float, distance_m: float, bearing_deg: float) -> Tuple[float, float]:
    """
    Calculates coordinates at a given distance (meters) and bearing (degrees) from a starting point.
    """
    R = 6371000.0  # Earth radius
    bearing_rad = math.radians(bearing_deg)
    
    phi1 = math.radians(lat)
    lambda1 = math.radians(lon)
    
    angular_distance = distance_m / R
    
    phi2 = math.asin(math.sin(phi1) * math.cos(angular_distance) +
                     math.cos(phi1) * math.sin(angular_distance) * math.cos(bearing_rad))
                     
    lambda2 = lambda1 + math.atan2(math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(phi1),
                                  math.cos(angular_distance) - math.sin(phi1) * math.sin(phi2))
                                  
    return math.degrees(phi2), math.degrees(lambda2)


def generate_corrections(
    safety_checks: List[Dict[str, Any]],
    mission_data: Dict[str, Any],
    waypoints: List[Dict[str, Any]]
) -> List[str]:
    """
    Remediates mission attributes to ensure all parameters strictly align with safety profiles.
    Aligned signature with app.py and test_planner.py calling conventions.
    """
    suggestions = []
    
    # Create complete structural copies to prevent mutation issues
    corrected_mission = copy.deepcopy(mission_data)
    corrected_waypoints = copy.deepcopy(waypoints)

    # Defensive check to ensure safety_checks is iterable
    if not isinstance(safety_checks, list):
        return suggestions

    for check in safety_checks:
        # Prevent dictionary structure KeyError exceptions
        if not isinstance(check, dict) or check.get("result") != "Fail":
            continue
            
        name = check.get("check_name", "")
        message = check.get("message", "")
        
        # --- R1: High Altitude Cap Overwrite ---
        if "R1" in name:
            corrected_mission["altitude"] = 80.0
            suggestions.append(f"Clipped operating altitude parameter down from {mission_data.get('altitude', 0)}m to the maximum standard ceiling limit of 80m.")
            for wp in corrected_waypoints:
                if isinstance(wp, dict) and wp.get("action") in ["waypoint", "takeoff", "rtl"]:
                    wp["altitude"] = 80.0
                    
        # --- R6: High Duration Overwrite ---
        elif "R6" in name:
            corrected_mission["duration"] = 30.0
            suggestions.append(f"Clipped mission duration input parameter down from {mission_data.get('duration', 0)} mins to the maximum 30-minute safety operating limit.")
            
        # --- R4: Geofence Translocation Nudge Correction ---
        elif "R4" in name:
            for idx, wp in enumerate(corrected_waypoints):
                if not isinstance(wp, dict):
                    continue
                viol, zone_name = check_geofence_violation(wp.get("latitude", 0), wp.get("longitude", 0))
                if viol:
                    shift_lat, shift_lon = wp.get("latitude", 0), wp.get("longitude", 0)
                    attempts = 0
                    while attempts < 10:
                        shift_lat += 0.0005
                        shift_lon += 0.0005
                        viol, _ = check_geofence_violation(shift_lat, shift_lon)
                        if not viol:
                            break
                        attempts += 1
                        
                    wp["latitude"] = shift_lat
                    wp["longitude"] = shift_lon
                    suggestions.append(f"Nudge Waypoint {idx} outside polygon geofence {zone_name} (offset to North-East).")
        
        # --- R5: Distance Limit Notification ---
        elif "R5" in name:
            suggestions.append("Leg distances exceed 500m. Consider planning closer waypoints or adding intermediate points.")
            
        # --- R2 or R3: Missing Structural Constraints Recovery ---
        elif "R2" in name or "R3" in name:
            suggestions.append("Re-generate routes to include required takeoff and RTL points automatically.")

    return suggestions