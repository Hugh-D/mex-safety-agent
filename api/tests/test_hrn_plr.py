"""
Tests for deterministic HRN calculation and PLr lookup.

These cover every band boundary, the critical Needs Review zone (ED-001),
all eight PLr risk graph entries, and invalid input handling.
Auto-acceptable threshold: score < 4 (Acceptable or Very Low). Scores 4–6 require engineer review.
"""
import pytest
from services.hrn_plr import calculate_hrn, risk_band_for_score, calculate_plr


# ---------------------------------------------------------------------------
# HRN calculation
# ---------------------------------------------------------------------------
class TestCalculateHRN:
    def test_unity_product(self):
        assert calculate_hrn(1, 1, 1, 1) == 1.0

    def test_max_catalogue_values(self):
        # LO=15, FE=5, DPH=15, NP=12 → 13500
        assert calculate_hrn(15, 5, 15, 12) == 13500.0

    def test_minimum_realistic_values(self):
        # LO=0.033 (almost impossible), FE=0.5 (annually), DPH=0.1 (scratch), NP=1
        result = calculate_hrn(0.033, 0.5, 0.1, 1)
        assert result == round(0.033 * 0.5 * 0.1 * 1, 3)

    def test_typical_site_walk_values(self):
        # LO=2, FE=2.5, DPH=8, NP=2 → 80.0
        assert calculate_hrn(2, 2.5, 8, 2) == 80.0

    def test_rounding_to_3_decimal_places(self):
        result = calculate_hrn(1.5, 2.5, 4, 2)
        assert result == round(1.5 * 2.5 * 4 * 2, 3)

    def test_returns_float(self):
        assert isinstance(calculate_hrn(1, 1, 1, 1), float)


# ---------------------------------------------------------------------------
# Risk band lookup — boundaries (ED-001)
#
# Iteration order determines overlap resolution (first match wins):
#   Acceptable:   [0,    1]
#   Very Low:     [1,  3.999]  ← HRN=1 hits Acceptable first; scores <4 are auto-acceptable
#   Needs Review: [4,    6]    ← engineer judgment required (not auto-acceptable)
#   Low:          [6,   10]
#   Significant:  [10,  50]
#   High:         [50, 100]
#   Very High:    [100, 500]
#   Extreme:      [500, 1000]
#   Unacceptable: [1000, ∞)
# ---------------------------------------------------------------------------
class TestRiskBandLookup:
    def test_score_zero(self):
        b = risk_band_for_score(0)
        assert b["label"] == "Acceptable"
        assert b["acceptable"] is True

    def test_midpoint_acceptable(self):
        assert risk_band_for_score(0.5)["label"] == "Acceptable"

    def test_boundary_1_exact_returns_acceptable(self):
        # 1 matches Acceptable (max=1) before Very Low (min=1) — first match wins
        b = risk_band_for_score(1.0)
        assert b["label"] == "Acceptable"
        assert b["acceptable"] is True

    def test_just_above_1_returns_very_low(self):
        b = risk_band_for_score(1.001)
        assert b["label"] == "Very Low"
        assert b["acceptable"] is True

    def test_midpoint_very_low(self):
        assert risk_band_for_score(3)["label"] == "Very Low"

    # --- Needs Review zone (ED-001) ---
    def test_needs_review_lower_boundary(self):
        """Score=4 is the start of Needs Review; not auto-acceptable."""
        b = risk_band_for_score(4.0)
        assert b["label"] == "Needs Review"
        assert b["acceptable"] is False

    def test_needs_review_midpoint(self):
        assert risk_band_for_score(5.0)["label"] == "Needs Review"

    def test_needs_review_upper_boundary(self):
        b = risk_band_for_score(6.0)
        assert b["label"] == "Needs Review"
        assert b["acceptable"] is False

    def test_just_above_needs_review_is_low(self):
        b = risk_band_for_score(6.001)
        assert b["label"] == "Low"
        assert b["acceptable"] is False

    def test_just_below_needs_review_is_very_low(self):
        b = risk_band_for_score(3.999)
        assert b["label"] == "Very Low"
        assert b["acceptable"] is True

    # --- Further boundary pairs ---
    def test_boundary_10_exact(self):
        assert risk_band_for_score(10.0)["label"] == "Low"

    def test_just_above_10(self):
        assert risk_band_for_score(10.001)["label"] == "Significant"

    def test_boundary_50_exact(self):
        assert risk_band_for_score(50.0)["label"] == "Significant"

    def test_just_above_50(self):
        assert risk_band_for_score(50.001)["label"] == "High"

    def test_boundary_100_exact(self):
        assert risk_band_for_score(100.0)["label"] == "High"

    def test_just_above_100(self):
        assert risk_band_for_score(100.001)["label"] == "Very High"

    def test_boundary_500_exact(self):
        assert risk_band_for_score(500.0)["label"] == "Very High"

    def test_just_above_500(self):
        assert risk_band_for_score(500.001)["label"] == "Extreme"

    def test_boundary_1000_exact(self):
        # 1000 matches Extreme (max=1000) before Unacceptable (min=1000) — Extreme wins
        assert risk_band_for_score(1000.0)["label"] == "Extreme"

    def test_just_above_1000(self):
        assert risk_band_for_score(1001.0)["label"] == "Unacceptable"

    def test_extreme_score(self):
        assert risk_band_for_score(9999)["label"] == "Unacceptable"

    def test_all_bands_have_required_fields(self):
        for score in [0.5, 3, 7, 20, 75, 200, 750, 2000]:
            b = risk_band_for_score(score)
            assert "label" in b
            assert "acceptable" in b
            assert "colour" in b, f"No colour for score {score}"
            assert isinstance(b["acceptable"], bool)


# ---------------------------------------------------------------------------
# PLr risk graph (ISO 13849-1 / AS/NZS 4024.1503)
# ---------------------------------------------------------------------------
class TestCalculatePLR:
    @pytest.mark.parametrize("s,f,p,expected", [
        ("S1", "F1", "P1", "a"),
        ("S1", "F1", "P2", "b"),
        ("S1", "F2", "P1", "b"),
        ("S1", "F2", "P2", "c"),
        ("S2", "F1", "P1", "c"),
        ("S2", "F1", "P2", "d"),
        ("S2", "F2", "P1", "d"),
        ("S2", "F2", "P2", "e"),
    ])
    def test_all_eight_combinations(self, s, f, p, expected):
        assert calculate_plr(s, f, p) == expected

    def test_invalid_severity_raises(self):
        with pytest.raises(ValueError, match="Invalid PLR"):
            calculate_plr("S3", "F1", "P1")

    def test_invalid_frequency_raises(self):
        with pytest.raises(ValueError, match="Invalid PLR"):
            calculate_plr("S1", "F3", "P1")

    def test_invalid_avoidance_raises(self):
        with pytest.raises(ValueError, match="Invalid PLR"):
            calculate_plr("S1", "F1", "P3")

    def test_worst_case_is_ple(self):
        assert calculate_plr("S2", "F2", "P2") == "e"

    def test_best_case_is_pla(self):
        assert calculate_plr("S1", "F1", "P1") == "a"
