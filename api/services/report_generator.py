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
    Image as RLImage,
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


def _load_photo(filepath: str) -> bytes | None:
    """Fetch photo bytes from a Spaces URL or local fallback path."""
    try:
        if filepath.startswith("http://") or filepath.startswith("https://"):
            from urllib.parse import quote
            import urllib.request
            # Avoid urlparse — '#' in project numbers (e.g. "Live Test #3") is
            # treated as a fragment delimiter and truncates the path.
            scheme_end = filepath.index("://") + 3
            scheme = filepath[:scheme_end]
            rest = filepath[scheme_end:]
            slash_idx = rest.index("/")
            host = rest[:slash_idx]
            path = rest[slash_idx + 1:]
            encoded_path = "/".join(quote(seg, safe="") for seg in path.split("/"))
            url = f"{scheme}{host}/{encoded_path}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.read()
        else:
            from services.project_store import PHOTOS_DIR
            p = PHOTOS_DIR / filepath
            return p.read_bytes() if p.exists() else None
    except Exception as exc:
        log.warning("Could not load photo %s: %s", filepath, exc)
        return None


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
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, spaceAfter=3),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, textColor=NAVY, spaceBefore=10, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, spaceBefore=6, spaceAfter=3),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=13, textColor=BLACK, spaceAfter=4),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7.5, leading=11, textColor=MID_GREY),
        "ai_flag": ParagraphStyle("ai_flag", fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#334e68"), spaceBefore=2),
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
        _sp(5),
        _LimeRule(),
        _sp(10),
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

    # 7 columns: Task | Hazard | LO | FE | DPH | NP | HRN
    # Total = 174 mm (A4 210 mm − 2 × 18 mm margins)
    # Task and Hazard get most of the width; number cols kept minimal
    # Total = 174 mm (A4 210 mm − 2 × 18 mm margins)
    col_w = [46 * mm, 72 * mm, 10 * mm, 10 * mm, 10 * mm, 10 * mm, 16 * mm]

    RR_GREEN = colors.HexColor("#e8f5e1")

    for h in hazards:
        items.append(Paragraph(f"3.{h.id}  {h.location}", s["h3"]))
        if h.typed_notes:
            items.append(Paragraph(h.typed_notes, s["body"]))

        if h.photos:
            img_bytes = _load_photo(h.photos[0].filepath)
            if img_bytes:
                try:
                    img = RLImage(BytesIO(img_bytes))
                    max_w = PAGE_W - 2 * MARGIN
                    max_h = 80 * mm
                    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
                    img.drawWidth = img.imageWidth * scale
                    img.drawHeight = img.imageHeight * scale
                    items += [img, _sp(3)]
                except Exception:
                    pass

        td = s["td"]
        tc = s["tdc"]
        th = s["th"]

        band_bg = BAND_COLOURS.get(h.risk_band_before, MID_GREY)
        band_txt = BLACK if h.risk_band_before in LIGHT_BANDS else WHITE
        hazard_str = "; ".join(h.hazard_types) if h.hazard_types else "—"

        table_data = [
            # Row 0: Mode title (spans all 7 cols)
            [Paragraph(f"Mode: {h.mode}", th), "", "", "", "", "", ""],
            # Row 1: blank left (cols 0-1) | "Risk Estimation" right (cols 2-6)
            ["", "", Paragraph("Risk Estimation", th), "", "", "", ""],
            # Row 2: Column headers
            [Paragraph("Task", th), Paragraph("Hazard", th),
             Paragraph("LO", th), Paragraph("FE", th),
             Paragraph("DPH", th), Paragraph("NP", th), Paragraph("HRN", th)],
            # Row 3: Before-mitigation data
            [Paragraph(h.task, td), Paragraph(hazard_str, td),
             Paragraph(str(h.hrn_before.LO), tc), Paragraph(str(h.hrn_before.FE), tc),
             Paragraph(str(h.hrn_before.DPH), tc), Paragraph(str(h.hrn_before.NP), tc),
             Paragraph(str(h.hrn_score_before), tc)],
        ]

        cmds = [
            # Global
            ("GRID", (0, 0), (-1, -1), 0.3, MID_GREY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            # Tighter padding on number columns so values like "0.033" fit
            ("LEFTPADDING", (2, 0), (6, -1), 2),
            ("RIGHTPADDING", (2, 0), (6, -1), 2),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            # Row 0 — Mode title
            ("SPAN", (0, 0), (6, 0)),
            ("BACKGROUND", (0, 0), (6, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (6, 0), WHITE),
            ("ALIGN", (0, 0), (6, 0), "CENTER"),
            ("FONTNAME", (0, 0), (6, 0), "Helvetica-Bold"),
            # Row 1 — Risk Estimation sub-header
            ("SPAN", (0, 1), (1, 1)),
            ("SPAN", (2, 1), (6, 1)),
            ("BACKGROUND", (0, 1), (1, 1), WHITE),
            ("BACKGROUND", (2, 1), (6, 1), NAVY),
            ("TEXTCOLOR", (2, 1), (6, 1), WHITE),
            ("ALIGN", (2, 1), (6, 1), "CENTER"),
            ("FONTNAME", (0, 1), (6, 1), "Helvetica-Bold"),
            # Row 2 — Column headers
            ("BACKGROUND", (0, 2), (6, 2), NAVY),
            ("TEXTCOLOR", (0, 2), (6, 2), WHITE),
            ("ALIGN", (0, 2), (6, 2), "CENTER"),
            ("FONTNAME", (0, 2), (6, 2), "Helvetica-Bold"),
            # Row 3 — Data
            ("FONTNAME", (0, 3), (6, 3), "Helvetica"),
            ("ALIGN", (2, 3), (6, 3), "CENTER"),
            ("BACKGROUND", (6, 3), (6, 3), band_bg),
            ("TEXTCOLOR", (6, 3), (6, 3), band_txt),
            ("FONTNAME", (6, 3), (6, 3), "Helvetica-Bold"),
        ]

        has_rr = bool(h.risk_reduction_measures) or (h.hrn_after and h.hrn_score_after is not None)
        if has_rr:
            rr_label_row = len(table_data)   # row 4
            rr_data_row  = rr_label_row + 1  # row 5
            rr_text = "; ".join(h.risk_reduction_measures) if h.risk_reduction_measures else "—"

            # Row 4: "Risk Reduction" (left) | "New Risk Estimation" (right, navy header)
            table_data.append([
                Paragraph("Risk Reduction", td), "",
                Paragraph("New Risk Estimation", th), "", "", "", "",
            ])
            cmds += [
                ("SPAN", (0, rr_label_row), (1, rr_label_row)),
                ("SPAN", (2, rr_label_row), (6, rr_label_row)),
                ("BACKGROUND", (0, rr_label_row), (1, rr_label_row), RR_GREEN),
                ("TEXTCOLOR", (0, rr_label_row), (1, rr_label_row), NAVY),
                ("FONTNAME", (0, rr_label_row), (6, rr_label_row), "Helvetica-Bold"),
                ("BACKGROUND", (2, rr_label_row), (6, rr_label_row), NAVY),
                ("TEXTCOLOR", (2, rr_label_row), (6, rr_label_row), WHITE),
                ("ALIGN", (2, rr_label_row), (6, rr_label_row), "CENTER"),
            ]

            if h.hrn_after and h.hrn_score_after is not None:
                ab_bg = BAND_COLOURS.get(h.risk_band_after or "", MID_GREY)
                ab_txt = BLACK if (h.risk_band_after or "") in LIGHT_BANDS else WHITE

                # Row 5: risk reduction text (spans cols 0-1) + new HRN values
                table_data.append([
                    Paragraph(rr_text, td), "",
                    Paragraph(str(h.hrn_after.LO), tc),
                    Paragraph(str(h.hrn_after.FE), tc),
                    Paragraph(str(h.hrn_after.DPH), tc),
                    Paragraph(str(h.hrn_after.NP), tc),
                    Paragraph(str(h.hrn_score_after), tc),
                ])
                cmds += [
                    ("SPAN", (0, rr_data_row), (1, rr_data_row)),
                    ("BACKGROUND", (0, rr_data_row), (5, rr_data_row), RR_GREEN),
                    ("BACKGROUND", (6, rr_data_row), (6, rr_data_row), ab_bg),
                    ("TEXTCOLOR", (6, rr_data_row), (6, rr_data_row), ab_txt),
                    ("FONTNAME", (6, rr_data_row), (6, rr_data_row), "Helvetica-Bold"),
                    ("ALIGN", (2, rr_data_row), (6, rr_data_row), "CENTER"),
                    ("FONTNAME", (0, rr_data_row), (1, rr_data_row), "Helvetica"),
                ]
            else:
                # No after-HRN yet — just show the risk reduction text full-width
                table_data.append([
                    Paragraph(rr_text, td), "", "", "", "", "", "",
                ])
                cmds += [
                    ("SPAN", (0, rr_data_row), (6, rr_data_row)),
                    ("BACKGROUND", (0, rr_data_row), (6, rr_data_row), RR_GREEN),
                    ("FONTNAME", (0, rr_data_row), (6, rr_data_row), "Helvetica"),
                ]

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
                items.append(Paragraph(f"■ {flag}", s["ai_flag"]))

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
def build_risk_assessment_docx(request: ReportDraftRequest) -> bytes:
    """Generate an editable Word risk assessment report."""
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.oxml.ns import qn
    from lxml import etree

    NAVY_RGB = RGBColor(0x00, 0x25, 0x59)
    LIME_RGB = RGBColor(0x70, 0xBF, 0x54)
    GREY_RGB = RGBColor(0x8A, 0x9A, 0xB0)

    BAND_TEXT: dict[str, RGBColor] = {}
    BAND_BG_HEX = {
        "Acceptable":   "00B050", "Very Low":    "92D050", "Needs Review": "FFA000",
        "Low":          "FFFF00", "Significant": "FFC000", "High":         "FF6600",
        "Very High":    "FF0000", "Extreme":     "CC0000", "Unacceptable": "990000",
    }
    LIGHT_BANDS = {"Acceptable", "Very Low", "Needs Review", "Low"}

    doc = Document()
    for section in doc.sections:
        section.top_margin    = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin   = Inches(0.9)
        section.right_margin  = Inches(0.9)

    def h1(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.bold = True; r.font.size = Pt(18); r.font.color.rgb = NAVY_RGB

    def h2(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.bold = True; r.font.size = Pt(12); r.font.color.rgb = NAVY_RGB

    def h3(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.bold = True; r.font.size = Pt(10); r.font.color.rgb = NAVY_RGB

    def body(text: str):
        p = doc.add_paragraph(text)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
            r.font.size = Pt(9)
        return p

    def lime_rule():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(4)
        pPr = p._p.get_or_add_pPr()
        pBdr = etree.SubElement(pPr, qn("w:pBdr"))
        bottom = etree.SubElement(pBdr, qn("w:bottom"))
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "70BF54")

    def set_cell(cell, text: str, bold: bool = False, size: int = 9,
                 colour: RGBColor = None, bg_hex: str = None, center: bool = False):
        cell.text = text
        r = cell.paragraphs[0].runs[0] if cell.paragraphs[0].runs else cell.paragraphs[0].add_run(text)
        if not cell.paragraphs[0].runs:
            cell.text = ""
            r = cell.paragraphs[0].add_run(text)
        r.bold = bold
        r.font.size = Pt(size)
        if colour:
            r.font.color.rgb = colour
        if bg_hex:
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsmap
            w_ns = nsmap["w"]
            shading = parse_xml(
                f'<w:shd xmlns:w="{w_ns}" w:val="clear" w:color="auto" w:fill="{bg_hex}"/>'
            )
            cell._tc.get_or_add_tcPr().append(shading)
        if center:
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            cell.paragraphs[0].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def set_cell_formula(cell, formula: str, fallback: str, bold: bool = False,
                         size: int = 9, colour: RGBColor = None, bg_hex: str = None):
        """Insert a Word calculation field (=FORMULA) into a cell so the value recalculates."""
        from docx.oxml import parse_xml
        from docx.oxml.ns import nsmap
        w_ns = nsmap["w"]
        sz = size * 2
        if bg_hex:
            shading = parse_xml(
                f'<w:shd xmlns:w="{w_ns}" w:val="clear" w:color="auto" w:fill="{bg_hex}"/>'
            )
            cell._tc.get_or_add_tcPr().append(shading)
        cell.text = ""
        p = cell.paragraphs[0]
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

        b_tag = "<w:b/>" if bold else ""
        col_tag = ""
        if colour:
            col_hex = "%02X%02X%02X" % (colour.red, colour.green, colour.blue)
            col_tag = f'<w:color w:val="{col_hex}"/>'

        def _rpr():
            return f"<w:rPr>{b_tag}<w:sz w:val=\"{sz}\"/>{col_tag}</w:rPr>"

        def _fld(fld_type: str):
            return parse_xml(
                f'<w:r xmlns:w="{w_ns}">{_rpr()}'
                f'<w:fldChar w:fldCharType="{fld_type}"/></w:r>'
            )

        def _instr(text: str):
            return parse_xml(
                f'<w:r xmlns:w="{w_ns}">{_rpr()}'
                f'<w:instrText xml:space="preserve" xmlns:w="{w_ns}"> {text} </w:instrText></w:r>'
            )

        def _cached(text: str):
            return parse_xml(
                f'<w:r xmlns:w="{w_ns}">{_rpr()}<w:t>{text}</w:t></w:r>'
            )

        p._p.append(_fld("begin"))
        p._p.append(_instr(formula))
        p._p.append(_fld("separate"))
        p._p.append(_cached(fallback))
        p._p.append(_fld("end"))

    b = request.project_brief

    # ── Cover ─────────────────────────────────────────────────────────────────
    h1("Risk Assessment Report")
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run(f"{b.project_number} — {b.machine_or_line}")
    r_sub.bold = True; r_sub.font.size = Pt(13); r_sub.font.color.rgb = NAVY_RGB
    lime_rule()

    meta = doc.add_table(rows=0, cols=2)
    meta.style = "Table Grid"
    for k, v in [("Client", b.client), ("Site", b.site),
                  ("Machine / Line", b.machine_or_line),
                  ("Assessment Date", str(b.assessment_date)),
                  ("Project Number", b.project_number)]:
        row = meta.add_row()
        set_cell(row.cells[0], k, bold=True, colour=NAVY_RGB)
        set_cell(row.cells[1], str(v))
    doc.add_paragraph()

    if b.scope_description:
        h2("Scope")
        lime_rule()
        body(b.scope_description)

    # ── Hazards ───────────────────────────────────────────────────────────────
    h2(f"Risk Analysis — {len(request.hazards)} Hazard(s)")
    lime_rule()

    WHITE_RGB = RGBColor(0xFF, 0xFF, 0xFF)
    RR_GREEN_HEX = "E8F5E1"
    NAVY_HEX = "002559"

    for h in request.hazards:
        h3(f"{h.id}  {h.location}")
        if h.typed_notes:
            body(h.typed_notes)

        if h.photos:
            img_bytes = _load_photo(h.photos[0].filepath)
            if img_bytes:
                try:
                    doc.add_picture(BytesIO(img_bytes), width=Inches(5))
                    doc.add_paragraph()
                except Exception:
                    pass

        # 7-column table matching the MEX report layout
        detail = doc.add_table(rows=4, cols=7)
        detail.style = "Table Grid"

        # Fix column widths via XML — tblW + tblGrid + tblLayout (fixed)
        # This is the reliable path; cell.width alone doesn't stick after merges
        from docx.oxml import parse_xml as _px
        from docx.oxml.ns import nsmap as _nsmap, qn as _qn
        _col_mm = [44, 68, 9, 9, 9, 9, 15]
        _col_tw = [round(w * 1440 / 25.4) for w in _col_mm]  # mm → twips
        _total_tw = sum(_col_tw)
        _wns = _nsmap["w"]

        # tblW — total table width
        _tblPr = detail._tbl.tblPr
        for _el in _tblPr.findall(_qn("w:tblW")):
            _tblPr.remove(_el)
        _tblPr.append(_px(f'<w:tblW xmlns:w="{_wns}" w:w="{_total_tw}" w:type="dxa"/>'))

        # tblLayout fixed
        for _el in _tblPr.findall(_qn("w:tblLayout")):
            _tblPr.remove(_el)
        _tblPr.append(_px(f'<w:tblLayout xmlns:w="{_wns}" w:type="fixed"/>'))

        # tblGrid — one gridCol per column; must sit right after tblPr
        _existing_grid = detail._tbl.find(_qn("w:tblGrid"))
        if _existing_grid is not None:
            detail._tbl.remove(_existing_grid)
        _grid_xml = (
            f'<w:tblGrid xmlns:w="{_wns}">'
            + "".join(f'<w:gridCol w:w="{tw}"/>' for tw in _col_tw)
            + "</w:tblGrid>"
        )
        _tblPr_idx = list(detail._tbl).index(_tblPr)
        detail._tbl.insert(_tblPr_idx + 1, _px(_grid_xml))

        # tcW on every cell in every row (set before any merges)
        for _row in detail.rows:
            for _ci, _tw in enumerate(_col_tw):
                _tc = _row.cells[_ci]._tc
                _tcPr = _tc.get_or_add_tcPr()
                for _el in _tcPr.findall(_qn("w:tcW")):
                    _tcPr.remove(_el)
                _tcPr.append(_px(f'<w:tcW xmlns:w="{_wns}" w:w="{_tw}" w:type="dxa"/>'))

        # Row 0: "Mode: {mode}" spanning all 7 columns
        r0 = detail.rows[0]
        r0.cells[0].merge(r0.cells[6])
        set_cell(r0.cells[0], f"Mode: {h.mode}", bold=True, size=8,
                 bg_hex=NAVY_HEX, colour=WHITE_RGB, center=True)

        # Row 1: blank left (cols 0-1) | "Risk Estimation" right (cols 2-6)
        r1 = detail.rows[1]
        r1.cells[0].merge(r1.cells[1])
        r1.cells[2].merge(r1.cells[6])
        set_cell(r1.cells[0], "", size=8)
        set_cell(r1.cells[2], "Risk Estimation", bold=True, size=8,
                 bg_hex=NAVY_HEX, colour=WHITE_RGB, center=True)

        # Row 2: Column headers
        r2 = detail.rows[2]
        for i, hdr in enumerate(["Task", "Hazard", "LO", "FE", "DPH", "NP", "HRN"]):
            set_cell(r2.cells[i], hdr, bold=True, size=8,
                     bg_hex=NAVY_HEX, colour=WHITE_RGB, center=(i >= 2))

        # Row 3: Before-mitigation data (Word row 4 — 1-indexed)
        r3 = detail.rows[3]
        hrn = h.hrn_before
        band = h.risk_band_before
        band_hex = BAND_BG_HEX.get(band, "CCCCCC")
        hz_types = "; ".join(h.hazard_types) if h.hazard_types else "—"
        data_vals = [h.task, hz_types,
                     str(hrn.LO), str(hrn.FE), str(hrn.DPH), str(hrn.NP)]
        for i, val in enumerate(data_vals):
            set_cell(r3.cells[i], val, size=8, center=(i >= 2))
        # HRN cell (col G, Word row 4): dynamic formula
        set_cell_formula(
            r3.cells[6],
            formula="=C4*D4*E4*F4",
            fallback=str(h.hrn_score_before),
            bold=True, size=8,
            bg_hex=band_hex,
        )

        # Rows 4-5: Risk Reduction if present
        has_rr = bool(h.risk_reduction_measures) or (h.hrn_after and h.hrn_score_after is not None)
        if has_rr:
            rr_text = "; ".join(h.risk_reduction_measures) if h.risk_reduction_measures else "—"

            # Row 4: "Risk Reduction" | "New Risk Estimation"
            rr_label = detail.add_row()
            rr_label.cells[0].merge(rr_label.cells[1])
            rr_label.cells[2].merge(rr_label.cells[6])
            set_cell(rr_label.cells[0], "Risk Reduction", bold=True, size=8,
                     bg_hex=RR_GREEN_HEX, colour=NAVY_RGB)
            set_cell(rr_label.cells[2], "New Risk Estimation", bold=True, size=8,
                     bg_hex=NAVY_HEX, colour=WHITE_RGB, center=True)

            if h.hrn_after and h.hrn_score_after is not None:
                ab_hex = BAND_BG_HEX.get(h.risk_band_after or "", "CCCCCC")

                # Row 5: risk reduction text (cols 0-1) + new HRN values (Word row 6)
                rr_data = detail.add_row()
                rr_data.cells[0].merge(rr_data.cells[1])
                set_cell(rr_data.cells[0], rr_text, size=8, bg_hex=RR_GREEN_HEX)
                new_vals = [str(h.hrn_after.LO), str(h.hrn_after.FE),
                            str(h.hrn_after.DPH), str(h.hrn_after.NP)]
                for i, val in enumerate(new_vals):
                    set_cell(rr_data.cells[i + 2], val, size=8,
                             bg_hex=RR_GREEN_HEX, center=True)
                # HRN cell (col G, Word row 6): dynamic formula
                set_cell_formula(
                    rr_data.cells[6],
                    formula="=C6*D6*E6*F6",
                    fallback=str(h.hrn_score_after),
                    bold=True, size=8,
                    bg_hex=ab_hex,
                )
            else:
                # Risk reduction noted but no after-HRN yet
                rr_data = detail.add_row()
                rr_data.cells[0].merge(rr_data.cells[6])
                set_cell(rr_data.cells[0], rr_text, size=8, bg_hex=RR_GREEN_HEX)

        doc.add_paragraph()

    # ── Sign-off ──────────────────────────────────────────────────────────────
    h2("Review Sign-off")
    lime_rule()
    signoff = doc.add_table(rows=4, cols=4)
    signoff.style = "Table Grid"
    headers_row = ["Role", "Name", "Signature", "Date"]
    for i, hdr in enumerate(headers_row):
        set_cell(signoff.rows[0].cells[i], hdr, bold=True, colour=NAVY_RGB, size=9)
    for role in ["Reviewed by (CMSE)", "Approved by (Eng Manager)", "Client Acceptance"]:
        row = signoff.add_row()
        set_cell(row.cells[0], role, bold=True, size=9)
        for c in row.cells[1:]:
            c.text = ""

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


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
