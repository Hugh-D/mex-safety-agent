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
MAX_H      = 620      # cap height so it always fits on one A4 page at full width

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

# ── SLD-specific constants ─────────────────────────────────────────────────────
SLD_RAIL_H  = 11    # height of power rail stripe
SLD_BUS_OFS = 13    # horizontal offset from col right edge to inter-col bus line

SLD_COL_LABELS = [
    "SAFETY INPUTS",
    "SAFETY RELAY / PLC",
    "OUTPUT CONTACTS",
]

CHAIN_GAP = 14   # extra vertical pixels between unrelated series chains in same column

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


# ── SLD builder ───────────────────────────────────────────────────────────────

def _build_sld_svg(parse_result, review_result) -> str:
    """
    SLD-style diagram using Phase 1 connection topology.
    Uses series chain detection, channel labels, bus-routed inter-column wires,
    redline wire highlighting, and dashed feedback paths.
    """
    components  = list(_g(parse_result, "components",  []))
    connections = list(_g(parse_result, "connections", []))
    changes     = list(_g(review_result, "changes",    []))

    change_by_id  = {_g(ch, "id", i): ch for i, ch in enumerate(changes)}
    renderable    = [c for c in components
                     if _type_to_col(_g(c, "type", "unknown")) is not None]
    change_map    = _map_changes_to_components(renderable, changes)
    conn_redlines = _map_changes_to_connections(connections, changes)

    # Assign components to columns
    cols: list[list] = [[], [], []]
    for comp in renderable:
        col = _type_to_col(_g(comp, "type", "unknown"))
        if col is not None:
            cols[col].append(comp)

    # Build series chains per column
    chains_per_col = [
        _build_series_chains(cols[0], connections),
        _build_series_chains(cols[1], connections),
        _build_series_chains(cols[2], connections),
    ]

    # SLD Y start — below title + top power rail + column headers
    sld_comp_y0 = TITLE_H + SLD_RAIL_H + 4 + COL_HDR_H + 4

    # Dynamic row height: account for chain gaps in effective row count
    def _effective_rows(ci: int) -> int:
        n_comps  = len(cols[ci])
        n_chains = len(chains_per_col[ci])
        return max(1, n_comps + max(0, n_chains - 1) * CHAIN_GAP // 22)

    max_eff_rows = max(_effective_rows(i) for i in range(3))
    available_h  = MAX_H - sld_comp_y0 - SLD_RAIL_H - LEGEND_H - 20
    dyn_row_h    = max(22, available_h // max(max_eff_rows, 1))
    dyn_box_h    = max(18, dyn_row_h - 4)

    # Compute component positions using chain-aware layout
    comp_pos: dict[str, tuple] = {}       # comp_id -> (col_x, y_top, box_h)
    col_chain_info: list[list[dict]] = [] # per col: [{chain, y_start, y_end}]

    for ci in range(3):
        chains = chains_per_col[ci]
        cy = sld_comp_y0
        chain_info: list[dict] = []
        for i, chain in enumerate(chains):
            if i > 0:
                cy += CHAIN_GAP
            y_chain_start = cy
            for comp in chain:
                cid = str(_g(comp, "id", "")).strip()
                if cid:
                    comp_pos[cid] = (COL_X[ci], cy, dyn_box_h)
                cy += dyn_row_h
            y_chain_end = cy - dyn_row_h + dyn_box_h
            chain_info.append({"chain": chain, "y_start": y_chain_start,
                                "y_end": y_chain_end})
        col_chain_info.append(chain_info)

    # SVG height derived from actual layout extent
    max_y = max((pos[1] + pos[2] for pos in comp_pos.values()),
                default=sld_comp_y0 + 100)
    svg_h = min(MAX_H, max(MIN_H, max_y + SLD_RAIL_H + LEGEND_H + 25))

    # Feedback routing Y — below all components, above bottom rail
    feedback_y = min(max_y + 6, svg_h - LEGEND_H - SLD_RAIL_H - 10)

    # Partition connections by wire_type
    safety_conns   = [c for c in connections
                      if _g(c, "wire_type", "control") in ("safety", "control")]
    feedback_conns = [c for c in connections
                      if _g(c, "wire_type", "") == "feedback"]

    parts = []

    # ── SVG root ──────────────────────────────────────────────────────────────
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_W} {svg_h}" width="{SVG_W}" height="{svg_h}">'
    )
    parts.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="{C_WHITE}"/>')

    # ── Title bar ─────────────────────────────────────────────────────────────
    parts.append(f'<rect x="0" y="0" width="{SVG_W}" height="{TITLE_H}" fill="{C_NAVY}"/>')
    parts.append(f'<rect x="0" y="{TITLE_H - 4}" width="{SVG_W}" height="4" fill="{C_LIME}"/>')
    parts.append(
        f'<text x="10" y="22" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="11" font-weight="bold" fill="{C_WHITE}">'
        f'Safety Circuit Schematic \u2014 Redline Review</text>'
    )
    parts.append(
        f'<text x="10" y="38" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7.5" fill="#AEB6BF">MEX Engineering Group \u00b7 '
        f'Redline annotations correspond to numbered change items in the review report</text>'
    )

    # ── Top power rail (+24VDC) ───────────────────────────────────────────────
    parts.append(_draw_power_rail(TITLE_H + 2, "+24VDC"))

    # ── Column headers (SLD labels) ───────────────────────────────────────────
    hdr_y = TITLE_H + SLD_RAIL_H + 4
    for ci, lbl in enumerate(SLD_COL_LABELS):
        parts.append(
            f'<rect x="{COL_X[ci]}" y="{hdr_y}" width="{BOX_W}" '
            f'height="{COL_HDR_H - 4}" rx="3" fill="{C_NAVY}"/>'
            f'<text x="{COL_X[ci] + BOX_W // 2}" y="{hdr_y + 12}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="7.5" '
            f'font-weight="bold" fill="{C_WHITE}" text-anchor="middle">'
            f'{_xe(lbl)}</text>'
        )

    # ── Series wires within each chain ────────────────────────────────────────
    for ci in range(3):
        cx_ctr = COL_X[ci] + BOX_W // 2
        for chain_d in col_chain_info[ci]:
            chain = chain_d["chain"]
            for j in range(len(chain) - 1):
                cid1 = str(_g(chain[j],     "id", "")).strip()
                cid2 = str(_g(chain[j + 1], "id", "")).strip()
                if cid1 in comp_pos and cid2 in comp_pos:
                    y1 = comp_pos[cid1][1] + dyn_box_h
                    y2 = comp_pos[cid2][1]
                    if y2 > y1:
                        parts.append(
                            f'<line x1="{cx_ctr}" y1="{y1}" x2="{cx_ctr}" y2="{y2}" '
                            f'stroke="{C_NAVY}" stroke-width="1.3"/>'
                        )
                        y_mid = (y1 + y2) // 2
                        parts.append(
                            f'<circle cx="{cx_ctr}" cy="{y_mid}" r="1.5" fill="{C_NAVY}"/>'
                        )

    # ── Chain separator lines between unrelated groups in same column ──────────
    for ci in range(3):
        if len(col_chain_info[ci]) > 1:
            for i in range(len(col_chain_info[ci]) - 1):
                y_end   = col_chain_info[ci][i]["y_end"]
                y_start = col_chain_info[ci][i + 1]["y_start"]
                y_sep   = (y_end + y_start) // 2
                parts.append(
                    f'<line x1="{COL_X[ci] + 8}" y1="{y_sep}" '
                    f'x2="{COL_X[ci] + BOX_W - 8}" y2="{y_sep}" '
                    f'stroke="{C_GREY}" stroke-width="0.5" '
                    f'stroke-dasharray="3,2" opacity="0.55"/>'
                )

    # ── Channel labels on input column ────────────────────────────────────────
    for chain_d in col_chain_info[0]:
        if chain_d["chain"]:
            ch_label = str(_g(chain_d["chain"][0], "channel", "") or "")
            if ch_label:
                first_cid = str(_g(chain_d["chain"][0], "id", "")).strip()
                if first_cid in comp_pos:
                    _, cy_ch, _ = comp_pos[first_cid]
                    parts.append(
                        f'<text x="{COL_X[0] + BOX_W + 3}" y="{cy_ch + 8}" '
                        f'font-family="Helvetica,Arial,sans-serif" font-size="6" '
                        f'font-weight="bold" fill="{C_NAVY2}">{_xe(ch_label)}</text>'
                    )

    # ── Inter-column bus wires ─────────────────────────────────────────────────
    for from_col, to_col in [(0, 1), (1, 2)]:
        bus_x = COL_X[from_col] + BOX_W + SLD_BUS_OFS

        lane_conns = [
            c for c in safety_conns
            if (_g(c, "from_id", "") in comp_pos
                and _g(c, "to_id", "") in comp_pos
                and comp_pos[_g(c, "from_id", "")][0] == COL_X[from_col]
                and comp_pos[_g(c, "to_id",   "")][0] == COL_X[to_col])
        ]

        if lane_conns:
            src_ys = [comp_pos[_g(c, "from_id", "")][1] + dyn_box_h // 2
                      for c in lane_conns if _g(c, "from_id", "") in comp_pos]
            if src_ys:
                bus_y1 = min(src_ys) - 2
                bus_y2 = max(src_ys) + 2
                # Vertical bus line
                parts.append(
                    f'<line x1="{bus_x}" y1="{bus_y1}" x2="{bus_x}" y2="{bus_y2}" '
                    f'stroke="{C_NAVY}" stroke-width="1.8"/>'
                )

                # Source stubs: right edge of source → bus
                seen_src: set = set()
                for conn in lane_conns:
                    fid = _g(conn, "from_id", "")
                    tid = _g(conn, "to_id", "")
                    fp  = str(_g(conn, "from_port", "") or "")
                    key = (str(fid).lower(), str(tid).lower())
                    is_rl  = key in conn_redlines
                    w_col  = C_RED  if is_rl else C_NAVY
                    w_w    = "1.6"  if is_rl else "1.2"
                    if fid in comp_pos and fid not in seen_src:
                        fy = comp_pos[fid][1] + dyn_box_h // 2
                        sx = COL_X[from_col] + BOX_W
                        dash = 'stroke-dasharray="4,2"' if is_rl else ""
                        parts.append(
                            f'<line x1="{sx}" y1="{fy}" x2="{bus_x}" y2="{fy}" '
                            f'stroke="{w_col}" stroke-width="{w_w}" {dash}/>'
                        )
                        if fp:
                            parts.append(
                                f'<text x="{sx + 2}" y="{fy - 2}" '
                                f'font-family="Helvetica,Arial,sans-serif" '
                                f'font-size="5.5" fill="{C_GREY}">{_xe(fp)}</text>'
                            )
                        seen_src.add(fid)

                # Target wires: bus → left edge of target with arrowhead
                seen_tgt: set = set()
                for conn in lane_conns:
                    fid = _g(conn, "from_id", "")
                    tid = _g(conn, "to_id",   "")
                    tp  = str(_g(conn, "to_port", "") or "")
                    key = (str(fid).lower(), str(tid).lower())
                    is_rl  = key in conn_redlines
                    w_col  = C_RED  if is_rl else C_NAVY
                    w_w    = "1.6"  if is_rl else "1.2"
                    arr_col = C_RED if is_rl else C_NAVY2
                    if tid in comp_pos and tid not in seen_tgt:
                        ty = comp_pos[tid][1] + dyn_box_h // 2
                        tx = COL_X[to_col]
                        dash = 'stroke-dasharray="4,2"' if is_rl else ""
                        parts.append(
                            f'<line x1="{bus_x}" y1="{ty}" x2="{tx}" y2="{ty}" '
                            f'stroke="{w_col}" stroke-width="{w_w}" {dash}/>'
                        )
                        parts.append(
                            f'<polygon points="{tx},{ty} {tx-7},{ty-3} {tx-7},{ty+3}" '
                            f'fill="{arr_col}"/>'
                        )
                        if tp:
                            parts.append(
                                f'<text x="{bus_x + 2}" y="{ty - 2}" '
                                f'font-family="Helvetica,Arial,sans-serif" '
                                f'font-size="5.5" fill="{C_GREY}">{_xe(tp)}</text>'
                            )
                        seen_tgt.add(tid)
        else:
            # Fallback: single midpoint arrow when no connection data
            arrow_y = (sld_comp_y0 + (len(cols[from_col]) * dyn_row_h) // 2 + dyn_box_h // 2
                       if cols[from_col] else sld_comp_y0 + dyn_box_h // 2)
            parts.append(_draw_connection_arrow(
                COL_X[from_col] + BOX_W + 4, arrow_y,
                COL_X[to_col]   - 4,         arrow_y,
            ))

    # ── Feedback connections (dashed amber, routed below components) ───────────
    for conn in feedback_conns:
        fid = _g(conn, "from_id", "")
        tid = _g(conn, "to_id",   "")
        if fid in comp_pos and tid in comp_pos:
            fx, fy, fh = comp_pos[fid]
            tx, ty, th = comp_pos[tid]
            src_cx = fx + BOX_W // 2
            tgt_cx = tx + BOX_W // 2
            parts.append(
                f'<polyline points="'
                f'{src_cx},{fy + fh} {src_cx},{feedback_y} '
                f'{tgt_cx},{feedback_y} {tgt_cx},{ty + th}" '
                f'fill="none" stroke="{C_AMBER}" stroke-width="1.1" '
                f'stroke-dasharray="4,3" opacity="0.9"/>'
            )
            ay = ty + th
            parts.append(
                f'<polygon points="{tgt_cx},{ay} {tgt_cx-3},{ay+7} {tgt_cx+3},{ay+7}" '
                f'fill="{C_AMBER}" opacity="0.9"/>'
            )

    # ── Components (drawn on top of all wires) ─────────────────────────────────
    for ci in range(3):
        for chain_d in col_chain_info[ci]:
            for comp in chain_d["chain"]:
                cid    = str(_g(comp, "id", "")).strip()
                ch_ids = change_map.get(cid, [])
                if cid in comp_pos:
                    x, y, bh = comp_pos[cid]
                    parts.append(_draw_component_box(comp, x, y, ch_ids, change_by_id,
                                                     box_h=bh))

    # ── Bottom power rail (0VDC) ──────────────────────────────────────────────
    bot_rail_y = svg_h - LEGEND_H - SLD_RAIL_H - 4
    parts.append(_draw_power_rail(bot_rail_y, "0VDC"))

    # ── Legend ────────────────────────────────────────────────────────────────
    leg_y = svg_h - LEGEND_H + 4
    parts.append(
        f'<rect x="0" y="{leg_y - 4}" width="{SVG_W}" height="{LEGEND_H}" fill="{C_LGREY}"/>'
    )
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
    lx3 = 320
    for lbl, col in [("CRITICAL", C_RED), ("MAJOR", C_AMBER), ("MINOR", "#2471A3")]:
        parts.append(f'<circle cx="{lx3}" cy="{leg_y + 12}" r="7" fill="{col}"/>')
        parts.append(
            f'<text x="{lx3 + 10}" y="{leg_y + 16}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="7.5" fill="{C_GREY}">'
            f'{lbl}</text>'
        )
        lx3 += 58

    parts.append('</svg>')
    return "\n".join(parts)


def build_diagram_svg(parse_result, review_result) -> str:
    """Route to SLD layout when connection topology is available, else block diagram."""
    connections = list(_g(parse_result, "connections", []))
    if connections:
        logger.info("Diagram: SLD mode (%d connections)", len(connections))
        return _build_sld_svg(parse_result, review_result)
    logger.info("Diagram: block mode (no connections)")
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
