from __future__ import annotations

import os
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable

from models.schemas import HazardEntry, ReportDraftRequest, SafetyFunctionSpec

import logging
log = logging.getLogger(__name__)


def _audit_complete() -> bool:
    """Return True only when AUDIT_COMPLETE env var is explicitly set to a truthy value."""
    return os.environ.get("AUDIT_COMPLETE", "").strip().lower() in ("1", "true", "yes")


def _draw_draft_watermark(canvas) -> None:
    """Draw a diagonal DRAFT watermark across the current page."""
    canvas.saveState()
    canvas.translate(PAGE_W / 2, PAGE_H / 2)
    canvas.rotate(45)
    canvas.setFillColor(colors.Color(0.8, 0, 0, alpha=0.12))
    canvas.setFont("Helvetica-Bold", 72)
    canvas.drawCentredString(0, 20, "DRAFT")
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(0, -20, "STANDARDS AUDIT INCOMPLETE")
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Brand constants
# ---------------------------------------------------------------------------
NAVY = colors.HexColor("#002559")
LIME = colors.HexColor("#70bf54")
LIGHT_GREY = colors.HexColor("#f2f4f7")
MID_GREY = colors.HexColor("#8a9ab0")
WHITE = colors.white
BLACK = colors.black

MARGIN = 18 * mm
FOOTER_H = 14 * mm
HEADER_H = 16 * mm
PAGE_W, PAGE_H = A4

BAND_COLOURS: dict[str, colors.HexColor] = {
    "Acceptable": colors.HexColor("#00B050"),
    "Very Low": colors.HexColor("#92D050"),
    "Needs Review": colors.HexColor("#FFA000"),
    "Low": colors.HexColor("#FFFF00"),
    "Significant": colors.HexColor("#FFC000"),
    "High": colors.HexColor("#FF6600"),
    "Very High": colors.HexColor("#FF0000"),
    "Extreme": colors.HexColor("#CC0000"),
    "Unacceptable": colors.HexColor("#990000"),
}
LIGHT_BANDS = {"Acceptable", "Very Low", "Needs Review", "Low"}

CONTACT_LINE = (
    "1800 MEX 24/7  |  PO Box 6425 Silverwater NSW 2128  |  admin@mexeng.com.au"
    "  |  Lic 141260C  |  ABN 68 101 789 584  |  mexeng.com.au"
)


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def _build_styles() -> dict:
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, textColor=NAVY, spaceBefore=10, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceBefore=6, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=13, textColor=BLACK, spaceAfter=4),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7.5, leading=11, textColor=MID_GREY),
        "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, alignment=TA_CENTER),
        "td": ParagraphStyle("td", fontName="Helvetica", fontSize=8, leading=10, textColor=BLACK),
        "tdc": ParagraphStyle("tdc", fontName="Helvetica", fontSize=8, leading=10, textColor=BLACK, alignment=TA_CENTER),
        "cover_label": ParagraphStyle("cover_label", fontName="Helvetica", fontSize=10, textColor=MID_GREY),
        "cover_value": ParagraphStyle("cover_value", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY, spaceAfter=6),
    }


# ---------------------------------------------------------------------------
# Page callbacks
# ---------------------------------------------------------------------------
def _page_header_footer(canvas, doc):
    if not _audit_complete():
        _draw_draft_watermark(canvas)

    canvas.saveState()

    # Navy header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(MARGIN, PAGE_H - HEADER_H + 4.5 * mm, "MEX Engineering Group")
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(LIME)
    title = getattr(doc, "_report_title", "Risk Assessment")
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - HEADER_H + 4.5 * mm, title)

    # Lime rule under header
    canvas.setStrokeColor(LIME)
    canvas.setLineWidth(1.5)
    canvas.line(0, PAGE_H - HEADER_H - 1, PAGE_W, PAGE_H - HEADER_H - 1)

    # Footer rule + text
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(PAGE_W / 2, FOOTER_H - 3.5 * mm, CONTACT_LINE)
    canvas.drawCentredString(PAGE_W / 2, FOOTER_H - 7 * mm, f"Page {doc.page}")

    canvas.restoreState()


