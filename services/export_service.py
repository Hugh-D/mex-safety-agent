"""
PDF export service — MEX Safety Agent
Generates the branded redline compliance report PDF.
"""

import datetime
import io
import logging
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.platypus import Flowable
from reportlab.graphics import renderPDF
from models import ExportRequest
from services.diagram_service import generate_diagram_drawing

logger = logging.getLogger(__name__)

# ── Brand colours ──────────────────────────────────────────────────────────────
NAVY      = HexColor('#002559')
BLUE1     = HexColor('#1d4382')
LIME      = HexColor('#70bf54')
LIME2     = HexColor('#bdd747')
RED       = HexColor('#C0392B')
AMBER     = HexColor('#E67E22')
INFO_BLUE = HexColor('#2471A3')
MID_GREY  = HexColor('#566573')
LIGHT_RED = HexColor('#FDEDEC')
LIGHT_AMB = HexColor('#FEF9E7')
LIGHT_BLU = HexColor('#EAF4FB')
LIGHT_GRN = HexColor('#EAFAF1')
LIGHT_GRY = HexColor('#F2F3F4')
BORDER    = HexColor('#BFC9CA')
WHITE     = colors.white
W, H      = A4


# ── Styles ─────────────────────────────────────────────────────────────────────
def make_styles():
    def s(name, **kw):
        return ParagraphStyle(name, **kw)
    return {
        'section':    s('section',    fontName='Helvetica-Bold', fontSize=10,
                        textColor=NAVY, leading=14, spaceBefore=8, spaceAfter=3),
        'body':       s('body',       fontName='Helvetica', fontSize=9,
                        textColor=HexColor('#2C3E50'), leading=14, spaceAfter=3),
        'action':     s('action',     fontName='Helvetica-Oblique', fontSize=8.5,
                        textColor=NAVY, leading=13),
        'ref':        s('ref',        fontName='Helvetica', fontSize=7.5,
                        textColor=MID_GREY, leading=11),
        'small':      s('small',      fontName='Helvetica', fontSize=8,
                        textColor=MID_GREY, leading=12),
        'table_hdr':  s('table_hdr',  fontName='Helvetica-Bold', fontSize=8,
                        textColor=WHITE, leading=11),
        'table_cell': s('table_cell', fontName='Helvetica', fontSize=8,
                        textColor=HexColor('#2C3E50'), leading=12),
        'table_cb':   s('table_cb',   fontName='Helvetica-Bold', fontSize=8,
                        textColor=HexColor('#2C3E50'), leading=12),
    }


ST = make_styles()


