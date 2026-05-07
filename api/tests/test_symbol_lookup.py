"""
Tests for symbol_lookup.py — block name parsing and family map queries.

Block names follow H/V + FAMILY_CODE + digit + optional suffix convention.
Examples: HPB11MTL (horizontal pushbutton, mushroom turn-to-release),
          VLS12 (vertical limit switch, NC), HPX11I (horizontal VFD, inverter output).
"""
import pytest
from services.symbol_lookup import (
    _family_code,
    compliance_type,
    component_type,
    is_safety_relevant,
    lookup_block,
    safety_note,
    tag_prefix,
)


# ---------------------------------------------------------------------------
# Family code extraction
# ---------------------------------------------------------------------------
class TestFamilyCode:
    def test_horizontal_estop_pushbutton(self):
        assert _family_code("HPB11MTL") == "PB"

    def test_vertical_limit_switch(self):
        assert _family_code("VLS12") == "LS"

    def test_vertical_drive(self):
        assert _family_code("HPX11I") == "PX"

    def test_horizontal_ammeter(self):
        assert _family_code("HAM1") == "AM"

    def test_unknown_no_hv_prefix_returns_none(self):
        assert _family_code("XUNKNOWN") is None

    def test_empty_string_returns_none(self):
        assert _family_code("") is None

    def test_lowercase_not_matched(self):
        # Convention is uppercase; lowercase fails the regex
        assert _family_code("hpb11") is None

    def test_motor_starter(self):
        assert _family_code("HMS1") == "MS"


# ---------------------------------------------------------------------------
# Block lookup
# ---------------------------------------------------------------------------
class TestLookupBlock:
    def test_known_pushbutton_estop(self):
        entry = lookup_block("VPB11MTL")
        assert entry is not None
        assert entry["type"] == "pushbutton"

    def test_known_ammeter(self):
        entry = lookup_block("HAM1")
        assert entry is not None
        assert entry["type"] == "ammeter"

    def test_known_limit_switch(self):
        entry = lookup_block("HLS12")
        assert entry is not None

    def test_unknown_block_returns_none(self):
        assert lookup_block("XRANDOM999") is None

    def test_no_hv_prefix_returns_none(self):
        assert lookup_block("PB11MTL") is None


# ---------------------------------------------------------------------------
# Safety relevance
# ---------------------------------------------------------------------------
class TestIsSafetyRelevant:
    def test_estop_is_safety_relevant(self):
        assert is_safety_relevant("VPB11MTL") is True

    def test_ammeter_is_not_safety_relevant(self):
        assert is_safety_relevant("HAM1") is False

    def test_limit_switch_is_safety_relevant(self):
        assert is_safety_relevant("HLS12") is True

    def test_drive_is_safety_relevant(self):
        assert is_safety_relevant("HPX11I") is True

    def test_unknown_block_returns_false(self):
        assert is_safety_relevant("XBADBLOCK") is False


# ---------------------------------------------------------------------------
# Compliance type
# ---------------------------------------------------------------------------
class TestComplianceType:
    def test_estop_is_e_stop(self):
        assert compliance_type("VPB11MTL") == "e_stop"

    def test_limit_switch_is_interlock(self):
        assert compliance_type("HLS12") == "interlock"

    def test_drive_is_drive(self):
        assert compliance_type("HPX11I") == "drive"

    def test_unknown_block_is_other(self):
        assert compliance_type("XBADBLOCK") == "other"

    def test_ammeter_is_other(self):
        assert compliance_type("HAM1") == "other"


# ---------------------------------------------------------------------------
# Safety notes
# ---------------------------------------------------------------------------
class TestSafetyNote:
    def test_drive_has_sto_safety_note(self):
        note = safety_note("HPX11I")
        assert note is not None
        assert "STO" in note

    def test_limit_switch_has_safety_note(self):
        note = safety_note("HLS12")
        assert note is not None
        assert len(note) > 10

    def test_unknown_block_has_no_note(self):
        assert safety_note("XBADBLOCK") is None

    def test_ammeter_has_no_note(self):
        assert safety_note("HAM1") is None


# ---------------------------------------------------------------------------
# Tag prefix
# ---------------------------------------------------------------------------
class TestTagPrefix:
    def test_ammeter_prefix_is_pa(self):
        assert tag_prefix("HAM1") == "PA"

    def test_limit_switch_prefix_is_sq(self):
        assert tag_prefix("HLS12") == "SQ"

    def test_drive_prefix_is_uf(self):
        assert tag_prefix("HPX11I") == "UF"

    def test_unknown_block_prefix_is_question(self):
        assert tag_prefix("XBADBLOCK") == "?"


# ---------------------------------------------------------------------------
# Component type
# ---------------------------------------------------------------------------
class TestComponentType:
    def test_pushbutton_type(self):
        assert component_type("VPB11MTL") == "pushbutton"

    def test_ammeter_type(self):
        assert component_type("HAM1") == "ammeter"

    def test_drive_type(self):
        assert component_type("HPX11I") == "variable_speed_drive"

    def test_unknown_type(self):
        assert component_type("XBADBLOCK") == "unknown"
