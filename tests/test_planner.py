# tests/test_planner.py
# Unit tests for Agentic UAV Mission Planner

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.waypoint_planner_agent import generate_waypoints, generate_square_route
from agents.safety_compliance_agent import perform_safety_checks, check_geofence_violation
from utils.distance_utils import calculate_haversine_distance


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


if __name__ == "__main__":
    unittest.main()