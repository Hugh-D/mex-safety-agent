"""
Compliance report generator — MEX Safety Platform
Produces a branded PDF and/or DOCX from a drawing analysis result.
PDF uses ReportLab + svglib for SLD embedding.
DOCX uses python-docx; diagram is noted as available in PDF.
"""

from __future__ import annotations

import io
import os
from datetime import date
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable

import logging
log = logging.getLogger(__name__)

# ── Brand constants ────────────────────────────────────────────────────────────
NAVY      = colors.HexColor("#002559")
LIME      = colors.HexColor("#70bf54")
WHITE     = colors.white
BLACK     = colors.black
MID_GREY  = colors.HexColor("#8a9ab0")
LIGHT_GREY = colors.HexColor("#f2f4f7")

SEVERITY_COLOUR = {
    "critical": colors.HexColor("#C0392B"),
    "major":    colors.HexColor("#E67E22"),
    "minor":    colors.HexColor("#2471A3"),
}
VERDICT_COLOUR = {
    "compliant":               colors.HexColor("#2e7d32"),
    "conditionally_compliant": colors.HexColor("#f57f17"),
    "non_compliant":           colors.HexColor("#c62828"),
}
VERDICT_BG = {
    "compliant":               colors.HexColor("#e8f5e1"),
    "conditionally_compliant": colors.HexColor("#fff8e1"),
    "non_compliant":           colors.HexColor("#fdecea"),
}
VERDICT_LABEL = {
    "compliant":               "COMPLIANT",
    "conditionally_compliant": "CONDITIONALLY COMPLIANT",
    "non_compliant":           "NON-COMPLIANT",
}

PAGE_W, PAGE_H = A4
MARGIN   = 18 * mm
FOOTER_H = 14 * mm
HEADER_H = 16 * mm
CONTACT_LINE = (
    "1800 MEX 24/7  |  PO Box 6425 Silverwater NSW 2128  |  admin@mexeng.com.au"
    "  |  Lic 141260C  |  ABN 68 101 789 584  |  mexeng.com.au"
)


def _audit_complete() -> bool:
    return os.environ.get("AUDIT_COMPLETE", "").strip().lower() in ("1", "true", "yes")


def _draw_draft_watermark(canvas) -> None:
    canvas.saveState()
    canvas.translate(PAGE_W / 2, PAGE_H / 2)
    canvas.rotate(45)
    canvas.setFillColor(colors.Color(0.8, 0, 0, alpha=0.12))
    canvas.setFont("Helvetica-Bold", 72)
    canvas.drawCentredString(0, 20, "DRAFT")
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(0, -20, "STANDARDS AUDIT INCOMPLETE")
    canvas.restoreState()


class _LimeRule(Flowable):
    def __init__(self, width: float = PAGE_W - 2 * MARGIN):
        super().__init__()
        self.width = width
        self.height = 1.5

    def draw(self):
        self.canv.setStrokeColor(LIME)
        self.canv.setLineWidth(1.5)
        self.canv.line(0, 0, self.width, 0)


