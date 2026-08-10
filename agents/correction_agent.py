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
) -> Tuple[List[str], Dict[str, Any], List[Dict[str, Any]]]:
    """
    Remediates mission attributes to ensure all parameters strictly align with safety profiles.
    Returns: (suggestions, corrected_mission_data, corrected_waypoints)
    """
    suggestions = []

    # Create complete structural copies to prevent mutation issues
    corrected_mission = copy.deepcopy(mission_data)
    corrected_waypoints = copy.deepcopy(waypoints)

    # Defensive check to ensure safety_checks is iterable
    if not isinstance(safety_checks, list):
        return suggestions, corrected_mission, corrected_waypoints

    for check in safety_checks:
        # Prevent dictionary structure KeyError exceptions
        if not isinstance(check, dict) or check.get("result") != "Fail":
            continue

        name = check.get("check_name", "")

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
                    placed = False
                    # Iteratively test 8 radial directions to ensure the candidate coordinate clears all no-fly zones
                    for nfz in NO_FLY_ZONES:
                        if nfz["name"] == zone_name:
                            base_dist = 30.0
                            if nfz["type"] == "circle":
                                base_dist = nfz["radius_m"] + 25.0

                            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                                test_lat, test_lon = get_point_at_distance_and_bearing(lat, lon, base_dist, angle)
                                test_viol, _ = check_geofence_violation(test_lat, test_lon)
                                if not test_viol:
                                    wp["latitude"] = test_lat
                                    wp["longitude"] = test_lon
                                    suggestions.append(f"Shift Waypoint {idx} safely outside geofence {zone_name} (radial clearance offset {base_dist:.1f}m at {angle}°).")
                                    placed = True
                                    break
                        if placed:
                            break


        # --- R5: Distance Limit Notification ---
        elif "R5" in name:
            suggestions.append("Leg distances exceed 500m. Consider planning closer waypoints or adding intermediate points.")

        # --- R2 or R3: Missing Structural Constraints Recovery ---
        elif "R2" in name or "R3" in name:
            suggestions.append("Re-generate routes to include required takeoff and RTL points automatically.")

    return suggestions, corrected_mission, corrected_waypoints