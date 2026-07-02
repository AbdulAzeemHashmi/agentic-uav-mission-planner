import math
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
    mission_data: Dict[str, Any],
    waypoints: List[Dict[str, Any]],
    safety_checks: List[Dict[str, Any]]
) -> Tuple[List[str], Dict[str, Any], List[Dict[str, Any]]]:
    """
    Remediates mission attributes to ensure all parameters strictly align with safety profiles.
    """
    suggestions = []
    
    # Create complete structural copies to prevent mutation issues
    import copy
    corrected_mission = copy.deepcopy(mission_data)
    corrected_waypoints = copy.deepcopy(waypoints)

    for check in safety_checks:
        if check["result"] == "Fail":
            name = check["check_name"]
            
            # --- R1: High Altitude Cap Overwrite ---
            if "R1" in name:
                corrected_mission["altitude"] = 80.0
                suggestions.append("Clipped operating altitude parameter to the maximum standard ceiling limit of 80m.")
                for wp in corrected_waypoints:
                    if wp["action"] in ["waypoint", "takeoff", "rtl"]:
                        wp["altitude"] = 80.0
                        
            # --- R6: High Duration Overwrite ---
            elif "R6" in name:
                corrected_mission["duration"] = 30.0
                suggestions.append("Clipped mission duration input parameter to the maximum 30-minute safety operating limit.")
                
            # --- R4: Geofence Translocation Nudge Correction ---
            elif "R4" in name:
                for idx, wp in enumerate(corrected_waypoints):
                    viol, zone_name = check_geofence_violation(wp["latitude"], wp["longitude"])
                    if viol:
                        # Attempt shift
                        shift_lat, shift_lon = wp["latitude"], wp["longitude"]
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

    return suggestions, corrected_mission, corrected_waypoints