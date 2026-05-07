from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import ezdxf

from services import symbol_lookup


@dataclass
class ParsedComponent:
    block_name: str
    tag: str                    # component reference label (e.g. "SF01", "KF03")
    description: str            # engineer-entered description attribute
    location: str               # panel / zone reference attribute
    x: float
    y: float
    component_type: str         # from family map (e.g. "pushbutton", "limit_switch")
    compliance_type: str        # from family map (e.g. "e_stop", "interlock", "drive")
    safety_relevant: bool
    safety_note: str | None
    orientation: str            # "horizontal" | "vertical"


@dataclass
class ParsedDrawing:
    source_filename: str
    dxf_version: str
    total_inserts: int
    components: list[ParsedComponent] = field(default_factory=list)
    unknown_blocks: list[str] = field(default_factory=list)
    library_gaps: list[str] = field(default_factory=list)

    @property
    def safety_components(self) -> list[ParsedComponent]:
        return [c for c in self.components if c.safety_relevant]

    def as_context_text(self) -> str:
        """Render a concise structured summary for injection into a Claude prompt."""
        lines = [
            f"DXF drawing parsed: {self.source_filename}",
            f"Total block inserts: {self.total_inserts}",
            f"Recognised components: {len(self.components)}",
            f"Safety-relevant components: {len(self.safety_components)}",
            "",
        ]

        if self.safety_components:
            lines.append("SAFETY-RELEVANT COMPONENTS (from symbol library):")
            seen_notes: set[str] = set()
            for c in self.safety_components:
                lines.append(
                    f"  [{c.compliance_type.upper()}] {c.tag or c.block_name}"
                    f"  type={c.component_type}"
                    f"  block={c.block_name}"
                    f"  loc=({c.x:.1f},{c.y:.1f})"
                    f"  desc={c.description or '-'}"
                )
            # Emit each unique safety note once, grouped after the list
            notes_by_type: dict[str, str] = {}
            for c in self.safety_components:
                if c.safety_note and c.compliance_type not in notes_by_type:
                    notes_by_type[c.compliance_type] = c.safety_note
            if notes_by_type:
                lines.append("")
                lines.append("SAFETY NOTES (apply to all instances of each type):")
                for ctype, note in notes_by_type.items():
                    lines.append(f"  [{ctype.upper()}] {note}")
            lines.append("")

        non_safety = [c for c in self.components if not c.safety_relevant]
        if non_safety:
            lines.append(f"NON-SAFETY COMPONENTS: {len(non_safety)} items")
            # Summarise by type rather than listing every one
            from collections import Counter
            counts = Counter(c.component_type for c in non_safety)
            for typ, cnt in counts.most_common():
                lines.append(f"  {typ}: {cnt}")
            lines.append("")

        if self.unknown_blocks:
            unique = sorted(set(self.unknown_blocks))
            lines.append(f"UNRECOGNISED BLOCKS ({len(unique)} unique — not in MEX symbol library):")
            for b in unique[:20]:
                lines.append(f"  {b}")
            if len(unique) > 20:
                lines.append(f"  ... and {len(unique) - 20} more")
            lines.append("")

        if self.library_gaps:
            lines.append("SYMBOL LIBRARY GAPS (safety-relevant types with no dedicated symbol):")
            for g in self.library_gaps:
                lines.append(f"  — {g}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Attribute tag names used by MEX DXF library (layer names in the DXF match)
# ---------------------------------------------------------------------------
_ATTR_TAG  = {"TAG",  "TAG1", "TAGS"}       # component reference (e.g. "SF01")
_ATTR_DESC = {"DESC", "DESCRIPTION", "DESCCHILD"}  # description text
_ATTR_LOC  = {"LOC",  "LOCBOX", "POS"}      # location / zone


def _pick_attr(attribs: dict[str, str], keys: set[str]) -> str:
    for k in keys:
        if k in attribs:
            return attribs[k].strip()
    return ""


def parse_dxf(dxf_bytes: bytes, source_filename: str = "drawing.dxf") -> ParsedDrawing:
    """
    Parse a DXF file and classify every INSERT entity using the MEX symbol library.

    Returns a ParsedDrawing with structured component data and a context text
    suitable for injecting into a Claude compliance prompt.
    """
    import os, tempfile
    # ezdxf.readfile() handles embedded binary data correctly; write to a temp file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".dxf")
    try:
        os.write(tmp_fd, dxf_bytes)
        os.close(tmp_fd)
        doc = ezdxf.readfile(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    msp = doc.modelspace()

    result = ParsedDrawing(
        source_filename=source_filename,
        dxf_version=doc.dxfversion,
        total_inserts=0,
        library_gaps=symbol_lookup.all_safety_gaps(),
    )

    for entity in msp.query("INSERT"):
        result.total_inserts += 1
        block_name: str = entity.dxf.name

        # Collect attribute values keyed by their tag (uppercased)
        attribs: dict[str, str] = {
            a.dxf.tag.upper(): a.dxf.text
            for a in entity.attribs
        }

        tag_val  = _pick_attr(attribs, _ATTR_TAG)
        desc_val = _pick_attr(attribs, _ATTR_DESC)
        loc_val  = _pick_attr(attribs, _ATTR_LOC)

        try:
            pos = entity.dxf.insert
            x, y = float(pos.x), float(pos.y)
        except Exception:
            x, y = 0.0, 0.0

        orientation = "horizontal" if block_name.startswith("H") else "vertical"

        entry = symbol_lookup.lookup_block(block_name)
        if entry is None:
            result.unknown_blocks.append(block_name)
            continue

        result.components.append(
            ParsedComponent(
                block_name=block_name,
                tag=tag_val,
                description=desc_val,
                location=loc_val,
                x=x,
                y=y,
                component_type=entry["type"],
                compliance_type=entry["compliance_type"],
                safety_relevant=bool(entry.get("safety_relevant")),
                safety_note=entry.get("safety_note"),
                orientation=orientation,
            )
        )

    return result
