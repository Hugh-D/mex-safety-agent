"""
Diagram service — MEX Safety Platform
Generates a programmatic ladder SLD with redline markup.
No AI call — deterministic layout from parsed DXF + topology data.
Returns None if topology has no connections.
"""

from __future__ import annotations

import io
import logging
import re
from collections import defaultdict

log = logging.getLogger(__name__)

# ── SVG layout constants ───────────────────────────────────────────────────────
SVG_W      = 500
LDR_L_X    = 24
LDR_R_X    = 476
LDR_RUNG_PITCH   = 48
LDR_SECTION_GAP  = 22
LDR_CONTACT_PITCH = 36
LDR_CW     = 7
LDR_CH     = 9
LDR_COIL_R = 11
LDR_COIL_BW = 24
LDR_COIL_BH = 16
LDR_COIL_CX = 444
LDR_LBL_FS  = 6.5
TITLE_H    = 52
LEGEND_H   = 36
MIN_H      = 320
MAX_H      = 900
BADGE_R    = 9

# ── Brand colours ──────────────────────────────────────────────────────────────
C_NAVY  = "#002559"
C_NAVY2 = "#1d4382"
C_LIME  = "#70bf54"
C_RED   = "#C0392B"
C_AMBER = "#E67E22"
C_WHITE = "#FFFFFF"
C_GREY  = "#566573"
C_LGREY = "#ECF0F1"

# Maps compliance_type (from dxf_parser) → diagram column
COMPLIANCE_TO_DIAGRAM_TYPE: dict[str, str] = {
    "e_stop":       "estop",
    "interlock":    "safety_switch",
    "light_curtain":"light_curtain",
    "scanner":      "scanner",
    "safety_relay": "safety_relay",
    "safety_plc":   "safety_plc",
    "contactor":    "contactor",
    "drive":        "vfd",
    "terminal":     "terminal",
}

TYPE_TO_COL: dict[str, int | None] = {
    "estop":         0,
    "safety_switch": 0,
    "light_curtain": 0,
    "scanner":       0,
    "safety_relay":  1,
    "safety_plc":    1,
    "contactor":     2,
    "vfd":           2,
    "unknown":       2,
    "terminal":      None,
}

