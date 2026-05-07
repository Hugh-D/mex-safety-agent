"""
Tests for dxf_parser.py helper functions and data structures.

Full integration tests (parse_dxf with a real drawing) are out of scope here
because the MEX symbol library DXF is a block definition file, not a drawing
with model-space INSERT entities. Tests use direct dataclass construction and
private helper functions to verify parsing logic.
"""
import pytest
from services.dxf_parser import (
    ParsedComponent,
    ParsedDrawing,
    _pick_attr,
    _ATTR_TAG,
    _ATTR_DESC,
    _ATTR_LOC,
)


# ---------------------------------------------------------------------------
# Attribute picker
# ---------------------------------------------------------------------------
class TestPickAttr:
    def test_picks_matching_key(self):
        # Only one key present — no set-ordering ambiguity
        attribs = {"TAG": "SF01"}
        assert _pick_attr(attribs, _ATTR_TAG) == "SF01"

    def test_falls_back_to_second_key(self):
        attribs = {"TAG1": "SF02"}
        assert _pick_attr(attribs, _ATTR_TAG) == "SF02"

    def test_tags_key_as_fallback(self):
        attribs = {"TAGS": "SF03"}
        assert _pick_attr(attribs, _ATTR_TAG) == "SF03"

    def test_returns_empty_when_no_match(self):
        assert _pick_attr({}, _ATTR_TAG) == ""

    def test_strips_whitespace(self):
        attribs = {"DESC": "  E-Stop   "}
        assert _pick_attr(attribs, _ATTR_DESC) == "E-Stop"

    def test_loc_attribute(self):
        attribs = {"LOC": "Panel A"}
        assert _pick_attr(attribs, _ATTR_LOC) == "Panel A"

    def test_locbox_fallback(self):
        attribs = {"LOCBOX": "Zone 1"}
        assert _pick_attr(attribs, _ATTR_LOC) == "Zone 1"

    def test_pos_fallback(self):
        attribs = {"POS": "Row 3"}
        assert _pick_attr(attribs, _ATTR_LOC) == "Row 3"


# ---------------------------------------------------------------------------
# ParsedDrawing data model
# ---------------------------------------------------------------------------
def _make_component(safety_relevant: bool, tag: str = "SF01") -> ParsedComponent:
    return ParsedComponent(
        block_name="VPB11MTL" if safety_relevant else "HAM1",
        tag=tag,
        description="E-Stop" if safety_relevant else "Ammeter",
        location="Panel 1",
        x=10.0,
        y=20.0,
        component_type="pushbutton" if safety_relevant else "ammeter",
        compliance_type="e_stop" if safety_relevant else "other",
        safety_relevant=safety_relevant,
        safety_note="Check PLr" if safety_relevant else None,
        orientation="vertical" if safety_relevant else "horizontal",
    )


class TestParsedDrawing:
    def test_safety_components_filters_correctly(self):
        safe = _make_component(True, "SF01")
        nonsafe = _make_component(False, "PA01")
        drawing = ParsedDrawing("test.dxf", "AC1032", 2, components=[safe, nonsafe])
        assert len(drawing.safety_components) == 1
        assert drawing.safety_components[0].tag == "SF01"

    def test_empty_drawing(self):
        drawing = ParsedDrawing("empty.dxf", "AC1032", 0)
        assert drawing.safety_components == []
        assert drawing.components == []

    def test_context_text_includes_filename(self):
        drawing = ParsedDrawing("my_drawing.dxf", "AC1032", 0)
        ctx = drawing.as_context_text()
        assert "my_drawing.dxf" in ctx

    def test_context_text_includes_safety_components(self):
        safe = _make_component(True, "SF01")
        drawing = ParsedDrawing("test.dxf", "AC1032", 1, components=[safe])
        ctx = drawing.as_context_text()
        assert "SAFETY-RELEVANT" in ctx
        assert "SF01" in ctx

    def test_context_text_includes_unknown_blocks(self):
        drawing = ParsedDrawing("test.dxf", "AC1032", 3, unknown_blocks=["XFOO", "XBAR"])
        ctx = drawing.as_context_text()
        assert "UNRECOGNISED" in ctx
        assert "XFOO" in ctx

    def test_context_text_shows_total_inserts(self):
        drawing = ParsedDrawing("test.dxf", "AC1032", 42)
        ctx = drawing.as_context_text()
        assert "42" in ctx

    def test_all_safety_no_nonsafety_section(self):
        safe = _make_component(True)
        drawing = ParsedDrawing("test.dxf", "AC1032", 1, components=[safe])
        ctx = drawing.as_context_text()
        assert "NON-SAFETY" not in ctx

    def test_unknown_blocks_capped_at_20_in_context(self):
        blocks = [f"XBLOCK{i:03d}" for i in range(30)]
        drawing = ParsedDrawing("test.dxf", "AC1032", 30, unknown_blocks=blocks)
        ctx = drawing.as_context_text()
        assert "and 10 more" in ctx
