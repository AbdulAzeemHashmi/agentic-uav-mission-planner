from typing import List, Dict, Any
from utils.distance_utils import calculate_haversine_distance

def generate_mission_summary_html(
    mission: Dict[str, Any],
    waypoints: List[Dict[str, Any]],
    safety_checks: List[Dict[str, Any]]
) -> str:
    """
    Generates a dark-themed HTML snippet summarizing mission parameters,
    waypoint totals, flight metrics, and safety checklist.
    All styles are fully inlined so Streamlit renders the HTML correctly
    without a separate <style> block breaking the markdown parser.
    """
    # Flight metrics
    total_waypoints = len(waypoints)
    total_distance_m = 0.0
    for i in range(total_waypoints - 1):
        total_distance_m += calculate_haversine_distance(
            waypoints[i]["latitude"], waypoints[i]["longitude"],
            waypoints[i + 1]["latitude"], waypoints[i + 1]["longitude"]
        )

    status = mission.get("status", "Needs Revision")
    is_safe = (status == "Safe")
    failed_checks = [c for c in safety_checks if c["result"] != "Pass"]

    # Status badge colours (inlined)
    badge_bg    = "#1a4731" if is_safe else "#4a1919"
    badge_color = "#4ade80" if is_safe else "#f87171"
    badge_text  = "SAFE" if is_safe else "NEEDS REVISION"

    # Metric card template (dark theme, no external class)
    def metric_card(label: str, value: str) -> str:
        return (
            f'<div style="flex:1;min-width:120px;background:#1E1E1E;padding:0.8rem 1rem;'
            f'border-radius:8px;border:1px solid #2a2a2a;border-left:4px solid #1E90FF">'
            f'<div style="font-size:0.7rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">{label}</div>'
            f'<div style="font-size:1.2rem;font-weight:700;color:#FAFAFA">{value}</div>'
            f'</div>'
        )

    metrics_html = (
        metric_card("Altitude", f"{mission.get('altitude')} m") +
        metric_card("Duration", f"{mission.get('duration')} min") +
        metric_card("Waypoints", str(total_waypoints)) +
        metric_card("Path Length", f"{total_distance_m:.0f} m")
    )

    # Safety checklist rows
    checklist_rows = ""
    for check in safety_checks:
        if check["result"] == "Pass":
            icon     = "✅"
            row_bg   = "#1a2a1a"
            name_col = "#FAFAFA"
            msg_col  = "#aaaaaa"
        else:
            icon     = "❌"
            row_bg   = "#2a1a1a"
            name_col = "#f87171"
            msg_col  = "#cc8888"

        checklist_rows += (
            f'<tr style="background:{row_bg}">'
            f'<td style="padding:7px 10px;font-size:0.9rem;width:28px">{icon}</td>'
            f'<td style="padding:7px 10px;font-weight:600;color:{name_col};font-size:0.82rem;white-space:nowrap">'
            f'{check["check_name"]}</td>'
            f'<td style="padding:7px 10px;color:{msg_col};font-size:0.82rem">{check["message"]}</td>'
            f'</tr>'
        )

    # Bottom approval notice
    if failed_checks:
        notice_html = (
            '<div style="margin-top:12px;padding:10px 14px;background:#2a1a1a;border:1px solid #7f1d1d;'
            'border-radius:6px;color:#f87171;font-size:0.82rem">'
            '<b>Notice:</b> This mission has failed safety constraints and is not approved for flight. '
            'Review the Suggestions page for corrections.'
            '</div>'
        )
    else:
        notice_html = (
            '<div style="margin-top:12px;padding:10px 14px;background:#1a2a1a;border:1px solid #14532d;'
            'border-radius:6px;color:#4ade80;font-size:0.82rem">'
            '<b>Approved:</b> This mission passes all rule-based safety checks and is cleared for planning.'
            '</div>'
        )

    html = f"""<div style="font-family:'Segoe UI',Arial,sans-serif;padding:16px;border-radius:10px;background:#141414;border:1px solid #2a2a2a;margin-top:10px">
    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2a2a2a;padding-bottom:10px;margin-bottom:14px">
        <div style="font-size:1rem;font-weight:700;color:#FAFAFA">{mission.get('mission_name', 'UAV Mission Plan')}</div>
        <span style="padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.72rem;letter-spacing:0.06em;background:{badge_bg};color:{badge_color}">{badge_text}</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px">
        {metrics_html}
    </div>
    <div style="font-size:0.78rem;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">Safety Checklist</div>
    <table style="width:100%;border-collapse:collapse;border-radius:8px;overflow:hidden">
        <thead>
            <tr style="background:#1E1E1E">
                <th style="padding:7px 10px;text-align:left;font-size:0.75rem;color:#555;font-weight:600;width:28px"></th>
                <th style="padding:7px 10px;text-align:left;font-size:0.75rem;color:#555;font-weight:600">Rule</th>
                <th style="padding:7px 10px;text-align:left;font-size:0.75rem;color:#555;font-weight:600">Details</th>
            </tr>
        </thead>
        <tbody>
            {checklist_rows}
        </tbody>
    </table>
    {notice_html}
</div>"""

    return html
