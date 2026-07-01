import json
import csv
import io
import os
from typing import List, Dict, Any

def export_mission_json(mission: Dict[str, Any], waypoints: List[Dict[str, Any]], safety_checks: List[Dict[str, Any]]) -> str:
    """Format mission, waypoints, and safety checks as a formatted JSON string."""
    data = {
        "mission": mission,
        "waypoints": waypoints,
        "safety_checks": safety_checks
    }
    return json.dumps(data, indent=4)

def export_waypoints_csv(waypoints: List[Dict[str, Any]]) -> str:
    """Format waypoints list as a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["sequence_no", "latitude", "longitude", "altitude", "action"])
    
    for wp in waypoints:
        writer.writerow([
            wp.get("sequence_no"),
            wp.get("latitude"),
            wp.get("longitude"),
            wp.get("altitude"),
            wp.get("action")
        ])
        
    return output.getvalue()

def generate_text_report(mission: Dict[str, Any], waypoints: List[Dict[str, Any]], safety_checks: List[Dict[str, Any]]) -> str:
    """Generate a clean markdown text report for the mission."""
    report = []
    report.append(f"# UAV MISSION PLAN REPORT: {mission.get('mission_name', 'Unnamed Mission')}")
    report.append(f"Generated at: {mission.get('created_at', 'N/A')}")
    report.append(f"Status: **{mission.get('status', 'Needs Revision').upper()}**")
    report.append("")
    report.append("## 1. Mission Metadata")
    report.append(f"- **Type**: {mission.get('mission_type', 'N/A')}")
    report.append(f"- **Requested Altitude**: {mission.get('altitude')} m")
    report.append(f"- **Estimated Duration**: {mission.get('duration')} minutes")
    report.append("")
    
    report.append("## 2. Safety Compliance Checklist")
    all_passed = True
    for check in safety_checks:
        result_icon = "✅ PASS" if check.get("result") == "Pass" else "❌ FAIL"
        if check.get("result") != "Pass":
            all_passed = False
        report.append(f"- **{check.get('check_name')}**: {result_icon} - {check.get('message')}")
    
    report.append("")
    report.append(f"**Overall Compliance Status**: {'APPROVED' if all_passed else 'NEEDS REVISION'}")
    report.append("")
    
    report.append("## 3. Flight Waypoints")
    report.append("| Seq | Latitude | Longitude | Altitude (m) | Flight Action |")
    report.append("|---|---|---|---|---|")
    for wp in waypoints:
        report.append(f"| {wp.get('sequence_no')} | {wp.get('latitude'):.6f} | {wp.get('longitude'):.6f} | {wp.get('altitude')} | {wp.get('action')} |")
        
    return "\n".join(report)

def generate_pdf_report(mission: Dict[str, Any], waypoints: List[Dict[str, Any]], safety_checks: List[Dict[str, Any]], filepath: str):
    """
    Generate a formatted PDF report using reportlab and save it to the specified filepath.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#8B0000'), # Deep Red to match UI
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2F4F4F'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldStyle', parent=normal_style, fontName='Helvetica-Bold')
    
    # Title
    story.append(Paragraph(f"UAV Mission Summary Report", title_style))
    story.append(Paragraph(f"Mission Name: <b>{mission.get('mission_name', 'Unnamed Mission')}</b>", normal_style))
    story.append(Paragraph(f"Created: {mission.get('created_at', 'N/A')}", normal_style))
    
    status_color = "#006400" if mission.get('status') == "Safe" else "#8B0000"
    story.append(Paragraph(f"Status: <font color='{status_color}'><b>{mission.get('status', 'Needs Revision').upper()}</b></font>", normal_style))
    story.append(Spacer(1, 15))
    
    # Section 1: Metadata
    story.append(Paragraph("1. Mission Parameters", h2_style))
    meta_data = [
        [Paragraph("<b>Parameter</b>", normal_style), Paragraph("<b>Value</b>", normal_style)],
        [Paragraph("Mission Type", normal_style), Paragraph(str(mission.get('mission_type', 'N/A')).capitalize(), normal_style)],
        [Paragraph("Reference Altitude", normal_style), Paragraph(f"{mission.get('altitude')} meters", normal_style)],
        [Paragraph("Estimated Duration", normal_style), Paragraph(f"{mission.get('duration')} minutes", normal_style)],
    ]
    t1 = Table(meta_data, colWidths=[150, 250])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # Section 2: Safety Checklist
    story.append(Paragraph("2. Safety & Compliance Log", h2_style))
    safety_data = [
        [Paragraph("<b>Check Point</b>", normal_style), Paragraph("<b>Result</b>", normal_style), Paragraph("<b>Message</b>", normal_style)]
    ]
    for check in safety_checks:
        res = check.get("result")
        res_text = f"<font color='green'><b>PASS</b></font>" if res == "Pass" else f"<font color='red'><b>FAIL</b></font>"
        safety_data.append([
            Paragraph(check.get('check_name'), normal_style),
            Paragraph(res_text, normal_style),
            Paragraph(check.get('message', ''), normal_style)
        ])
    t2 = Table(safety_data, colWidths=[150, 70, 250])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))
    
    # Section 3: Waypoints Table
    story.append(Paragraph("3. Generated Flight Waypoints", h2_style))
    wp_data = [
        [
            Paragraph("<b>Seq</b>", normal_style), 
            Paragraph("<b>Latitude</b>", normal_style), 
            Paragraph("<b>Longitude</b>", normal_style), 
            Paragraph("<b>Alt (m)</b>", normal_style), 
            Paragraph("<b>Action</b>", normal_style)
        ]
    ]
    for wp in waypoints:
        wp_data.append([
            Paragraph(str(wp.get('sequence_no')), normal_style),
            Paragraph(f"{wp.get('latitude'):.6f}", normal_style),
            Paragraph(f"{wp.get('longitude'):.6f}", normal_style),
            Paragraph(str(wp.get('altitude')), normal_style),
            Paragraph(str(wp.get('action')).upper(), normal_style),
        ])
    t3 = Table(wp_data, colWidths=[40, 100, 100, 70, 100])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t3)
    
    doc.build(story)