class CoverBlock(Flowable):
    def __init__(self, width, project_number, machine, status, target_pl, target_cat):
        self.bw = width
        self.bh = 88 * mm
        self.project_number = project_number
        self.machine = machine
        self.status = status
        self.target_pl = target_pl
        self.target_cat = target_cat

    def wrap(self, *a):
        return self.bw, self.bh

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.rect(0, 0, self.bw, self.bh, fill=1, stroke=0)
        c.setFillColor(LIME)
        c.rect(0, self.bh - 5, self.bw, 5, fill=1, stroke=0)

        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(WHITE)
        c.drawString(14*mm, self.bh - 22*mm, 'MEX Engineering Group')
        c.setFont('Helvetica', 8)
        c.setFillColor(HexColor('#AEB6BF'))
        c.drawString(14*mm, self.bh - 28*mm, 'mexeng.com.au  ·  Machine Safety Division')

        c.setStrokeColor(HexColor('#1d4382'))
        c.setLineWidth(0.5)
        c.line(14*mm, self.bh - 32*mm, self.bw - 14*mm, self.bh - 32*mm)

        c.setFont('Helvetica-Bold', 19)
        c.setFillColor(WHITE)
        c.drawString(14*mm, self.bh - 46*mm, 'Compliance Review Report')
        c.setFont('Helvetica-Bold', 12)
        c.setFillColor(LIME2)
        c.drawString(14*mm, self.bh - 56*mm,
                     f'{self.project_number}  ·  {self.machine}')

        status_upper = self.status.upper()
        badge_color  = RED if self.status == "fail" else (AMBER if self.status == "warn" else HexColor('#1E8449'))
        c.setFillColor(badge_color)
        c.roundRect(14*mm, self.bh - 69*mm, 40*mm, 8*mm, 2, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(WHITE)
        c.drawString(16*mm, self.bh - 65.5*mm,
                     'NON-COMPLIANT' if self.status == 'fail' else
                     'REVIEW REQUIRED' if self.status == 'warn' else 'COMPLIANT')

        today = datetime.date.today().strftime('%d %B %Y')
        c.setFont('Helvetica', 8)
        c.setFillColor(HexColor('#AEB6BF'))
        c.drawString(14*mm, self.bh - 77*mm, f'Issue date: {today}')
        c.drawString(14*mm, self.bh - 83*mm,
                     f'Target: {self.target_pl} / Category {self.target_cat}  ·  '
                     f'AS4024 · ISO 13849-1:2015 · IEC 61800-5-2')


class ColorBar(Flowable):
    def __init__(self, width, height=1.5, color=NAVY):
        self.bw = width; self.bh = height; self.color = color
    def wrap(self, *a): return self.bw, self.bh + 2
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.bw, self.bh, fill=1, stroke=0)


def _to_list(val) -> list:
    """Normalise to list — accept list or prose string, split into sentences."""
    if isinstance(val, list):
        return [str(s).strip() for s in val if str(s).strip()]
    text = str(val or '').strip()
    if not text:
        return []
    # Split on sentence boundaries (period/!/? followed by space + capital)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [p.strip() for p in parts if p.strip()]


def bullet_paragraphs(val, style) -> list:
    """Story-level: returns one Paragraph per point, bulleted if >1 point."""
    parts = _to_list(val)
    if not parts:
        return [Paragraph('', style)]
    if len(parts) == 1:
        return [Paragraph(parts[0], style)]
    bs = ParagraphStyle('bullet_body', parent=style, leftIndent=10, spaceBefore=1, spaceAfter=1)
    return [Paragraph(f'\u2022\u2002{p}', bs) for p in parts]


def bullet_paragraph_inline(val, style) -> Paragraph:
    """Table-cell: single Paragraph with <br/> separating bullet points."""
    parts = _to_list(val)
    if not parts:
        return Paragraph('', style)
    if len(parts) == 1:
        return Paragraph(parts[0], style)
    joined = '<br/>'.join(f'\u2022\u2002{p}' for p in parts)
    return Paragraph(joined, style)


def priority_colors(p):
    return {
        'CRITICAL': (RED,       LIGHT_RED),
        'MAJOR':    (AMBER,     LIGHT_AMB),
        'MINOR':    (INFO_BLUE, LIGHT_BLU),
    }.get(p.upper(), (MID_GREY, LIGHT_GRY))


