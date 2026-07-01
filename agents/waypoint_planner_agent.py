import math
from typing import List, Dict, Any, Optional

# ---------------------------------------------------------------------------
# COORDINATE GEOMETRY PRIMER
# ---------------------------------------------------------------------------
# The Earth is approximately a sphere with a circumference of ~40,075 km.
# This means 1 degree of latitude always equals roughly 111,000 meters.
# Longitude degrees shrink toward the poles, so we scale by cos(latitude).
#
#   lat_offset  = distance_meters / 111_000
#   lon_offset  = distance_meters / (111_000 * cos(lat_radians))
#
# This is a "flat-Earth" / "small-area" approximation — accurate enough
# for areas < 50 km across (well within UAV operating range).
# ---------------------------------------------------------------------------

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

    Coordinate Geometry:
    --------------------
    We convert `side_length_meters` into degree offsets using the
    111,000 m/degree approximation:

        half  = side_length_meters / 2          (half the square side)
        d_lat = half / 111_000                  (latitude offset, degrees)
        d_lon = half / (111_000 * cos(lat))     (longitude offset, degrees)

    The four corners are placed at:
        NE  →  (+d_lat, +d_lon)
        NW  →  (+d_lat, -d_lon)
        SW  →  (-d_lat, -d_lon)
        SE  →  (-d_lat, +d_lon)

    Args:
        home_lat          : Latitude of the takeoff / home point (decimal degrees)
        home_lon          : Longitude of the takeoff / home point (decimal degrees)
        altitude          : Cruise altitude in meters (applied to every node)
        side_length_meters: Physical side length of the square in meters (default 100 m)

    Returns:
        List of waypoint dicts: [{sequence_no, latitude, longitude, altitude, action}, ...]
        Starts with Takeoff (seq 0), ends with RTL.
    """
    waypoints: List[Dict[str, Any]] = []
    seq: int = 0

    # --- Step 1: Compute degree offsets from meters ---
    half_side: float = side_length_meters / 2.0

    # Latitude offset is constant (111,000 m per degree)
    d_lat: float = half_side / METERS_PER_DEG_LAT

    # Longitude offset shrinks near the poles — we scale by cos(latitude)
    # math.radians() converts degrees to radians, which cos() requires
    lat_rad: float = math.radians(home_lat)
    d_lon: float = half_side / (METERS_PER_DEG_LAT * math.cos(lat_rad))

    # --- Step 2: Takeoff at Home Point (Sequence 0) ---
    waypoints.append({
        "sequence_no": seq,
        "latitude":    home_lat,
        "longitude":   home_lon,
        "altitude":    altitude,
        "action":      "takeoff"
    })
    seq += 1

    # --- Step 3: Four corners of the square (NE → NW → SW → SE) ---
    # This order creates a clean closed loop when connected by PolyLine.
    square_corners = [
        ( d_lat,  d_lon),   # NE corner
        ( d_lat, -d_lon),   # NW corner
        (-d_lat, -d_lon),   # SW corner
        (-d_lat,  d_lon),   # SE corner
    ]

    for lat_off, lon_off in square_corners:
        waypoints.append({
            "sequence_no": seq,
            "latitude":    home_lat + lat_off,
            "longitude":   home_lon + lon_off,
            "altitude":    altitude,
            "action":      "waypoint"
        })
        seq += 1

    # --- Step 4: Return-to-Launch back at Home (auto-appended) ---
    waypoints.append({
        "sequence_no": seq,
        "latitude":    home_lat,
        "longitude":   home_lon,
        "altitude":    altitude,
        "action":      "rtl"
    })

    return waypoints


def generate_perimeter_route(
    home_lat: float,
    home_lon: float,
    altitude: float,
    bounds: Optional[dict] = None
) -> List[Dict[str, Any]]:
    """
    Generates a boundary perimeter patrol route.

    If `bounds` is provided, the UAV flies the exact edges of that bounding box.
    If `bounds` is None, a default perimeter is auto-computed as a rectangle
    roughly 300 m × 300 m centered on the home point.

    Boundary Check Purpose:
    -----------------------
    This route is used to verify that the entire flight area is within allowed
    airspace before committing to a detailed grid or circular scan. The UAV
    traces the outer boundary first, flags any geofence violations, and then
    the Safety Compliance Agent approves or rejects the inner mission plan.

    Args:
        home_lat : Latitude of the takeoff / home point (decimal degrees)
        home_lon : Longitude of the takeoff / home point (decimal degrees)
        altitude : Cruise altitude in meters
        bounds   : Optional dict with keys {"north", "south", "east", "west"}
                   in decimal degrees. If None, a default 300 m boundary is used.

    Returns:
        List of waypoint dicts: [{sequence_no, latitude, longitude, altitude, action}, ...]
        Starts with Takeoff (seq 0), ends with RTL.
    """
    waypoints: List[Dict[str, Any]] = []
    seq: int = 0

    # --- Step 1: Compute default bounds if none provided ---
    if bounds is None:
        # Default: 300 m boundary box centered on home
        perimeter_meters: float = 150.0   # half-width = 150 m (→ 300 m total)
        d_lat: float = perimeter_meters / METERS_PER_DEG_LAT
        lat_rad: float = math.radians(home_lat)
        d_lon: float = perimeter_meters / (METERS_PER_DEG_LAT * math.cos(lat_rad))

        north: float = home_lat + d_lat
        south: float = home_lat - d_lat
        east:  float = home_lon + d_lon
        west:  float = home_lon - d_lon
    else:
        # Use caller-supplied bounding box
        north = float(bounds["north"])
        south = float(bounds["south"])
        east  = float(bounds["east"])
        west  = float(bounds["west"])

    # --- Safety guard: avoid empty/inverted bounds crashing the map ---
    if north <= south or east <= west:
        # Degenerate bounds — return minimal takeoff + RTL only
        return [
            {"sequence_no": 0, "latitude": home_lat, "longitude": home_lon,
             "altitude": altitude, "action": "takeoff"},
            {"sequence_no": 1, "latitude": home_lat, "longitude": home_lon,
             "altitude": altitude, "action": "rtl"}
        ]

    # --- Step 2: Takeoff at Home Point (Sequence 0) ---
    waypoints.append({
        "sequence_no": seq,
        "latitude":    home_lat,
        "longitude":   home_lon,
        "altitude":    altitude,
        "action":      "takeoff"
    })
    seq += 1

    # --- Step 3: Trace the four corners of the bounding box ---
    # Order: NW → NE → SE → SW (clockwise when viewed on map)
    perimeter_corners = [
        (north, west),   # NW
        (north, east),   # NE
        (south, east),   # SE
        (south, west),   # SW
    ]

    for lat, lon in perimeter_corners:
        waypoints.append({
            "sequence_no": seq,
            "latitude":    lat,
            "longitude":   lon,
            "altitude":    altitude,
            "action":      "waypoint"
        })
        seq += 1

    # --- Step 4: Return-to-Launch back at Home (auto-appended) ---
    waypoints.append({
        "sequence_no": seq,
        "latitude":    home_lat,
        "longitude":   home_lon,
        "altitude":    altitude,
        "action":      "rtl"
    })

    return waypoints


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
