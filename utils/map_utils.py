"""
utils/map_utils.py
==================
Folium map builder utilities for the Agentic UAV Mission Planner.

Public API
----------
  initialize_mission_map(home_lat, home_lon)          -> folium.Map
      Creates a blank base map centered on the home point.

  draw_flight_path(folium_map, waypoint_list)         -> folium.Map
      Layers color-coded waypoint markers and a PolyLine path onto an
      existing map object. Returns the same map (mutated in-place).

  draw_no_fly_zones(folium_map, nfz_list)             -> folium.Map
      Renders all no-fly zone polygons/circles in red on the map.

  create_mission_map(waypoints, home_coords)          -> folium.Map
      Convenience wrapper: calls all three helpers above in sequence.
      Kept for backward compatibility with existing app.py calls.
"""

import folium
from typing import List, Dict, Any, Tuple

# Import the no-fly zone definitions from the safety agent
from agents.safety_compliance_agent import NO_FLY_ZONES


# ---------------------------------------------------------------------------
# FUNCTION 1: initialize_mission_map
# ---------------------------------------------------------------------------

def initialize_mission_map(
    home_lat: float,
    home_lon: float,
    zoom_start: int = 16
) -> folium.Map:
    """
    Creates and returns a blank base Folium map centered on the home point.

    This is the foundation layer - think of it like a blank canvas before
    drawing. All other draw_*() functions accept this map and paint onto it.

    Tile Layer:
    -----------
    We use OpenStreetMap (the Folium default). It shows roads, buildings,
    and landmarks that help a UAV operator orient the flight area visually.

    Args:
        home_lat   : Latitude of the home / takeoff point (decimal degrees)
        home_lon   : Longitude of the home / takeoff point (decimal degrees)
        zoom_start : Initial map zoom level (16 = neighbourhood level, good for UAVs)

    Returns:
        A folium.Map object centered on (home_lat, home_lon).
    """
    # folium.Map(location=[lat, lon]) centers the map viewport on that coordinate.
    # control_scale=True adds a distance scale bar to the bottom-left corner.
    mission_map = folium.Map(
        location=[home_lat, home_lon],
        zoom_start=zoom_start,
        control_scale=True
    )

    # Place a blue "home" marker at the takeoff point so the operator always
    # knows where ground zero is, even before any waypoints are drawn.
    folium.Marker(
        location=[home_lat, home_lon],
        popup=f"🏠 Home Point<br>Lat: {home_lat:.6f}<br>Lon: {home_lon:.6f}",
        tooltip="Home / Takeoff Origin",
        icon=folium.Icon(color="blue", icon="home", prefix="glyphicon")
    ).add_to(mission_map)

    return mission_map


# ---------------------------------------------------------------------------
# FUNCTION 2: draw_flight_path
# ---------------------------------------------------------------------------

def draw_flight_path(
    folium_map: folium.Map,
    waypoint_list: List[Dict[str, Any]]
) -> folium.Map:
    """
    Draws colored waypoint markers and a connecting flight path line on the map.

    Marker Color Coding:
    --------------------
      Green   → Takeoff point  (where the UAV lifts off)
      Blue    → Waypoints      (scanning / patrol positions)
      Orange  → RTL            (Return-to-Launch point)
      Red     → Land           (alternate landing point)

    Flight Path Line:
    -----------------
    A dashed `folium.PolyLine` is drawn connecting all waypoints in sequence
    order. The dashed style visually conveys "planned path, not yet flown"
    which is standard in UAV ground control software UIs.

    Args:
        folium_map    : An existing folium.Map object (from initialize_mission_map)
        waypoint_list : List of waypoint dicts with keys:
                        {sequence_no, latitude, longitude, altitude, action}

    Returns:
        The same folium.Map with all markers and PolyLine added (mutated in-place).
    """
    # Guard: nothing to draw if the list is empty or None
    if not waypoint_list:
        return folium_map

    # Collect (lat, lon) tuples to build the PolyLine after all markers
    path_coords: List[Tuple[float, float]] = []

    for wp in waypoint_list:
        lat    = wp["latitude"]
        lon    = wp["longitude"]
        alt    = wp["altitude"]
        action = wp["action"].lower()
        seq    = wp["sequence_no"]

        # Record this coordinate for the path line
        path_coords.append((lat, lon))

        # --- Choose marker style based on the waypoint action type ---
        if action == "takeoff":
            color        = "green"
            icon_name    = "cloud-upload"
            popup_text   = (
                f"<b>🚀 Takeoff</b><br>"
                f"Sequence: {seq}<br>"
                f"Lat: {lat:.6f}<br>"
                f"Lon: {lon:.6f}<br>"
                f"Alt: {alt} m"
            )
        elif action == "rtl":
            color        = "orange"
            icon_name    = "repeat"
            popup_text   = (
                f"<b>🔄 Return-to-Launch</b><br>"
                f"Sequence: {seq}<br>"
                f"Lat: {lat:.6f}<br>"
                f"Lon: {lon:.6f}<br>"
                f"Alt: {alt} m"
            )
        elif action == "land":
            color        = "red"
            icon_name    = "cloud-download"
            popup_text   = (
                f"<b>🛬 Landing</b><br>"
                f"Sequence: {seq}<br>"
                f"Lat: {lat:.6f}<br>"
                f"Lon: {lon:.6f}<br>"
                f"Alt: {alt} m"
            )
        else:
            # Generic scanning / patrol waypoint
            color        = "blue"
            icon_name    = "info-sign"
            popup_text   = (
                f"<b>📍 Waypoint {seq}</b><br>"
                f"Action: {action.upper()}<br>"
                f"Lat: {lat:.6f}<br>"
                f"Lon: {lon:.6f}<br>"
                f"Alt: {alt} m"
            )

        # Add the marker to the map
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=220),
            tooltip=f"{action.upper()} (Seq {seq})",
            icon=folium.Icon(color=color, icon=icon_name, prefix="glyphicon")
        ).add_to(folium_map)

    # --- Draw the flight path PolyLine connecting all waypoints ---
    # Only draw if we have at least 2 points (a line needs two endpoints)
    if len(path_coords) > 1:
        folium.PolyLine(
            locations=path_coords,
            color="#1E90FF",        # Dodger Blue - clear but not aggressive
            weight=4,               # Line thickness in pixels
            opacity=0.85,
            dash_array="8, 6",      # Dashed pattern: 8px dash, 6px gap
            tooltip="UAV Flight Path"
        ).add_to(folium_map)

    return folium_map


