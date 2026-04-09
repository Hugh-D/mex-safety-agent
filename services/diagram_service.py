"""
Diagram service — MEX Safety Agent
Generates a programmatic SVG safety circuit diagram with redline markup.
No Claude API call — layout and annotations are built deterministically.

SLD mode (Phase 2): used when parse_result contains connection topology data.
  - Power rails (+24VDC / 0VDC)
  - Series wires between safety inputs (left column)
  - Bus-and-stub inter-column wiring with terminal labels from connection data
  - Dashed amber feedback/monitoring paths
  - Column labels: SAFETY INPUTS | SAFETY RELAY / PLC | OUTPUT CONTACTS

Block diagram mode (fallback): used when no connection data is available.
  - 3-column layout, simple midpoint arrows between columns
"""

import io
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

# ── SVG layout constants ───────────────────────────────────────────────────────
SVG_W      = 500                  # matches A4 usable width (~493pt) so scale ≈ 1
COL_X      = [10, 185, 360]      # left edge of boxes for each column
BOX_W      = 130
BOX_H      = 32
BOX_GAP    = 10
COMP_Y0    = 92                   # y of first component row
TITLE_H    = 52                   # height of title / header area
COL_HDR_H  = 28                   # column header strip height
LEGEND_H   = 36                   # legend strip at bottom
MIN_H      = 320
MAX_H      = 900      # tall enough for ladder diagrams; export_service scales to fit page

BADGE_R    = 9                    # redline circled-number radius

# ── Colours ────────────────────────────────────────────────────────────────────
C_NAVY  = "#002559"
C_NAVY2 = "#1d4382"
C_LIME  = "#70bf54"
C_RED   = "#C0392B"
C_AMBER = "#E67E22"
C_WHITE = "#FFFFFF"
C_GREY  = "#566573"
C_LGREY = "#ECF0F1"
C_BG    = "#F8F9FA"

# ── Column definitions ─────────────────────────────────────────────────────────
COLUMN_LABELS = [
    "E-STOP INPUTS",
    "SAFETY RELAY / RESET",
    "OUTPUTS / PLC / CONTACTORS",
]

# ── SLD-specific constants (legacy block diagram) ─────────────────────────────
SLD_RAIL_H  = 11
SLD_BUS_OFS = 13
SLD_COL_LABELS = ["SAFETY INPUTS", "SAFETY RELAY / PLC", "OUTPUT CONTACTS"]
CHAIN_GAP = 14

# ── Ladder diagram constants ───────────────────────────────────────────────────
LDR_L_X          = 24      # left power rail x
LDR_R_X          = 476     # right power rail x
LDR_RUNG_PITCH   = 48      # base vertical pitch between rungs
LDR_SECTION_GAP  = 22      # extra y before each section's first rung
LDR_CONTACT_PITCH = 36     # horizontal pitch per inline contact
LDR_CW           = 7       # contact bar half-width
LDR_CH           = 9       # contact bar half-height
LDR_COIL_R       = 11      # output coil circle radius
LDR_COIL_BW      = 24      # coil box half-width (relay/PLC rectangle)
LDR_COIL_BH      = 16      # coil box height
LDR_COIL_CX      = 444     # coil symbol centre x  (LDR_R_X - LDR_COIL_BW - 8)
LDR_LBL_FS       = 6.5     # inline label font size

# Maps ParsedComponent.type -> column index (None = skip / don't render)
TYPE_TO_COL = {
    "estop":          0,
    "safety_switch":  0,
    "light_curtain":  0,
    "scanner":        0,
    "safety_relay":   1,
    "safety_plc":     1,
    "contactor":      2,
    "vfd":            2,
    "unknown":        2,
    "terminal":       None,
}

