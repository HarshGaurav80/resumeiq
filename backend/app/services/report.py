"""
Generates a downloadable PDF report for an analysis using ReportLab.
"""
import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

INDIGO = colors.HexColor("#4f46e5")
PURPLE = colors.HexColor("#7c3aed")
GRAY = colors.HexColor("#6b7280")
LIGHT = colors.HexColor("#f5f3ff")

# Built-in PDF fonts only support Latin-1, so swap common unicode symbols
_REPLACEMENTS = {"→": "->", "–": "-", "—": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "•": "-",
                 "₹": "Rs.", "…": "...", " ": " "}


def _safe(text) -> str:
    text = str(text or "")
    for k, v in _REPLACEMENTS.items():
        text = text.replace(k, v)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return escape(text)


def _score_color(score: int):
    if score > 75:
        return colors.HexColor("#16a34a")
    if score >= 50:
        return colors.HexColor("#ca8a04")
    return colors.HexColor("#dc2626")


def build_pdf_report(record: dict) -> bytes:
    result = record["result"]
    cand = result.get("candidate", {})
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title="ResumeIQ Analysis Report", author="ResumeIQ")

    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=INDIGO, fontSize=22, leading=28, spaceAfter=6)
    sub = ParagraphStyle("sub", parent=ss["Normal"], textColor=GRAY, alignment=TA_CENTER, fontSize=9)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=PURPLE, fontSize=13, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("body", parent=ss["Normal"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, textColor=GRAY)

    def bullets(items, color=None):
        if not items:
            return Paragraph("<i>None</i>", small)
        style = ParagraphStyle("b", parent=body, textColor=color or colors.black)
        return ListFlowable([ListItem(Paragraph(_safe(i), style), leftIndent=10) for i in items],
                            bulletType="bullet", start="•", leftIndent=12, bulletFontSize=8)

    story = []
    created = record.get("created_at", "")
    try:
        created = datetime.fromisoformat(created).strftime("%d %b %Y, %H:%M UTC")
    except ValueError:
        pass
    method = {"gemini": "Google Gemini AI", "openai": "OpenAI"}.get(record.get("method"),
                                                                     "Offline keyword + TF-IDF analysis")
    story += [
        Paragraph("ResumeIQ - Resume Analysis Report", h1),
        Paragraph(_safe(f"{record.get('file_name')}  |  Role: {record.get('job_role') or 'Not specified'}  |  "
                        f"{created}  |  Engine: {method}"), sub),
        Spacer(1, 6), HRFlowable(width="100%", color=INDIGO, thickness=1.2), Spacer(1, 8),
    ]

    # ---- Score summary table -----------------------------------------------------
    ms, ats = result.get("match_score", 0), result.get("ats_score", 0)
    score_style = lambda s: ParagraphStyle("s", parent=body, fontSize=22, leading=26, alignment=TA_CENTER,
                                           textColor=_score_color(s), fontName="Helvetica-Bold")
    label = ParagraphStyle("l", parent=small, alignment=TA_CENTER)
    t = Table([[Paragraph(f"{ms}/100", score_style(ms)), Paragraph(f"{ats}/100", score_style(ats))],
               [Paragraph("Overall Match Score", label), Paragraph("ATS Compatibility", label)]],
              colWidths=[85 * mm, 85 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.5, INDIGO),
                           ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.white),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [t, Spacer(1, 6)]

    if result.get("summary"):
        story += [Paragraph("Summary", h2), Paragraph(_safe(result["summary"]), body)]

    # ---- Section scores -----------------------------------------------------------
    story.append(Paragraph("Section Scores", h2))
    rows = [["Section", "Score", ""]]
    for key, val in result.get("section_scores", {}).items():
        bar = Table([[""]], colWidths=[max(1, val) * 0.9 * mm], rowHeights=[3.5 * mm])
        bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), _score_color(val))]))
        rows.append([key.title(), f"{val}/100", bar])
    st = Table(rows, colWidths=[40 * mm, 25 * mm, 100 * mm])
    st.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("LINEBELOW", (0, 0), (-1, 0), 0.5, GRAY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]))
    story.append(st)

    # ---- Candidate details ------------------------------------------------------
    story.append(Paragraph("Candidate Details", h2))
    info = [["Name", cand.get("name") or "-"], ["Email", cand.get("email") or "-"], ["Phone", cand.get("phone") or "-"]]
    it = Table([[Paragraph(f"<b>{k}</b>", body), Paragraph(_safe(v), body)] for k, v in info],
               colWidths=[30 * mm, 140 * mm])
    it.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 2)]))
    story.append(it)
    for key, title in [("education", "Education"), ("experience", "Experience"),
                       ("projects", "Projects"), ("certifications", "Certifications")]:
        story += [Paragraph(f"<b>{title}</b>", body), bullets(cand.get(key, [])), Spacer(1, 3)]

    # ---- Skills ------------------------------------------------------------------
    story.append(Paragraph("Skills Analysis", h2))
    story.append(Paragraph("<b>Skills found:</b> " + (_safe(", ".join(result.get("skills_found", []))) or "-"),
                           ParagraphStyle("g", parent=body, textColor=colors.HexColor("#15803d"))))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Missing skills:</b> " + (_safe(", ".join(result.get("missing_skills", []))) or "None"),
                           ParagraphStyle("r", parent=body, textColor=colors.HexColor("#b91c1c"))))

    story += [Paragraph("Strengths", h2), bullets(result.get("strengths", []))]
    story += [Paragraph("Suggestions for Improvement", h2), bullets(result.get("suggestions", []))]

    story += [Spacer(1, 14), HRFlowable(width="100%", color=GRAY, thickness=0.4),
              Paragraph("Generated by ResumeIQ - AI Resume Analyzer", sub)]

    doc.build(story)
    return buf.getvalue()
