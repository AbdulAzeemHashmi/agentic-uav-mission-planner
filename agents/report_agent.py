from typing import List, Dict, Any
from utils.distance_utils import calculate_haversine_distance

def generate_mission_summary_html(
    mission: Dict[str, Any],
    waypoints: List[Dict[str, Any]],
    safety_checks: List[Dict[str, Any]],
    theme: str = "Dark"
) -> str:
    """
    Generates an HTML snippet summarizing mission parameters, waypoint totals,
    flight metrics, and safety checklist, responding dynamically to Light or Dark mode.
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

    # Status badge colours
    badge_bg    = "#D1FAE5" if is_safe else "#FEE2E2"
    badge_color = "#065F46" if is_safe else "#991B1B"
    badge_text  = "SAFE" if is_safe else "NEEDS REVISION"

    # Theme dynamic styling:
    # In Dark Mode: boxes are white with black text
    # In Light Mode: boxes are black with white text
    is_dark_mode = (theme == "Dark")
    card_bg     = "#FFFFFF" if is_dark_mode else "#000000"
    card_text   = "#000000" if is_dark_mode else "#FFFFFF"
    border_col  = "#CBD5E1" if is_dark_mode else "#333333"
    th_bg       = "#F8FAFC" if is_dark_mode else "#18181B"
    row_pass_bg = "#FFFFFF" if is_dark_mode else "#050505"

    def metric_card(label: str, value: str) -> str:
        return (
            f'<div style="flex:1;min-width:110px;background:{card_bg};padding:0.75rem 0.9rem;'
            f'border-radius:10px;border:1px solid {border_col};border-left:4px solid #0072FF;box-shadow:0 2px 8px rgba(0,0,0,0.05);box-sizing:border-box">'
            f'<div style="font-size:0.7rem;color:{card_text};text-transform:uppercase;letter-spacing:0.06em;font-weight:700;margin-bottom:4px">{label}</div>'
            f'<div style="font-size:1.15rem;font-weight:800;color:{card_text}">{value}</div>'
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
            row_bg   = row_pass_bg
            name_col = card_text
            msg_col  = card_text
        else:
            icon     = "❌"
            row_bg   = "#FEF2F2" if is_dark_mode else "#311111"
            name_col = "#991B1B" if is_dark_mode else "#FCA5A5"
            msg_col  = "#7F1D1D" if is_dark_mode else "#FECACA"

        checklist_rows += (
            f'<tr style="background:{row_bg};border-bottom:1px solid {border_col}">'
            f'<td style="padding:8px 10px;text-align:center;font-size:0.95rem;width:40px;box-sizing:border-box">{icon}</td>'
            f'<td style="padding:8px 12px;font-weight:700;color:{name_col};font-size:0.85rem;word-break:break-word;box-sizing:border-box">{check["check_name"]}</td>'
            f'<td style="padding:8px 12px;color:{msg_col};font-size:0.85rem;word-break:break-word;box-sizing:border-box">{check["message"]}</td>'
            f'</tr>'
        )

    # Bottom approval notice
    if failed_checks:
        notice_bg = "#FEF2F2" if is_dark_mode else "#311111"
        notice_txt_col = "#991B1B" if is_dark_mode else "#FCA5A5"
        notice_html = (
            f'<div style="margin-top:14px;padding:12px 16px;background:{notice_bg};border:1px solid #FCA5A5;'
            f'border-radius:8px;color:{notice_txt_col};font-size:0.85rem;font-weight:500;box-sizing:border-box;width:100%">'
            f'<b>Notice:</b> Mission failed safety constraints and is not approved for flight. '
            f'Review the Suggestions page for recommended corrections.'
            f'</div>'
        )
    else:
        notice_bg = "#ECFDF5" if is_dark_mode else "#06231A"
        notice_txt_col = "#065F46" if is_dark_mode else "#6EE7B7"
        notice_html = (
            f'<div style="margin-top:14px;padding:12px 16px;background:{notice_bg};border:1px solid #A7F3D0;'
            f'border-radius:8px;color:{notice_txt_col};font-size:0.85rem;font-weight:500;box-sizing:border-box;width:100%">'
            f'<b>Approved:</b> Mission passed all safety rules and is cleared for execution.'
            f'</div>'
        )

    html = f"""<div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;padding:20px;border-radius:12px;background:{card_bg};border:1px solid {border_col};margin-top:12px;box-shadow:0 4px 16px rgba(0,0,0,0.06);box-sizing:border-box;width:100%">
    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid {border_col};padding-bottom:12px;margin-bottom:16px;box-sizing:border-box;width:100%">
        <div style="font-size:1.1rem;font-weight:700;color:{card_text};letter-spacing:-0.01em">{mission.get('mission_name', 'UAV Mission Plan')}</div>
        <span style="padding:5px 14px;border-radius:20px;font-weight:700;font-size:0.75rem;letter-spacing:0.08em;background:{badge_bg};color:{badge_color};border:1px solid {badge_color}44">{badge_text}</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:18px;width:100%;box-sizing:border-box">
        {metrics_html}
    </div>
    <div style="font-size:0.8rem;font-weight:700;color:{card_text};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px">Rule Compliance Checklist</div>
    <table style="width:100%;table-layout:fixed;border-collapse:separate;border-spacing:0;border-radius:8px;overflow:hidden;border:1px solid {border_col};box-sizing:border-box">
        <thead>
            <tr style="background:{th_bg}">
                <th style="padding:9px 10px;text-align:center;font-size:0.78rem;color:{card_text};font-weight:700;width:40px;box-sizing:border-box"></th>
                <th style="padding:9px 12px;text-align:left;font-size:0.78rem;color:{card_text};font-weight:700;width:40%;box-sizing:border-box">Rule</th>
                <th style="padding:9px 12px;text-align:left;font-size:0.78rem;color:{card_text};font-weight:700;width:calc(60% - 40px);box-sizing:border-box">Details</th>
            </tr>
        </thead>
        <tbody>
            {checklist_rows}
        </tbody>
    </table>
    {notice_html}
</div>"""

    return html
