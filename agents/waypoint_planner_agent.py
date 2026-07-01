import math
from typing import List, Dict, Any

def generate_waypoints(
    home_lat: float,
    home_lon: float,
    altitude: float,
    pattern: str = "square",
    rtl_enabled: bool = True
) -> List[Dict[str, Any]]:
    """
    Generates a sequence of UAV waypoints based on the route pattern, home location, and altitude.
    Each waypoint is a dictionary containing sequence_no, latitude, longitude, altitude, and action.
    """
    waypoints = []
    seq = 0
    
    # 1. Always start with Takeoff at the Home Point
    waypoints.append({
        "sequence_no": seq,
        "latitude": home_lat,
        "longitude": home_lon,
        "altitude": altitude,
        "action": "takeoff"
    })
    seq += 1
    
    # Degree offsets for local waypoints (0.001 deg is approx. 111 meters)
    offset = 0.001 
    
    if pattern.lower() == "square":
        # Create 4 points of a square path
        square_offsets = [
            (offset, offset),
            (offset, -offset),
            (-offset, -offset),
            (-offset, offset)
        ]
        for lat_off, lon_off in square_offsets:
            waypoints.append({
                "sequence_no": seq,
                "latitude": home_lat + lat_off,
                "longitude": home_lon + lon_off,
                "altitude": altitude,
                "action": "waypoint"
            })
            seq += 1
            
    elif pattern.lower() == "circle":
        # 8-point circular orbit path
        num_points = 8
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            lat_off = offset * math.cos(angle)
            lon_off = offset * math.sin(angle)
            waypoints.append({
                "sequence_no": seq,
                "latitude": home_lat + lat_off,
                "longitude": home_lon + lon_off,
                "altitude": altitude,
                "action": "waypoint"
            })
            seq += 1
            
    elif pattern.lower() == "grid":
        # Grid/Lawnmower path: 3 parallel passes
        # Pass 1: Bottom-Left to Top-Left
        # Pass 2: Top-Middle to Bottom-Middle
        # Pass 3: Bottom-Right to Top-Right
        grid_offsets = [
            (-offset, -offset),
            (offset, -offset),
            (offset, 0.0),
            (-offset, 0.0),
            (-offset, offset),
            (offset, offset)
        ]
        for lat_off, lon_off in grid_offsets:
            waypoints.append({
                "sequence_no": seq,
                "latitude": home_lat + lat_off,
                "longitude": home_lon + lon_off,
                "altitude": altitude,
                "action": "waypoint"
            })
            seq += 1
            
    elif pattern.lower() == "perimeter":
        # Bounding perimeter check (slightly larger square)
        perim_offset = offset * 1.5
        perimeter_offsets = [
            (perim_offset, perim_offset),
            (perim_offset, -perim_offset),
            (-perim_offset, -perim_offset),
            (-perim_offset, perim_offset)
        ]
        for lat_off, lon_off in perimeter_offsets:
            waypoints.append({
                "sequence_no": seq,
                "latitude": home_lat + lat_off,
                "longitude": home_lon + lon_off,
                "altitude": altitude,
                "action": "waypoint"
            })
            seq += 1
            
    else:  # "manual" or unrecognized pattern
        # Returns takeoff and RTL as placeholder, manual points can be appended dynamically in UI
        pass
        
    # 2. Add Return-to-Launch or Land point at the end
    if rtl_enabled:
        waypoints.append({
            "sequence_no": seq,
            "latitude": home_lat,
            "longitude": home_lon,
            "altitude": altitude,
            "action": "rtl"
        })
    else:
        # Land at the last waypoint position
        if len(waypoints) > 1:
            last_wp = waypoints[-1]
            waypoints.append({
                "sequence_no": seq,
                "latitude": last_wp["latitude"],
                "longitude": last_wp["longitude"],
                "altitude": 0.0,
                "action": "land"
            })
        else:
            waypoints.append({
                "sequence_no": seq,
                "latitude": home_lat,
                "longitude": home_lon,
                "altitude": 0.0,
                "action": "land"
            })
            
    return waypoints
