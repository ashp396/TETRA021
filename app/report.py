"""One page investor readiness report, generated with reportlab so it has
no external system dependencies to install."""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_report_pdf(workspace_name: str, analysis: dict, documents: list[dict]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=colors.HexColor("#3a2154"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#7a3d5e"))
    body = styles["BodyText"]

    story = [
        Paragraph("Finvestor Fundraising Readiness Report", title_style),
        Paragraph(f"Workspace: {workspace_name}", body),
        Paragraph(f"Generated: {datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')}", body),
        Spacer(1, 10),
        Paragraph(f"Composite readiness score: {analysis.get('compositeScore', analysis.get('composite_score'))} / 850", h2),
        Spacer(1, 6),
        Paragraph(analysis.get("summary", ""), body),
        Spacer(1, 12),
        Paragraph("Category breakdown", h2),
    ]

    cat_scores = analysis.get("categoryScores") or analysis.get("category_scores") or {}
    cat_notes = analysis.get("categoryNotes") or analysis.get("category_notes") or {}
    rows = [["Category", "Score", "Note"]]
    for key, label in [("pitch", "Pitch narrative"), ("financials", "Financial statements"),
                        ("capTable", "Cap table"), ("team", "Team credibility"),
                        ("market", "Market sizing"), ("ddPrep", "DD preparedness")]:
        rows.append([label, f"{cat_scores.get(key, 0)}/100", cat_notes.get(key, "")])
    table = Table(rows, colWidths=[110, 50, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d7a83f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Discrepancies", h2))
    for d in analysis.get("discrepancies", []):
        line = f"<b>[{d.get('classification')}]</b> {d.get('title')}: {d.get('description')} " \
               f"<i>(Sources: {', '.join(d.get('sources', []))})</i>"
        story.append(Paragraph(line, body))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Likely investor follow up questions", h2))
    for q in analysis.get("followUpQuestions") or analysis.get("follow_ups") or []:
        story.append(Paragraph(f"- {q}", body))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Documents reviewed", h2))
    for d in documents:
        story.append(Paragraph(f"- {d['name']} ({d['doc_type']})", body))

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "This report reflects completeness and internal consistency of the documents "
        "provided. It is not a valuation and not an investment recommendation.",
        ParagraphStyle("note", parent=body, textColor=colors.grey, fontSize=8)))

    doc.build(story)
    return buf.getvalue()