def _cover_page(canvas, doc):
    if not _audit_complete():
        _draw_draft_watermark(canvas)

    canvas.saveState()

    # Full-bleed navy band
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 68 * mm, PAGE_W, 68 * mm, fill=1, stroke=0)
    # Lime accent stripe
    canvas.setFillColor(LIME)
    canvas.rect(0, PAGE_H - 70 * mm, PAGE_W, 2 * mm, fill=1, stroke=0)

    # Wordmark
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawString(MARGIN, PAGE_H - 34 * mm, "MEX Engineering Group")
    canvas.setFont("Helvetica", 11)
    canvas.setFillColor(LIME)
    canvas.drawString(MARGIN, PAGE_H - 42 * mm, "mexeng.com.au  |  1800 MEX 24/7")

    # Footer
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(PAGE_W / 2, FOOTER_H - 3.5 * mm, CONTACT_LINE)

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Helper flowable — coloured rule
# ---------------------------------------------------------------------------
class _LimeRule(Flowable):
    def __init__(self, width: float = PAGE_W - 2 * MARGIN):
        super().__init__()
        self.width = width
        self.height = 1.5

    def draw(self):
        self.canv.setStrokeColor(LIME)
        self.canv.setLineWidth(1.5)
        self.canv.line(0, 0, self.width, 0)


def _sp(h: float = 4) -> Spacer:
    return Spacer(1, h * mm)


def _base_table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.3, MID_GREY),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ])


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------
def _section_cover(req: ReportDraftRequest, s: dict) -> list:
    b = req.project_brief
    return [
        _sp(72),  # clear the navy band
        Paragraph("Risk Assessment Report", s["h1"]),
        _LimeRule(),
        _sp(6),
        Paragraph("Client", s["cover_label"]),
        Paragraph(b.client, s["cover_value"]),
        Paragraph("Site", s["cover_label"]),
        Paragraph(b.site, s["cover_value"]),
        Paragraph("Machine / Line", s["cover_label"]),
        Paragraph(b.machine_or_line, s["cover_value"]),
        Paragraph("Project Number", s["cover_label"]),
        Paragraph(b.project_number, s["cover_value"]),
        Paragraph("Assessment Date", s["cover_label"]),
        Paragraph(str(b.assessment_date), s["cover_value"]),
    ]


def _section_project(req: ReportDraftRequest, s: dict) -> list:
    b = req.project_brief
    items: list = [
        Paragraph("1. Project Details", s["h2"]),
        _LimeRule(),
        _sp(),
    ]

    cw = (PAGE_W - 2 * MARGIN) / 4
    info = Table([
        ["Project Number", b.project_number, "Client", b.client],
        ["Site", b.site, "Machine / Line", b.machine_or_line],
        ["Assessment Date", str(b.assessment_date), "", ""],
    ], colWidths=[cw] * 4)
    info.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (2, 0), (2, -1), NAVY),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    items.append(info)
    items.append(_sp(5))

    if b.scope_description:
        items += [Paragraph("Scope", s["h3"]), Paragraph(b.scope_description, s["body"]), _sp()]

    if b.team:
        items.append(Paragraph("Assessment Team", s["h3"]))
        cw3 = (PAGE_W - 2 * MARGIN) / 3
        t = Table(
            [["Name", "Company", "Role"]] + [[m.name, m.company, m.role] for m in b.team],
            colWidths=[cw3] * 3,
        )
        t.setStyle(_base_table_style())
        items += [t, _sp()]

    if b.standards_applicable:
        items.append(Paragraph("Applicable Standards", s["h3"]))
        for std in b.standards_applicable:
            items.append(Paragraph(f"• {std}", s["body"]))

    return items


