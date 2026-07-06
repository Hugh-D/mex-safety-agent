"""
Generate MEX Safety Platform — API Key Setup Guide
Output: docs/team-api-key-setup.pdf
Run: python docs/generate_setup_guide.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
import os

# ── Brand colours ──────────────────────────────────────────────
NAVY      = colors.HexColor("#002559")
MID_BLUE  = colors.HexColor("#1a4a8a")
ACCENT    = colors.HexColor("#2e7dd1")
LIGHT     = colors.HexColor("#c8d8ea")
BG        = colors.HexColor("#f6f8fb")
TEXT      = colors.HexColor("#102a43")
MUTED     = colors.HexColor("#6b8299")
CODE_BG   = colors.HexColor("#0f1e30")
CODE_FG   = colors.HexColor("#a8d4ff")
CODE_VAL  = colors.HexColor("#a8e6a3")
GREEN     = colors.HexColor("#2e8b57")
GREEN_BG  = colors.HexColor("#eaf5ee")
AMBER     = colors.HexColor("#b45309")
AMBER_BG  = colors.HexColor("#fef3c7")
WHITE     = colors.white

W, H = A4  # 595.27 x 841.89 pts
MARGIN = 22 * mm

OUT = os.path.join(os.path.dirname(__file__), "team-api-key-setup.pdf")


# ── Page canvas (header + footer) ─────────────────────────────
def draw_page(c: canvas.Canvas, doc):
    c.saveState()

    # ── Top header bar ──
    bar_h = 52
    c.setFillColor(NAVY)
    c.rect(0, H - bar_h, W, bar_h, fill=1, stroke=0)

    # Logo box
    c.setFillColor(WHITE)
    c.roundRect(MARGIN, H - bar_h + 10, 52, 30, 4, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 8, H - bar_h + 20, "MEX")

    # Header text
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN + 64, H - bar_h + 26, "API Key Setup Guide")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN + 64, H - bar_h + 13, "MEX Safety Platform — Team Onboarding · May 2026")

    # ── Bottom footer bar ──
    foot_h = 28
    c.setFillColor(NAVY)
    c.rect(0, 0, W, foot_h, fill=1, stroke=0)
    c.setFillColor(LIGHT)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, 10, "MEX Engineering Group  ·  mexeng.com.au")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    page_w = c.stringWidth("MEX Safety Platform v1.0", "Helvetica-Bold", 8)
    c.drawString(W - MARGIN - page_w, 10, "MEX Safety Platform v1.0")

    c.restoreState()


# ── Styles ─────────────────────────────────────────────────────
def styles():
    return {
        "intro": ParagraphStyle("intro", fontName="Helvetica", fontSize=11, leading=17, textColor=TEXT),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=13,
                                  textColor=NAVY, leading=18, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=15, textColor=TEXT),
        "muted": ParagraphStyle("muted", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=10, leading=14,
                               textColor=CODE_VAL, backColor=CODE_BG,
                               leftIndent=8, rightIndent=8, spaceBefore=2, spaceAfter=2),
        "step_num": ParagraphStyle("step_num", fontName="Helvetica-Bold", fontSize=10,
                                   textColor=WHITE, leading=14, alignment=TA_CENTER),
    }


def step_table(steps, s):
    """Build a numbered-steps table for one platform."""
    rows = []
    for num, (desc, code) in enumerate(steps, 1):
        num_cell = Paragraph(str(num), s["step_num"])
        if code:
            content = [Paragraph(desc, s["body"]), Spacer(1, 4),
                       Paragraph(code, s["code"])]
        else:
            content = [Paragraph(desc, s["body"])]
        rows.append([num_cell, content])

    t = Table(rows, colWidths=[20, None])
    t.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND",  (0, 0), (0, -1), NAVY),
        ("ROUNDEDCORNERS", [4]),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [BG, WHITE]),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (0, -1), 4),
        ("RIGHTPADDING", (0, 0), (0, -1), 4),
        ("LEFTPADDING", (1, 0), (1, -1), 10),
        ("RIGHTPADDING", (1, 0), (1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LIGHT),
    ]))
    return t


def platform_card(title, subtitle, badge, steps, s, col_w):
    badge_style = ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=9,
                                 textColor=WHITE, backColor=NAVY, leading=13,
                                 borderPadding=(3, 8, 3, 8))
    header = Table(
        [[Paragraph(badge, badge_style), Paragraph(title, s["section"])]],
        colWidths=[60, col_w - 70]
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    inner = [
        header,
        Paragraph(subtitle, s["muted"]),
        Spacer(1, 8),
        step_table(steps, s),
    ]

    outer = Table([[inner]], colWidths=[col_w])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 1, LIGHT),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))
    return outer


def build():
    doc = BaseDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=60,
        bottomMargin=38,
        title="MEX Safety Platform — API Key Setup Guide",
        author="MEX Engineering Group",
    )
    frame = Frame(MARGIN, 38, W - 2 * MARGIN, H - 98, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_page)])

    s = styles()
    story = []
    col_w = (W - 2 * MARGIN - 10) / 2  # two-column width

    # ── Intro box ──
    intro_data = [[
        Paragraph(
            "Each team member gets a <b>personal API key</b> that authenticates your device "
            "with the MEX Safety Platform API. Follow the steps for your platform, then confirm "
            "with Buzzy that your key appears in the table below.",
            s["intro"]
        )
    ]]
    intro = Table(intro_data, colWidths=[W - 2 * MARGIN])
    intro.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WHITE),
        ("LINEAFTER",     (0, 0), (0, -1), 4, ACCENT),    # left accent stripe via right-of-prev col
        ("LINEBEFORE",    (0, 0), (0, -1), 4, ACCENT),
        ("BOX",           (0, 0), (-1, -1), 1, LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(intro)
    story.append(Spacer(1, 14))

    # ── Two platform cards ──
    web_steps = [
        ("Open the project folder and navigate to <b>apps/web/</b>", None),
        ("Create a new file called <b>.env.local</b> (note the leading dot)", None),
        ("Paste exactly this line — replace with your assigned key:",
         "VITE_API_KEY=mex-yourname-2026"),
        ("Save the file and restart the dev server: npm run dev", None),
    ]
    mob_steps = [
        ("Open the project folder and navigate to <b>apps/mobile/</b>", None),
        ("Open the <b>existing</b> file <b>.env</b> (do not create a new one)", None),
        ("Find and replace the placeholder with your assigned key:",
         "EXPO_PUBLIC_API_KEY=mex-yourname-2026"),
        ("Save and restart Expo: npx expo start --web", None),
    ]

    web_card = platform_card("Web (Desktop)", "apps/web/.env.local",
                             "  WEB APP  ", web_steps, s, col_w)
    mob_card = platform_card("Mobile (Expo)", "apps/mobile/.env",
                             "  MOBILE   ", mob_steps, s, col_w)

    cards = Table([[web_card, mob_card]], colWidths=[col_w, col_w], hAlign="LEFT",
                  spaceBefore=0, spaceAfter=14,
                  style=[("LEFTPADDING", (1, 0), (1, -1), 10),
                         ("RIGHTPADDING", (0, 0), (0, -1), 10),
                         ("VALIGN", (0, 0), (-1, -1), "TOP")])
    story.append(KeepTogether(cards))
    story.append(Spacer(1, 4))

    # ── Key registry table ──
    story.append(KeepTogether([
        Paragraph("Team Key Registry", s["section"]),
        Paragraph("Use the key assigned to your name exactly as shown — no spaces, all lowercase", s["muted"]),
        Spacer(1, 8),
        _key_table(s),
        Spacer(1, 14),
    ]))

    # ── Notice row ──
    notices = Table([
        [
            _notice("HOW IT WORKS", GREEN, GREEN_BG,
                    "Your key is sent as an X-API-Key header with every request. "
                    "The server checks it against the approved list and returns 403 if it doesn't match.",
                    s),
            _notice("KEEP IT PRIVATE", AMBER, AMBER_BG,
                    ".env.local and .env are in .gitignore — never commit them. "
                    "Don't share your key in Slack or email. Contact Buzzy if you think it's been exposed.",
                    s),
        ]
    ], colWidths=[col_w, col_w],
       style=[("LEFTPADDING", (1, 0), (1, -1), 10),
              ("RIGHTPADDING", (0, 0), (0, -1), 10),
              ("VALIGN", (0, 0), (-1, -1), "TOP")])
    story.append(notices)

    doc.build(story)
    print(f"Done. Written: {OUT}")


def _key_table(s):
    header = ["Name", "API Key", "Platform"]
    rows = [
        ["Eion",          "mex-eion-2026",  "Web"],
        ["Jie",           "mex-jie-2026",   "Mobile"],
        ["Buzzy (admin)", "mex-admin-2026", "Both"],
    ]
    tag_colours = {"Web": (colors.HexColor("#dbeafe"), colors.HexColor("#1e40af")),
                   "Mobile": (colors.HexColor("#ede9fe"), colors.HexColor("#5b21b6")),
                   "Both": (GREEN_BG, GREEN)}

    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle("th", fontName="Helvetica-Bold",
             fontSize=9, textColor=MUTED, leading=13)) for h in header]]
    for name, key, platform in rows:
        bg, fg = tag_colours[platform]
        tag_style = ParagraphStyle("tag", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=fg, backColor=bg, leading=13,
                                   borderPadding=(2, 6, 2, 6))
        data.append([
            Paragraph(f"<b>{name}</b>", ParagraphStyle("name", fontName="Helvetica-Bold",
                      fontSize=10, textColor=NAVY, leading=14)),
            Paragraph(key, ParagraphStyle("key", fontName="Courier", fontSize=10,
                      textColor=CODE_VAL, backColor=CODE_BG, leading=14,
                      borderPadding=(3, 8, 3, 8))),
            Paragraph(platform, tag_style),
        ])

    col_w_total = W - 2 * MARGIN
    t = Table(data, colWidths=[col_w_total * 0.3, col_w_total * 0.45, col_w_total * 0.25])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BG),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.5, LIGHT),
        ("LINEBELOW",     (0, 1), (-1, -2), 0.5, LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOX",           (0, 0), (-1, -1), 1, LIGHT),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return t


def _notice(title, border_colour, bg_colour, text, s):
    head = Paragraph(title, ParagraphStyle("nh", fontName="Helvetica-Bold", fontSize=9,
                     textColor=border_colour, leading=13, spaceAfter=4))
    body = Paragraph(text, ParagraphStyle("nb", fontName="Helvetica", fontSize=9,
                     textColor=TEXT, leading=14))
    inner = Table([[head], [body]], colWidths=[None])
    inner.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    outer = Table([[inner]], colWidths=[None])
    outer.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), bg_colour),
        ("LINEBEFORE",  (0, 0), (0, -1), 4, border_colour),
        ("BOX",         (0, 0), (-1, -1), 0.5, border_colour),
        ("TOPPADDING",  (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return outer


if __name__ == "__main__":
    build()
