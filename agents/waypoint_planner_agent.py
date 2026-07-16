import math
from typing import Any, Optional

# Meters per degree of latitude (constant, because latitude lines are parallel)
METERS_PER_DEG_LAT: float = 111_000.0


def generate_square_route(
    home_lat: float,
    home_lon: float,
    altitude: float,
    side_length_meters: float = 100.0
) -> list[dict[str, Any]]:
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
    square_offsets = [\
        (lat_offset, lon_offset),    # North-East
        (lat_offset, -lon_offset),   # North-West
        (-lat_offset, -lon_offset),  # South-West
        (-lat_offset, lon_offset),   # South-East
    ]
    
    waypoints = []
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
    pattern: str,
    rtl_enabled: bool = True
) -> list[dict[str, Any]]:
    """
    Main orchestration entry point to map out dynamic UAV flight routes.
    """
    waypoints = []
    
    # 1. Base mandatory structural checkpoint: Takeoff point sequence
    waypoints.append({
        "sequence_no": 0,
        "latitude": home_lat,
        "longitude": home_lon,
        "altitude": altitude,
        "action": "takeoff"
    })
    
    seq = 1
    
    # 2. Select matching geometry generation model
    if pattern == "square":
        square_wps = generate_square_route(home_lat, home_lon, altitude)
        for wp in square_wps:
            wp["sequence_no"] = seq
            waypoints.append(wp)
            seq += 1
            
    elif pattern == "grid":
        # Lawn-mower scan mapping simulation sequence matrix
        lat_radians = math.radians(home_lat)
        meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(lat_radians)
        
        step_lat = 40.0 / METERS_PER_DEG_LAT
        step_lon = 40.0 / meters_per_deg_lon
        
        grid_offsets = [\
            (0.0, 0.0),
            (step_lat * 2, 0.0),
            (step_lat * 2, step_lon * 2),
            (0.0, step_lon * 2),
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
            
    elif pattern == "perimeter":
        lat_radians = math.radians(home_lat)
        meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(lat_radians)
        
        perim_offset = 60.0 / METERS_PER_DEG_LAT
        lon_perim_offset = 60.0 / meters_per_deg_lon
        
        perimeter_offsets = [\
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
            
    elif pattern == "circle":
        # Radial orbit calculation trajectory model (8 coordinates, 45-degree steps)
        radius_meters = 50.0  
        lat_radians = math.radians(home_lat)
        meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(lat_radians)
        
        for i in range(8):
            angle_rad = math.radians(i * 45.0)
            lat_offset = (radius_meters * math.cos(angle_rad)) / METERS_PER_DEG_LAT
            lon_offset = (radius_meters * math.sin(angle_rad)) / meters_per_deg_lon
            
            waypoints.append({
                "sequence_no": seq,
                "latitude": home_lat + lat_offset,
                "longitude": home_lon + lon_offset,
                "altitude": altitude,
                "action": "waypoint"
            })
            seq += 1
            
    else:
        # Fallback placeholder mode
        pass
        
    # 3. Add Return-to-Launch or Land point securely at the end
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