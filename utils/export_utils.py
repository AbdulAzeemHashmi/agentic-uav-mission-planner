import json
import csv
import io
import os
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def export_mission_json(mission: Dict[str, Any], waypoints: List[Dict[str, Any]], safety_checks: List[Dict[str, Any]]) -> str:
    """Format mission, waypoints, and safety checks as a formatted JSON string."""
    data = {\
        "mission": mission,\
        "waypoints": waypoints,\
        "safety_checks": safety_checks\
    }
    return json.dumps(data, indent=4)

def export_waypoints_csv(waypoints: List[Dict[str, Any]]) -> str:
    """Format waypoints list as a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["sequence_no", "latitude", "longitude", "altitude", "action"])
    
    for wp in waypoints:
        writer.writerow([\
            wp.get("sequence_no"),\
            wp.get("latitude"),\
            wp.get("longitude"),\
            wp.get("altitude"),\
            wp.get("action")\
        ])
        
    return output.getvalue()

def generate_text_report(mission: Dict[str, Any], waypoints: List[Dict[str, Any]], safety_checks: List[Dict[str, Any]]) -> str:
    """Generate a clean markdown text report for the mission."""
    report = []
    report.append(f"# UAV MISSION PLAN REPORT: {mission.get('mission_name', 'Unnamed Mission')}")
    report.append(f"Generated at: {mission.get('created_at', 'N/A')}\n")
    report.append(f"## 1. Mission Metadata")
    report.append(f"- **Type**: {mission.get('mission_type', 'N/A')}")
    report.append(f"- **Altitude Bound**: {mission.get('altitude', 0.0)}m")
    report.append(f"- **Target Duration**: {mission.get('duration', 0.0)} mins")
    report.append(f"- **Final Verdict Status**: {mission.get('status', 'UNCHECKED').upper()}\n")
    
    report.append(f"## 2. Rule Compliance Checklist")
    for check in safety_checks:
        report.append(f"- [{ 'X' if check.get('result') == 'Pass' else ' ' }] {check.get('check_name')}: {check.get('message')}")
    report.append("")
    
    report.append(f"## 3. Flight Sequence Coordinates")
    report.append("| Seq | Latitude | Longitude | Altitude (m) | Action |")
    report.append("|---|---|---|---|---|")
    for wp in waypoints:
        report.append(f"| {wp.get('sequence_no')} | {wp.get('latitude'):.6f} | {wp.get('longitude'):.6f} | {wp.get('altitude')} | {str(wp.get('action')).upper()} |")
        
    return "\n".join(report)

def generate_pdf_report(mission: Dict[str, Any], waypoints: List[Dict[str, Any]], safety_checks: List[Dict[str, Any]]) -> bytes:
    """Generates a complete, publication-quality binary PDF mission record using ReportLab."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2C5282'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    normal_style = ParagraphStyle(
        'TableCellText',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )
    
    pass_style = ParagraphStyle(
        'PassText',
        parent=normal_style,
        textColor=colors.HexColor('#2F855A'),
        fontWeight='Bold'
    )
    
    fail_style = ParagraphStyle(
        'FailText',
        parent=normal_style,
        textColor=colors.HexColor('#C53030'),
        fontWeight='Bold'
    )
    
    story = []
    
    # Header block
    story.append(Paragraph(f"UAV Flight Mission Brief: {mission.get('mission_name', 'Unnamed')}", title_style))
    story.append(Paragraph(f"<b>Timestamp:</b> {mission.get('created_at', 'N/A')} | <b>System Verdict:</b> {str(mission.get('status', 'UNCHECKED')).upper()}", normal_style))
    story.append(Spacer(1, 15))
    
    # Section 1: Overview Metadata
    story.append(Paragraph("1. Mission Metadata Parameters", h2_style))
    meta_data = [\
        [Paragraph("<b>Parameter</b>", normal_style), Paragraph("<b>Target Specification Value</b>", normal_style)],\
        [Paragraph("Mission Profile Type", normal_style), Paragraph(str(mission.get('mission_type')).capitalize(), normal_style)],\
        [Paragraph("Programmed Cruise Altitude", normal_style), Paragraph(f"{mission.get('altitude')} meters", normal_style)],\
        [Paragraph("Calculated Mission Duration Bound", normal_style), Paragraph(f"{mission.get('duration')} minutes", normal_style)]\
    ]
    t1 = Table(meta_data, colWidths=[200, 320])
    t1.setStyle(TableStyle([\
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),\
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),\
        ('PADDING', (0,0), (-1,-1), 6),\
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # Section 2: Safety Audit Rules Checklist
    story.append(Paragraph("2. Airspace Safety Verification Rules Audit", h2_style))
    safety_data = [\
        [Paragraph("<b>Safety Rule Reference Standard</b>", normal_style), Paragraph("<b>Status Check</b>", normal_style), Paragraph("<b>Telemetry Evaluation Analysis</b>", normal_style)]\
    ]
    for check in safety_checks:
        res = check.get('result', 'Fail')
        res_style = pass_style if res == 'Pass' else fail_style
        safety_data.append([\
            Paragraph(check.get('check_name', ''), normal_style),\
            Paragraph(res.upper(), res_style),\
            Paragraph(check.get('message', ''), normal_style)\
        ])
    t2 = Table(safety_data, colWidths=[150, 70, 300])
    t2.setStyle(TableStyle([\
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),\
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),\
        ('PADDING', (0,0), (-1,-1), 6),\
        ('VALIGN', (0,0), (-1,-1), 'TOP'),\
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))
    
    # Section 3: Waypoint Telemetry Sequence Records Table
    story.append(Paragraph("3. Generated Flight Path Target Waypoints Sequence", h2_style))
    wp_data = [\
        [\
            Paragraph("<b>Seq No.</b>", normal_style), \
            Paragraph("<b>Latitude Coordinate</b>", normal_style), \
            Paragraph("<b>Longitude Coordinate</b>", normal_style), \
            Paragraph("<b>Altitude (m)</b>", normal_style), \
            Paragraph("<b>Nav Action Block</b>", normal_style)\
        ]\
    ]
    for wp in waypoints:
        wp_data.append([\
            Paragraph(str(wp.get('sequence_no')), normal_style),\
            Paragraph(f"{wp.get('latitude'):.6f}", normal_style),\
            Paragraph(f"{wp.get('longitude'):.6f}", normal_style),\
            Paragraph(str(wp.get('altitude')), normal_style),\
            Paragraph(str(wp.get('action')).upper(), normal_style)\
        ])
    t3 = Table(wp_data, colWidths=[60, 120, 120, 80, 140])
    t3.setStyle(TableStyle([\
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),\
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),\
        ('PADDING', (0,0), (-1,-1), 4),\
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),\
    ]))
    story.append(t3)
    
    doc.build(story)
    return pdf_buffer.getvalue()