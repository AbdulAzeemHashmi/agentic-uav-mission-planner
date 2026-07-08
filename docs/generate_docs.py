import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_user_manual():
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_manual.pdf")
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for publication-quality aesthetic
    title_style = ParagraphStyle(
        'ManualTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=15,
        alignment=1  # Centered
    )
    
    subtitle_style = ParagraphStyle(
        'ManualSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=30,
        alignment=1  # Centered
    )
    
    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubSectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2D3748'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ManualBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'ManualBullet',
        parent=body_style,
        leftIndent=20,
        spaceAfter=4
    )
    
    code_style = ParagraphStyle(
        'CodeBlockText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2D3748')
    )
    
    story = []
    
    # ------------------ COVER PAGE / HEADER ------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("🛸 SkyGuard AI User Manual", title_style))
    story.append(Paragraph("<b>Agentic UAV Mission Planning and Compliance Auditor</b><br/>Author: Abdul Azeem Hashmi | Version 1.1", subtitle_style))
    story.append(Spacer(1, 20))
    
    # A beautiful decorative colored line
    divider = Table([[""]], colWidths=[500], rowHeights=[4])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2B6CB0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 20))
    
    # ------------------ SECTION 1: INTRODUCTION ------------------
    story.append(Paragraph("1. System Introduction", h1_style))
    story.append(Paragraph(
        "SkyGuard AI is a software assistant designed to planning UAV autonomous operations, visualize dynamic "
        "flight trajectories, and verify safety rule compliance. The system uses a multi-agent AI architecture "
        "to translate natural language requirements, generate route waypoints, checks no-fly zones, and suggest "
        "optimal parameter corrections before takeoff.",
        body_style
    ))
    
    story.append(Paragraph("1.1 Core Architecture & Agents", h2_style))
    story.append(Paragraph("The system is divided into five modular agents cooperating in sequence:", body_style))
    story.append(Paragraph("• <b>Mission Understanding Agent</b>: Parses natural language requests using Google Gemini Generative AI models.", bullet_style))
    story.append(Paragraph("• <b>Waypoint Planner Agent</b>: Calculates geometric paths (Square, Grid scanning, Circle orbit, Perimeter).", bullet_style))
    story.append(Paragraph("• <b>Safety Compliance Agent</b>: Enforces 7 compliance safety rules using physics and Shapely metrics.", bullet_style))
    story.append(Paragraph("• <b>Correction Agent</b>: Adjusts flight coordinates and clips bounds in response to failed checks.", bullet_style))
    story.append(Paragraph("• <b>Report Generation Agent</b>: Complies detailed PDFs, CSV logs, and QGC plan files.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(PageBreak())
    
    # ------------------ SECTION 2: SYSTEM SETUP ------------------
    story.append(Paragraph("2. System Setup & Running Instructions", h1_style))
    story.append(Paragraph(
        "SkyGuard AI requires Python 3.8+ and standard dependencies (Streamlit, Folium, Shapely, ReportLab, etc.).",
        body_style
    ))
    
    story.append(Paragraph("2.1 Installation Steps", h2_style))
    story.append(Paragraph("Follow these terminal steps to launch the application locally:", body_style))
    
    # Code snippet block using a table
    setup_commands = [
        [Paragraph("git clone https://github.com/AbdulAzeemHashmi/agentic-uav-mission-planner.git", code_style)],
        [Paragraph("cd agentic-uav-mission-planner", code_style)],
        [Paragraph("python -m venv .venv", code_style)],
        [Paragraph(".venv\\Scripts\\Activate  # On Windows", code_style)],
        [Paragraph("pip install -r requirements.txt", code_style)],
        [Paragraph("streamlit run app.py", code_style)]
    ]
    t_cmd = Table(setup_commands, colWidths=[480])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cmd)
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 3: SAFETY CONTROLS ------------------
    story.append(Paragraph("3. Airspace Compliance Safety Controls", h1_style))
    story.append(Paragraph(
        "The system enforces 7 crucial safety standards to prevent UAV crashes and airspace regulations violations:",
        body_style
    ))
    
    # Safety Standards table
    rules_data = [
        [Paragraph("<b>Rule ID</b>", body_style), Paragraph("<b>Standard Limit</b>", body_style), Paragraph("<b>Compliance Implementation Detail</b>", body_style)],
        [Paragraph("R1", body_style), Paragraph("Altitude Ceiling ≤ 80m", body_style), Paragraph("Enforces legal flying boundaries", body_style)],
        [Paragraph("R2 / R3", body_style), Paragraph("Takeoff & Landing/RTL", body_style), Paragraph("Ensures terminal control nodes", body_style)],
        [Paragraph("R4", body_style), Paragraph("Geofence Clearance", body_style), Paragraph("Checks waypoint and line-segment intersections", body_style)],
        [Paragraph("R5", body_style), Paragraph("Leg Length ≤ 500m", body_style), Paragraph("Limits max distance between waypoints", body_style)],
        [Paragraph("R6", body_style), Paragraph("Flight Window ≤ 30 min", body_style), Paragraph("Caps total operational duration", body_style)],
        [Paragraph("R7", body_style), Paragraph("Battery Consumption < 80%", body_style), Paragraph("Uses dynamic physics energy calculation", body_style)],
    ]
    t_rules = Table(rules_data, colWidths=[60, 140, 280])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_rules)
    story.append(Spacer(1, 10))
    story.append(PageBreak())
    
    # ------------------ SECTION 4: ADVANCED CORRECTIONS & EXPORTS ------------------
    story.append(Paragraph("4. Geofence Corrections & Telemetry Exporting", h1_style))
    story.append(Paragraph(
        "SkyGuard AI implements mathematical projections to resolve compliance issues and formats outputs for real controllers:",
        body_style
    ))
    
    story.append(Paragraph("4.1 Shapely Boundary-Normal Corrections", h2_style))
    story.append(Paragraph(
        "If a waypoint or path segment violates restricted airspace, the Correction Agent does not perform a simple offset. "
        "It projects the coordinate to the nearest polygon boundary point using Shapely algorithms and shifts it along the outward "
        "normal vector by exactly 15.0 meters. For circular no-fly zones, coordinates are shifted along the center-outward radial vector.",
        body_style
    ))
    
    story.append(Paragraph("4.2 Physics-Based Battery Estimation", h2_style))
    story.append(Paragraph(
        "Battery consumption (R7) computes climb energy (215W at 4m/s), cruise energy (120W at 10m/s), descent energy (115W at 2m/s), "
        "and residual hovering states (130W) based on UAV mass (1.5 kg) and a 90 Wh capacity model.",
        body_style
    ))
    
    story.append(Paragraph("4.3 QGroundControl (.plan) File Export", h2_style))
    story.append(Paragraph(
        "You can export flight plans as standard JSON `.plan` files. These contain mapped MAVLink commands "
        "(MAV_CMD_NAV_TAKEOFF, MAV_CMD_NAV_WAYPOINT, MAV_CMD_NAV_RETURN_TO_LAUNCH) which are directly importable "
        "into QGroundControl or standard drone autopilot systems.",
        body_style
    ))
    story.append(Spacer(1, 20))
    
    doc.build(story)
    print(f"Generated user manual successfully at: {pdf_path}")

if __name__ == "__main__":
    generate_user_manual()
