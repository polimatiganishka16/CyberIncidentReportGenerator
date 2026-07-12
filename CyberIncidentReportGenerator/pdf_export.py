"""
pdf_export.py
-------------
Uses ReportLab to turn a generated report into a downloadable PDF file.
Saved PDFs go into the reports/ folder, then Flask sends them to the
browser as a file download.
"""

import os
import re
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

import config

SEVERITY_COLORS = {
    "Critical": colors.HexColor("#e63946"),
    "High": colors.HexColor("#f77f00"),
    "Medium": colors.HexColor("#fcbf49"),
    "Low": colors.HexColor("#2a9d8f"),
}


def build_pdf(data: dict, plain_text: str, filename: str) -> str:
    """
    Builds a PDF at reports/<filename> from the incident data and the
    already-generated plain-text report. Returns the full path.
    """
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(config.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        output_path, pagesize=LETTER,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#0d1b2a")
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#1b263b"), spaceBefore=12, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["BodyText"], fontSize=10.5, leading=15,
    )

    story = []
    story.append(Paragraph("Cybersecurity Incident Report", title_style))
    story.append(Spacer(1, 12))

    severity = data.get("severity", "")
    sev_color = SEVERITY_COLORS.get(severity, colors.grey)

    # Summary table of the raw incident fields
    table_data = [
        ["Incident ID", data.get("incident_id", "")],
        ["Date / Time", f"{data.get('date', '')} {data.get('time', '')}"],
        ["Attack Type", data.get("attack_type", "")],
        ["Severity", severity],
        ["Source IP", data.get("source_ip", "")],
        ["Destination System", data.get("destination_system", "")],
        ["Affected User", data.get("affected_user", "")],
        ["Malware", data.get("malware", "")],
        ["Detection Tool", data.get("detection_tool", "")],
        ["Status", data.get("status", "")],
        ["Action Taken", data.get("action_taken", "")],
    ]
    table = Table(table_data, colWidths=[1.8 * inch, 4.2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e0e1dd")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0d1b2a")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#adb5bd")),
        ("BACKGROUND", (1, 3), (1, 3), sev_color),
        ("TEXTCOLOR", (1, 3), (1, 3), colors.white),
        ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Body: the generated narrative report, split into sections on blank lines
    for block in plain_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        first_line = lines[0]
        rest = " ".join(lines[1:]).strip()

        looks_like_heading = len(first_line) < 60 and (first_line.isupper() or first_line[:2].isdigit())
        if looks_like_heading:
            story.append(Paragraph(first_line, heading_style))
            if rest:
                story.append(Paragraph(rest, body_style))
        else:
            story.append(Paragraph(block.replace("\n", "<br/>"), body_style))

    doc.build(story)
    return output_path
