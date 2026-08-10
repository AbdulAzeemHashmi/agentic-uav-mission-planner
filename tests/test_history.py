# tests/test_history.py
# Unit tests for Mission History database operations, import/export, and search filters

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_utils import (
    init_db, save_mission, search_missions, get_mission_by_id,
    delete_mission, clone_mission, export_filtered_missions_batch_json,
    import_mission_from_json
)

class TestMissionHistory(unittest.TestCase):

    def setUp(self):
        """Initialize database before each test."""
        init_db()

    def test_save_and_retrieve_mission(self):
        """Test saving a complete mission and retrieving metadata, waypoints, and safety checks."""
        meta = {
            "mission_name": "Test History Mission Alpha",
            "mission_type": "mapping",
            "altitude": 60.0,
            "duration": 20.0,
            "status": "Safe"
        }
        wps = [
            {"sequence_no": 0, "latitude": 33.6425, "longitude": 73.0232, "altitude": 0.0, "action": "takeoff"},
            {"sequence_no": 1, "latitude": 33.6435, "longitude": 73.0242, "altitude": 60.0, "action": "waypoint"},
            {"sequence_no": 2, "latitude": 33.6425, "longitude": 73.0232, "altitude": 0.0, "action": "rtl"}
        ]
        checks = [
            {"check_name": "R1: Max Altitude", "result": "Pass", "message": "60.0m <= 80.0m limit"}
        ]

        mid = save_mission(meta, wps, checks)
        self.assertGreater(mid, 0)

        ret_meta, ret_wps, ret_checks = get_mission_by_id(mid)
        self.assertEqual(ret_meta["mission_name"], "Test History Mission Alpha")
        self.assertEqual(len(ret_wps), 3)
        self.assertEqual(len(ret_checks), 1)

        # Clean up
        delete_mission(mid)

    def test_search_and_filter_missions(self):
        """Test searching missions by name and status filter."""
        mid = save_mission(
            {"mission_name": "Filter Target Mission", "mission_type": "inspection", "altitude": 40.0, "duration": 10.0, "status": "Safe"},
            [], []
        )

        results = search_missions(name_filter="Filter Target", status_filter="Safe")
        self.assertTrue(any(m["mission_id"] == mid for m in results))

        no_results = search_missions(name_filter="NonExistentMission12345")
        self.assertEqual(len(no_results), 0)

        delete_mission(mid)

    def test_batch_export_and_import(self):
        """Test batch JSON export generation and re-importing mission data."""
        mid1 = save_mission(
            {"mission_name": "Batch Mission 1", "mission_type": "surveillance", "altitude": 50.0, "duration": 15.0, "status": "Safe"},
            [{"sequence_no": 0, "latitude": 33.64, "longitude": 73.02, "altitude": 50.0, "action": "waypoint"}],
            [{"check_name": "R1", "result": "Pass", "message": "OK"}]
        )
        mid2 = save_mission(
            {"mission_name": "Batch Mission 2", "mission_type": "mapping", "altitude": 70.0, "duration": 25.0, "status": "Unsafe"},
            [{"sequence_no": 0, "latitude": 33.65, "longitude": 73.03, "altitude": 70.0, "action": "waypoint"}],
            [{"check_name": "R1", "result": "Fail", "message": "High altitude"}]
        )

        missions = search_missions(name_filter="Batch Mission")
        self.assertGreaterEqual(len(missions), 2)

        json_export_str = export_filtered_missions_batch_json(missions)
        self.assertIn("Batch Mission 1", json_export_str)
        self.assertIn("Batch Mission 2", json_export_str)

        # Import JSON string
        new_ids = import_mission_from_json(json_export_str)
        self.assertEqual(len(new_ids), len(missions))

        # Cleanup
        delete_mission(mid1)
        delete_mission(mid2)
        for nid in new_ids:
            delete_mission(nid)

    def test_clone_mission(self):
        """Test cloning a mission."""
        orig_id = save_mission(
            {"mission_name": "Original Mission", "mission_type": "surveillance", "altitude": 45.0, "duration": 12.0, "status": "Safe"},
            [{"sequence_no": 0, "latitude": 33.64, "longitude": 73.02, "altitude": 45.0, "action": "waypoint"}],
            []
        )
        cloned_id = clone_mission(orig_id, "Cloned Mission Copy")
        self.assertNotEqual(orig_id, cloned_id)

        cloned_meta, cloned_wps, _ = get_mission_by_id(cloned_id)
        self.assertEqual(cloned_meta["mission_name"], "Cloned Mission Copy")
        self.assertEqual(len(cloned_wps), 1)

        delete_mission(orig_id)
        delete_mission(cloned_id)

if __name__ == "__main__":
    unittest.main()