# Colours for the priority badge on a change-number circle
PRIORITY_COLOUR = {
    "CRITICAL": C_RED,
    "MAJOR":    C_AMBER,
    "MINOR":    "#2471A3",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _g(obj, attr, default=""):
    """Get attribute from a Pydantic model or dict."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _xe(s: str) -> str:
    """Escape XML special characters."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _trunc(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + "\u2026"


def _type_to_col(device_type) -> int | None:
    # Handle both raw strings and str-enum instances (ComponentType)
    val = device_type.value if hasattr(device_type, "value") else str(device_type)
    return TYPE_TO_COL.get(val.lower(), 2)


def _priority(change) -> str:
    return str(_g(change, "priority", "MINOR")).upper()


# ── Change-to-component mapping ────────────────────────────────────────────────

def _map_changes_to_components(components: list, changes: list) -> dict[str, list]:
    """
    Returns {comp_id: [change_id, ...]} by scanning each change's description
    and action text for component IDs and label fragments.
    """
    result: dict[str, list] = defaultdict(list)

    for ch in changes:
        ch_id = _g(ch, "id", 0)
        desc  = _g(ch, "description", "")
        desc  = " ".join(desc) if isinstance(desc, list) else desc
        text  = (desc + " " + _g(ch, "action", "")).upper()

        for comp in components:
            cid   = str(_g(comp, "id",    "")).strip()
            label = str(_g(comp, "label", "")).strip()
            model = str(_g(comp, "model", "") or "").strip()

            matched = False
            if cid and re.search(r'\b' + re.escape(cid.upper()) + r'\b', text):
                matched = True
            elif label and len(label) >= 4 and label.upper() in text:
                matched = True
            elif model and len(model) >= 4 and model.upper() in text:
                matched = True

            if matched and ch_id not in result[cid]:
                result[cid].append(ch_id)

    return dict(result)


# ── IEC 60617-inspired symbol drawing ─────────────────────────────────────────
# Each function draws into a 26×26 viewport centred at (cx, cy).

SYM_W = 28   # symbol zone width (left side of each box); text starts at x + SYM_W + 4


def _sym_estop(cx: int, cy: int) -> str:
    """Mushroom-head e-stop: IEC 60617 — red cap + stem + NC contact (two bars + diagonal)."""
    return (
        # Mushroom cap (red filled ellipse)
        f'<ellipse cx="{cx}" cy="{cy - 8}" rx="10" ry="5" '
        f'fill="{C_RED}" stroke="#8B0000" stroke-width="0.8"/>'
        # Stem
        f'<line x1="{cx}" y1="{cy - 3}" x2="{cx}" y2="{cy + 1}" '
        f'stroke="#555555" stroke-width="2.5"/>'
        # IEC NC contact: top terminal line
        f'<line x1="{cx - 7}" y1="{cy + 2}" x2="{cx + 7}" y2="{cy + 2}" '
        f'stroke="{C_NAVY}" stroke-width="1.5"/>'
        # IEC NC contact: actuator diagonal (top-left to bottom-right)
        f'<line x1="{cx - 5}" y1="{cy + 2}" x2="{cx + 5}" y2="{cy + 10}" '
        f'stroke="{C_NAVY}" stroke-width="1.2"/>'
        # IEC NC contact: bottom terminal line
        f'<line x1="{cx - 7}" y1="{cy + 10}" x2="{cx + 7}" y2="{cy + 10}" '
        f'stroke="{C_NAVY}" stroke-width="1.5"/>'
    )


def _sym_safety_switch(cx: int, cy: int) -> str:
    """Interlocked guard switch: actuator key + NC contact."""
    return (
        # Key shaft
        f'<rect x="{cx - 7}" y="{cy - 10}" width="5" height="12" rx="2" '
        f'fill="{C_NAVY2}" stroke="{C_NAVY}" stroke-width="1"/>'
        # Key bit
        f'<rect x="{cx - 7}" y="{cy - 2}" width="8" height="4" rx="1" '
        f'fill="{C_NAVY2}"/>'
        # NC contact bar
        f'<line x1="{cx - 1}" y1="{cy + 6}" x2="{cx + 9}" y2="{cy + 6}" '
        f'stroke="{C_NAVY}" stroke-width="1.5"/>'
        f'<line x1="{cx + 1}" y1="{cy + 2}" x2="{cx + 8}" y2="{cy + 10}" '
        f'stroke="{C_NAVY}" stroke-width="1.2"/>'
    )


def _sym_light_curtain(cx: int, cy: int) -> str:
    """Light curtain: two vertical bars with arrows between."""
    return (
        # Left emitter bar
        f'<rect x="{cx - 11}" y="{cy - 10}" width="4" height="20" rx="1" '
        f'fill="{C_NAVY}" stroke="{C_NAVY}" stroke-width="0.5"/>'
        # Right receiver bar
        f'<rect x="{cx + 7}" y="{cy - 10}" width="4" height="20" rx="1" '
        f'fill="{C_NAVY2}" stroke="{C_NAVY}" stroke-width="0.5"/>'
        # Beam arrows (3 horizontal dashed lines)
        f'<line x1="{cx - 7}" y1="{cy - 5}" x2="{cx + 7}" y2="{cy - 5}" '
        f'stroke="{C_LIME}" stroke-width="1" stroke-dasharray="2,2"/>'
        f'<line x1="{cx - 7}" y1="{cy}" x2="{cx + 7}" y2="{cy}" '
        f'stroke="{C_LIME}" stroke-width="1" stroke-dasharray="2,2"/>'
        f'<line x1="{cx - 7}" y1="{cy + 5}" x2="{cx + 7}" y2="{cy + 5}" '
        f'stroke="{C_LIME}" stroke-width="1" stroke-dasharray="2,2"/>'
    )


def _sym_scanner(cx: int, cy: int) -> str:
    """Laser scanner: fan-shaped scan sector."""
    return (
        # Scanner body (small circle)
        f'<circle cx="{cx}" cy="{cy + 6}" r="5" '
        f'fill="{C_NAVY}" stroke="{C_NAVY}" stroke-width="0.5"/>'
        # Scan sector (arc approximated by two lines)
        f'<line x1="{cx}" y1="{cy + 6}" x2="{cx - 12}" y2="{cy - 8}" '
        f'stroke="{C_LIME}" stroke-width="1.2"/>'
        f'<line x1="{cx}" y1="{cy + 6}" x2="{cx + 12}" y2="{cy - 8}" '
        f'stroke="{C_LIME}" stroke-width="1.2"/>'
        # Arc top
        f'<path d="M {cx - 12} {cy - 8} Q {cx} {cy - 16} {cx + 12} {cy - 8}" '
        f'fill="none" stroke="{C_LIME}" stroke-width="1" stroke-dasharray="2,2"/>'
    )


def _sym_safety_relay(cx: int, cy: int) -> str:
    """Safety relay: coil rectangle with 'K' designation and dual contacts."""
    return (
        # Relay coil rectangle (IEC style)
        f'<rect x="{cx - 10}" y="{cy - 8}" width="20" height="10" rx="1" '
        f'fill="none" stroke="{C_NAVY}" stroke-width="1.5"/>'
        # Coil terminal lines
        f'<line x1="{cx - 10}" y1="{cy - 3}" x2="{cx - 14}" y2="{cy - 3}" '
        f'stroke="{C_NAVY}" stroke-width="1.2"/>'
        f'<line x1="{cx + 10}" y1="{cy - 3}" x2="{cx + 14}" y2="{cy - 3}" '
        f'stroke="{C_NAVY}" stroke-width="1.2"/>'
        # S label inside coil (S = Safety relay designation per IEC)
        f'<text x="{cx}" y="{cy - 1}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="6.5" font-weight="bold" fill="{C_NAVY}" text-anchor="middle">S</text>'
        # Forced-guided contact dots (safety feature indicator)
        f'<circle cx="{cx - 4}" cy="{cy + 6}" r="2.5" fill="{C_NAVY2}"/>'
        f'<circle cx="{cx + 4}" cy="{cy + 6}" r="2.5" fill="{C_NAVY2}"/>'
    )


def _sym_safety_plc(cx: int, cy: int) -> str:
    """Safety PLC: CPU block with I/O pins."""
    return (
        # CPU body
        f'<rect x="{cx - 9}" y="{cy - 10}" width="18" height="16" rx="2" '
        f'fill="{C_NAVY2}" stroke="{C_NAVY}" stroke-width="1.5"/>'
        # CPU label
        f'<text x="{cx}" y="{cy - 1}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="5.5" font-weight="bold" fill="{C_WHITE}" text-anchor="middle">CPU</text>'
        # Left I/O pins
        f'<line x1="{cx - 13}" y1="{cy - 6}" x2="{cx - 9}" y2="{cy - 6}" '
        f'stroke="{C_LIME}" stroke-width="1.5"/>'
        f'<line x1="{cx - 13}" y1="{cy - 1}" x2="{cx - 9}" y2="{cy - 1}" '
        f'stroke="{C_LIME}" stroke-width="1.5"/>'
        # Right I/O pins
        f'<line x1="{cx + 9}" y1="{cy - 6}" x2="{cx + 13}" y2="{cy - 6}" '
        f'stroke="{C_LIME}" stroke-width="1.5"/>'
        f'<line x1="{cx + 9}" y1="{cy - 1}" x2="{cx + 13}" y2="{cy - 1}" '
        f'stroke="{C_LIME}" stroke-width="1.5"/>'
        # Safety indicator (small green bar at bottom)
        f'<rect x="{cx - 9}" y="{cy + 4}" width="18" height="3" rx="1" fill="{C_LIME}"/>'
    )


def _sym_contactor(cx: int, cy: int) -> str:
    """Contactor: main contacts above, operating coil below (IEC style)."""
    return (
        # Main contact — moving bridge
        f'<line x1="{cx - 8}" y1="{cy - 9}" x2="{cx - 8}" y2="{cy - 4}" '
        f'stroke="{C_NAVY}" stroke-width="1.5"/>'
        f'<line x1="{cx + 8}" y1="{cy - 9}" x2="{cx + 8}" y2="{cy - 4}" '
        f'stroke="{C_NAVY}" stroke-width="1.5"/>'
        f'<line x1="{cx - 8}" y1="{cy - 4}" x2="{cx + 8}" y2="{cy - 4}" '
        f'stroke="{C_NAVY}" stroke-width="2"/>'
        # Coil rectangle
        f'<rect x="{cx - 8}" y="{cy + 1}" width="16" height="8" rx="1" '
        f'fill="none" stroke="{C_NAVY}" stroke-width="1.5"/>'
        # Coil terminal stubs
        f'<line x1="{cx - 4}" y1="{cy + 9}" x2="{cx - 4}" y2="{cy + 13}" '
        f'stroke="{C_NAVY}" stroke-width="1.2"/>'
        f'<line x1="{cx + 4}" y1="{cy + 9}" x2="{cx + 4}" y2="{cy + 13}" '
        f'stroke="{C_NAVY}" stroke-width="1.2"/>'
    )


def _sym_vfd(cx: int, cy: int) -> str:
    """VFD: box with AC-to-variable-frequency symbol."""
    return (
        # Drive body
        f'<rect x="{cx - 11}" y="{cy - 10}" width="22" height="18" rx="2" '
        f'fill="{C_LGREY}" stroke="{C_NAVY}" stroke-width="1.5"/>'
        # AC input sine squiggle (left)
        f'<path d="M {cx - 9} {cy - 2} Q {cx - 7} {cy - 6} {cx - 5} {cy - 2} '
        f'Q {cx - 3} {cy + 2} {cx - 1} {cy - 2}" '
        f'fill="none" stroke="{C_NAVY}" stroke-width="1"/>'
        # Arrow pointing right
        f'<line x1="{cx - 1}" y1="{cy - 2}" x2="{cx + 2}" y2="{cy - 2}" '
        f'stroke="{C_NAVY}" stroke-width="1"/>'
        f'<polygon points="{cx + 2},{cy - 4} {cx + 5},{cy - 2} {cx + 2},{cy}" '
        f'fill="{C_NAVY}"/>'
        # Variable freq output (short waves)
        f'<path d="M {cx + 5} {cy - 2} Q {cx + 7} {cy - 5} {cx + 9} {cy - 2}" '
        f'fill="none" stroke="{C_NAVY2}" stroke-width="1"/>'
        # "VFD" label at bottom
        f'<text x="{cx}" y="{cy + 10}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="5" font-weight="bold" fill="{C_GREY}" text-anchor="middle">VFD</text>'
    )


def _sym_unknown(cx: int, cy: int) -> str:
    """Generic component: plain rectangle with '?' marker."""
    return (
        f'<rect x="{cx - 10}" y="{cy - 8}" width="20" height="16" rx="2" '
        f'fill="{C_LGREY}" stroke="{C_GREY}" stroke-width="1" stroke-dasharray="3,2"/>'
        f'<text x="{cx}" y="{cy + 4}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="10" fill="{C_GREY}" text-anchor="middle">?</text>'
    )


# Dispatch table: component type -> symbol function
_SYMBOL_FN = {
    "estop":         _sym_estop,
    "safety_switch": _sym_safety_switch,
    "light_curtain": _sym_light_curtain,
    "scanner":       _sym_scanner,
    "safety_relay":  _sym_safety_relay,
    "safety_plc":    _sym_safety_plc,
    "contactor":     _sym_contactor,
    "vfd":           _sym_vfd,
}


def _draw_iec_symbol(comp_type: str, x: int, y: int, box_h: int = BOX_H) -> str:
    """Draw the IEC symbol for comp_type in the left zone of a component box."""
    cx = x + SYM_W // 2
    cy = y + box_h // 2
    val = comp_type.value if hasattr(comp_type, "value") else str(comp_type).lower()
    fn  = _SYMBOL_FN.get(val, _sym_unknown)
    return fn(cx, cy)


# ── SVG building blocks ────────────────────────────────────────────────────────

def _draw_component_box(comp, x: int, y: int, change_ids: list, all_changes: dict,
                        box_h: int = BOX_H) -> str:
    """Draw a component box with IEC 60617 symbol on the left and ID/label text on the right."""
    cid       = _xe(_g(comp, "id",    "?"))
    label     = _xe(_trunc(_g(comp, "label", ""), 18))
    model     = _xe(_trunc(_g(comp, "model", "") or "", 16))
    comp_type = _g(comp, "type", "unknown")

    has_redline = bool(change_ids)
    border_col  = C_RED     if has_redline else C_NAVY
    fill_col    = "#FFF5F5" if has_redline else C_LGREY
    stroke_w    = 1.5       if has_redline else 1
    dash        = 'stroke-dasharray="5,3"' if has_redline else ""

    # Scale font sizes down when boxes are small
    fs_id    = 8.5 if box_h >= 28 else 7.0
    fs_label = 7.5 if box_h >= 28 else 6.0
    # Text positions as fractions of box height
    text_y1 = y + max(10, box_h * 2 // 5)
    text_y2 = y + max(17, box_h * 4 // 5)

    parts = []

    # Outer box
    parts.append(
        f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{box_h}" '
        f'rx="3" fill="{fill_col}" stroke="{border_col}" stroke-width="{stroke_w}" {dash}/>'
    )

    # Symbol zone divider
    sym_div_x = x + SYM_W + 2
    parts.append(
        f'<line x1="{sym_div_x}" y1="{y + 3}" x2="{sym_div_x}" y2="{y + box_h - 3}" '
        f'stroke="{border_col}" stroke-width="0.5" opacity="0.4"/>'
    )

    # IEC symbol (only when box is tall enough to show it meaningfully)
    if box_h >= 20:
        parts.append(_draw_iec_symbol(comp_type, x, y, box_h))

    # Text zone (right of symbol)
    tx = x + SYM_W + 6

    # ID label (bold)
    parts.append(
        f'<text x="{tx}" y="{text_y1}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="{fs_id}" '
        f'font-weight="bold" fill="{C_NAVY}">{cid}</text>'
    )

    # Label or model (smaller, second line — skip if box too short for two lines)
    if box_h >= 24:
        display = label if label else model
        parts.append(
            f'<text x="{tx}" y="{text_y2}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="{fs_label}" '
            f'fill="{C_GREY}">{display}</text>'
        )

    # Redline change-number badges (top-right, stacked left)
    if change_ids:
        badge_r = min(BADGE_R, box_h // 2 - 1)
        badge_x = x + BOX_W - badge_r - 2
        for ch_id in sorted(change_ids)[:4]:   # max 4 badges
            priority  = _priority(all_changes.get(ch_id, {}))
            badge_col = PRIORITY_COLOUR.get(priority, C_RED)
            badge_y   = y - badge_r + min(6, box_h // 2)
            parts.append(
                f'<circle cx="{badge_x}" cy="{badge_y}" r="{badge_r}" '
                f'fill="{badge_col}" stroke="{C_WHITE}" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{badge_x}" y="{badge_y + badge_r // 2}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="{max(5, badge_r - 2)}" '
                f'font-weight="bold" fill="{C_WHITE}" '
                f'text-anchor="middle">{ch_id}</text>'
            )
            badge_x -= (badge_r * 2 + 3)

    return "\n".join(parts)


def _draw_connection_arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    """Draw a horizontal flow arrow between two column boxes using a line + triangle tip."""
    tip_w, tip_h = 10, 7
    # Line stops short of the arrowhead
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2 - tip_w}" y2="{y2}" '
        f'stroke="{C_NAVY2}" stroke-width="1.5"/>'
        f'<polygon points="{x2 - tip_w},{y2 - tip_h // 2} {x2},{y2} {x2 - tip_w},{y2 + tip_h // 2}" '
        f'fill="{C_NAVY2}"/>'
    )


def _draw_col_header(col_idx: int, y: int) -> str:
    x     = COL_X[col_idx]
    label = COLUMN_LABELS[col_idx]
    # Full-width header background covering the column boxes
    return (
        f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{COL_HDR_H - 4}" '
        f'rx="3" fill="{C_NAVY}"/>'
        f'<text x="{x + BOX_W // 2}" y="{y + 12}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="7.5" '
        f'font-weight="bold" fill="{C_WHITE}" text-anchor="middle">'
        f'{_xe(label)}</text>'
    )


# ── SLD-specific drawing helpers ──────────────────────────────────────────────

def _draw_power_rail(y: int, label: str) -> str:
    """Horizontal power rail stripe (+24VDC / 0VDC) with label."""
    mid_y = y + SLD_RAIL_H // 2
    return (
        f'<rect x="0" y="{y}" width="{SVG_W}" height="{SLD_RAIL_H}" '
        f'fill="{C_NAVY2}" opacity="0.15"/>'
        f'<line x1="38" y1="{mid_y}" x2="{SVG_W - 4}" y2="{mid_y}" '
        f'stroke="{C_NAVY}" stroke-width="2"/>'
        f'<text x="3" y="{y + SLD_RAIL_H - 2}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="6.5" font-weight="bold" fill="{C_NAVY2}">{_xe(label)}</text>'
    )


# ── Ladder inline symbol helpers ──────────────────────────────────────────────
# All symbols are drawn CENTRED on the rung wire at (cx, wy).
# The rung wire passes through the symbol; bars create the visual break.

def _ldr_nc(cx: int, wy: int, col: str = C_NAVY) -> str:
    """IEC NC contact: two vertical bars + diagonal crossing."""
    w, h = LDR_CW, LDR_CH
    return (
        f'<line x1="{cx-w}" y1="{wy-h}" x2="{cx-w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
        f'<line x1="{cx+w}" y1="{wy-h}" x2="{cx+w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
        f'<line x1="{cx-w}" y1="{wy-4}" x2="{cx+w}" y2="{wy+4}" stroke="{col}" stroke-width="1.2"/>'
    )


def _ldr_no(cx: int, wy: int, col: str = C_NAVY) -> str:
    """IEC NO contact: two vertical bars, no diagonal."""
    w, h = LDR_CW, LDR_CH
    return (
        f'<line x1="{cx-w}" y1="{wy-h}" x2="{cx-w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
        f'<line x1="{cx+w}" y1="{wy-h}" x2="{cx+w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
    )


def _ldr_estop_sym(cx: int, wy: int, col: str = C_NAVY) -> str:
    """E-stop: mushroom cap above + NC contact on wire."""
    h = LDR_CH
    return (
        f'<ellipse cx="{cx}" cy="{wy-h-9}" rx="8" ry="4" fill="{C_RED}" stroke="#8B0000" stroke-width="0.8"/>'
        f'<line x1="{cx}" y1="{wy-h-5}" x2="{cx}" y2="{wy-h}" stroke="#555" stroke-width="2"/>'
        + _ldr_nc(cx, wy, col)
    )


def _ldr_lc_sym(cx: int, wy: int, col: str = C_NAVY) -> str:
    """Light curtain inline: two vertical bars with dashed beams."""
    h = LDR_CH
    return (
        f'<rect x="{cx-12}" y="{wy-h}" width="3" height="{h*2}" rx="1" fill="{col}"/>'
        f'<rect x="{cx+9}"  y="{wy-h}" width="3" height="{h*2}" rx="1" fill="{C_NAVY2}"/>'
        f'<line x1="{cx-9}" y1="{wy-3}" x2="{cx+9}" y2="{wy-3}" stroke="{C_LIME}" stroke-width="0.9" stroke-dasharray="2,1.5"/>'
        f'<line x1="{cx-9}" y1="{wy+3}" x2="{cx+9}" y2="{wy+3}" stroke="{C_LIME}" stroke-width="0.9" stroke-dasharray="2,1.5"/>'
    )


def _ldr_scanner_sym(cx: int, wy: int, col: str = C_NAVY) -> str:
    """Scanner inline: small fan-sector symbol."""
    h = LDR_CH
    return (
        f'<circle cx="{cx}" cy="{wy+3}" r="4" fill="{col}"/>'
        f'<line x1="{cx}" y1="{wy+3}" x2="{cx-8}" y2="{wy-h}" stroke="{C_LIME}" stroke-width="1"/>'
        f'<line x1="{cx}" y1="{wy+3}" x2="{cx+8}" y2="{wy-h}" stroke="{C_LIME}" stroke-width="1"/>'
    )


def _ldr_sym_for_comp(comp, cx: int, wy: int, redline: bool = False) -> str:
    """Dispatch to the correct inline contact symbol by component type."""
    col = C_RED if redline else C_NAVY
    typ = _g(comp, 'type', 'unknown')
    val = typ.value if hasattr(typ, 'value') else str(typ).lower()
    if   val == 'estop':          return _ldr_estop_sym(cx, wy, col)
    elif val == 'light_curtain':  return _ldr_lc_sym(cx, wy, col)
    elif val == 'scanner':        return _ldr_scanner_sym(cx, wy, col)
    elif val in ('safety_relay', 'safety_plc'):
        return _ldr_no(cx, wy, col)   # relay used as contact → NO
    else:
        return _ldr_nc(cx, wy, col)


def _ldr_coil_for_comp(comp, cx: int, wy: int, redline: bool = False) -> str:
    """Coil symbol at right end of rung, dispatched by component type."""
    col  = C_RED if redline else C_NAVY
    fill = '#FFF5F5' if redline else 'none'
    label = _trunc(str(_g(comp, 'id', '?')), 9)
    typ = _g(comp, 'type', 'unknown')
    val = typ.value if hasattr(typ, 'value') else str(typ).lower()
    bw, bh, r = LDR_COIL_BW, LDR_COIL_BH, LDR_COIL_R
    if val in ('safety_relay', 'safety_plc'):
        # IEC relay coil: rectangle
        return (
            f'<rect x="{cx-bw}" y="{wy-bh//2}" width="{bw*2}" height="{bh}" rx="2" '
            f'fill="{fill}" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{wy+4}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="6.5" font-weight="bold" fill="{col}" text-anchor="middle">{_xe(label)}</text>'
        )
    else:
        # IEC contactor/output coil: circle
        return (
            f'<circle cx="{cx}" cy="{wy}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{wy+3}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="6" font-weight="bold" fill="{col}" text-anchor="middle">{_xe(label)}</text>'
        )


def _build_rungs_for_ladder(components: list, connections: list, changes: list) -> list:
    """
    Convert component list and connection topology into an ordered list of ladder rungs.
    Each rung: {'contacts': [comp,...], 'coil': comp|None, 'nc': bool, 'section': str}
    """
    col0 = [c for c in components if _type_to_col(_g(c, 'type', 'unknown')) == 0]
    col1 = [c for c in components if _type_to_col(_g(c, 'type', 'unknown')) == 1]
    col2 = [c for c in components if _type_to_col(_g(c, 'type', 'unknown')) == 2]

    comp_by_id = {str(_g(c, 'id', '')).strip(): c for c in components}
    col0_ids   = {str(_g(c, 'id', '')).strip() for c in col0}
    col1_ids   = {str(_g(c, 'id', '')).strip() for c in col1}
    col2_ids   = {str(_g(c, 'id', '')).strip() for c in col2}

    # Directed adjacency from connections (ignore feedback/power)
    relay_inputs:  dict = defaultdict(list)   # relay_id → [input_ids]
    relay_outputs: dict = defaultdict(list)   # relay_id → [output_ids]

    for conn in connections:
        fid = str(_g(conn, 'from_id', '')).strip()
        tid = str(_g(conn, 'to_id',   '')).strip()
        wt  = str(_g(conn, 'wire_type', 'control')).lower()
        if wt in ('feedback', 'power'):
            continue
        if fid in col0_ids and tid in col1_ids:
            if fid not in relay_inputs[tid]:
                relay_inputs[tid].append(fid)
        elif fid in col1_ids and tid in col2_ids:
            if tid not in relay_outputs[fid]:
                relay_outputs[fid].append(tid)

    rungs: list = []
    placed_inputs  = set()
    placed_relays  = set()
    placed_outputs = set()

    # ── Input rungs: one per relay that receives safety inputs ────────────────
    first_in = True
    for relay_id, inp_ids in relay_inputs.items():
        relay_comp = comp_by_id.get(relay_id)
        contacts   = [comp_by_id[i] for i in inp_ids if i in comp_by_id]
        placed_inputs.update(inp_ids)
        placed_relays.add(relay_id)
        rungs.append({'contacts': contacts, 'coil': relay_comp, 'nc': True,
                      'section': 'SAFETY INPUT CHAIN' if first_in else ''})
        first_in = False

    # Unconnected col0 → group by series_group/channel, pair with remaining col1
    leftover_in = [c for c in col0 if str(_g(c, 'id', '')).strip() not in placed_inputs]
    if leftover_in:
        groups: dict = defaultdict(list)
        for c in leftover_in:
            sg = str(_g(c, 'series_group', '') or '')
            ch = str(_g(c, 'channel',      '') or '')
            groups[sg if sg else (ch if ch else '__all__')].append(c)
        for gi, (_, comps) in enumerate(groups.items()):
            idx  = len(placed_relays)
            coil = col1[idx] if idx < len(col1) else None
            if coil:
                placed_relays.add(str(_g(coil, 'id', '')).strip())
            rungs.append({'contacts': comps, 'coil': coil, 'nc': True,
                          'section': 'SAFETY INPUT CHAIN' if first_in else ''})
            first_in = False

    # Unconnected col1 relays (no inputs mapped to them)
    for c in col1:
        cid = str(_g(c, 'id', '')).strip()
        if cid not in placed_relays:
            rungs.append({'contacts': [], 'coil': c, 'nc': True,
                          'section': 'SAFETY INPUT CHAIN' if first_in else ''})
            placed_relays.add(cid)
            first_in = False

    # ── Output rungs: one per output connected via relay topology ────────────
    first_out = True
    for relay_id, out_ids in relay_outputs.items():
        relay_comp = comp_by_id.get(relay_id)
        for out_id in out_ids:
            out_comp = comp_by_id.get(out_id)
            if out_comp:
                placed_outputs.add(out_id)
                rungs.append({'contacts': [relay_comp] if relay_comp else [],
                              'coil': out_comp, 'nc': False,
                              'section': 'OUTPUT CONTACTS' if first_out else ''})
                first_out = False

    # Remaining col2 outputs not matched by any connection
    for c in col2:
        cid = str(_g(c, 'id', '')).strip()
        if cid not in placed_outputs:
            rungs.append({'contacts': [], 'coil': c, 'nc': True,
                          'section': 'OUTPUT CONTACTS' if first_out else ''})
            first_out = False

    return rungs


# ── Main SVG builder ───────────────────────────────────────────────────────────

def _build_block_svg(parse_result, review_result) -> str:
    """
    Fallback 3-column block diagram. Used when no connection topology is available.
    """
    # Gather data
    components = list(_g(parse_result, "components", []))
    changes    = list(_g(review_result, "changes", []))
    machine    = _xe(_g(getattr(review_result, '__dict__', {}) or review_result, "project_number", "")
                     or "Safety Circuit Review")

    # Build a lookup: change_id -> change object (for priority lookup in badges)
    change_by_id = {_g(ch, "id", i): ch for i, ch in enumerate(changes)}

    # Filter to renderable components (skip terminals)
    renderable = [c for c in components if _type_to_col(_g(c, "type", "unknown")) is not None]

    # Assign components to columns
    cols: list[list] = [[], [], []]
    for comp in renderable:
        col = _type_to_col(_g(comp, "type", "unknown"))
        if col is not None:
            cols[col].append(comp)

    # Map changes to component IDs
    change_map = _map_changes_to_components(renderable, changes)

    # Dynamic row sizing — guarantee all components fit within MAX_H so no element
    # is drawn outside the viewBox (svglib measures all elements, not just the viewport).
    max_rows    = max((len(c) for c in cols), default=1)
    available_h = MAX_H - TITLE_H - COL_HDR_H - LEGEND_H - 20
    dyn_row_h   = max(22, available_h // max(max_rows, 1))
    dyn_box_h   = max(18, dyn_row_h - 4)
    dyn_box_gap = dyn_row_h - dyn_box_h

    content_h = max_rows * dyn_row_h + 4
    svg_h     = min(MAX_H, max(MIN_H, TITLE_H + COL_HDR_H + content_h + LEGEND_H + 20))

    parts = []

    # SVG root + background
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_W} {svg_h}" '
        f'width="{SVG_W}" height="{svg_h}">'
    )
    parts.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="{C_WHITE}"/>')

    # Title bar
    parts.append(
        f'<rect x="0" y="0" width="{SVG_W}" height="{TITLE_H}" fill="{C_NAVY}"/>'
    )
    parts.append(
        f'<rect x="0" y="{TITLE_H - 4}" width="{SVG_W}" height="4" fill="{C_LIME}"/>'
    )
    parts.append(
        f'<text x="10" y="22" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" font-weight="bold" fill="{C_WHITE}">'
        f'Safety Circuit Schematic \u2014 Redline Review'
        f'</text>'
    )
    parts.append(
        f'<text x="10" y="38" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7.5" fill="#AEB6BF">MEX Engineering Group \u00b7 '
        f'Redline annotations correspond to numbered change items in the review report</text>'
    )

    # Column headers
    hdr_y = TITLE_H + 4
    for ci in range(3):
        parts.append(_draw_col_header(ci, hdr_y))

    # Connection arrows (drawn behind components)
    # Col0 -> Col1: from right edge of col0 to left edge of col1, at 1/2 height of logic area
    arrow_y = COMP_Y0 + (len(cols[1]) * dyn_row_h) // 2 + dyn_box_h // 2 if cols[1] else COMP_Y0 + dyn_box_h // 2
    x0_r  = COL_X[0] + BOX_W + 4
    x1_l  = COL_X[1] - 4
    x1_r  = COL_X[1] + BOX_W + 4
    x2_l  = COL_X[2] - 4

    parts.append(_draw_connection_arrow(x0_r, arrow_y, x1_l, arrow_y))
    parts.append(_draw_connection_arrow(x1_r, arrow_y, x2_l, arrow_y))

    # Components per column
    for ci, col_comps in enumerate(cols):
        cy = COMP_Y0
        for comp in col_comps:
            cid    = str(_g(comp, "id", "")).strip()
            ch_ids = change_map.get(cid, [])
            parts.append(_draw_component_box(comp, COL_X[ci], cy, ch_ids, change_by_id,
                                             box_h=dyn_box_h))
            cy += dyn_box_h + dyn_box_gap

    # Legend — laid out to fit SVG_W=500
    leg_y = svg_h - LEGEND_H + 4
    parts.append(
        f'<rect x="0" y="{leg_y - 4}" width="{SVG_W}" height="{LEGEND_H}" fill="{C_LGREY}"/>'
    )
    # Normal component sample
    lx = 8
    parts.append(
        f'<rect x="{lx}" y="{leg_y + 4}" width="28" height="16" rx="3" '
        f'fill="{C_LGREY}" stroke="{C_NAVY}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{lx + 32}" y="{leg_y + 16}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="7.5" fill="{C_GREY}">'
        f'No findings</text>'
    )
    # Redline component sample
    lx2 = 130
    parts.append(
        f'<rect x="{lx2}" y="{leg_y + 4}" width="28" height="16" rx="3" '
        f'fill="#FFF5F5" stroke="{C_RED}" stroke-width="1.5" stroke-dasharray="5,3"/>'
    )
    parts.append(
        f'<circle cx="{lx2 + 28}" cy="{leg_y + 4}" r="{BADGE_R}" '
        f'fill="{C_RED}" stroke="{C_WHITE}" stroke-width="1"/>'
    )
    parts.append(
        f'<text x="{lx2 + 28}" y="{leg_y + 8}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="7" font-weight="bold" '
        f'fill="{C_WHITE}" text-anchor="middle">N</text>'
    )
    parts.append(
        f'<text x="{lx2 + 42}" y="{leg_y + 16}" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="7.5" fill="{C_GREY}">'
        f'Redline (N = change no.)</text>'
    )
    # Priority badges
    lx3 = 320
    for label, col in [("CRITICAL", C_RED), ("MAJOR", C_AMBER), ("MINOR", "#2471A3")]:
        parts.append(
            f'<circle cx="{lx3}" cy="{leg_y + 12}" r="7" fill="{col}"/>'
        )
        parts.append(
            f'<text x="{lx3 + 10}" y="{leg_y + 16}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="7.5" fill="{C_GREY}">'
            f'{label}</text>'
        )
        lx3 += 58

    parts.append('</svg>')

    return "\n".join(parts)


def _build_series_chains(col_comps: list, connections: list) -> list[list]:
    """
    Group components in a column into ordered series chains using connection topology.
    Falls back to a single chain (all components assumed in series) when no
    intra-column connections are present — correct for most safety input circuits.
    """
    if not col_comps:
        return []

    comp_ids  = {str(_g(c, "id", "")).strip() for c in col_comps if _g(c, "id", "")}
    comp_by_id = {str(_g(c, "id", "")).strip(): c for c in col_comps if _g(c, "id", "")}

    # Intra-column directed edges (exclude feedback/power)
    nxt: dict[str, str] = {}
    for conn in connections:
        fid = str(_g(conn, "from_id", "")).strip()
        tid = str(_g(conn, "to_id",   "")).strip()
        wt  = str(_g(conn, "wire_type", "control")).lower()
        if fid in comp_ids and tid in comp_ids and wt not in ("feedback", "power"):
            nxt[fid] = tid

    if not nxt:
        # No intra-column connections — assume single series chain
        return [list(col_comps)]

    # Build chains: start from nodes with no in-edge within this column
    in_targets = set(nxt.values())
    starts = [str(_g(c, "id", "")).strip() for c in col_comps
              if str(_g(c, "id", "")).strip() not in in_targets]

    chains: list[list] = []
    visited: set = set()
    for start in starts:
        if start in visited or start not in comp_by_id:
            continue
        chain: list = []
        cur: str | None = start
        while cur and cur in comp_by_id and cur not in visited:
            chain.append(comp_by_id[cur])
            visited.add(cur)
            cur = nxt.get(cur)
        if chain:
            chains.append(chain)

    # Remaining isolated components each become their own single-item chain
    for c in col_comps:
        cid = str(_g(c, "id", "")).strip()
        if cid not in visited and cid in comp_by_id:
            chains.append([comp_by_id[cid]])

    return chains if chains else [list(col_comps)]


def _map_changes_to_connections(connections: list, changes: list) -> dict:
    """
    Returns {(from_id, to_id): [change_id, ...]} for connections mentioned in change items.
    Used to draw redlined wires.
    """
    result: dict[tuple, list] = {}
    for ch in changes:
        ch_id = _g(ch, "id", 0)
        desc  = _g(ch, "description", "")
        desc  = " ".join(desc) if isinstance(desc, list) else str(desc)
        text  = (desc + " " + str(_g(ch, "action", ""))).upper()
        for conn in connections:
            fid = str(_g(conn, "from_id", "") or "").strip()
            tid = str(_g(conn, "to_id",   "") or "").strip()
            fp  = str(_g(conn, "from_port", "") or "").strip().upper()
            tp  = str(_g(conn, "to_port",   "") or "").strip().upper()
            if not fid or not tid:
                continue
            matched = (fid.upper() in text and tid.upper() in text)
            if not matched and fp and len(fp) >= 2:
                matched = fp in text and (fid.upper() in text or tid.upper() in text)
            if not matched and tp and len(tp) >= 2:
                matched = tp in text and (fid.upper() in text or tid.upper() in text)
            if matched:
                key = (fid.lower(), tid.lower())
                if key not in result:
                    result[key] = []
                if ch_id not in result[key]:
                    result[key].append(ch_id)
    return result


# ── Ladder SLD builder ────────────────────────────────────────────────────────

def _build_sld_svg(parse_result, review_result) -> str:
    """
    Ladder-style SLD: left/right vertical power rails, horizontal rungs with
    inline IEC contact symbols (NC/NO) and output coil symbols.
    Redlined rungs draw in red/dashed; numbered badges mark each finding.
    """
    components  = list(_g(parse_result, "components",  []))
    connections = list(_g(parse_result, "connections", []))
    changes     = list(_g(review_result, "changes",    []))

    change_by_id = {_g(ch, "id", i): ch for i, ch in enumerate(changes)}
    renderable   = [c for c in components if _type_to_col(_g(c, "type", "unknown")) is not None]
    change_map   = _map_changes_to_components(renderable, changes)

    rungs = _build_rungs_for_ladder(renderable, connections, changes)

    # ── Dynamic rung pitch ─────────────────────────────────────────────────────
    n_secs   = sum(1 for r in rungs if r.get("section"))
    overhead = TITLE_H + 28 + n_secs * LDR_SECTION_GAP + LEGEND_H + 20
    pitch    = max(32, min(LDR_RUNG_PITCH, (MAX_H - overhead) // max(len(rungs), 1)))

    # ── Rung Y positions ───────────────────────────────────────────────────────
    rung_ys: list[int] = []
    cur_y = TITLE_H + 28
    for r in rungs:
        if r.get("section"):
            cur_y += LDR_SECTION_GAP
        rung_ys.append(cur_y)
        cur_y += pitch

    svg_h    = min(MAX_H, max(MIN_H, cur_y + LEGEND_H + 16))
    rail_top = rung_ys[0]  if rung_ys else TITLE_H + 28
    rail_bot = rung_ys[-1] if rung_ys else svg_h - LEGEND_H - 16

    parts: list[str] = []

    # ── SVG root + background ─────────────────────────────────────────────────
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_W} {svg_h}" width="{SVG_W}" height="{svg_h}">'
    )
    parts.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="{C_WHITE}"/>')

    # ── Title bar ─────────────────────────────────────────────────────────────
    parts.append(f'<rect x="0" y="0" width="{SVG_W}" height="{TITLE_H}" fill="{C_NAVY}"/>')
    parts.append(f'<rect x="0" y="{TITLE_H - 4}" width="{SVG_W}" height="4" fill="{C_LIME}"/>')
    parts.append(
        f'<text x="10" y="22" font-family="Helvetica,Arial,sans-serif" font-size="11" '
        f'font-weight="bold" fill="{C_WHITE}">Safety Circuit Schematic \u2014 Redline Review</text>'
    )
    parts.append(
        f'<text x="10" y="38" font-family="Helvetica,Arial,sans-serif" font-size="7.5" '
        f'fill="#AEB6BF">MEX Engineering Group \u00b7 Redline annotations correspond to '
        f'numbered change items in the review report</text>'
    )

    # ── Power rail labels ─────────────────────────────────────────────────────
    parts.append(
        f'<text x="{LDR_L_X + 1}" y="{rail_top - 5}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" font-weight="bold" fill="{C_NAVY}">+24VDC</text>'
    )
    parts.append(
        f'<text x="{LDR_L_X + 1}" y="{rail_bot + 14}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" font-weight="bold" fill="{C_NAVY}">0VDC</text>'
    )

    # ── Vertical power rails ──────────────────────────────────────────────────
    parts.append(
        f'<line x1="{LDR_L_X}" y1="{rail_top}" x2="{LDR_L_X}" y2="{rail_bot}" '
        f'stroke="{C_NAVY}" stroke-width="3"/>'
    )
    parts.append(
        f'<line x1="{LDR_R_X}" y1="{rail_top}" x2="{LDR_R_X}" y2="{rail_bot}" '
        f'stroke="{C_NAVY}" stroke-width="3"/>'
    )

    # ── Rungs ─────────────────────────────────────────────────────────────────
    for rung, wy in zip(rungs, rung_ys):
        contacts  = rung.get("contacts", [])
        coil_comp = rung.get("coil")
        nc        = rung.get("nc", True)
        section   = rung.get("section", "")

        # Section header label
        if section:
            sl_y = wy - 8
            parts.append(
                f'<rect x="{LDR_L_X + 2}" y="{sl_y - 11}" width="154" height="13" rx="2" fill="{C_NAVY}"/>'
                f'<text x="{LDR_L_X + 6}" y="{sl_y}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="7.5" font-weight="bold" fill="{C_WHITE}">{_xe(section)}</text>'
            )

        # Determine rung redline state
        rung_rl = any(change_map.get(str(_g(c, "id", "")).strip()) for c in contacts)
        if coil_comp:
            rung_rl = rung_rl or bool(change_map.get(str(_g(coil_comp, "id", "")).strip()))

        wire_col  = C_RED  if rung_rl else C_NAVY
        wire_dash = 'stroke-dasharray="5,3"' if rung_rl else ""
        wire_w    = "1.6"  if rung_rl else "1.4"

        # Coil geometry
        coil_left  = LDR_COIL_CX - LDR_COIL_BW
        coil_right = LDR_COIL_CX + LDR_COIL_BW

        # Contact positions: spread evenly in available zone
        x_start = LDR_L_X + 10
        x_end   = coil_left - 12 if coil_comp else LDR_R_X - 6
        n = len(contacts)
        if n > 0:
            span = x_end - x_start
            step = max(26, min(LDR_CONTACT_PITCH, span // n))
            total_w = n * step
            cx0 = x_start + max(0, (span - total_w) // 2) + step // 2
            contact_xs = [cx0 + i * step for i in range(n)]
        else:
            contact_xs = []
            step = LDR_CONTACT_PITCH

        # Rung wires (draw first, symbols on top)
        wire_end = coil_left - 2 if coil_comp else LDR_R_X
        parts.append(
            f'<line x1="{LDR_L_X}" y1="{wy}" x2="{wire_end}" y2="{wy}" '
            f'stroke="{wire_col}" stroke-width="{wire_w}" {wire_dash}/>'
        )
        if coil_comp:
            parts.append(
                f'<line x1="{coil_right + 2}" y1="{wy}" x2="{LDR_R_X}" y2="{wy}" '
                f'stroke="{wire_col}" stroke-width="{wire_w}" {wire_dash}/>'
            )

        # ── Inline contact symbols ─────────────────────────────────────────────
        for comp_c, cx_c in zip(contacts, contact_xs):
            cid    = str(_g(comp_c, "id", "")).strip()
            ch_ids = change_map.get(cid, [])
            rl_c   = bool(ch_ids)
            # Draw symbol on wire
            if nc:
                parts.append(_ldr_sym_for_comp(comp_c, cx_c, wy, rl_c))
            else:
                parts.append(_ldr_no(cx_c, wy, C_RED if rl_c else C_NAVY))
            # Label below
            col_t = C_RED if rl_c else C_GREY
            lbl_y = wy + LDR_CH + 9
            parts.append(
                f'<text x="{cx_c}" y="{lbl_y}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="{LDR_LBL_FS}" font-weight="bold" fill="{col_t}" '
                f'text-anchor="middle">{_xe(_trunc(cid, 9))}</text>'
            )
            # Redline badges above contact
            if ch_ids:
                br = 6
                bx = cx_c + LDR_CW + br + 2
                by = wy - LDR_CH - br - 1
                for ch_id in sorted(ch_ids)[:2]:
                    pri = _priority(change_by_id.get(ch_id, {}))
                    bc  = PRIORITY_COLOUR.get(pri, C_RED)
                    parts.append(
                        f'<circle cx="{bx}" cy="{by}" r="{br}" fill="{bc}" '
                        f'stroke="{C_WHITE}" stroke-width="0.8"/>'
                        f'<text x="{bx}" y="{by + 2}" font-family="Helvetica,Arial,sans-serif" '
                        f'font-size="5" font-weight="bold" fill="{C_WHITE}" '
                        f'text-anchor="middle">{ch_id}</text>'
                    )
                    bx += br * 2 + 2

        # ── Coil symbol ────────────────────────────────────────────────────────
        if coil_comp:
            cid    = str(_g(coil_comp, "id", "")).strip()
            ch_ids = change_map.get(cid, [])
            rl_c   = bool(ch_ids)
            parts.append(_ldr_coil_for_comp(coil_comp, LDR_COIL_CX, wy, rl_c))
            # Label below coil
            col_t = C_RED if rl_c else C_GREY
            lbl_y = wy + LDR_COIL_R + 9
            parts.append(
                f'<text x="{LDR_COIL_CX}" y="{lbl_y}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="{LDR_LBL_FS}" '
                f'font-weight="bold" fill="{col_t}" text-anchor="middle">'
                f'{_xe(_trunc(cid, 10))}</text>'
            )
            # Redline badges on coil
            if ch_ids:
                br = 6
                bx = LDR_COIL_CX + LDR_COIL_BW + br + 2
                by = wy - LDR_COIL_R - br
                for ch_id in sorted(ch_ids)[:2]:
                    pri = _priority(change_by_id.get(ch_id, {}))
                    bc  = PRIORITY_COLOUR.get(pri, C_RED)
                    parts.append(
                        f'<circle cx="{bx}" cy="{by}" r="{br}" fill="{bc}" '
                        f'stroke="{C_WHITE}" stroke-width="0.8"/>'
                        f'<text x="{bx}" y="{by + 2}" font-family="Helvetica,Arial,sans-serif" '
                        f'font-size="5" font-weight="bold" fill="{C_WHITE}" '
                        f'text-anchor="middle">{ch_id}</text>'
                    )
                    bx += br * 2 + 2

    # ── Legend ────────────────────────────────────────────────────────────────
    leg_y = svg_h - LEGEND_H + 2
    parts.append(f'<rect x="0" y="{leg_y - 2}" width="{SVG_W}" height="{LEGEND_H + 2}" fill="{C_LGREY}"/>')

    # NC contact sample
    lx = 8
    parts.append(f'<line x1="{lx}" y1="{leg_y+12}" x2="{lx+26}" y2="{leg_y+12}" stroke="{C_NAVY}" stroke-width="1.2"/>')
    parts.append(_ldr_nc(lx + 13, leg_y + 12, C_NAVY))
    parts.append(
        f'<text x="{lx + 30}" y="{leg_y + 16}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" fill="{C_GREY}">NC contact</text>'
    )
    # Coil sample
    lx2 = 118
    parts.append(f'<line x1="{lx2}" y1="{leg_y+12}" x2="{lx2+11}" y2="{leg_y+12}" stroke="{C_NAVY}" stroke-width="1.2"/>')
    parts.append(
        f'<circle cx="{lx2+22}" cy="{leg_y+12}" r="11" fill="none" stroke="{C_NAVY}" stroke-width="1.5"/>'
        f'<text x="{lx2+22}" y="{leg_y+15}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="6" fill="{C_NAVY}" text-anchor="middle">K</text>'
        f'<text x="{lx2+37}" y="{leg_y+16}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" fill="{C_GREY}">Output coil</text>'
    )
    # Redline wire sample
    lx3 = 232
    parts.append(
        f'<line x1="{lx3}" y1="{leg_y+12}" x2="{lx3+26}" y2="{leg_y+12}" '
        f'stroke="{C_RED}" stroke-width="1.5" stroke-dasharray="4,2"/>'
        f'<circle cx="{lx3+32}" cy="{leg_y+12}" r="6" fill="{C_RED}" stroke="{C_WHITE}" stroke-width="0.8"/>'
        f'<text x="{lx3+32}" y="{leg_y+15}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="5" font-weight="bold" fill="{C_WHITE}" text-anchor="middle">N</text>'
        f'<text x="{lx3+42}" y="{leg_y+16}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" fill="{C_GREY}">Redline</text>'
    )
    # Priority badges
    lx4 = 340
    for lbl, col in [("CRIT", C_RED), ("MAJ", C_AMBER), ("MIN", "#2471A3")]:
        parts.append(
            f'<circle cx="{lx4}" cy="{leg_y+12}" r="6" fill="{col}"/>'
            f'<text x="{lx4+9}" y="{leg_y+16}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="7" fill="{C_GREY}">{lbl}</text>'
        )
        lx4 += 44

    parts.append("</svg>")
    return "\n".join(parts)


def build_diagram_svg(parse_result, review_result) -> str:
    """Always use the ladder SLD renderer; fall back to block diagram on error."""
    try:
        components = list(_g(parse_result, "components", []))
        logger.info("Diagram: ladder mode (%d components)", len(components))
        return _build_sld_svg(parse_result, review_result)
    except Exception as e:
        logger.warning("Ladder diagram failed (%s), falling back to block diagram", e)
        return _build_block_svg(parse_result, review_result)


# ── Public API (called from export_service) ────────────────────────────────────

def generate_diagram_drawing(parse_result, review_result):
    """
    Returns a ReportLab Drawing of the redline SVG diagram, or None on failure.
    """
    try:
        from svglib.svglib import svg2rlg

        svg_text = build_diagram_svg(parse_result, review_result)
        drawing  = svg2rlg(io.StringIO(svg_text))
        if drawing is None:
            logger.error("svg2rlg returned None for generated SVG")
            return None
        logger.info("Diagram generated: %d components, drawing %dx%d",
                    len(list(_g(parse_result, "components", []))),
                    int(drawing.width), int(drawing.height))
        return drawing

    except Exception as e:
        logger.error("Diagram generation failed: %s", e, exc_info=True)
        return None
