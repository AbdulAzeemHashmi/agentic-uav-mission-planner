import unittest
import sys
import os

# Include project paths for import compatibility
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.distance_utils import calculate_haversine_distance
from agents.waypoint_planner_agent import generate_waypoints
from agents.safety_compliance_agent import perform_safety_checks, check_geofence_violation
from agents.correction_agent import generate_corrections

class TestUAVPlanner(unittest.TestCase):
    
    def test_haversine_distance(self):
        # Coordinates of FAST-NUCES Islamabad (approx) and a nearby point
        lat1, lon1 = 33.6425, 73.0232
        lat2, lon2 = 33.6425, 73.0242 # approx 92.8 meters east
        dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
        self.assertTrue(90.0 < dist < 96.0)

    def test_waypoint_planner_square(self):
        home_lat, home_lon = 33.6425, 73.0232
        altitude = 50.0
        wps = generate_waypoints(home_lat, home_lon, altitude, "square", rtl_enabled=True)
        
        # Takeoff + 4 square corners + RTL = 6 waypoints
        self.assertEqual(len(wps), 6)
        self.assertEqual(wps[0]["action"], "takeoff")
        self.assertEqual(wps[-1]["action"], "rtl")
        for wp in wps:
            self.assertEqual(wp["altitude"], altitude)

    def test_waypoint_planner_circle(self):
        home_lat, home_lon = 33.6425, 73.0232
        altitude = 60.0
        wps = generate_waypoints(home_lat, home_lon, altitude, "circle", rtl_enabled=True)
        
        # Takeoff + 8 circular points + RTL = 10 waypoints
        self.assertEqual(len(wps), 10)
        self.assertEqual(wps[0]["action"], "takeoff")
        self.assertEqual(wps[-1]["action"], "rtl")

    def test_safety_compliance_safe_mission(self):
        mission_meta = {"altitude": 60.0, "duration": 15.0}
        # Use coordinates away from mock geofences (e.g. 73.0350 lon)
        wps = generate_waypoints(33.6425, 73.0350, 60.0, "square", rtl_enabled=True)
        
        checks = perform_safety_checks(mission_meta, wps)
        all_passed = all(c["result"] == "Pass" for c in checks)
        self.assertTrue(all_passed)

    def test_safety_compliance_unsafe_altitude(self):
        mission_meta = {"altitude": 100.0, "duration": 15.0}
        wps = generate_waypoints(33.6425, 73.0350, 100.0, "square", rtl_enabled=True)
        
        checks = perform_safety_checks(mission_meta, wps)
        r1_check = [c for c in checks if "R1" in c["check_name"]][0]
        self.assertEqual(r1_check["result"], "Fail")

    def test_safety_compliance_unsafe_duration(self):
        mission_meta = {"altitude": 50.0, "duration": 45.0}
        wps = generate_waypoints(33.6425, 73.0350, 50.0, "square", rtl_enabled=True)
        
        checks = perform_safety_checks(mission_meta, wps)
        r6_check = [c for c in checks if "R6" in c["check_name"]][0]
        self.assertEqual(r6_check["result"], "Fail")

    def test_geofence_violation(self):
        # Restricted Military Airspace center is at (33.6438, 73.0210)
        violated, zone = check_geofence_violation(33.6438, 73.0210)
        self.assertTrue(violated)
        self.assertIn("Zone A", zone)

    def test_correction_agent(self):
        mission_meta = {"mission_name": "Test", "altitude": 100.0, "duration": 40.0}
        wps = generate_waypoints(33.6425, 73.0350, 100.0, "square", rtl_enabled=True)
        
        checks = perform_safety_checks(mission_meta, wps)
        suggestions, corr_meta, corr_wps = generate_corrections(mission_meta, wps, checks)
        
        # Verify corrections applied
        self.assertEqual(corr_meta["altitude"], 80.0)
        self.assertTrue(corr_meta["duration"] <= 30.0)
        self.assertTrue(len(suggestions) >= 2)

if __name__ == '__main__':
    unittest.main()
