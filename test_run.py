# test_run.py
from agents.waypoint_planner_agent import generate_waypoints

try:
    wps = generate_waypoints(33.6425, 73.0232, 50.0, 'square')
    print(f"Success! Generated {len(wps)} waypoints for square pattern.")
    print("\nWaypoint Breakdown:")
    for wp in wps:
        print(f"  Seq {wp['sequence_no']}: ({wp['latitude']:.4f}, {wp['longitude']:.4f}) - {wp['action']} at {wp['altitude']}m")
except Exception as e:
    print(f"An error occurred: {e}")