def _styles() -> dict:
    return {
        "h1":   ParagraphStyle("h1",   fontName="Helvetica-Bold", fontSize=20, textColor=NAVY, spaceAfter=6),
        "h2":   ParagraphStyle("h2",   fontName="Helvetica-Bold", fontSize=13, textColor=NAVY, spaceBefore=10, spaceAfter=4),
        "h3":   ParagraphStyle("h3",   fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, spaceBefore=6, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica",      fontSize=9,  leading=13, spaceAfter=4),
        "small":ParagraphStyle("small",fontName="Helvetica",      fontSize=7.5, leading=11, textColor=MID_GREY),
        "th":   ParagraphStyle("th",   fontName="Helvetica-Bold", fontSize=8,  textColor=WHITE, alignment=TA_CENTER),
        "td":   ParagraphStyle("td",   fontName="Helvetica",      fontSize=8,  leading=10),
        "tdc":  ParagraphStyle("tdc",  fontName="Helvetica",      fontSize=8,  leading=10, alignment=TA_CENTER),
        "clause": ParagraphStyle("clause", fontName="Helvetica-Oblique", fontSize=7.5, textColor=MID_GREY, spaceAfter=2),
    }


def _page_callback(canvas, doc):
    if not _audit_complete():
        _draw_draft_watermark(canvas)
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(MARGIN, PAGE_H - HEADER_H + 4.5 * mm, "MEX Engineering Group")
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(LIME)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - HEADER_H + 4.5 * mm,
                           getattr(doc, "_report_title", "Drawing Review"))
    canvas.setStrokeColor(LIME)
    canvas.setLineWidth(1.5)
    canvas.line(0, PAGE_H - HEADER_H - 1, PAGE_W, PAGE_H - HEADER_H - 1)
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(PAGE_W / 2, FOOTER_H - 3.5 * mm, CONTACT_LINE)
    canvas.drawCentredString(PAGE_W / 2, FOOTER_H - 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _bullet_para(text: str, style) -> Paragraph:
    clean = text.strip().lstrip("-•*").strip()
    return Paragraph(f"• {clean}", style)


def _finding_table(findings: list[dict], s: dict, key_label: str = "description",
                   key_remedy: str = "remediation", key_clause: str = "clauseReference") -> list:
    """Render a list of non-conformances as a styled table."""
    rows = [[
        Paragraph("Sev", s["th"]),
        Paragraph("Finding", s["th"]),
        Paragraph("Clause", s["th"]),
        Paragraph("Remediation", s["th"]),
    ]]
    row_styles: list[tuple] = []
    for i, nc in enumerate(findings):
        sev = (nc.get("severity") or "minor").lower()
        sev_col = SEVERITY_COLOUR.get(sev, SEVERITY_COLOUR["minor"])
        rows.append([
            Paragraph(sev.upper(), ParagraphStyle(
                "sevbadge", fontName="Helvetica-Bold", fontSize=7,
                textColor=WHITE, alignment=TA_CENTER
            )),
            Paragraph(nc.get(key_label, ""), s["td"]),
            Paragraph(nc.get(key_clause, ""), s["clause"]),
            Paragraph(nc.get(key_remedy, ""), s["td"]),
        ])
        row_styles.append(("BACKGROUND", (0, i + 1), (0, i + 1), sev_col))

    col_w = PAGE_W - 2 * MARGIN
    tbl = Table(rows, colWidths=[col_w * 0.10, col_w * 0.36, col_w * 0.22, col_w * 0.32])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        *row_styles,
    ]))
    return [tbl]


# ── PDF generator ──────────────────────────────────────────────────────────────

