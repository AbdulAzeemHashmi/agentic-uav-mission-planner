# tests/test_planner.py
# Unit tests for Agentic UAV Mission Planner

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.waypoint_planner_agent import generate_waypoints, generate_square_route
from agents.safety_compliance_agent import perform_safety_checks, check_geofence_violation, add_custom_no_fly_zone
from utils.distance_utils import calculate_haversine_distance
from utils.export_utils import export_qgroundcontrol_plan, export_ardupilot_waypoints, export_kml_format
from config.settings import DRONE_PROFILES


class TestUAVPlanner(unittest.TestCase):

    def test_haversine_distance(self):
        """Test Haversine distance calculation"""
        dist = calculate_haversine_distance(0, 0, 1, 1)
        self.assertAlmostEqual(dist, 157249.38, places=2)

    def test_square_route_generation(self):
        """Test square route generation"""
        wps = generate_square_route(33.6425, 73.0232, 50.0)
        self.assertEqual(len(wps), 4)
        self.assertEqual(wps[0]["altitude"], 50.0)

    def test_geofence_check(self):
        """Test geofence violation detection"""
        # Point inside zone
        violated, name = check_geofence_violation(33.6438, 73.0210)
        self.assertTrue(violated)
        # Point outside zone
        violated, name = check_geofence_violation(33.6500, 73.0300)
        self.assertFalse(violated)

    def test_battery_model(self):
        """Test battery estimation"""
        wps = generate_waypoints(33.6425, 73.0232, 50.0, "square")
        meta = {"altitude": 50.0, "duration": 15.0}
        checks = perform_safety_checks(meta, wps)
        # Find R7 check
        r7 = next((c for c in checks if "R7" in c["check_name"]), None)
        self.assertIsNotNone(r7)
        self.assertEqual(r7["result"], "Pass")

    def test_waypoint_generation_all_patterns(self):
        """Test all waypoint patterns"""
        patterns = ["square", "grid", "circle", "perimeter"]
        for pattern in patterns:
            wps = generate_waypoints(33.6425, 73.0232, 50.0, pattern)
            self.assertGreater(len(wps), 2)
            self.assertEqual(wps[0]["action"], "takeoff")
            self.assertEqual(wps[-1]["action"], "rtl")

    def test_gcs_exports(self):
        """Test QGroundControl, ArduPilot, and KML export format generators"""
        wps = generate_waypoints(33.6425, 73.0232, 50.0, "square")
        meta = {"mission_name": "Test Mission", "altitude": 50.0, "duration": 15.0}
        
        qgc_json = export_qgroundcontrol_plan(meta, wps)
        self.assertIn('"fileType": "Plan"', qgc_json)
        self.assertIn('"command": 22', qgc_json)

        ardupilot_txt = export_ardupilot_waypoints(wps)
        self.assertTrue(ardupilot_txt.startswith("QGC WPL 110"))

        kml_xml = export_kml_format(meta, wps)
        self.assertIn('<kml xmlns="http://www.opengis.net/kml/2.2">', kml_xml)
        self.assertIn('<coordinates>', kml_xml)

    def test_raster_grid_waypoints(self):
        """Test serpentine raster grid waypoint pattern generation"""
        wps = generate_waypoints(33.6425, 73.0232, 50.0, "grid")
        # Takeoff + 8 scan points (4 passes * 2 endpoints) + RTL = 10 total waypoints
        self.assertEqual(len(wps), 10)

    def test_custom_geofence_registration(self):
        """Test dynamic registration of custom no-fly zones"""
        custom_zone = {
            "name": "Test Custom Reserved Zone",
            "type": "circle",
            "center": (33.7000, 73.1000),
            "radius_m": 50.0
        }
        add_custom_no_fly_zone(custom_zone)
        violated, name = check_geofence_violation(33.7000, 73.1000)
        self.assertTrue(violated)
        self.assertEqual(name, "Test Custom Reserved Zone")


if __name__ == "__main__":
    unittest.main()