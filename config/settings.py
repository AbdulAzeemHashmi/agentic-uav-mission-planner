# config/settings.py
# Centralized configuration file for the Agentic UAV Mission Planner

from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent

# Theme defaults
THEME_DEFAULT = "Dark"

# Mission defaults
MISSION_DEFAULTS = {
    "name": "FAST Surveillance",
    "type": "surveillance",
    "altitude": 50.0,
    "duration": 15.0,
    "pattern": "square",
    "home_lat": 33.6425,
    "home_lon": 73.0232
}

# Battery model defaults
BATTERY_CONFIG = {
    "capacity_wh": 90.0,
    "v_cruise": 10.0,
    "v_climb": 4.0,
    "v_descend": 2.0,
    "p_climb": 215.0,
    "p_cruise": 120.0,
    "p_hover": 130.0,
    "p_descend": 115.0
}

# Route defaults
ROUTE_CONFIG = {
    "square_side_m": 100.0,
    "grid_step_m": 40.0,
    "perimeter_offset_m": 60.0,
    "circle_radius_m": 50.0
}

# Safety rules
SAFETY_CONFIG = {
    "max_altitude_m": 80.0,
    "max_duration_min": 30.0,
    "max_leg_distance_m": 500.0,
    "max_battery_pct": 80.0
}

# Aircraft Safety Profiles for dynamic rule configuration
DRONE_PROFILES = {
    "quadcopter_inspection": {
        "name": "Standard Inspection Quadcopter",
        "max_altitude_m": 80.0,
        "max_duration_min": 30.0,
        "max_leg_distance_m": 500.0,
        "max_battery_pct": 80.0,
        "battery_wh": 90.0,
        "cruise_speed_ms": 10.0
    },
    "fixed_wing_patrol": {
        "name": "Long-Range Fixed Wing Patrol",
        "max_altitude_m": 120.0,
        "max_duration_min": 60.0,
        "max_leg_distance_m": 1500.0,
        "max_battery_pct": 85.0,
        "battery_wh": 250.0,
        "cruise_speed_ms": 18.0
    },
    "heavy_delivery": {
        "name": "Heavy Payload Delivery UAV",
        "max_altitude_m": 60.0,
        "max_duration_min": 25.0,
        "max_leg_distance_m": 400.0,
        "max_battery_pct": 75.0,
        "battery_wh": 180.0,
        "cruise_speed_ms": 12.0
    }
}

# GCS Export Specs
GCS_CONFIG = {
    "qgroundcontrol_version": 1,
    "mavlink_system_id": 1,
    "mavlink_component_id": 1,
    "frame": 3  # MAV_FRAME_GLOBAL_RELATIVE_ALT
}