def _section_methodology(s: dict) -> list:
    items: list = [
        Paragraph("2. Risk Assessment Methodology", s["h2"]),
        _LimeRule(),
        _sp(),
        Paragraph("2.1 HRN Method", s["h3"]),
        Paragraph(
            "Hazard Rating Number (HRN) is calculated using the inductive (bottom-up) "
            "preliminary hazard analysis method per <b>AS/NZS 4024.1201</b>. Each hazard "
            "is evaluated using four independent parameters: <b>HRN = LO × FE × DPH × NP</b>. "
            "An HRN ≤ 5 is considered acceptable.",
            s["body"],
        ),
        _sp(3),
    ]

    # HRN parameter reference tables (two columns)
    params = [
        ("LO — Likelihood of Occurrence", [
            ("0.033", "Almost impossible"), ("1", "Highly unlikely"),
            ("1.5", "Unlikely"), ("2", "Possible"), ("5", "Even chance"),
            ("8", "Probable"), ("10", "Likely"), ("15", "Certain"),
        ]),
        ("FE — Frequency of Exposure", [
            ("0.5", "Annually"), ("1", "Monthly"), ("1.5", "Weekly"),
            ("2.5", "Daily"), ("4", "Hourly"), ("5", "Constantly"),
        ]),
        ("DPH — Degree of Possible Harm", [
            ("0.1", "Scratch / bruise"),
            ("0.5", "Laceration / mild ill health"),
            ("1", "Minor bone fracture (fingers/toes)"),
            ("2", "Major bone fracture (hand/arm/leg)"),
            ("4", "Loss of 1–2 fingers/toes"),
            ("8", "Amputation / partial loss of hearing or sight"),
            ("10", "Amputation of 2 limbs / total hearing or sight loss"),
            ("12", "Critical or permanent illness"),
            ("15", "Fatality"),
        ]),
        ("NP — Number of Persons at Risk", [
            ("1", "1–2 persons"), ("2", "3–7 persons"),
            ("4", "8–15 persons"), ("8", "16–50 persons"),
            ("12", "More than 50 persons"),
        ]),
    ]
    tw = (PAGE_W - 2 * MARGIN)
    cv, cl = 14 * mm, tw - 14 * mm

    for title, rows in params:
        items.append(Paragraph(title, s["h3"]))
        t = Table([["Value", "Description"]] + list(rows), colWidths=[cv, cl])
        t.setStyle(_base_table_style())
        items += [t, _sp(3)]

    # Risk band table
    items += [Paragraph("2.2 Risk Bands", s["h3"])]
    band_rows = [
        ("0 – 1", "Acceptable", True, "#00B050"),
        ("1 – 4", "Very Low", True, "#92D050"),
        ("4 – 6", "Needs Review", False, "#FFA000"),
        ("6 – 10", "Low", False, "#FFFF00"),
        ("10 – 50", "Significant", False, "#FFC000"),
        ("50 – 100", "High", False, "#FF6600"),
        ("100 – 500", "Very High", False, "#FF0000"),
        ("500 – 1000", "Extreme", False, "#CC0000"),
        ("> 1000", "Unacceptable", False, "#990000"),
    ]
    band_data = [["HRN Range", "Risk Band", "Acceptable"]]
    band_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, MID_GREY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, (rng, label, ok, hex_col) in enumerate(band_rows, 1):
        band_data.append([rng, label, "Yes" if ok else "No"])
        bg = colors.HexColor(hex_col)
        txt = BLACK if label in LIGHT_BANDS else WHITE
        band_cmds += [("BACKGROUND", (1, i), (1, i), bg), ("TEXTCOLOR", (1, i), (1, i), txt)]

    bw = (PAGE_W - 2 * MARGIN) / 3
    bt = Table(band_data, colWidths=[bw, bw, bw])
    bt.setStyle(TableStyle(band_cmds))
    items.append(bt)
    return items


