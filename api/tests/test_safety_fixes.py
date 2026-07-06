"""Regression tests for the 2026-07 safety-correctness fix set.

Covers:
1. Reaching-over snapping must never understate the required distance.
2. HRN inputs restricted to published table values.
3. Risk bands contiguous — no gap between 3.999 and 4; single threshold of 4.
4. Server-side hazard verification catches tampered scores/bands.
5. AI HRN suggestions snapped UP (conservative) when invalid.
6. _parse_json rejects non-JSON instead of guessing.
"""
import pytest

from services.safety_distance import reaching_over
from services.hrn_plr import (
    ALLOWED_VALUES,
    calculate_hrn,
    risk_band_for_score,
    get_hrn_tables,
    verify_hazards,
)


# ---------------------------------------------------------------------------
# 1. Reaching over — conservative snapping of a
# ---------------------------------------------------------------------------
class TestReachingOverConservative:
    def test_rising_region_snaps_up(self):
        # a=300, b=1000, high risk: floor row (200) gives 1200; ceil row (400)
        # gives 1400. Standard rule: use the greater distance.
        result = reaching_over(300, 1000, "high")
        assert result["c_mm"] == 1400
        assert result["a_mm_used"] == 400

    def test_falling_region_still_conservative(self):
        # a=2500, b=1000, high risk: rows 2400 (c=1100) and 2600 (c=900).
        # Greater distance wins → 1100 from the 2400 row.
        result = reaching_over(2500, 1000, "high")
        assert result["c_mm"] == 1100
        assert result["a_mm_used"] == 2400

    def test_exact_row_unchanged(self):
        result = reaching_over(1400, 1000, "high")
        assert result["c_mm"] == 1500
        assert result["a_mm_used"] == 1400

    def test_never_less_than_either_adjacent_row(self):
        # Property check across the whole high-risk table.
        from services.safety_distance import _SD
        table = _SD["reaching_over"]["high_risk"]
        rows = sorted(table["rows"], key=lambda r: r["a_mm"])
        b_values = table["b_values_mm"]
        for i in range(len(rows) - 1):
            lo, hi = rows[i], rows[i + 1]
            mid_a = (lo["a_mm"] + hi["a_mm"]) / 2
            for b_idx, b in enumerate(b_values):
                result = reaching_over(mid_a, b, "high")
                if result["c_mm"] is None:
                    continue
                required = max(lo["c_mm"][b_idx], hi["c_mm"][b_idx])
                assert result["c_mm"] >= required, (
                    f"a={mid_a}, b={b}: got {result['c_mm']}, adjacent rows require {required}"
                )

    def test_b_below_minimum_still_errors(self):
        result = reaching_over(1400, 500, "high")
        assert result["error"] == "b_below_minimum"
        assert result["c_mm"] is None


# ---------------------------------------------------------------------------
# 2. HRN input validation
# ---------------------------------------------------------------------------
class TestHRNInputValidation:
    def test_valid_values_pass(self):
        assert calculate_hrn(8, 2.5, 15, 2) == 600

    def test_invalid_lo_rejected(self):
        with pytest.raises(ValueError, match="LO=7"):
            calculate_hrn(7, 2.5, 15, 2)

    def test_invalid_fe_rejected(self):
        with pytest.raises(ValueError, match="FE=3.2"):
            calculate_hrn(8, 3.2, 15, 2)

    def test_all_allowed_combinations_have_a_band(self):
        # Every legal parameter combination must map to a defined band.
        for lo in ALLOWED_VALUES["LO"]:
            for fe in ALLOWED_VALUES["FE"]:
                for dph in ALLOWED_VALUES["DPH"]:
                    for np_ in ALLOWED_VALUES["NP"]:
                        band = risk_band_for_score(calculate_hrn(lo, fe, dph, np_))
                        assert band["label"] != "Unknown"