def generate_pdf(
    drawing_title: str,
    target_pl: str,
    target_category: str,
    analysis: dict[str, Any],
    svg_diagram: Optional[str] = None,
) -> bytes:
    """
    Generate a branded compliance review PDF.
    analysis: the dict representation of DrawingAnalysisResponse.
    svg_diagram: optional SVG string for the redline SLD.
    """
    buf = io.BytesIO()
    s = _styles()

    content_frame = Frame(
        MARGIN, FOOTER_H + 4 * mm,
        PAGE_W - 2 * MARGIN,
        PAGE_H - HEADER_H - FOOTER_H - 8 * mm,
        id="content",
    )
    doc = BaseDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=HEADER_H + 4 * mm, bottomMargin=FOOTER_H + 4 * mm,
    )
    doc._report_title = f"Drawing Review — {drawing_title}"
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[content_frame], onPage=_page_callback)
    ])

    verdict_key   = (analysis.get("overallVerdict") or "non_compliant").lower()
    verdict_label = VERDICT_LABEL.get(verdict_key, "UNKNOWN")
    verdict_col   = VERDICT_COLOUR.get(verdict_key, SEVERITY_COLOUR["critical"])
    verdict_bg    = VERDICT_BG.get(verdict_key, colors.white)

    arch  = analysis.get("architectureAssessment") or {}
    ncs   = analysis.get("nonConformances") or []
    confs = analysis.get("conformances") or []
    comps = analysis.get("componentsIdentified") or []

    story: list = []

    # ── Cover info ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Drawing Review", s["h1"]))
    story.append(Paragraph(drawing_title, ParagraphStyle(
        "title_sub", fontName="Helvetica-Bold", fontSize=14, textColor=NAVY, spaceAfter=8
    )))
    story.append(_LimeRule())
    story.append(Spacer(1, 4 * mm))

    meta_rows = [
        ["Target PL", target_pl, "Target Category", target_category],
        ["Review Date", date.today().strftime("%d %b %Y"), "Drawing Type",
         analysis.get("drawingType", "—").replace("_", " ").title()],
    ]
    meta_tbl = Table(meta_rows, colWidths=[35 * mm, 35 * mm, 45 * mm, 50 * mm])
    meta_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (2, 0), (2, -1), NAVY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 4 * mm))

    # ── Verdict banner ─────────────────────────────────────────────────────────
    gap_to = (analysis.get("gapToTarget") or "—").replace("_", " ").title()
    verdict_data = [[
        Paragraph(verdict_label, ParagraphStyle(
            "verdict_lbl", fontName="Helvetica-Bold", fontSize=12, textColor=verdict_col
        )),
        Paragraph(f"Gap to {target_pl} {target_category}: <b>{gap_to}</b>",
                  ParagraphStyle("verdict_gap", fontName="Helvetica", fontSize=9,
                                 textColor=BLACK, alignment=TA_RIGHT)),
    ]]
    verdict_tbl = Table(verdict_data, colWidths=[90 * mm, PAGE_W - 2 * MARGIN - 90 * mm])
    verdict_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), verdict_bg),
        ("BOX", (0, 0), (-1, -1), 1.5, verdict_col),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(verdict_tbl)

    gap_summary = analysis.get("gapSummary", "")
    if gap_summary:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(gap_summary, s["body"]))
    story.append(Spacer(1, 4 * mm))

    # ── Architecture Assessment ────────────────────────────────────────────────
    story.append(Paragraph("Architecture Assessment", s["h2"]))
    story.append(_LimeRule())
    story.append(Spacer(1, 2 * mm))

    arch_data = [[
        Paragraph("Detected PL",           s["th"]),
        Paragraph("Detected Category",     s["th"]),
        Paragraph("Channels",              s["th"]),
        Paragraph("Feedback Monitoring",   s["th"]),
    ], [
        Paragraph(arch.get("detectedPl", "—"),       s["tdc"]),
        Paragraph(arch.get("detectedCategory", "—"), s["tdc"]),
        Paragraph(arch.get("channelCount", "—"),     s["tdc"]),
        Paragraph(
            "Yes" if arch.get("hasFeedbackMonitoring") is True
            else ("No" if arch.get("hasFeedbackMonitoring") is False else "Unknown"),
            s["tdc"]
        ),
    ]]
    arch_tbl = Table(arch_data, colWidths=[(PAGE_W - 2 * MARGIN) / 4] * 4)
    arch_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GREY),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(arch_tbl)

    arch_summary = arch.get("summary", "")
    if arch_summary:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(arch_summary, s["body"]))
    story.append(Spacer(1, 4 * mm))

    # ── Non-conformances ───────────────────────────────────────────────────────
    if ncs:
        story.append(Paragraph(f"Non-Conformances ({len(ncs)})", s["h2"]))
        story.append(_LimeRule())
        story.append(Spacer(1, 2 * mm))
        story.extend(_finding_table(ncs, s))
        story.append(Spacer(1, 4 * mm))

    # ── Conformances ───────────────────────────────────────────────────────────
    if confs:
        story.append(Paragraph(f"Conformances ({len(confs)})", s["h2"]))
        story.append(_LimeRule())
        story.append(Spacer(1, 2 * mm))
        conf_rows = [[Paragraph("✓ " + c.get("description", ""), s["body"]),
                      Paragraph(c.get("clauseReference", ""), s["clause"])]
                     for c in confs]
        conf_tbl = Table(conf_rows, colWidths=[120 * mm, PAGE_W - 2 * MARGIN - 120 * mm])
        conf_tbl.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(conf_tbl)
        story.append(Spacer(1, 4 * mm))

    # ── Components identified ──────────────────────────────────────────────────
    if comps:
        story.append(Paragraph(f"Components Identified ({len(comps)})", s["h2"]))
        story.append(_LimeRule())
        story.append(Spacer(1, 2 * mm))
        comp_rows = [[
            Paragraph("Component", s["th"]),
            Paragraph("Type", s["th"]),
            Paragraph("Drawing Reference", s["th"]),
        ]]
        for c in comps:
            comp_rows.append([
                Paragraph(c.get("component", "—"), s["td"]),
                Paragraph(c.get("type", "—"), s["td"]),
                Paragraph(c.get("location", "—"), s["td"]),
            ])
        w = PAGE_W - 2 * MARGIN
        comp_tbl = Table(comp_rows, colWidths=[w * 0.35, w * 0.25, w * 0.40])
        comp_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(comp_tbl)

    # ── Redline SLD ────────────────────────────────────────────────────────────
    if svg_diagram:
        story.append(PageBreak())
        story.append(Paragraph("Redline Safety Circuit Diagram", s["h2"]))
        story.append(_LimeRule())
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(
            "Red annotations correspond to numbered non-conformance items above.",
            s["small"]
        ))
        story.append(Spacer(1, 3 * mm))
        try:
            from services.diagram_service import svg_to_rl_drawing
            from reportlab.platypus import Image as RLImage
            drawing = svg_to_rl_drawing(svg_diagram)
            if drawing is not None:
                from reportlab.graphics.shapes import Drawing
                from reportlab.graphics import renderPDF
                # Scale drawing to fit page width
                available_w = PAGE_W - 2 * MARGIN
                scale = available_w / drawing.width
                scaled_h = drawing.height * scale
                drawing.width  = available_w
                drawing.height = scaled_h
                drawing.transform = (scale, 0, 0, scale, 0, 0)
                story.append(drawing)
        except Exception as exc:
            log.warning("Could not embed SLD in PDF: %s", exc)
            story.append(Paragraph("[Redline diagram could not be rendered]", s["small"]))

    # ── Sign-off ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Review Sign-off", s["h2"]))
    story.append(_LimeRule())
    story.append(Spacer(1, 2 * mm))
    signoff_rows = [
        [Paragraph("Reviewed by (CMSE)", s["td"]), Paragraph("", s["td"]),
         Paragraph("Date", s["td"]), Paragraph("", s["td"])],
        [Paragraph("Approved by (Eng Manager)", s["td"]), Paragraph("", s["td"]),
         Paragraph("Date", s["td"]), Paragraph("", s["td"])],
        [Paragraph("Client Acceptance", s["td"]), Paragraph("", s["td"]),
         Paragraph("Date", s["td"]), Paragraph("", s["td"])],
    ]
    w = PAGE_W - 2 * MARGIN
    signoff_tbl = Table(signoff_rows, colWidths=[w * 0.35, w * 0.25, w * 0.15, w * 0.25])
    signoff_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(signoff_tbl)

    doc.build(story)
    return buf.getvalue()


