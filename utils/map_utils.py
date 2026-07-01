import folium
from typing import List, Dict, Any, Tuple
from agents.safety_compliance_agent import NO_FLY_ZONES

def create_mission_map(
    waypoints: List[Dict[str, Any]],
    home_coords: Tuple[float, float] = (33.6425, 73.0232)
) -> folium.Map:
    """
    Creates an interactive Folium Map showing the home point, UAV waypoints,
    flight path polyline, and restricted geofence zones.
    """
    # 1. Initialize map centered around home point
    m = folium.Map(location=home_coords, zoom_start=16, control_scale=True)
    
    # 2. Draw Geofences (No-Fly Zones) in Red / Semi-transparent
    for nfz in NO_FLY_ZONES:
        if nfz["type"] == "circle":
            c_lat, c_lon = nfz["center"]
            folium.Circle(
                location=[c_lat, c_lon],
                radius=nfz["radius_m"],
                color="red",
                weight=2,
                fill=True,
                fill_color="red",
                fill_opacity=0.3,
                tooltip=nfz["name"]
            ).add_to(m)
        elif nfz["type"] == "polygon":
            folium.Polygon(
                locations=nfz["coords"],
                color="red",
                weight=2,
                fill=True,
                fill_color="red",
                fill_opacity=0.3,
                tooltip=nfz["name"]
            ).add_to(m)
            
    # If no waypoints are defined, just add a marker for Home and return
    if not waypoints:
        folium.Marker(
            location=home_coords,
            popup="Home Point (FAST Campus)",
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(m)
        return m
        
    # 3. Draw Waypoint Markers
    wp_coords = []
    for idx, wp in enumerate(waypoints):
        lat = wp["latitude"]
        lon = wp["longitude"]
        alt = wp["altitude"]
        action = wp["action"]
        seq = wp["sequence_no"]
        
        wp_coords.append((lat, lon))
        
        # Color-coded icons based on action
        if action == "takeoff":
            color = "green"
            icon = "cloud-upload"
            popup_text = f"Takeoff Point<br>Alt: {alt}m"
        elif action == "rtl":
            color = "orange"
            icon = "repeat"
            popup_text = f"Return-to-Launch<br>Alt: {alt}m"
        elif action == "land":
            color = "red"
            icon = "cloud-download"
            popup_text = f"Landing Point<br>Alt: {alt}m"
        else:
            color = "blue"
            icon = "info-sign"
            popup_text = f"Waypoint {seq}<br>Alt: {alt}m"
            
        folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            tooltip=f"{action.upper()} ({seq})",
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
        
    # 4. Draw flight path line connecting waypoints
    if len(wp_coords) > 1:
        folium.PolyLine(
            locations=wp_coords,
            color="darkblue",
            weight=4,
            opacity=0.8,
            dash_array="5, 10"  # Dashed line looks very premium
        ).add_to(m)
        
    return m
