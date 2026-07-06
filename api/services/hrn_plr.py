from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "hrn_tables.json", "r", encoding="utf-8") as handle:
    HRN_TABLES = json.load(handle)

with open(DATA_DIR / "plr_risk_graph.json", "r", encoding="utf-8") as handle:
    PLR_RISK_GRAPH = json.load(handle)


# Exact parameter values permitted by the HRN methodology. Any other input is
# rejected — the calculation must be deterministic against the published tables.
ALLOWED_VALUES: Dict[str, List[float]] = {
    key: [entry["value"] for entry in HRN_TABLES["parameters"][key]["values"]]
    for key in ("LO", "FE", "DPH", "NP")
}


def validate_hrn_parameters(lo: float, fe: float, dph: float, np: float) -> List[str]:
    """Return a list of error strings for any parameter not in the allowed value set."""
    errors: List[str] = []
    for name, value in (("LO", lo), ("FE", fe), ("DPH", dph), ("NP", np)):
        if not any(abs(value - allowed) < 1e-9 for allowed in ALLOWED_VALUES[name]):
            errors.append(
                f"{name}={value} is not a valid HRN table value. Allowed: {ALLOWED_VALUES[name]}"
            )
    return errors


def calculate_hrn(lo: float, fe: float, dph: float, np: float) -> float:
    errors = validate_hrn_parameters(lo, fe, dph, np)
    if errors:
        raise ValueError("; ".join(errors))
    score = lo * fe * dph * np
    return round(float(score), 3)


def risk_band_for_score(score: float) -> Dict[str, Any]:
    """Match score to a band using min <= score < max (exclusive upper bound).

    Bands in hrn_tables.json are contiguous, so every non-negative score maps
    to exactly one band — no gaps, no overlaps, no order dependence.
    """
    for band in HRN_TABLES.get("risk_bands", []):
        min_value = band.get("min", 0)
        max_value = band.get("max")
        if max_value is None:
            if score >= min_value:
                return band
        elif min_value <= score < max_value:
            return band
    return {
        "min": 0,
        "max": None,
        "label": "Unknown",
        "acceptable": False,
        "colour": "#000000",
    }


def verify_hazards(hazards: List[Any]) -> List[str]:
    """Recompute every hazard's HRN score and band server-side and compare with
    the client-supplied values. Returns a list of mismatch descriptions
    (empty list = all verified). The server calculation is authoritative —
    reports must never print a score the server has not reproduced.
    """
    errors: List[str] = []
    for h in hazards:
        for label, params, score, band in (
            ("before", h.hrn_before, h.hrn_score_before, h.risk_band_before),
            ("after", h.hrn_after, h.hrn_score_after, h.risk_band_after),
        ):
            if params is None:
                continue
            try:
                expected = calculate_hrn(params.LO, params.FE, params.DPH, params.NP)
            except ValueError as exc:
                errors.append(f"Hazard {h.id} ({label}): {exc}")
                continue
            if score is None or abs(expected - score) > 0.001:
                errors.append(
                    f"Hazard {h.id} ({label}): supplied HRN score {score} does not match "
                    f"server calculation {expected} (LO×FE×DPH×NP)."
                )
                continue
            expected_band = risk_band_for_score(expected)["label"]
            if band != expected_band:
                errors.append(
                    f"Hazard {h.id} ({label}): supplied risk band '{band}' does not match "
                    f"server band '{expected_band}' for score {expected}."
                )
    return errors


def get_hrn_tables() -> Dict[str, Any]:
    return {
        "parameters": HRN_TABLES.get("parameters", {}),
        "risk_bands": HRN_TABLES.get("risk_bands", []),
        "acceptance_threshold": HRN_TABLES["acceptance_threshold"],
        "formula": HRN_TABLES.get("formula", "HRN = LO × FE × DPH × NP"),
    }


def calculate_plr(severity: str, frequency: str, avoidance: str) -> str:
    key = f"{severity}-{frequency}-{avoidance}"
    risk_graph = PLR_RISK_GRAPH.get("risk_graph", {})
    result = risk_graph.get(key)
    if result is None:
        raise ValueError(f"Invalid PLR parameter combination: {key}")
    return result


def get_plr_parameters() -> Dict[str, Any]:
    return {
        "source_standard": PLR_RISK_GRAPH.get("source_standard", "ISO 13849-1"),
        "parameters": PLR_RISK_GRAPH.get("parameters", {}),
        "risk_graph": PLR_RISK_GRAPH.get("risk_graph", {}),
        "performance_levels": PLR_RISK_GRAPH.get("performance_levels", {}),
    }