def _section_hazards(hazards: List[HazardEntry], s: dict) -> list:
    items: list = [
        Paragraph("3. Risk Analysis", s["h2"]),
        _LimeRule(),
        _sp(),
    ]
    if not hazards:
        items.append(Paragraph("No hazards recorded.", s["body"]))
        return items

    tw = PAGE_W - 2 * MARGIN
    col_w = [22 * mm, 30 * mm, 40 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 14 * mm, tw - 146 * mm]

    for h in hazards:
        items.append(Paragraph(f"3.{h.id}  {h.location}", s["h3"]))
        if h.typed_notes:
            items.append(Paragraph(h.typed_notes, s["body"]))

        th = s["th"]
        td = s["td"]
        tc = s["tdc"]
        hdr = [Paragraph(x, th) for x in ["Mode", "Task", "Hazard Types", "LO", "FE", "DPH", "NP", "HRN", "Risk Band"]]
        hazard_types_str = ", ".join(h.hazard_types) if h.hazard_types else "—"
        row1 = [
            Paragraph(h.mode, td),
            Paragraph(h.task, td),
            Paragraph(hazard_types_str, td),
            Paragraph(str(h.hrn_before.LO), tc),
            Paragraph(str(h.hrn_before.FE), tc),
            Paragraph(str(h.hrn_before.DPH), tc),
            Paragraph(str(h.hrn_before.NP), tc),
            Paragraph(str(h.hrn_score_before), tc),
            Paragraph(h.risk_band_before, tc),
        ]

        band_bg = BAND_COLOURS.get(h.risk_band_before, MID_GREY)
        band_txt = BLACK if h.risk_band_before in LIGHT_BANDS else WHITE

        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.3, MID_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (7, 1), (8, 1), band_bg),
            ("TEXTCOLOR", (7, 1), (8, 1), band_txt),
        ]
        table_data = [hdr, row1]

        if h.risk_reduction_measures:
            rr = "; ".join(h.risk_reduction_measures)
            table_data.append([
                Paragraph("<b>Risk Reduction</b>", td),
                Paragraph(rr, td),
                "", "", "", "", "", "", "",
            ])
            cmds += [
                ("SPAN", (1, 2), (8, 2)),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#e8f5e1")),
            ]

        if h.hrn_after and h.hrn_score_after is not None:
            ab_bg = BAND_COLOURS.get(h.risk_band_after or "", MID_GREY)
            ab_txt = BLACK if (h.risk_band_after or "") in LIGHT_BANDS else WHITE
            ri = len(table_data)
            table_data.append([
                Paragraph("<b>After mitigation</b>", td),
                Paragraph("Post-control HRN", td),
                Paragraph("", td),
                Paragraph(str(h.hrn_after.LO), tc),
                Paragraph(str(h.hrn_after.FE), tc),
                Paragraph(str(h.hrn_after.DPH), tc),
                Paragraph(str(h.hrn_after.NP), tc),
                Paragraph(str(h.hrn_score_after), tc),
                Paragraph(h.risk_band_after or "—", tc),
            ])
            cmds += [("BACKGROUND", (7, ri), (8, ri), ab_bg), ("TEXTCOLOR", (7, ri), (8, ri), ab_txt)]

        t = Table(table_data, colWidths=col_w)
        t.setStyle(TableStyle(cmds))
        items.append(t)

        if h.standards_references:
            items.append(Paragraph("Standards: " + "  |  ".join(h.standards_references), s["small"]))
        if h.ai_recommendations:
            items.append(Paragraph("AI Recommendations:", s["body"]))
            for rec in h.ai_recommendations:
                items.append(Paragraph(f"• {rec}", s["body"]))
        if h.ai_validation_flags:
            for flag in h.ai_validation_flags:
                items.append(Paragraph(f"⚠ {flag}", s["small"]))

        items.append(_sp(5))

    return items


def _section_safety_functions(functions: Optional[List[SafetyFunctionSpec]], s: dict) -> list:
    if not functions:
        return []

    items: list = [
        Paragraph("4. Safety Functions & Performance Level", s["h2"]),
        _LimeRule(),
        _sp(),
        Paragraph(
            "Required Performance Level (PLr) is determined per the ISO 13849-1 risk graph "
            "using severity (S), frequency (F), and avoidance (P) parameters.",
            s["body"],
        ),
        _sp(3),
    ]

    tw = PAGE_W - 2 * MARGIN
    cw = [tw * r for r in [0.24, 0.08, 0.10, 0.07, 0.07, 0.07, 0.15, 0.22]]
    hdrs = ["Safety Function", "PLr", "Category", "S", "F", "P", "Source Hazards", "Notes"]
    data = [[Paragraph(h, s["th"]) for h in hdrs]]

    for fn in functions:
        data.append([
            Paragraph(fn.function_name, s["td"]),
            Paragraph(fn.plr_required, s["tdc"]),
            Paragraph(fn.category_required, s["tdc"]),
            Paragraph(fn.severity, s["tdc"]),
            Paragraph(fn.frequency, s["tdc"]),
            Paragraph(fn.avoidance, s["tdc"]),
            Paragraph(", ".join(fn.source_hazard_ids), s["td"]),
            Paragraph(fn.notes or "—", s["td"]),
        ])

    t = Table(data, colWidths=cw)
    t.setStyle(_base_table_style())
    items.append(t)
    return items


