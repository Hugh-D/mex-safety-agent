from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

_MAP_PATH = Path(__file__).parent.parent.parent / "symbols" / "family_map.json"
_DXF_PATH = Path(__file__).parent.parent.parent / "symbols" / "Elec_Symbols.dxf"


@lru_cache(maxsize=1)
def _load_map() -> dict[str, Any]:
    with open(_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


def _family_code(block_name: str) -> str | None:
    """Extract the family code from a block name, e.g. 'VPB11MTL' → 'PB'."""
    m = re.match(r"^[HV]([A-Z]+)\d", block_name)
    return m.group(1) if m else None


def lookup_block(block_name: str) -> dict[str, Any] | None:
    """Return the family map entry for a block name, or None if unknown."""
    code = _family_code(block_name)
    if not code:
        return None
    return _load_map()["families"].get(code)


def compliance_type(block_name: str) -> str:
    entry = lookup_block(block_name)
    return entry["compliance_type"] if entry else "other"


def is_safety_relevant(block_name: str) -> bool:
    entry = lookup_block(block_name)
    return bool(entry and entry.get("safety_relevant"))


def safety_note(block_name: str) -> str | None:
    entry = lookup_block(block_name)
    return entry.get("safety_note") if entry else None


def component_type(block_name: str) -> str:
    entry = lookup_block(block_name)
    return entry["type"] if entry else "unknown"


def tag_prefix(block_name: str) -> str:
    entry = lookup_block(block_name)
    # Some safety families override the default prefix (e.g. PB e-stops → SF)
    if entry:
        return entry.get("safety_tag_override", entry["tag_prefix"])
    return "?"


def describe_variant(block_name: str) -> str:
    """Return a human-readable description of the specific variant, e.g. 'mushroom turn-to-release (e-stop)'."""
    fmap = _load_map()
    suffixes = fmap.get("_meta", {}).get("variant_suffixes", {})
    code = _family_code(block_name)
    if not code:
        return block_name

    # Strip H/V prefix and family code+first digit group to get variant suffix
    # e.g. VPB11MTL → strip V + PB11 → MTL
    m = re.match(r"^[HV][A-Z]+\d+(.*)$", block_name)
    suffix = m.group(1) if m else ""
    if not suffix:
        return component_type(block_name)

    # Check each suffix category
    for category, mapping in suffixes.items():
        if isinstance(mapping, dict) and suffix in mapping:
            return mapping[suffix]

    return f"{component_type(block_name)} ({suffix})"


def all_safety_gaps() -> list[str]:
    return _load_map().get("safety_relevant_summary", {}).get("gaps", [])