PRIORITY_COLOUR = {
    "CRITICAL": C_RED,
    "MAJOR":    C_AMBER,
    "MINOR":    "#2471A3",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _g(obj, attr, default=""):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _xe(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _trunc(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + "…"


def _type_to_col(device_type) -> int | None:
    val = device_type.value if hasattr(device_type, "value") else str(device_type).lower()
    return TYPE_TO_COL.get(val, 2)


def _priority(change) -> str:
    return str(_g(change, "priority", "MINOR")).upper()


# ── Change-to-component mapping ────────────────────────────────────────────────

def _map_changes_to_components(components: list, changes: list) -> dict[str, list]:
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


def _map_changes_to_connections(connections: list, changes: list) -> dict:
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


# ── IEC 60617-inspired symbols ─────────────────────────────────────────────────

def _ldr_nc(cx: int, wy: int, col: str = C_NAVY) -> str:
    w, h = LDR_CW, LDR_CH
    return (
        f'<line x1="{cx-w}" y1="{wy-h}" x2="{cx-w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
        f'<line x1="{cx+w}" y1="{wy-h}" x2="{cx+w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
        f'<line x1="{cx-w}" y1="{wy-4}" x2="{cx+w}" y2="{wy+4}" stroke="{col}" stroke-width="1.2"/>'
    )


def _ldr_no(cx: int, wy: int, col: str = C_NAVY) -> str:
    w, h = LDR_CW, LDR_CH
    return (
        f'<line x1="{cx-w}" y1="{wy-h}" x2="{cx-w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
        f'<line x1="{cx+w}" y1="{wy-h}" x2="{cx+w}" y2="{wy+h}" stroke="{col}" stroke-width="1.6"/>'
    )


def _ldr_estop_sym(cx: int, wy: int, col: str = C_NAVY) -> str:
    h = LDR_CH
    return (
        f'<ellipse cx="{cx}" cy="{wy-h-9}" rx="8" ry="4" fill="{C_RED}" stroke="#8B0000" stroke-width="0.8"/>'
        f'<line x1="{cx}" y1="{wy-h-5}" x2="{cx}" y2="{wy-h}" stroke="#555" stroke-width="2"/>'
        + _ldr_nc(cx, wy, col)
    )


def _ldr_lc_sym(cx: int, wy: int, col: str = C_NAVY) -> str:
    h = LDR_CH
    return (
        f'<rect x="{cx-12}" y="{wy-h}" width="3" height="{h*2}" rx="1" fill="{col}"/>'
        f'<rect x="{cx+9}"  y="{wy-h}" width="3" height="{h*2}" rx="1" fill="{C_NAVY2}"/>'
        f'<line x1="{cx-9}" y1="{wy-3}" x2="{cx+9}" y2="{wy-3}" stroke="{C_LIME}" stroke-width="0.9" stroke-dasharray="2,1.5"/>'
        f'<line x1="{cx-9}" y1="{wy+3}" x2="{cx+9}" y2="{wy+3}" stroke="{C_LIME}" stroke-width="0.9" stroke-dasharray="2,1.5"/>'
    )


def _ldr_scanner_sym(cx: int, wy: int, col: str = C_NAVY) -> str:
    h = LDR_CH
    return (
        f'<circle cx="{cx}" cy="{wy+3}" r="4" fill="{col}"/>'
        f'<line x1="{cx}" y1="{wy+3}" x2="{cx-8}" y2="{wy-h}" stroke="{C_LIME}" stroke-width="1"/>'
        f'<line x1="{cx}" y1="{wy+3}" x2="{cx+8}" y2="{wy-h}" stroke="{C_LIME}" stroke-width="1"/>'
    )


def _ldr_sym_for_comp(comp, cx: int, wy: int, redline: bool = False) -> str:
    col = C_RED if redline else C_NAVY
    typ = _g(comp, "type", "unknown")
    val = typ.value if hasattr(typ, "value") else str(typ).lower()
    if   val == "estop":         return _ldr_estop_sym(cx, wy, col)
    elif val == "light_curtain": return _ldr_lc_sym(cx, wy, col)
    elif val == "scanner":       return _ldr_scanner_sym(cx, wy, col)
    elif val in ("safety_relay", "safety_plc"):
        return _ldr_no(cx, wy, col)
    else:
        return _ldr_nc(cx, wy, col)


def _ldr_coil_for_comp(comp, cx: int, wy: int, redline: bool = False) -> str:
    col  = C_RED if redline else C_NAVY
    fill = "#FFF5F5" if redline else "none"
    label = _trunc(str(_g(comp, "id", "?")), 9)
    typ = _g(comp, "type", "unknown")
    val = typ.value if hasattr(typ, "value") else str(typ).lower()
    bw, bh, r = LDR_COIL_BW, LDR_COIL_BH, LDR_COIL_R
    if val in ("safety_relay", "safety_plc"):
        return (
            f'<rect x="{cx-bw}" y="{wy-bh//2}" width="{bw*2}" height="{bh}" rx="2" '
            f'fill="{fill}" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{wy+4}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="6.5" font-weight="bold" fill="{col}" text-anchor="middle">{_xe(label)}</text>'
        )
    else:
        return (
            f'<circle cx="{cx}" cy="{wy}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{wy+3}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="6" font-weight="bold" fill="{col}" text-anchor="middle">{_xe(label)}</text>'
        )


# ── Rung builder ───────────────────────────────────────────────────────────────

def _build_rungs_for_ladder(components: list, connections: list, changes: list) -> list:
    col0 = [c for c in components if _type_to_col(_g(c, "type", "unknown")) == 0]
    col1 = [c for c in components if _type_to_col(_g(c, "type", "unknown")) == 1]
    col2 = [c for c in components if _type_to_col(_g(c, "type", "unknown")) == 2]

    comp_by_id  = {str(_g(c, "id", "")).strip(): c for c in components}
    col0_ids    = {str(_g(c, "id", "")).strip() for c in col0}
    col1_ids    = {str(_g(c, "id", "")).strip() for c in col1}
    col2_ids    = {str(_g(c, "id", "")).strip() for c in col2}

    relay_inputs:  dict = defaultdict(list)
    relay_outputs: dict = defaultdict(list)
    for conn in connections:
        fid = str(_g(conn, "from_id", "")).strip()
        tid = str(_g(conn, "to_id",   "")).strip()
        wt  = str(_g(conn, "wire_type", "control")).lower()
        if wt in ("feedback", "power"):
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

    first_in = True
    for relay_id, inp_ids in relay_inputs.items():
        relay_comp = comp_by_id.get(relay_id)
        contacts   = [comp_by_id[i] for i in inp_ids if i in comp_by_id]
        placed_inputs.update(inp_ids)
        placed_relays.add(relay_id)
        rungs.append({"contacts": contacts, "coil": relay_comp, "nc": True,
                      "section": "SAFETY INPUT CHAIN" if first_in else ""})
        first_in = False

    leftover_in = [c for c in col0 if str(_g(c, "id", "")).strip() not in placed_inputs]
    if leftover_in:
        groups: dict = defaultdict(list)
        for c in leftover_in:
            sg = str(_g(c, "series_group", "") or "")
            ch = str(_g(c, "channel",      "") or "")
            groups[sg if sg else (ch if ch else "__all__")].append(c)
        for _, comps in groups.items():
            idx  = len(placed_relays)
            coil = col1[idx] if idx < len(col1) else None
            if coil:
                placed_relays.add(str(_g(coil, "id", "")).strip())
            rungs.append({"contacts": comps, "coil": coil, "nc": True,
                          "section": "SAFETY INPUT CHAIN" if first_in else ""})
            first_in = False

    for c in col1:
        cid = str(_g(c, "id", "")).strip()
        if cid not in placed_relays:
            rungs.append({"contacts": [], "coil": c, "nc": True,
                          "section": "SAFETY INPUT CHAIN" if first_in else ""})
            placed_relays.add(cid)
            first_in = False

    first_out = True
    for relay_id, out_ids in relay_outputs.items():
        relay_comp = comp_by_id.get(relay_id)
        for out_id in out_ids:
            out_comp = comp_by_id.get(out_id)
            if out_comp:
                placed_outputs.add(out_id)
                rungs.append({"contacts": [relay_comp] if relay_comp else [],
                              "coil": out_comp, "nc": False,
                              "section": "OUTPUT CONTACTS" if first_out else ""})
                first_out = False

    for c in col2:
        cid = str(_g(c, "id", "")).strip()
        if cid not in placed_outputs:
            rungs.append({"contacts": [], "coil": c, "nc": True,
                          "section": "OUTPUT CONTACTS" if first_out else ""})
            first_out = False

    return rungs


# ── Ladder SLD SVG builder ─────────────────────────────────────────────────────

def _build_sld_svg(parse_result: dict, review_result: dict) -> str:
    components  = list(_g(parse_result, "components",  []))
    connections = list(_g(parse_result, "connections", []))
    changes     = list(_g(review_result, "changes",    []))

    change_by_id = {_g(ch, "id", i): ch for i, ch in enumerate(changes)}
    renderable   = [c for c in components if _type_to_col(_g(c, "type", "unknown")) is not None]
    change_map   = _map_changes_to_components(renderable, changes)
    rungs        = _build_rungs_for_ladder(renderable, connections, changes)

    if not rungs:
        raise ValueError("No renderable rungs from component/connection data")

    n_secs   = sum(1 for r in rungs if r.get("section"))
    overhead = TITLE_H + 28 + n_secs * LDR_SECTION_GAP + LEGEND_H + 20
    pitch    = max(32, min(LDR_RUNG_PITCH, (MAX_H - overhead) // max(len(rungs), 1)))

    rung_ys: list[int] = []
    cur_y = TITLE_H + 28
    for r in rungs:
        if r.get("section"):
            cur_y += LDR_SECTION_GAP
        rung_ys.append(cur_y)
        cur_y += pitch

    svg_h    = min(MAX_H, max(MIN_H, cur_y + LEGEND_H + 16))
    rail_top = rung_ys[0]
    rail_bot = rung_ys[-1]

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_W} {svg_h}" width="{SVG_W}" height="{svg_h}">'
    )
    parts.append(f'<rect width="{SVG_W}" height="{svg_h}" fill="{C_WHITE}"/>')
    parts.append(f'<rect x="0" y="0" width="{SVG_W}" height="{TITLE_H}" fill="{C_NAVY}"/>')
    parts.append(f'<rect x="0" y="{TITLE_H - 4}" width="{SVG_W}" height="4" fill="{C_LIME}"/>')
    parts.append(
        f'<text x="10" y="22" font-family="Helvetica,Arial,sans-serif" font-size="11" '
        f'font-weight="bold" fill="{C_WHITE}">Safety Circuit Schematic — Redline Review</text>'
    )
    parts.append(
        f'<text x="10" y="38" font-family="Helvetica,Arial,sans-serif" font-size="7.5" '
        f'fill="#AEB6BF">MEX Engineering Group · Redline annotations correspond to '
        f'numbered change items in the review report</text>'
    )
    parts.append(
        f'<text x="{LDR_L_X + 1}" y="{rail_top - 5}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" font-weight="bold" fill="{C_NAVY}">+24VDC</text>'
    )
    parts.append(
        f'<text x="{LDR_L_X + 1}" y="{rail_bot + 14}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" font-weight="bold" fill="{C_NAVY}">0VDC</text>'
    )
    parts.append(
        f'<line x1="{LDR_L_X}" y1="{rail_top}" x2="{LDR_L_X}" y2="{rail_bot}" '
        f'stroke="{C_NAVY}" stroke-width="3"/>'
    )
    parts.append(
        f'<line x1="{LDR_R_X}" y1="{rail_top}" x2="{LDR_R_X}" y2="{rail_bot}" '
        f'stroke="{C_NAVY}" stroke-width="3"/>'
    )

    for rung, wy in zip(rungs, rung_ys):
        contacts  = rung.get("contacts", [])
        coil_comp = rung.get("coil")
        nc        = rung.get("nc", True)
        section   = rung.get("section", "")

        if section:
            sl_y = wy - 8
            parts.append(
                f'<rect x="{LDR_L_X + 2}" y="{sl_y - 11}" width="154" height="13" rx="2" fill="{C_NAVY}"/>'
                f'<text x="{LDR_L_X + 6}" y="{sl_y}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="7.5" font-weight="bold" fill="{C_WHITE}">{_xe(section)}</text>'
            )

        rung_rl = any(change_map.get(str(_g(c, "id", "")).strip()) for c in contacts)
        if coil_comp:
            rung_rl = rung_rl or bool(change_map.get(str(_g(coil_comp, "id", "")).strip()))

        wire_col  = C_RED  if rung_rl else C_NAVY
        wire_dash = 'stroke-dasharray="5,3"' if rung_rl else ""
        wire_w    = "1.6"  if rung_rl else "1.4"
        coil_left  = LDR_COIL_CX - LDR_COIL_BW
        coil_right = LDR_COIL_CX + LDR_COIL_BW

        x_start = LDR_L_X + 10
        x_end   = coil_left - 12 if coil_comp else LDR_R_X - 6
        n = len(contacts)
        if n > 0:
            span     = x_end - x_start
            step     = max(26, min(LDR_CONTACT_PITCH, span // n))
            total_w  = n * step
            cx0      = x_start + max(0, (span - total_w) // 2) + step // 2
            contact_xs = [cx0 + i * step for i in range(n)]
        else:
            contact_xs = []

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

        for comp_c, cx_c in zip(contacts, contact_xs):
            cid    = str(_g(comp_c, "id", "")).strip()
            ch_ids = change_map.get(cid, [])
            rl_c   = bool(ch_ids)
            if nc:
                parts.append(_ldr_sym_for_comp(comp_c, cx_c, wy, rl_c))
            else:
                parts.append(_ldr_no(cx_c, wy, C_RED if rl_c else C_NAVY))
            col_t = C_RED if rl_c else C_GREY
            lbl_y = wy + LDR_CH + 9
            parts.append(
                f'<text x="{cx_c}" y="{lbl_y}" font-family="Helvetica,Arial,sans-serif" '
                f'font-size="{LDR_LBL_FS}" font-weight="bold" fill="{col_t}" '
                f'text-anchor="middle">{_xe(_trunc(cid, 9))}</text>'
            )
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

        if coil_comp:
            cid    = str(_g(coil_comp, "id", "")).strip()
            ch_ids = change_map.get(cid, [])
            rl_c   = bool(ch_ids)
            parts.append(_ldr_coil_for_comp(coil_comp, LDR_COIL_CX, wy, rl_c))
            col_t = C_RED if rl_c else C_GREY
            lbl_y = wy + LDR_COIL_R + 9
            parts.append(
                f'<text x="{LDR_COIL_CX}" y="{lbl_y}" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="{LDR_LBL_FS}" '
                f'font-weight="bold" fill="{col_t}" text-anchor="middle">'
                f'{_xe(_trunc(cid, 10))}</text>'
            )
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

    # Legend
    leg_y = svg_h - LEGEND_H + 2
    parts.append(f'<rect x="0" y="{leg_y - 2}" width="{SVG_W}" height="{LEGEND_H + 2}" fill="{C_LGREY}"/>')
    lx = 8
    parts.append(f'<line x1="{lx}" y1="{leg_y+12}" x2="{lx+26}" y2="{leg_y+12}" stroke="{C_NAVY}" stroke-width="1.2"/>')
    parts.append(_ldr_nc(lx + 13, leg_y + 12, C_NAVY))
    parts.append(
        f'<text x="{lx + 30}" y="{leg_y + 16}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" fill="{C_GREY}">NC contact</text>'
    )
    lx2 = 118
    parts.append(f'<line x1="{lx2}" y1="{leg_y+12}" x2="{lx2+11}" y2="{leg_y+12}" stroke="{C_NAVY}" stroke-width="1.2"/>')
    parts.append(
        f'<circle cx="{lx2+22}" cy="{leg_y+12}" r="11" fill="none" stroke="{C_NAVY}" stroke-width="1.5"/>'
        f'<text x="{lx2+22}" y="{leg_y+15}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="6" fill="{C_NAVY}" text-anchor="middle">K</text>'
        f'<text x="{lx2+37}" y="{leg_y+16}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="7" fill="{C_GREY}">Output coil</text>'
    )
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


# ── Public API ─────────────────────────────────────────────────────────────────

def build_diagram_svg(parsed_dxf, topology: dict, non_conformances: list[dict]) -> str | None:
    """
    Build ladder SLD from ParsedDrawing + topology.
    Returns SVG string, or None if topology has no connections.
    """
    if not topology or not topology.get("connections"):
        log.info("Diagram: no connections in topology — skipping SLD")
        return None

    topo_comp_by_id = {c.get("id", ""): c for c in topology.get("components", [])}

    components = []
    for pc in parsed_dxf.safety_components:
        comp_id     = pc.tag or pc.block_name
        topo_info   = topo_comp_by_id.get(comp_id, {})
        diagram_type = COMPLIANCE_TO_DIAGRAM_TYPE.get(pc.compliance_type, "unknown")
        components.append({
            "id":           comp_id,
            "type":         diagram_type,
            "label":        pc.description or pc.block_name,
            "model":        None,
            "channel":      topo_info.get("channel"),
            "series_group": topo_info.get("series_group"),
        })

    changes = [
        {
            "id":          i + 1,
            "priority":    nc.get("severity", "minor").upper(),
            "description": nc.get("description", ""),
            "action":      nc.get("remediation", ""),
        }
        for i, nc in enumerate(non_conformances)
    ]

    parse_result  = {"components": components, "connections": topology.get("connections", [])}
    review_result = {"changes": changes}

    try:
        svg = _build_sld_svg(parse_result, review_result)
        log.info("SLD generated: %d components, %d connections",
                 len(components), len(topology.get("connections", [])))
        return svg
    except Exception as exc:
        log.error("SLD generation failed: %s", exc, exc_info=True)
        return None


def svg_to_rl_drawing(svg_text: str):
    """Convert SVG string to a ReportLab Drawing for PDF embedding. Returns None on failure."""
    try:
        from svglib.svglib import svg2rlg
        drawing = svg2rlg(io.StringIO(svg_text))
        if drawing is None:
            log.error("svg2rlg returned None")
        return drawing
    except Exception as exc:
        log.error("svg_to_rl_drawing failed: %s", exc)
        return None
