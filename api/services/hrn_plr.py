from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "hrn_tables.json", "r", encoding="utf-8") as handle:
    HRN_TABLES = json.load(handle)

with open(DATA_DIR / "plr_risk_graph.json", "r", encoding="utf-8") as handle:
    PLR_RISK_GRAPH = json.load(handle)


def calculate_hrn(lo: float, fe: float, dph: float, np: float) -> float:
    score = lo * fe * dph * np
    return round(float(score), 3)


def risk_band_for_score(score: float) -> Dict[str, Any]:
    for band in HRN_TABLES.get("risk_bands", []):
        min_value = band.get("min", 0)
        max_value = band.get("max")
        if max_value is None:
            if score >= min_value:
                return band
        elif min_value <= score <= max_value:
            return band
    return {
        "min": 0,
        "max": None,
        "label": "Unknown",
        "acceptable": False,
        "colour": "#000000",
    }


def get_hrn_tables() -> Dict[str, Any]:
    return {
        "parameters": HRN_TABLES.get("parameters", {}),
        "risk_bands": HRN_TABLES.get("risk_bands", []),
        "acceptance_threshold": HRN_TABLES.get("acceptance_threshold", 5),
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