# ── DOCX generator ─────────────────────────────────────────────────────────────

def generate_docx(
    drawing_title: str,
    target_pl: str,
    target_category: str,
    analysis: dict[str, Any],
    svg_diagram: Optional[str] = None,
) -> bytes:
    """
    Generate an editable DOCX compliance report.
    Diagram is referenced as a note — engineer can insert from PDF.
    """
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from lxml import etree

    NAVY_RGB  = RGBColor(0x00, 0x25, 0x59)
    LIME_RGB  = RGBColor(0x70, 0xBF, 0x54)
    RED_RGB   = RGBColor(0xC0, 0x39, 0x2B)
    AMBER_RGB = RGBColor(0xE6, 0x7E, 0x22)
    BLUE_RGB  = RGBColor(0x24, 0x71, 0xA3)
    GREY_RGB  = RGBColor(0x8A, 0x9A, 0xB0)

    SEV_COLOUR: dict[str, RGBColor] = {
        "critical": RED_RGB, "major": AMBER_RGB, "minor": BLUE_RGB,
    }

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin   = Inches(0.9)
        section.right_margin  = Inches(0.9)

    def h1(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(18)
        run.font.color.rgb = NAVY_RGB
        return p

    def h2(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after  = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = NAVY_RGB
        return p

    def body(text: str, italic: bool = False):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_after = Pt(4)
        if italic:
            for run in p.runs:
                run.italic = True
        return p

    def lime_rule():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(4)
        # Add a bottom border to simulate a rule
        pPr = p._p.get_or_add_pPr()
        pBdr = etree.SubElement(pPr, qn("w:pBdr"))
        bottom = etree.SubElement(pBdr, qn("w:bottom"))
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "70BF54")

    def add_kv_row(table, key: str, value: str):
        row = table.add_row()
        row.cells[0].text = key
        row.cells[1].text = value
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = NAVY_RGB

    # ── Header ────────────────────────────────────────────────────────────────
    h1("Drawing Review")
    p_title = doc.add_paragraph()
    run = p_title.add_run(drawing_title)
    run.bold = True
    run.font.size = Pt(13)
    run.font.color.rgb = NAVY_RGB
    lime_rule()

    # ── Meta table ────────────────────────────────────────────────────────────
    meta = doc.add_table(rows=0, cols=4)
    meta.style = "Table Grid"
    add_kv_row_4 = lambda t, k1, v1, k2, v2: (
        t.add_row().cells.__setitem__(0, None) or True  # placeholder
    )

    def add_row4(t, k1, v1, k2, v2):
        row = t.add_row()
        for i, txt in enumerate([k1, v1, k2, v2]):
            cell = row.cells[i]
            cell.text = txt
            r = cell.paragraphs[0].runs[0]
            r.font.size = Pt(9)
            if i in (0, 2):
                r.bold = True
                r.font.color.rgb = NAVY_RGB

    add_row4(meta, "Target PL", target_pl, "Target Category", target_category)
    add_row4(meta, "Review Date", date.today().strftime("%d %b %Y"),
             "Drawing Type", (analysis.get("drawingType") or "—").replace("_", " ").title())

    doc.add_paragraph()

    # ── Verdict ───────────────────────────────────────────────────────────────
    verdict_key   = (analysis.get("overallVerdict") or "non_compliant").lower()
    verdict_label = VERDICT_LABEL.get(verdict_key, "UNKNOWN")
    gap_to = (analysis.get("gapToTarget") or "—").replace("_", " ").title()
    p_v = doc.add_paragraph()
    r_v = p_v.add_run(f"Overall Verdict: {verdict_label}  |  Gap to {target_pl} {target_category}: {gap_to}")
    r_v.bold = True
    r_v.font.size = Pt(11)
    r_v.font.color.rgb = VERDICT_COLOUR.get(verdict_key,
        RGBColor(0xC0, 0x39, 0x2B)) if False else (
        RED_RGB if verdict_key == "non_compliant"
        else (RGBColor(0xF5, 0x7F, 0x17) if verdict_key == "conditionally_compliant"
              else RGBColor(0x2E, 0x7D, 0x32))
    )

    gap_summary = analysis.get("gapSummary", "")
    if gap_summary:
        body(gap_summary)

    # ── Architecture Assessment ────────────────────────────────────────────────
    h2("Architecture Assessment")
    lime_rule()
    arch = analysis.get("architectureAssessment") or {}
    arch_tbl = doc.add_table(rows=2, cols=4)
    arch_tbl.style = "Table Grid"
    headers = ["Detected PL", "Detected Category", "Channels", "Feedback Monitoring"]
    values  = [
        arch.get("detectedPl", "—"),
        arch.get("detectedCategory", "—"),
        arch.get("channelCount", "—"),
        "Yes" if arch.get("hasFeedbackMonitoring") is True
        else ("No" if arch.get("hasFeedbackMonitoring") is False else "Unknown"),
    ]
    for i, (hdr, val) in enumerate(zip(headers, values)):
        hc = arch_tbl.rows[0].cells[i]
        hc.text = hdr
        hc.paragraphs[0].runs[0].bold = True
        hc.paragraphs[0].runs[0].font.color.rgb = NAVY_RGB
        hc.paragraphs[0].runs[0].font.size = Pt(9)
        vc = arch_tbl.rows[1].cells[i]
        vc.text = val
        vc.paragraphs[0].runs[0].font.size = Pt(9)

    arch_summary = arch.get("summary", "")
    if arch_summary:
        doc.add_paragraph()
        body(arch_summary)

    # ── Non-conformances ───────────────────────────────────────────────────────
    ncs = analysis.get("nonConformances") or []
    if ncs:
        h2(f"Non-Conformances ({len(ncs)})")
        lime_rule()
        for nc in ncs:
            sev = (nc.get("severity") or "minor").lower()
            sev_col = SEV_COLOUR.get(sev, BLUE_RGB)
            p_nc = doc.add_paragraph()
            r_sev = p_nc.add_run(f"[{sev.upper()}]  ")
            r_sev.bold = True
            r_sev.font.color.rgb = sev_col
            r_sev.font.size = Pt(9)
            r_desc = p_nc.add_run(nc.get("description", ""))
            r_desc.font.size = Pt(9)
            clause = nc.get("clauseReference", "")
            if clause:
                p_cl = doc.add_paragraph(f"    {clause}")
                p_cl.paragraph_format.space_before = Pt(0)
                p_cl.paragraph_format.space_after  = Pt(2)
                p_cl.runs[0].font.size = Pt(8)
                p_cl.runs[0].italic = True
                p_cl.runs[0].font.color.rgb = GREY_RGB
            remedy = nc.get("remediation", "")
            if remedy:
                p_rem = doc.add_paragraph(f"    → {remedy}")
                p_rem.paragraph_format.space_before = Pt(0)
                p_rem.paragraph_format.space_after  = Pt(6)
                p_rem.runs[0].font.size = Pt(9)

    # ── Conformances ───────────────────────────────────────────────────────────
    confs = analysis.get("conformances") or []
    if confs:
        h2(f"Conformances ({len(confs)})")
        lime_rule()
        for c in confs:
            p_c = doc.add_paragraph()
            r_tick = p_c.add_run("✓  ")
            r_tick.bold = True
            r_tick.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)
            r_c = p_c.add_run(c.get("description", ""))
            r_c.font.size = Pt(9)
            clause = c.get("clauseReference", "")
            if clause:
                p_cl = doc.add_paragraph(f"    {clause}")
                p_cl.paragraph_format.space_before = Pt(0)
                p_cl.paragraph_format.space_after  = Pt(2)
                p_cl.runs[0].font.size = Pt(8)
                p_cl.runs[0].italic = True
                p_cl.runs[0].font.color.rgb = GREY_RGB

    # ── Components identified ──────────────────────────────────────────────────
    comps = analysis.get("componentsIdentified") or []
    if comps:
        h2(f"Components Identified ({len(comps)})")
        lime_rule()
        comp_tbl = doc.add_table(rows=1, cols=3)
        comp_tbl.style = "Table Grid"
        for i, hdr_txt in enumerate(["Component", "Type", "Drawing Reference"]):
            cell = comp_tbl.rows[0].cells[i]
            cell.text = hdr_txt
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = NAVY_RGB
            cell.paragraphs[0].runs[0].font.size = Pt(9)
        for c in comps:
            row = comp_tbl.add_row()
            for i, val in enumerate([c.get("component", "—"), c.get("type", "—"), c.get("location", "—")]):
                row.cells[i].text = val
                row.cells[i].paragraphs[0].runs[0].font.size = Pt(9)

    # ── Diagram note ───────────────────────────────────────────────────────────
    doc.add_page_break()
    h2("Redline Safety Circuit Diagram")
    lime_rule()
    if svg_diagram:
        body(
            "The redline safety circuit diagram is included in the PDF version of this report. "
            "Insert diagram here — refer to the PDF export for the annotated schematic.",
            italic=True
        )
    else:
        body(
            "No DXF topology data was available — redline diagram could not be generated. "
            "Attach the source DXF file and re-analyse to generate the schematic.",
            italic=True
        )

    # ── Sign-off ───────────────────────────────────────────────────────────────
    doc.add_paragraph()
    h2("Review Sign-off")
    lime_rule()
    signoff_tbl = doc.add_table(rows=3, cols=4)
    signoff_tbl.style = "Table Grid"
    signoff_headers = [
        ("Reviewed by (CMSE)", "Signature", "Date", ""),
        ("Approved by (Eng Manager)", "Signature", "Date", ""),
        ("Client Acceptance", "Signature", "Date", ""),
    ]
    for row_data, row in zip(signoff_headers, signoff_tbl.rows):
        for i, txt in enumerate(row_data):
            c = row.cells[i]
            c.text = txt
            if txt:
                c.paragraphs[0].runs[0].font.size = Pt(9)
                if i == 0:
                    c.paragraphs[0].runs[0].bold = True

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