# ---------------------------------------------------------------------------
# FUNCTION 3: draw_no_fly_zones  (helper, keeps create_mission_map clean)
# ---------------------------------------------------------------------------

def draw_no_fly_zones(
    folium_map: folium.Map,
    nfz_list: list
) -> folium.Map:
    """
    Renders no-fly zone overlays (circles and polygons) in red on the map.

    Each zone is styled with:
      - A red border (weight=2)
      - A semi-transparent red fill (fill_opacity=0.30)
      - A tooltip with the zone name

    Args:
        folium_map : An existing folium.Map object
        nfz_list   : List of NFZ dicts from safety_compliance_agent.NO_FLY_ZONES

    Returns:
        The same folium.Map with NFZ overlays added.
    """
    for nfz in nfz_list:
        if nfz["type"] == "circle":
            c_lat, c_lon = nfz["center"]
            folium.Circle(
                location=[c_lat, c_lon],
                radius=nfz["radius_m"],
                color="red",
                weight=2,
                fill=True,
                fill_color="red",
                fill_opacity=0.30,
                tooltip=f"🚫 {nfz['name']}"
            ).add_to(folium_map)

        elif nfz["type"] == "polygon":
            folium.Polygon(
                locations=nfz["coords"],
                color="red",
                weight=2,
                fill=True,
                fill_color="red",
                fill_opacity=0.30,
                tooltip=f"🚫 {nfz['name']}"
            ).add_to(folium_map)

    return folium_map


# ---------------------------------------------------------------------------
# FUNCTION 4: create_mission_map  (backward-compatible convenience wrapper)
# ---------------------------------------------------------------------------

def create_mission_map(
    waypoints: List[Dict[str, Any]],
    home_coords: Tuple[float, float] = (33.6425, 73.0232)
) -> folium.Map:
    """
    Convenience wrapper that composes all three helper functions into one call.

    Build order:
      1. initialize_mission_map()  → blank base map at home point
      2. draw_no_fly_zones()       → red restricted area overlays
      3. draw_flight_path()        → waypoint markers + PolyLine

    This function signature is unchanged from the original, so all existing
    app.py calls (create_mission_map(waypoints, (lat, lon))) work without
    any modification.

    Args:
        waypoints    : List of waypoint dicts (may be empty list [])
        home_coords  : (lat, lon) tuple for the home point

    Returns:
        A fully decorated folium.Map ready for st_folium() rendering.
    """
    home_lat, home_lon = home_coords

    # Step 1: Blank canvas map centered on home
    mission_map = initialize_mission_map(home_lat, home_lon)

    # Step 2: Paint no-fly zones in red so they are always visible
    draw_no_fly_zones(mission_map, NO_FLY_ZONES)

    # Step 3: Draw the flight path (markers + PolyLine) on top
    draw_flight_path(mission_map, waypoints)

    return mission_map
