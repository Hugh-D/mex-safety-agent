from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "safety_distances.json", "r", encoding="utf-8") as _fh:
    _SD = json.load(_fh)


# ---------------------------------------------------------------------------
# Reaching upward (clause 4.2.1)
# ---------------------------------------------------------------------------

def reaching_upward_threshold(risk_level: str) -> int:
    """Return the minimum hazard zone height (mm) above which no horizontal safety distance is needed."""
    key = "high_risk_mm" if risk_level == "high" else "low_risk_mm"
    return _SD["reaching_upward"][key]


# ---------------------------------------------------------------------------
# Reaching over (clause 4.2.2, Tables 1 & 2)
# ---------------------------------------------------------------------------

def _snap_floor(value: float, tabulated: List[int]) -> Optional[int]:
    """Return the largest tabulated value <= value, or None if value < all tabulated values."""
    candidates = [t for t in tabulated if t <= value]
    return max(candidates) if candidates else None


def reaching_over(a_mm: float, b_mm: float, risk_level: str) -> Dict[str, Any]:
    """
    Determine required horizontal safety distance c (mm) for reaching over a protective structure.

    a_mm: height of nearest hazard point above reference plane (mm)
    b_mm: height of protective structure above reference plane (mm)
    risk_level: 'low' or 'high'

    Returns dict with c_mm, snapped a/b used, and any advisory flags.
    """
    table = _SD["reaching_over"]["high_risk" if risk_level == "high" else "low_risk"]
    upward_threshold = reaching_upward_threshold(risk_level)

    flags: List[str] = []

    # If hazard is at or above the upward-reach threshold, no horizontal distance needed
    if a_mm >= upward_threshold:
        return {
            "c_mm": 0,
            "a_mm_used": a_mm,
            "b_mm_used": b_mm,
            "risk_level": risk_level,
            "flags": [f"Hazard zone >= {upward_threshold} mm — upward reach check applies (clause 4.2.1). No horizontal safety distance required."],
        }

    b_values: List[int] = table["b_values_mm"]
    rows: List[Dict] = table["rows"]
    a_values: List[int] = sorted(r["a_mm"] for r in rows)

    # Snap b DOWN (floor). A lower structure always requires an equal or greater
    # distance c, so flooring b is conservative.
    b_snapped = _snap_floor(b_mm, b_values)
    if b_snapped is None:
        return {
            "c_mm": None,
            "a_mm_used": a_mm,
            "b_mm_used": b_mm,
            "risk_level": risk_level,
            "flags": [f"Protective structure height {b_mm} mm is below the minimum tabulated value ({min(b_values)} mm). Structure is insufficient — additional safety measures required."],
            "error": "b_below_minimum",
        }
    b_idx = b_values.index(b_snapped)

    def _c_for_a(a_val: int) -> int:
        row = next(r for r in rows if r["a_mm"] == a_val)
        return row["c_mm"][b_idx]

    # Snap a using the standard's rule: when a value lies between two tabulated
    # rows, use whichever adjacent row gives the GREATER safety distance
    # (AS/NZS 4024.1801 / ISO 13857 — no interpolation; select the value
    # resulting in the higher risk). c is not monotonic in a, so flooring
    # alone is NOT conservative.
    if a_mm in a_values:
        a_snapped = next(v for v in a_values if v == a_mm)
        c_mm = _c_for_a(a_snapped)
    else:
        a_floor = _snap_floor(a_mm, a_values)
        a_ceil_candidates = [v for v in a_values if v >= a_mm]
        a_ceil = min(a_ceil_candidates) if a_ceil_candidates else None

        candidates: List[int] = []
        if a_floor is not None:
            candidates.append(a_floor)
        if a_ceil is not None:
            candidates.append(a_ceil)
        if not candidates:
            candidates = [a_values[0]]
            flags.append(f"a_mm ({a_mm}) outside tabulated range — using a={a_values[0]} row.")

        # Choose the adjacent row that yields the larger (more conservative) c.
        a_snapped = max(candidates, key=_c_for_a)
        c_mm = _c_for_a(a_snapped)
        flags.append(
            f"a_mm ({a_mm}) not tabulated — adjacent rows evaluated, "
            f"using a={a_snapped} mm which gives the greater safety distance "
            f"(AS/NZS 4024.1801 rule: no interpolation, select the higher-risk value)."
        )

    if risk_level == "high" and b_mm < 1400:
        flags.append("Protective structures < 1400 mm should not be used without additional safety measures (Table 2 note).")

    if b_mm != b_snapped:
        flags.append(f"b_mm ({b_mm}) not tabulated — snapped down to {b_snapped} mm (conservative: lower structure requires greater distance).")

    return {
        "c_mm": c_mm,
        "a_mm_used": a_snapped,
        "b_mm_used": b_snapped,
        "risk_level": risk_level,
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Reaching around (clause 4.2.3, Table 3)
# ---------------------------------------------------------------------------

def get_reaching_around_table() -> List[Dict[str, Any]]:
    return _SD["reaching_around"]["entries"]


def reaching_around(limitation_key: str) -> Dict[str, Any]:
    """
    Return the radial safety distance sr for reaching around with a given movement limitation.
    limitation_key: 'shoulder_armpit' | 'elbow' | 'wrist' | 'knuckle'
    """
    for entry in _SD["reaching_around"]["entries"]:
        if entry["key"] == limitation_key:
            return entry
    raise ValueError(f"Unknown limitation key: {limitation_key!r}. Valid: shoulder_armpit, elbow, wrist, knuckle")


# ---------------------------------------------------------------------------
# Reaching around with additional structures (clause 4.2.5, Table 6)
# ---------------------------------------------------------------------------

def get_reaching_around_additional_table() -> List[Dict[str, Any]]:
    return _SD["reaching_around_additional"]["entries"]


# ---------------------------------------------------------------------------
# Reaching through openings — adults (clause 4.2.4.1, Table 4)
# Reaching through openings — children (clause 4.2.4.2, Table 5)
# ---------------------------------------------------------------------------

def _lookup_through(ranges: List[Dict], e_mm: float, shape: str) -> Dict[str, Any]:
    shape = shape.lower()
    if shape not in ("slot", "square", "round"):
        raise ValueError(f"shape must be 'slot', 'square', or 'round', got {shape!r}")

    for r in ranges:
        lo = r.get("e_min_mm", 0)
        hi = r["e_max_mm"]
        if lo < e_mm <= hi or (lo == 0 and e_mm <= hi):
            sr_key = f"{shape}_sr_mm"
            sr = r.get(sr_key)
            result: Dict[str, Any] = {
                "sr_mm": sr,
                "body_part": r["body_part"],
                "e_mm": e_mm,
                "shape": shape,
            }
            note_key = f"{shape}_note" if shape == "slot" else None
            if note_key and note_key in r:
                result["note"] = r[note_key]
            elif "slot_note" in r and shape == "slot":
                result["note"] = r["slot_note"]
            return result

    raise ValueError(f"Opening size e={e_mm} mm is outside the table range.")


def reaching_through_adults(e_mm: float, shape: str) -> Dict[str, Any]:
    """
    Safety distance sr (mm) for reaching through an opening — persons 14 years and above (Table 4).
    e_mm: opening dimension (mm). shape: 'slot' | 'square' | 'round'.
    For e > 120 mm, use reaching_over instead.
    """
    ranges = _SD["reaching_through_adults"]["ranges"]
    if e_mm > 120:
        return {
            "sr_mm": None,
            "e_mm": e_mm,
            "shape": shape,
            "note": "Opening > 120 mm — use reaching_over (clause 4.2.2) values instead.",
        }
    return _lookup_through(ranges, e_mm, shape)


def reaching_through_children(e_mm: float, shape: str) -> Dict[str, Any]:
    """
    Safety distance sr (mm) for reaching through an opening — persons 3 years and above (Table 5).
    e_mm: opening dimension (mm). shape: 'slot' | 'square' | 'round'.
    For e > 100 mm, use reaching_over instead.
    """
    ranges = _SD["reaching_through_children"]["ranges"]
    if e_mm > 100:
        return {
            "sr_mm": None,
            "e_mm": e_mm,
            "shape": shape,
            "note": "Opening > 100 mm — use reaching_over (clause 4.2.2) values instead.",
        }
    return _lookup_through(ranges, e_mm, shape)


# ---------------------------------------------------------------------------
# Lower limb through openings (clause 4.3, Table 7)
# ---------------------------------------------------------------------------

def lower_limb_through(e_mm: float, shape: str) -> Dict[str, Any]:
    """
    Safety distance sr (mm) for reaching through openings by lower limbs (Table 7).
    Use only where upper limb access through the opening is not foreseeable.
    shape: 'slot' | 'square_round'
    """
    shape = shape.lower()
    if shape not in ("slot", "square_round"):
        raise ValueError(f"shape must be 'slot' or 'square_round', got {shape!r}")

    ranges = _SD["lower_limb_through"]["ranges"]
    for r in ranges:
        lo = r.get("e_min_mm", 0)
        hi = r["e_max_mm"]
        if lo < e_mm <= hi or (lo == 0 and e_mm <= hi):
            if shape == "slot":
                sr = r.get("slot_sr_mm")
                result: Dict[str, Any] = {
                    "sr_mm": sr,
                    "body_part": r["body_part"],
                    "e_mm": e_mm,
                    "shape": shape,
                }
                if sr is None:
                    result["note"] = r.get("slot_sr_note", "Not admissible")
                elif "slot_note" in r:
                    result["note"] = r["slot_note"]
            else:
                result = {
                    "sr_mm": r["square_round_sr_mm"],
                    "body_part": r["body_part"],
                    "e_mm": e_mm,
                    "shape": shape,
                }
            return result

    if e_mm > 240:
        return {
            "sr_mm": None,
            "e_mm": e_mm,
            "shape": shape,
            "note": "Opening > 240 mm (square/round) or > 180 mm (slot) — whole body access possible. Guard design is inadequate.",
        }
    raise ValueError(f"Opening size e={e_mm} mm is outside the lower limb table range.")


# ---------------------------------------------------------------------------
# Impede lower limbs — Annex B, Table B.1
# ---------------------------------------------------------------------------

def impede_lower_limbs(h_mm: float, case: int) -> Dict[str, Any]:
    """
    Horizontal distance l (mm) to impede free access of lower limbs under a protective structure.
    h_mm: height from ground/reference plane to the protective structure (mm).
    case: 1 (single structure, person outside), 2 (person between two parallel structures),
          3 (person at corner between two perpendicular structures).

    NOTE: These are NOT safety distances. Additional precautions may be required.
    """
    if case not in (1, 2, 3):
        raise ValueError(f"case must be 1, 2, or 3, got {case!r}")

    ranges = _SD["impede_lower_limbs"]["ranges"]
    key = f"case{case}_l_mm"

    for r in ranges:
        lo = r.get("h_min_mm", 0)
        hi = r["h_max_mm"]
        if lo < h_mm <= hi or (lo == 0 and h_mm <= hi):
            return {
                "l_mm": r[key],
                "h_mm": h_mm,
                "case": case,
                "note": "These are NOT safety distances. Additional precautions may be required (Annex B).",
            }

    if h_mm > 1000:
        return {
            "l_mm": None,
            "h_mm": h_mm,
            "case": case,
            "note": "h_mm > 1000 mm — outside table range. Refer to engineer judgement.",
        }
    raise ValueError(f"h_mm={h_mm} is outside the Annex B table range.")


# ---------------------------------------------------------------------------
# Raw data accessor (for lookup endpoints)
# ---------------------------------------------------------------------------

def get_safety_distances_data() -> Dict[str, Any]:
    return _SD
