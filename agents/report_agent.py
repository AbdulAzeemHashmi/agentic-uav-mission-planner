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

    is_dark_mode = (theme == "Dark")

    if is_dark_mode:
        # Dark mode color tokens: stark visual contrast between dark outer card and bright elevated metric boxes
        outer_bg       = "linear-gradient(135deg, #0F122B 0%, #0A0D22 100%)"
        outer_border   = "1px solid rgba(0, 114, 255, 0.32)"
        outer_shadow   = "0 12px 40px rgba(0, 0, 0, 0.55)"
        title_text     = "#F8FAFC"

        # Vibrant elevated medium slate-blue metric cards (#262E67 -> #1D2352)
        metric_bg      = "linear-gradient(135deg, #262E67 0%, #1D2352 100%)"
        metric_border  = "1px solid rgba(0, 198, 255, 0.35)"
        metric_accent  = "#00C6FF"
        metric_label   = "#C7D2FE"
        metric_val     = "#FFFFFF"
        metric_shadow  = "0 4px 18px rgba(0, 0, 0, 0.40)"

        th_bg          = "#1E2556"
        th_text        = "#A5B4FC"
        table_border   = "1px solid rgba(255, 255, 255, 0.12)"
        row_pass_bg    = "#0F122B"
        row_pass_text  = "#E2E8F0"
        row_fail_bg    = "#3A1620"
        row_fail_text  = "#FCA5A5"

        badge_bg       = "rgba(16, 185, 129, 0.22)" if is_safe else "rgba(239, 68, 68, 0.22)"
        badge_fg       = "#34D399" if is_safe else "#FCA5A5"
        badge_br       = "#10B981" if is_safe else "#EF4444"

        notice_bg      = "rgba(16, 185, 129, 0.14)" if is_safe else "rgba(239, 68, 68, 0.14)"
        notice_fg      = "#34D399" if is_safe else "#FCA5A5"
        notice_br      = "rgba(16, 185, 129, 0.40)" if is_safe else "rgba(239, 68, 68, 0.40)"
    else:
        # Light mode color tokens: soft indigo-slate metric cards contrasting against pure white outer card
        outer_bg       = "#FFFFFF"
        outer_border   = "1px solid #CBD5E1"
        outer_shadow   = "0 8px 24px rgba(0, 0, 0, 0.08)"
        title_text     = "#0F172A"

        metric_bg      = "linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)"
        metric_border  = "1px solid #C7D2FE"
        metric_accent  = "#0072FF"
        metric_label   = "#3730A3"
        metric_val     = "#1E1B4B"
        metric_shadow  = "0 3px 10px rgba(0, 114, 255, 0.08)"

        th_bg          = "#F1F5F9"
        th_text        = "#334155"
        table_border   = "1px solid #E2E8F0"
        row_pass_bg    = "#FFFFFF"
        row_pass_text  = "#1E293B"
        row_fail_bg    = "#FEF2F2"
        row_fail_text  = "#991B1B"

        badge_bg       = "#D1FAE5" if is_safe else "#FEE2E2"
        badge_fg       = "#065F46" if is_safe else "#991B1B"
        badge_br       = "#10B981" if is_safe else "#EF4444"

        notice_bg      = "#ECFDF5" if is_safe else "#FEF2F2"
        notice_fg      = "#065F46" if is_safe else "#991B1B"
        notice_br      = "#A7F3D0" if is_safe else "#FCA5A5"

    badge_text = "SAFE" if is_safe else "NEEDS REVISION"
    mission_title = str(mission.get('mission_name', 'UAV Mission Plan'))

    def metric_card(label: str, value: str) -> str:
        return (
            f'<div style="flex:1;min-width:110px;background:{metric_bg};padding:0.85rem 1rem;'
            f'border-radius:10px;border:{metric_border};border-left:4px solid {metric_accent};box-shadow:{metric_shadow};box-sizing:border-box">'
            f'<div style="font-size:0.72rem;color:{metric_label};text-transform:uppercase;letter-spacing:0.06em;font-weight:700;margin-bottom:6px">{label}</div>'
            f'<div style="font-size:1.25rem;font-weight:800;color:{metric_val};letter-spacing:-0.01em">{value}</div>'
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
            name_col = row_pass_text
            msg_col  = row_pass_text
        else:
            icon     = "❌"
            row_bg   = row_fail_bg
            name_col = row_fail_text
            msg_col  = row_fail_text

        checklist_rows += (
            f'<tr style="background:{row_bg};border-bottom:{table_border}">'
            f'<td style="padding:10px 10px;text-align:center;font-size:0.95rem;width:40px;box-sizing:border-box">{icon}</td>'
            f'<td style="padding:10px 12px;font-weight:700;color:{name_col};font-size:0.85rem;word-break:break-word;box-sizing:border-box">{check["check_name"]}</td>'
            f'<td style="padding:10px 12px;color:{msg_col};font-size:0.85rem;word-break:break-word;box-sizing:border-box">{check["message"]}</td>'
            f'</tr>'
        )

    # Bottom approval notice
    if failed_checks:
        notice_html = (
            f'<div style="margin-top:16px;padding:12px 16px;background:{notice_bg};border:1px solid {notice_br};'
            f'border-radius:8px;color:{notice_fg};font-size:0.85rem;font-weight:600;box-sizing:border-box;width:100%">'
            f'<b>Notice:</b> Mission failed safety constraints and is not approved for flight. '
            f'Review the Suggestions page for recommended corrections.'
            f'</div>'
        )
    else:
        notice_html = (
            f'<div style="margin-top:16px;padding:12px 16px;background:{notice_bg};border:1px solid {notice_br};'
            f'border-radius:8px;color:{notice_fg};font-size:0.85rem;font-weight:600;box-sizing:border-box;width:100%">'
            f'<b>Approved:</b> Mission passed all safety rules and is cleared for execution.'
            f'</div>'
        )

    html = f"""<div style="font-family:'Segoe UI',Roboto,Arial,sans-serif;padding:22px;border-radius:14px;background:{outer_bg};border:{outer_border};margin-top:12px;box-shadow:{outer_shadow};box-sizing:border-box;width:100%;overflow:hidden">
    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:{table_border};padding-bottom:14px;margin-bottom:18px;box-sizing:border-box;width:100%;gap:12px">
        <div style="font-size:1.15rem;font-weight:800;color:{title_text};letter-spacing:-0.01em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0" title="{mission_title}">{mission_title}</div>
        <span style="padding:6px 14px;border-radius:20px;font-weight:800;font-size:0.75rem;letter-spacing:0.08em;background:{badge_bg};color:{badge_fg};border:1px solid {badge_br};flex-shrink:0;white-space:nowrap">{badge_text}</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:14px;margin-bottom:20px;width:100%;box-sizing:border-box">
        {metrics_html}
    </div>
    <div style="font-size:0.8rem;font-weight:800;color:{th_text};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px">Rule Compliance Checklist</div>
    <table style="width:100%;table-layout:fixed;border-collapse:separate;border-spacing:0;border-radius:10px;overflow:hidden;border:{table_border};box-sizing:border-box">
        <thead>
            <tr style="background:{th_bg}">
                <th style="padding:10px 10px;text-align:center;font-size:0.78rem;color:{th_text};font-weight:700;width:40px;box-sizing:border-box"></th>
                <th style="padding:10px 12px;text-align:left;font-size:0.78rem;color:{th_text};font-weight:700;width:40%;box-sizing:border-box">Rule</th>
                <th style="padding:10px 12px;text-align:left;font-size:0.78rem;color:{th_text};font-weight:700;width:calc(60% - 40px);box-sizing:border-box">Details</th>
            </tr>
        </thead>
        <tbody>
            {checklist_rows}
        </tbody>
    </table>
    {notice_html}
</div>"""

    return html
