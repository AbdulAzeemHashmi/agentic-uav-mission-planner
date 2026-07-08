import math
import copy
from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, Polygon
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
                lat, lon = wp.get("latitude", 0), wp.get("longitude", 0)
                viol, zone_name = check_geofence_violation(lat, lon)
                if viol:
                    # Find which zone was violated
                    for nfz in NO_FLY_ZONES:
                        if nfz["name"] == zone_name:
                            if nfz["type"] == "circle":
                                c_lat, c_lon = nfz["center"]
                                radius_m = nfz["radius_m"]
                                bearing_deg = calculate_bearing(c_lat, c_lon, lat, lon)
                                # Move 15 meters beyond circle radius
                                new_lat, new_lon = get_point_at_distance_and_bearing(c_lat, c_lon, radius_m + 15.0, bearing_deg)
                                wp["latitude"] = new_lat
                                wp["longitude"] = new_lon
                                suggestions.append(f"Shift Waypoint {idx} outside circular geofence {zone_name} (radial offset by {radius_m + 15.0:.1f}m).")
                            elif nfz["type"] == "polygon":
                                poly = Polygon(nfz["coords"])
                                p_geom = Point(lat, lon)
                                boundary = poly.boundary
                                closest_point_geom = boundary.interpolate(boundary.project(p_geom))
                                closest_lat, closest_lon = closest_point_geom.x, closest_point_geom.y
                                
                                # Calculate vector and bearing from point to closest boundary point (outward normal)
                                bearing_deg = calculate_bearing(lat, lon, closest_lat, closest_lon)
                                dist_to_boundary = calculate_haversine_distance(lat, lon, closest_lat, closest_lon)
                                
                                # Move 15 meters beyond the closest boundary point
                                new_lat, new_lon = get_point_at_distance_and_bearing(lat, lon, dist_to_boundary + 15.0, bearing_deg)
                                wp["latitude"] = new_lat
                                wp["longitude"] = new_lon
                                suggestions.append(f"Shift Waypoint {idx} outside polygon geofence {zone_name} (shifted along outward normal by {dist_to_boundary + 15.0:.1f}m).")
                            break
        
        # --- R5: Distance Limit Notification ---
        elif "R5" in name:
            suggestions.append("Leg distances exceed 500m. Consider planning closer waypoints or adding intermediate points.")
            
        # --- R2 or R3: Missing Structural Constraints Recovery ---
        elif "R2" in name or "R3" in name:
            suggestions.append("Re-generate routes to include required takeoff and RTL points automatically.")

    return suggestions