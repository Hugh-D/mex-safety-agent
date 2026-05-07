"""
Standards catalogue loader — single source of truth for all standards referenced
by MEX Safety Platform system prompts and documentation.

Both compliance_service and claude_service import from here. Edit
api/data/standards_catalogue.json to update any standard code or year;
all prompts regenerate automatically at import time.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_CATALOGUE_PATH = Path(__file__).resolve().parent.parent / "data" / "standards_catalogue.json"


@lru_cache(maxsize=1)
def catalogue() -> dict:
    with open(_CATALOGUE_PATH, encoding="utf-8") as f:
        return json.load(f)


def primary_as4024_block() -> str:
    """Return the AS/NZS 4024 primary standards as a formatted bullet list for system prompts."""
    lines = []
    for s in catalogue()["as_nzs_4024"]["primary"]:
        line = f"- {s['code']}  — {s['title']}"
        if s.get("iso_equiv"):
            line += f" (≡ {s['iso_equiv']})"
        lines.append(line)
    return "\n".join(lines)


def supplementary_as4024_block() -> str:
    """Return AS/NZS 4024 supplementary standards as a formatted bullet list."""
    lines = []
    for s in catalogue()["as_nzs_4024"]["supplementary"]:
        line = f"- {s['code']}  — {s['title']}"
        if s.get("iso_equiv"):
            line += f" (≡ {s['iso_equiv']})"
        lines.append(line)
    return "\n".join(lines)


def secondary_international_block() -> str:
    """Return secondary international standards as a formatted bullet list."""
    lines = []
    for s in catalogue()["international_secondary"]:
        lines.append(f"- {s['code']}  — {s['title']}")
    return "\n".join(lines)


def field_agent_standards_line() -> str:
    """One-line summary of standards for the field-mode risk agent system prompt."""
    primary_codes = [s["code"] for s in catalogue()["as_nzs_4024"]["primary"]]
    secondary_codes = [s["code"] for s in catalogue()["international_secondary"]]
    all_codes = primary_codes + secondary_codes
    return ", ".join(all_codes)


def all_codes() -> list[str]:
    """Flat list of every standard code — useful for validation or docs."""
    cat = catalogue()
    codes = (
        [s["code"] for s in cat["as_nzs_4024"]["primary"]]
        + [s["code"] for s in cat["as_nzs_4024"]["supplementary"]]
        + [s["code"] for s in cat["international_secondary"]]
    )
    return codes
