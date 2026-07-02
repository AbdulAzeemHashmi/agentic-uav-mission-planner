import math
from typing import List, Dict, Any, Optional

# Meters per degree of latitude (constant, because latitude lines are parallel)
METERS_PER_DEG_LAT: float = 111_000.0


def generate_square_route(
    home_lat: float,
    home_lon: float,
    altitude: float,
    side_length_meters: float = 100.0
) -> List[Dict[str, Any]]:
    """
    Generates a square patrol route centered on the home (takeoff) point.
    """
    # Calculate offsets in degrees
    lat_radians = math.radians(home_lat)
    meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(lat_radians)
    
    half_side = side_length_meters / 2.0
    lat_offset = half_side / METERS_PER_DEG_LAT
    lon_offset = half_side / meters_per_deg_lon

    # Define vertices relative to the home center coordinate
    square_offsets = [
        (lat_offset, lon_offset),    # North-East
        (lat_offset, -lon_offset),   # North-West
        (-lat_offset, -lon_offset),  # South-West
        (-lat_offset, lon_offset),   # South-East
    ]
    
    waypoints = []
    # Begin loop tracking immediately after takeoff
    seq = 1
    for lat_off, lon_off in square_offsets:
        waypoints.append({
            "sequence_no": seq,
            "latitude": home_lat + lat_off,
            "longitude": home_lon + lon_off,
            "altitude": altitude,
            "action": "waypoint"
        })
        seq += 1
        
    return waypoints


def generate_waypoints(
    home_lat: float,
    home_lon: float,
    altitude: float,
    pattern: str = "square",
    rtl_enabled: bool = True
) -> List[Dict[str, Any]]:
    """
    Main orchestration function to generate structural flight tracks.
    """
    waypoints = []
    seq = 0

    # 1. Add baseline initial Takeoff position
    waypoints.append({
        "sequence_no": seq,
        "latitude": home_lat,
        "longitude": home_lon,
        "altitude": altitude,
        "action": "takeoff"
    })
    seq += 1

    pattern_lower = pattern.strip().lower()

    if pattern_lower == "square":
        wps = generate_square_route(home_lat, home_lon, altitude, side_length_meters=100.0)
        for wp in wps:
            wp["sequence_no"] = seq
            waypoints.append(wp)
            seq += 1

    elif pattern_lower == "grid":
        # Multi-leg lawnmower search scan tracks
        lat_radians = math.radians(home_lat)
        meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(lat_radians)
        grid_offset = 60.0 / METERS_PER_DEG_LAT
        lon_grid_offset = 60.0 / meters_per_deg_lon
        
        grid_offsets = [
            (grid_offset, 0.0),
            (grid_offset, lon_grid_offset),
            (-grid_offset, lon_grid_offset),
            (-grid_offset, lon_grid_offset * 2),
            (grid_offset, lon_grid_offset * 2)
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

    elif pattern_lower == "perimeter":
        # Perimeter ring boundary path tracker
        lat_radians = math.radians(home_lat)
        meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(lat_radians)
        perim_offset = 80.0 / METERS_PER_DEG_LAT
        lon_perim_offset = 80.0 / meters_per_deg_lon
        
        perimeter_offsets = [
            (perim_offset, 0.0),
            (0.0, -lon_perim_offset),
            (-perim_offset, 0.0),
            (0.0, lon_perim_offset)
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
            
    else:
        # Fallback placeholder mode
        pass
        
    # 2. Add Return-to-Launch or Land point securely at the end
    if rtl_enabled:
        waypoints.append({
            "sequence_no": seq,
            "latitude": home_lat,
            "longitude": home_lon,
            "altitude": altitude,
            "action": "rtl"
        })
    else:
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