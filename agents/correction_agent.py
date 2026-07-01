import math
from typing import List, Dict, Any, Tuple
from agents.safety_compliance_agent import NO_FLY_ZONES, check_geofence_violation
from utils.distance_utils import calculate_haversine_distance, calculate_bearing

def get_point_at_distance_and_bearing(lat: float, lon: float, distance_m: float, bearing_deg: float) -> Tuple[float, float]:
    """Calculate coordinate at a given distance (meters) and bearing (degrees) from a starting point."""
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
    Analyzes safety check failures and builds a list of recommendation strings, 
    as well as auto-corrected mission parameters and waypoints.
    """
    suggestions = []
    
    # Deep copy parameters so we don't mutate original inputs
    corrected_mission = dict(mission_data)
    corrected_waypoints = [dict(wp) for wp in waypoints]
    
    for check in safety_checks:
        if check["result"] == "Fail":
            name = check["check_name"]
            
            # --- R1: Altitude Correction ---
            if "R1" in name:
                orig_alt = float(corrected_mission.get("altitude", 100))
                corrected_mission["altitude"] = 80.0
                suggestions.append(f"Reduce mission altitude from {orig_alt}m to standard 80.0m limit.")
                # Update all waypoints to matching altitude
                for wp in corrected_waypoints:
                    wp["altitude"] = 80.0
            
            # --- R6: Duration Correction ---
            elif "R6" in name:
                orig_dur = float(corrected_mission.get("duration", 45))
                corrected_mission["duration"] = 30.0
                suggestions.append(f"Cap mission duration from {orig_dur} mins to max allowed 30.0 mins.")
            
            # --- R7: Battery Correction ---
            elif "R7" in name:
                # If battery exceeds margin, capping duration to 20m often helps
                orig_dur = float(corrected_mission.get("duration", 30))
                if orig_dur > 20.0:
                    corrected_mission["duration"] = 20.0
                    suggestions.append(f"Battery usage too high. Recommended to reduce duration to 20.0 mins to save power.")
            
            # --- R4: No-Fly Zone / Geofence Correction ---
            elif "R4" in name:
                for idx, wp in enumerate(corrected_waypoints):
                    violated, zone_name = check_geofence_violation(wp["latitude"], wp["longitude"])
                    if violated:
                        # Attempt to push the waypoint out of the geofence
                        # We find the matching zone
                        for zone in NO_FLY_ZONES:
                            if zone["name"] == zone_name:
                                if zone["type"] == "circle":
                                    c_lat, c_lon = zone["center"]
                                    radius = zone["radius_m"]
                                    
                                    # Get bearing from center to waypoint
                                    bearing = calculate_bearing(c_lat, c_lon, wp["latitude"], wp["longitude"])
                                    # Shift coordinate to (radius + 20 meters) away from center
                                    new_lat, new_lon = get_point_at_distance_and_bearing(c_lat, c_lon, radius + 20.0, bearing)
                                    
                                    wp["latitude"] = new_lat
                                    wp["longitude"] = new_lon
                                    suggestions.append(f"Shift Waypoint {idx} outside circular geofence {zone_name} (moved 20m past boundary).")
                                
                                elif zone["type"] == "polygon":
                                    # For simplicity, move polygon violators slightly North-East by offset
                                    # Loop until it's outside
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
            
            # --- R5: Distance limit Correction ---
            elif "R5" in name:
                # If leg distance is too high, we can insert intermediate waypoints.
                # Or suggest moving waypoints closer.
                suggestions.append("Leg distances exceed 500m. Consider planning closer waypoints or adding intermediate points.")
                
            # --- R2 or R3: Missing Takeoff/Landing ---
            elif "R2" in name or "R3" in name:
                suggestions.append("Re-generate routes to include required takeoff and RTL points automatically.")

    return suggestions, corrected_mission, corrected_waypoints
