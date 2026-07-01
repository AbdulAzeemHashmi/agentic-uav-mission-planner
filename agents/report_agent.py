from typing import List, Dict, Any
from utils.distance_utils import calculate_haversine_distance

def generate_mission_summary_html(
    mission: Dict[str, Any],
    waypoints: List[Dict[str, Any]],
    safety_checks: List[Dict[str, Any]]
) -> str:
    """
    Generates a beautifully structured HTML snippet summarizing the mission parameters,
    waypoint totals, flight metrics, and safety checklist.
    """
    # Calculate flight metrics
    total_waypoints = len(waypoints)
    total_distance_m = 0.0
    for i in range(total_waypoints - 1):
        total_distance_m += calculate_haversine_distance(
            waypoints[i]["latitude"], waypoints[i]["longitude"],
            waypoints[i+1]["latitude"], waypoints[i+1]["longitude"]
        )
        
    status = mission.get("status", "Needs Revision")
    status_class = "status-safe" if status == "Safe" else "status-revision"
    
    # Check if there are any failed checks
    failed_checks = [c for c in safety_checks if c["result"] != "Pass"]
    checklist_html = ""
    
    for check in safety_checks:
        icon = "✅" if check["result"] == "Pass" else "❌"
        row_class = "check-pass" if check["result"] == "Pass" else "check-fail"
        checklist_html += f"""
        <tr class="{row_class}">
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{icon}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">{check['check_name']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{check['message']}</td>
        </tr>
        """
        
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; padding: 20px; border-radius: 10px; background-color: #fcfcfc; border: 1px solid #e0e0e0; margin-top: 15px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 15px;">
            <h2 style="margin: 0; color: #333;">{mission.get('mission_name', 'UAV Mission Plan')}</h2>
            <span class="{status_class}" style="padding: 6px 12px; border-radius: 20px; font-weight: bold; text-transform: uppercase; font-size: 12px;">
                {status}
            </span>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
            <div style="flex: 1; min-width: 150px; background: #f0f4f8; padding: 12px; border-radius: 8px; border-left: 4px solid #3182ce;">
                <div style="font-size: 12px; color: #4a5568; text-transform: uppercase;">Reference Altitude</div>
                <div style="font-size: 20px; font-weight: bold; color: #2d3748;">{mission.get('altitude')} m</div>
            </div>
            <div style="flex: 1; min-width: 150px; background: #f0f4f8; padding: 12px; border-radius: 8px; border-left: 4px solid #3182ce;">
                <div style="font-size: 12px; color: #4a5568; text-transform: uppercase;">Planned Duration</div>
                <div style="font-size: 20px; font-weight: bold; color: #2d3748;">{mission.get('duration')} mins</div>
            </div>
            <div style="flex: 1; min-width: 150px; background: #f0f4f8; padding: 12px; border-radius: 8px; border-left: 4px solid #3182ce;">
                <div style="font-size: 12px; color: #4a5568; text-transform: uppercase;">Total Flight Legs</div>
                <div style="font-size: 20px; font-weight: bold; color: #2d3748;">{total_waypoints} wps</div>
            </div>
            <div style="flex: 1; min-width: 150px; background: #f0f4f8; padding: 12px; border-radius: 8px; border-left: 4px solid #3182ce;">
                <div style="font-size: 12px; color: #4a5568; text-transform: uppercase;">Flight Path Length</div>
                <div style="font-size: 20px; font-weight: bold; color: #2d3748;">{total_distance_m:.1f} m</div>
            </div>
        </div>
        
        <h3 style="margin-top: 20px; margin-bottom: 10px; color: #444; font-size: 16px;">Safety Checklist Summary</h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
            <thead>
                <tr style="background-color: #f7fafc;">
                    <th style="padding: 8px; border-bottom: 2px solid #ddd; width: 30px;"></th>
                    <th style="padding: 8px; border-bottom: 2px solid #ddd; width: 220px;">Rule Check</th>
                    <th style="padding: 8px; border-bottom: 2px solid #ddd;">Log / Details</th>
                </tr>
            </thead>
            <tbody>
                {checklist_html}
            </tbody>
        </table>
        
        {f'''<div style="margin-top: 15px; padding: 12px; background-color: #fff5f5; border: 1px solid #feb2b2; border-radius: 6px; color: #c53030; font-size: 14px;">
            <strong>Notice:</strong> This mission plan has failed safety constraints and is not approved for flight. Please review correction suggestions in the adjustments panel.
        </div>''' if failed_checks else f'''<div style="margin-top: 15px; padding: 12px; background-color: #f0fff4; border: 1px solid #9ae6b4; border-radius: 6px; color: #22543d; font-size: 14px;">
            <strong>Approved:</strong> This mission passes all rule-based checks and safety guidelines.
        </div>'''}
    </div>
    
    <style>
        .status-safe {{
            background-color: #c6f6d5;
            color: #22543d;
        }}
        .status-revision {{
            background-color: #fed7d7;
            color: #742a2a;
        }}
        .check-pass {{
            background-color: #f7fafc;
        }}
        .check-fail {{
            background-color: #fff5f5;
            color: #9b2c2c;
        }}
    </style>
    """
    return html