# ---------------------------------------------------------------------------
# 3. Band contiguity and single threshold
# ---------------------------------------------------------------------------
class TestBandsAndThreshold:
    def test_no_gap_at_four(self):
        assert risk_band_for_score(3.9995)["label"] == "Very Low"
        assert risk_band_for_score(4.0)["label"] == "Needs Review"

    def test_threshold_is_four(self):
        assert get_hrn_tables()["acceptance_threshold"] == 4

    def test_four_is_not_acceptable(self):
        assert risk_band_for_score(4.0)["acceptable"] is False

    def test_just_below_four_is_acceptable(self):
        assert risk_band_for_score(3.999)["acceptable"] is True


# ---------------------------------------------------------------------------
# 4. Server-side hazard verification
# ---------------------------------------------------------------------------
class _P:
    def __init__(self, LO, FE, DPH, NP):
        self.LO, self.FE, self.DPH, self.NP = LO, FE, DPH, NP


class _H:
    def __init__(self, **kw):
        self.id = kw.get("id", "H01")
        self.hrn_before = kw.get("hrn_before")
        self.hrn_score_before = kw.get("hrn_score_before")
        self.risk_band_before = kw.get("risk_band_before")
        self.hrn_after = kw.get("hrn_after")
        self.hrn_score_after = kw.get("hrn_score_after")
        self.risk_band_after = kw.get("risk_band_after")


class TestVerifyHazards:
    def test_correct_hazard_passes(self):
        h = _H(hrn_before=_P(8, 2.5, 15, 2), hrn_score_before=600.0, risk_band_before="Extreme")
        assert verify_hazards([h]) == []

    def test_tampered_score_caught(self):
        h = _H(hrn_before=_P(8, 2.5, 15, 2), hrn_score_before=3.0, risk_band_before="Very Low")
        errors = verify_hazards([h])
        assert errors and "does not match" in errors[0]

    def test_wrong_band_caught(self):
        h = _H(hrn_before=_P(8, 2.5, 15, 2), hrn_score_before=600.0, risk_band_before="Low")
        errors = verify_hazards([h])
        assert errors and "risk band" in errors[0]

    def test_invalid_parameter_caught(self):
        h = _H(hrn_before=_P(7, 2.5, 15, 2), hrn_score_before=525.0, risk_band_before="Extreme")
        errors = verify_hazards([h])
        assert errors and "LO=7" in errors[0]


# ---------------------------------------------------------------------------
# 5. AI HRN suggestion sanitisation (conservative snap-up)
# ---------------------------------------------------------------------------
class TestAISuggestionSanitisation:
    def test_invalid_value_snapped_up(self):
        from services.claude_service import _sanitise_hrn_suggestions
        result = {"hrn_suggestions": {"LO": {"value": 6, "justification": "x"}}}
        _sanitise_hrn_suggestions(result)
        assert result["hrn_suggestions"]["LO"]["value"] == 8
        assert any("snapped UP" in f for f in result["flags"])

    def test_valid_value_untouched(self):
        from services.claude_service import _sanitise_hrn_suggestions
        result = {"hrn_suggestions": {"FE": {"value": 2.5, "justification": "daily"}}}
        _sanitise_hrn_suggestions(result)
        assert result["hrn_suggestions"]["FE"]["value"] == 2.5
        assert "flags" not in result or result["flags"] == []


# ---------------------------------------------------------------------------
# 6. AI JSON parsing never guesses
# ---------------------------------------------------------------------------
class TestParseJson:
    def test_plain_json(self):
        from services.claude_service import _parse_json
        assert _parse_json('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        from services.claude_service import _parse_json
        assert _parse_json('```json\n{"a": 1}\n```') == {"a": 1}

    def test_prose_wrapped_json(self):
        from services.claude_service import _parse_json
        assert _parse_json('Here is the result: {"a": 1} — done.') == {"a": 1}

    def test_garbage_rejected(self):
        from services.claude_service import _parse_json
        with pytest.raises(ValueError):
            _parse_json("no json here at all")