def change_card(ch: dict) -> KeepTogether:
    pc, bg = priority_colors(ch['priority'])
    num    = ch['id']
    pri    = ch['priority'].upper()
    desc   = ch.get('description', '')
    # description may be a list — first item is used as the header title
    desc_parts = _to_list(desc)
    title  = (desc_parts[0] if desc_parts else '')[:80]
    ref    = ch.get('reference', '')
    action = ch.get('action', '')

    hdr_data = [[
        Paragraph(f'<font color="white"><b>{num}</b></font>',
                  ParagraphStyle('bn', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=WHITE, alignment=TA_CENTER)),
        Paragraph(f'<b>{pri}</b>  ·  {title}',
                  ParagraphStyle('bt', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=WHITE, leading=13)),
    ]]
    hdr_tbl = Table(hdr_data, colWidths=[9*mm, None])
    hdr_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), pc),
        ('VALIGN',     (0,0),(-1,-1), 'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1), 4),
        ('RIGHTPADDING',(0,0),(-1,-1), 6),
        ('TOPPADDING', (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ]))

    body_tbl = Table([[bullet_paragraph_inline(desc, ST['body'])]], colWidths=[None])
    body_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), bg),
        ('LEFTPADDING',(0,0),(-1,-1), 7),
        ('RIGHTPADDING',(0,0),(-1,-1), 7),
        ('TOPPADDING', (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ]))

    ref_tbl = Table([[Paragraph(f'<b>Standard ref:</b> {ref}', ST['ref'])]], colWidths=[None])
    ref_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), bg),
        ('LEFTPADDING',(0,0),(-1,-1), 7),
        ('RIGHTPADDING',(0,0),(-1,-1), 7),
        ('TOPPADDING', (0,0),(-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ('LINEABOVE',(0,0),(-1,0), 0.3, BORDER),
    ]))

    act_tbl = Table([[Paragraph(f'<b>Redline action:</b> {action}', ST['action'])]], colWidths=[None])
    act_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), WHITE),
        ('LEFTPADDING',(0,0),(-1,-1), 7),
        ('RIGHTPADDING',(0,0),(-1,-1), 7),
        ('TOPPADDING', (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LINEABOVE',(0,0),(-1,0), 0.5, pc),
        ('LINEBEFORE',(0,0),(0,-1), 3, pc),
    ]))

    return KeepTogether([hdr_tbl, body_tbl, ref_tbl, act_tbl, Spacer(1, 5)])


def add_footer(canvas, doc, project_number):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(MID_GREY)
    canvas.drawString(18*mm, 10*mm,
        f'MEX Engineering Group  ·  {project_number} Compliance Review  ·  '
        f'CONFIDENTIAL  ·  {datetime.date.today().strftime("%d %b %Y")}')
    canvas.drawRightString(W - 18*mm, 10*mm, f'Page {doc.page}')
    canvas.setStrokeColor(LIME)
    canvas.setLineWidth(1.5)
    canvas.line(18*mm, 13*mm, W - 18*mm, 13*mm)
    canvas.restoreState()


