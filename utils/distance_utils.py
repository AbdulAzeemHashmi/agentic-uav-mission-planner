import math
from typing import Tuple

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    specified in decimal degrees of latitude and longitude.
    Returns distance in meters.
    """
    # Radius of the Earth in meters
    R = 6371000.0
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
         
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    distance = R * c
    return distance

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the bearing (direction) from point 1 to point 2.
    Returns bearing in degrees (0-360, where 0 is North).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    
    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))
         
    bearing = math.atan2(y, x)
    bearing_degrees = math.degrees(bearing)
    return (bearing_degrees + 360.0) % 360.0


def latlon_to_meters(lat: float, lon: float, ref_lat: float, ref_lon: float) -> Tuple[float, float]:
    """
    Converts decimal lat/lon coordinates into local Cartesian coordinates (x_meters, y_meters)
    relative to a reference coordinate point, using a local equirectangular flat-grid projection.
    This resolves the degree-to-meter aspect-ratio stretching at different latitudes.
    """
    METERS_PER_DEG_LAT = 111132.95
    dy = lat - ref_lat
    dx = lon - ref_lon
    y_meters = dy * METERS_PER_DEG_LAT
    ref_lat_rad = math.radians(ref_lat)
    x_meters = dx * METERS_PER_DEG_LAT * math.cos(ref_lat_rad)
    return x_meters, y_meters