def _section_conclusion(ai_result: Optional[dict], fallback_notes: Optional[str], s: dict) -> list:
    items: list = [
        Paragraph("5. Conclusion", s["h2"]),
        _LimeRule(),
        _sp(),
    ]

    if ai_result:
        # Main conclusion paragraphs
        for para in ai_result.get("conclusion_text", "").split("\n\n"):
            para = para.strip()
            if para:
                items += [Paragraph(para, s["body"]), _sp(2)]

        # Immediate actions box
        immediate = ai_result.get("immediate_actions_required", [])
        if immediate:
            items += [_sp(2), Paragraph("Immediate Actions Required", s["h3"])]
            for action in immediate:
                items.append(Paragraph(f"• {action}", s["body"]))

        # Follow-up actions
        follow_up = ai_result.get("follow_up_actions", [])
        if follow_up:
            items += [_sp(2), Paragraph("Follow-up Actions", s["h3"])]
            for action in follow_up:
                items.append(Paragraph(f"• {action}", s["body"]))

        # Overall PLr recommendation
        plr = ai_result.get("overall_plr_recommendation", "")
        if plr:
            items += [
                _sp(2),
                Paragraph(f"Overall PLr Recommendation: {plr}", s["h3"]),
            ]
    else:
        body = fallback_notes or (
            "This risk assessment identifies the hazards present at the assessed machine or "
            "production line and provides HRN scores and recommended risk reduction measures. "
            "All hazards with HRN > 5 require corrective action before the machine is deemed "
            "safe for continued operation. Refer to the Safety Functions section for required "
            "Performance Level targets per ISO 13849-1."
        )
        items.append(Paragraph(body, s["body"]))

    items += [
        _sp(4),
        Paragraph(
            "This report was prepared by MEX Engineering Group. The findings and recommendations "
            "are based on conditions observed at the time of the assessment. MEX Engineering Group "
            "accepts no liability for changes to site conditions after the assessment date.",
            s["small"],
        ),
    ]
    return items


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def build_risk_assessment_pdf(request: ReportDraftRequest) -> bytes:
    buffer = BytesIO()
    s = _build_styles()

    usable_h = PAGE_H - HEADER_H - FOOTER_H - 6 * mm
    cover_frame = Frame(MARGIN, FOOTER_H + 2 * mm, PAGE_W - 2 * MARGIN, PAGE_H - FOOTER_H - 4 * mm, id="cover")
    body_frame = Frame(MARGIN, FOOTER_H + 2 * mm, PAGE_W - 2 * MARGIN, usable_h, id="body")

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=HEADER_H + 4 * mm, bottomMargin=FOOTER_H + 4 * mm,
    )
    b = request.project_brief
    doc._report_title = f"{b.project_number} — {b.machine_or_line}"

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=_cover_page),
        PageTemplate(id="body", frames=[body_frame], onPage=_page_header_footer),
    ])

    story: list = []
    story += _section_cover(request, s)
    story += [NextPageTemplate("body"), PageBreak()]

    story += _section_project(request, s)
    story.append(PageBreak())

    story += _section_methodology(s)
    story.append(PageBreak())

    story += _section_hazards(request.hazards, s)

    if request.safety_functions:
        story.append(PageBreak())
        story += _section_safety_functions(request.safety_functions, s)

    # AI conclusion synthesis — skip if notes already provided
    ai_conclusion: Optional[dict] = None
    if not request.notes and request.hazards:
        try:
            from services.claude_service import synthesise_conclusion
            ai_conclusion, ai_log = synthesise_conclusion(
                request.project_brief,
                request.hazards,
                request.safety_functions,
            )
            log.info("AI audit (conclusion): %s", ai_log.model_dump_json())
        except Exception as exc:
            log.warning("Conclusion synthesis failed, using fallback: %s", exc)

    story.append(PageBreak())
    story += _section_conclusion(ai_conclusion, request.notes, s)

    doc.build(story)
    return buffer.getvalue()