def generate_pdf(req: ExportRequest) -> bytes:
    """Build and return the redline report as PDF bytes."""
    buf = io.BytesIO()
    project = req.project
    review  = req.review_result
    pn      = project.project_number

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=12*mm, bottomMargin=18*mm,
        title=f'{pn} Compliance Review',
        author='MEX Engineering Group',
    )

    page_w = W - 36*mm
    story  = []

    # Cover
    story.append(CoverBlock(
        page_w,
        project_number=pn,
        machine=project.machine,
        status=review.overall_status,
        target_pl=project.target_pl,
        target_cat=project.target_category,
    ))
    story.append(Spacer(1, 8*mm))

    # Summary stats
    story.append(Paragraph('Review summary', ST['section']))
    story.append(ColorBar(page_w))
    story.append(Spacer(1, 3))

    critical_count = sum(1 for c in review.changes if c.priority.upper() == 'CRITICAL')
    major_count    = sum(1 for c in review.changes if c.priority.upper() == 'MAJOR')
    minor_count    = sum(1 for c in review.changes if c.priority.upper() == 'MINOR')
    status_label   = {'fail':'Non-compliant','warn':'Review required','pass':'Compliant'}.get(
                        review.overall_status, review.overall_status)

    stats = [
        [Paragraph('<b>Project</b>',  ST['table_hdr']),
         Paragraph('<b>Machine</b>',  ST['table_hdr']),
         Paragraph('<b>Target</b>',   ST['table_hdr']),
         Paragraph('<b>Status</b>',   ST['table_hdr']),
         Paragraph('<b>Findings</b>', ST['table_hdr'])],
        [Paragraph(pn, ST['table_cell']),
         Paragraph(project.machine, ST['table_cell']),
         Paragraph(f'{project.target_pl} / Cat {project.target_category}', ST['table_cell']),
         Paragraph(f'<font color="#C0392B"><b>{status_label}</b></font>'
                   if review.overall_status == 'fail'
                   else f'<b>{status_label}</b>', ST['table_cb']),
         Paragraph(
             f'<font color="#C0392B"><b>{critical_count} Critical</b></font>  '
             f'{major_count} Major  {minor_count} Minor', ST['table_cell'])],
    ]
    stats_tbl = Table(stats, colWidths=[28*mm, 42*mm, 22*mm, 28*mm, None])
    stats_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), NAVY),
        ('BACKGROUND',(0,1),(-1,1), LIGHT_GRY),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('GRID',(0,0),(-1,-1),0.3,BORDER),
    ]))
    story.append(stats_tbl)
    story.append(Spacer(1, 4))
    story.extend(bullet_paragraphs(review.summary, ST['body']))
    story.append(Spacer(1, 5*mm))

    # PL achievability
    story.append(Paragraph('Performance level assessment', ST['section']))
    story.append(ColorBar(page_w))
    story.append(Spacer(1, 3))
    pl_status = 'Achievable' if review.pl_achievable else 'Not achievable with current design'
    pl_color  = '#1E8449' if review.pl_achievable else '#C0392B'
    pl_data = [[
        Paragraph(f'<font color="{pl_color}"><b>{project.target_pl} / Cat {project.target_category}: {pl_status}</b></font>',
                  ST['table_cb']),
    ],[
        bullet_paragraph_inline(review.pl_reasoning, ST['body']),
    ]]
    pl_tbl = Table(pl_data, colWidths=[None])
    pl_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), LIGHT_GRN if review.pl_achievable else LIGHT_RED),
        ('BACKGROUND',(0,1),(-1,1), LIGHT_GRY),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('GRID',(0,0),(-1,-1),0.3,BORDER),
    ]))
    story.append(pl_tbl)
    story.append(Spacer(1, 5*mm))

    # Change items grouped by priority
    story.append(Paragraph('Required changes — redline markup', ST['section']))
    story.append(ColorBar(page_w))
    story.append(Spacer(1, 3))

    for priority in ['CRITICAL', 'MAJOR', 'MINOR']:
        items = [c for c in review.changes if c.priority.upper() == priority]
        if not items:
            continue
        pc, _ = priority_colors(priority)
        story.append(Paragraph(
            f'<font color="#{pc.hexval()[2:]}"><b>{priority} ({len(items)})</b></font>',
            ParagraphStyle('pl', fontName='Helvetica-Bold', fontSize=9,
                           leading=13, spaceBefore=6, spaceAfter=3,
                           textColor=pc)))
        for item in items:
            story.append(change_card(item.__dict__ if hasattr(item, '__dict__') else item))

    story.append(Spacer(1, 4*mm))

    # Equipment notes
    if review.equipment_notes:
        story.append(Paragraph('Equipment compliance summary', ST['section']))
        story.append(ColorBar(page_w))
        story.append(Spacer(1, 3))

        eq_hdr = [Paragraph(h, ST['table_hdr'])
                  for h in ['Device', 'Status', 'Note']]
        eq_data = [eq_hdr]
        eq_style = [
            ('BACKGROUND',(0,0),(-1,0), NAVY),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',(0,0),(-1,-1),6),
            ('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),4),
            ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('GRID',(0,0),(-1,-1),0.3,BORDER),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, LIGHT_GRY]),
        ]
        status_col = {'ok': (LIGHT_GRN, HexColor('#196F3D')),
                      'warn': (LIGHT_AMB, HexColor('#784212')),
                      'fail': (LIGHT_RED, RED)}
        for i, en in enumerate(review.equipment_notes):
            st_val = (en.status if hasattr(en, 'status') else en.get('status','ok')).lower()
            bg, tc = status_col.get(st_val, (LIGHT_GRY, MID_GREY))
            item_str = en.item if hasattr(en, 'item') else en.get('item','')
            note_str = en.note if hasattr(en, 'note') else en.get('note','')
            row = [
                Paragraph(item_str, ST['table_cell']),
                Paragraph(f'<font color="white"><b>{st_val.upper()}</b></font>',
                          ParagraphStyle('s', fontName='Helvetica-Bold', fontSize=8,
                                         textColor=WHITE, alignment=TA_CENTER)),
                Paragraph(note_str, ST['table_cell']),
            ]
            eq_data.append(row)
            eq_style.append(('BACKGROUND',(1,i+1),(1,i+1), tc))

        eq_tbl = Table(eq_data, colWidths=[40*mm, 18*mm, None])
        eq_tbl.setStyle(TableStyle(eq_style))
        story.append(eq_tbl)
        story.append(Spacer(1, 5*mm))

    # Redline diagram — always starts on a fresh page so scaling is predictable
    parse_result = req.parse_result if hasattr(req, 'parse_result') else None
    logger.info("Export: parse_result present=%s, components=%s",
                parse_result is not None,
                len(parse_result.components) if parse_result else 0)
    if parse_result and parse_result.components:
        story.append(PageBreak())
        story.append(Paragraph('Redline safety circuit diagram', ST['section']))
        story.append(ColorBar(page_w))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            'The diagram below shows the safety circuit topology as identified from the '
            'electrical drawings. Red annotations correspond to the numbered change items above.',
            ST['body']))
        story.append(Spacer(1, 4))

        drawing = generate_diagram_drawing(parse_result, review)
        if drawing is not None:
            # Scale to fill page width; constrain by available height if needed.
            # SVG is vector so upscaling is fine.
            max_h = H - 75*mm   # ~222mm safe usable height on a fresh page
            scale = page_w / drawing.width if drawing.width > 0 else 1
            if drawing.height * scale > max_h:
                scale = max_h / drawing.height if drawing.height > 0 else 1
            drawing.width  *= scale
            drawing.height *= scale
            drawing.transform = (scale, 0, 0, scale, 0, 0)
            story.append(drawing)
        else:
            story.append(Paragraph(
                'Diagram could not be generated for this drawing set.',
                ST['small']))
        story.append(Spacer(1, 5*mm))

    # Sign-off — always on its own page for a clean formal document
    story.append(PageBreak())
    story.append(Paragraph('Review sign-off', ST['section']))
    story.append(ColorBar(page_w))
    story.append(Spacer(1, 3))
    so_hdr = [Paragraph(h, ST['table_hdr'])
              for h in ['Role', 'Name', 'Signature', 'Date']]
    so_data = [so_hdr] + [
        [Paragraph(r, ST['table_cell']), Paragraph('', ST['table_cell']),
         Paragraph('', ST['table_cell']), Paragraph('', ST['table_cell'])]
        for r in ['Reviewed by (CMSE)', 'Approved by (Engineering Manager)', 'Client acceptance']
    ]
    so_tbl = Table(so_data, colWidths=[52*mm, 44*mm, 44*mm, 26*mm])
    so_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), NAVY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE, LIGHT_GRY]),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,1),(-1,-1),10),
        ('BOTTOMPADDING',(0,1),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,0),5),
        ('BOTTOMPADDING',(0,0),(-1,0),5),
        ('GRID',(0,0),(-1,-1),0.3,BORDER),
    ]))
    story.append(so_tbl)
    story.append(Spacer(1,4*mm))
    story.append(Paragraph(
        'This report is issued by MEX Engineering Group for engineering review purposes. '
        'All redline actions must be implemented and verified by a qualified electrical engineer '
        'before final PL certification can be claimed.',
        ST['small']))

    pn_ref = pn
    doc.build(
        story,
        onFirstPage=lambda c, d: add_footer(c, d, pn_ref),
        onLaterPages=lambda c, d: add_footer(c, d, pn_ref),
    )

    buf.seek(0)
    return buf.read()
