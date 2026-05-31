from __future__ import annotations

import base64
import json
import os
from typing import Any

import anthropic

from services.claude_service import _client, _parse_json
from services.standards import primary_as4024_block, supplementary_as4024_block, secondary_international_block

MODEL = "claude-sonnet-4-6"

# Standards blocks are generated from api/data/standards_catalogue.json at import time.
# Edit that file to update any code or year — do not edit the strings below directly.
_COMPLIANCE_SYSTEM = f"""\
You are a CEFS-qualified functional safety engineer employed by MEX Engineering Group, \
an Australian machine safety consultancy (mexeng.com.au, Lic 141260C).

Primary standards framework — AS/NZS 4024 series (cite these first in all findings):
{primary_as4024_block()}

Supplementary standards:
{supplementary_as4024_block()}

Supporting international standards (cite as secondary reference in parentheses):
{secondary_international_block()}

Review rules:
- Identify every safety-relevant component visible in the drawing.
- Check circuit architecture against the target PL/Category.
- Flag missing feedback monitoring, single-channel where dual is required, incorrect reset logic.
- Cite the AS/NZS 4024 clause first, then the ISO/IEC clause in parentheses where both apply.
- Be precise — name the specific component, signal, or terminal with the issue.
- Write descriptions as short, plain-English bullet points (max 2 sentences each). No paragraphs.
- Summaries must be 2–3 short bullet points, not flowing prose.
- Respond only with valid JSON matching the requested schema exactly. No prose outside JSON.
"""


def analyse_drawing(
    image_bytes: bytes,
    drawing_title: str,
    target_pl: str,
    target_category: str,
    context: str | None = None,
    dxf_context: str | None = None,
) -> dict[str, Any]:
    """
    Analyse a safety circuit drawing or mechanical layout against a PLr/Category target.

    Returns a dict matching DrawingAnalysisResult schema.
    """
    client = _client()
    b64 = base64.standard_b64encode(image_bytes).decode()

    # Detect media type — PDFs go as document blocks, images as image blocks
    is_pdf = image_bytes[:4] == b"%PDF"
    if is_pdf:
        media_type = "application/pdf"
    elif image_bytes[:4] == b"\x89PNG":
        media_type = "image/png"
    elif image_bytes[:3] == b"\xff\xd8\xff":
        media_type = "image/jpeg"
    elif image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    _ctx_section = f"Additional context: {context}" if context else ""
    _dxf_section = (
        "Structured DXF component data (authoritative — prefer this over visual guesses):\n"
        + dxf_context
        if dxf_context
        else ""
    )
    prompt = f"""\
Drawing title: {drawing_title}
Target Performance Level: {target_pl}
Target Category: {target_category}
{_ctx_section}
{_dxf_section}

Analyse this safety drawing as a CEFS-qualified functional safety engineer.

Return JSON with this exact structure:
{{
  "drawing_type": "<electrical_schematic | mechanical_layout | block_diagram | wiring_diagram | other>",
  "components_identified": [
    {{
      "component": "<name/model if visible>",
      "type": "<safety_relay | safety_plc | interlock | light_curtain | e_stop | contactor | drive | sensor | other>",
      "location": "<Drawing # or sheet/zone reference, e.g. 'Dwg 03 — top-left', 'Sheet 2 Zone B'>",
      "safety_relevant": true
    }}
  ],
  "architecture_assessment": {{
    "detected_category": "<Cat B | 1 | 2 | 3 | 4 | unknown>",
    "detected_pl": "<PLa | PLb | PLc | PLd | PLe | unknown>",
    "channel_count": "<single | dual | unknown>",
    "has_feedback_monitoring": <true | false | null>,
    "has_cross_monitoring": <true | false | null>,
    "summary": "<2-3 sentences on the overall architecture>"
  }},
  "conformances": [
    {{
      "description": "<what is correctly implemented>",
      "clause_reference": "<standard and clause>"
    }}
  ],
  "non_conformances": [
    {{
      "severity": "<critical | major | minor>",
      "description": "<specific finding — name the component/signal/terminal>",
      "clause_reference": "<standard and clause number>",
      "remediation": "<specific corrective action required>"
    }}
  ],
  "gap_to_target": "<none | minor | significant | major>",
  "gap_summary": "<1-2 sentences: does the design meet {target_pl} {target_category}? What is missing?>",
  "overall_verdict": "<compliant | conditionally_compliant | non_compliant>"
}}
"""

    file_block: dict[str, Any] = (
        {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
        }
        if is_pdf
        else {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64},
        }
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=[
            {
                "type": "text",
                "text": _COMPLIANCE_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    file_block,
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    return _parse_json(response.content[0].text)


import re as _re

# Keys match both underscore form (from analysis prompt) and natural language fallbacks
_TYPE_TO_COMPLIANCE: dict[str, str] = {
    "e_stop":           "e_stop",
    "e-stop":           "e_stop",
    "estop":            "e_stop",
    "emergency stop":   "e_stop",
    "interlock":        "interlock",
    "gate":             "interlock",
    "guard":            "interlock",
    "door":             "interlock",
    "light_curtain":    "light_curtain",
    "light curtain":    "light_curtain",
    "light guard":      "light_curtain",
    "scanner":          "scanner",
    "area scanner":     "scanner",
    "laser scanner":    "scanner",
    "safety_relay":     "safety_relay",
    "safety relay":     "safety_relay",
    "safety controller":"safety_relay",
    "safety_plc":       "safety_plc",
    "safety plc":       "safety_plc",
    "contactor":        "contactor",
    "drive":            "drive",
    "vfd":              "drive",
    "terminal":         "terminal",
}

# Types from analysis prompt that contribute nothing to the SLD
_SKIP_TYPES = {"other", "sensor"}

# Safety-relevant compliance types (only these go into the SLD ground truth)
_SLD_COMPLIANCE_TYPES = {"e_stop", "interlock", "light_curtain", "scanner", "safety_relay", "safety_plc", "contactor", "drive"}


def _extract_tag(component_str: str) -> str:
    """Extract short drawing tag from a verbose component description."""
    s = component_str.strip()
    # Pattern 1: 'TAG – description' or 'TAG — description'
    m = _re.match(r'^([A-Z][A-Z0-9\-]*\d+)\s*[–—\-]', s)
    if m:
        return m.group(1)
    # Pattern 2: '(TAG)' suffix e.g. 'CompactLogix PLC (A10)'
    m = _re.search(r'\(([A-Z]{1,3}\d+)\)\s*$', s)
    if m:
        return m.group(1)
    # Pattern 3: standalone model number — uppercase+digits token e.g. 'MSR127T'
    m = _re.search(r'\b([A-Z]{2,}[0-9][A-Z0-9]*)\b', s)
    if m:
        return m.group(1)
    # Fallback: first word
    return s.split()[0] if s else s


def components_from_analysis(components_identified: list[dict]) -> list[dict]:
    """
    Convert analyse_drawing componentsIdentified to the ground-truth format for extract_topology.
    Filters to safety-relevant components only and extracts short tag labels.
    """
    result = []
    seen_tags: set[str] = set()
    for c in components_identified:
        type_str = c.get("type", "").lower().strip()
        if type_str in _SKIP_TYPES:
            continue
        compliance_type = next(
            (v for k, v in _TYPE_TO_COMPLIANCE.items() if k == type_str or k in type_str),
            "unknown",
        )
        if compliance_type not in _SLD_COMPLIANCE_TYPES:
            continue
        tag = _extract_tag(c.get("component", "").strip())
        if not tag or tag in seen_tags:
            continue
        seen_tags.add(tag)
        result.append({"id": tag, "compliance_type": compliance_type})
    return result


def extract_topology(
    image_bytes: bytes,
    dxf_components: list[dict],
) -> dict[str, Any] | None:
    """
    Extract wiring topology (connections + channel/series assignments) from a drawing image.
    When dxf_components is provided, uses those IDs as ground truth.
    When empty, Claude identifies components directly from the image.
    Returns {"components": [...], "connections": [...]} or None on failure.
    """
    client = _client()
    b64 = base64.standard_b64encode(image_bytes).decode()

    is_pdf = image_bytes[:4] == b"%PDF"
    if is_pdf:
        media_type = "application/pdf"
    elif image_bytes[:4] == b"\x89PNG":
        media_type = "image/png"
    elif image_bytes[:3] == b"\xff\xd8\xff":
        media_type = "image/jpeg"
    else:
        media_type = "image/jpeg"

    if dxf_components:
        comp_list = "\n".join(
            f"  {c.get('id', c.get('tag', '?'))}: {c.get('compliance_type', 'unknown')}"
            for c in dxf_components
        )
        prompt = f"""\
Known safety components from the DXF file (use these IDs exactly):
{comp_list}

Trace only the wiring topology of this safety circuit drawing.

For each component, determine:
- channel: "CH1", "CH2", or null if single-channel
- series_group: shared label for components wired in series (e.g. "ch1_inputs"), or null

Trace every wiring connection between the listed components.
wire_type: "safety" = main safety chain, "feedback" = output feedback to relay,
           "power" = 24VDC/0VDC supply, "control" = reset/enable signals.

Return JSON only — no prose:
{{
  "components": [
    {{"id": "<exact ID from list>", "channel": "<CH1|CH2|null>", "series_group": "<label or null>"}}
  ],
  "connections": [
    {{"from_id": "<source>", "to_id": "<dest>", "from_port": "<terminal or null>",
      "to_port": "<terminal or null>", "wire_type": "<safety|power|control|feedback>",
      "label": "<wire number or null>"}}
  ]
}}
"""
    else:
        prompt = """\
Identify all safety-relevant components visible in this drawing and trace the wiring topology between them.

For each component assign:
- id: a short unique label matching the tag shown on the drawing (e.g. "ES1", "K1", "K2", "LC1")
- compliance_type: one of: e_stop, interlock, light_curtain, scanner, safety_relay, safety_plc, contactor, drive, terminal
- channel: "CH1", "CH2", or null if single-channel
- series_group: shared label for components wired in series (e.g. "ch1_inputs"), or null

Trace every wiring connection between identified components.
wire_type: "safety" = main safety chain, "feedback" = output feedback to relay,
           "power" = 24VDC/0VDC supply, "control" = reset/enable signals.

Return JSON only — no prose:
{
  "components": [
    {"id": "<tag>", "compliance_type": "<type>", "channel": "<CH1|CH2|null>", "series_group": "<label or null>"}
  ],
  "connections": [
    {"from_id": "<source>", "to_id": "<dest>", "from_port": null,
     "to_port": null, "wire_type": "<safety|power|control|feedback>", "label": null}
  ]
}
"""

    file_block: dict[str, Any] = (
        {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}}
        if is_pdf
        else {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}}
    )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=8192,
            system=[{
                "type": "text",
                "text": (
                    "You are an electrical engineer tracing safety circuit wiring topology. "
                    "Return only valid JSON matching the requested schema. No prose outside JSON."
                ),
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": [file_block, {"type": "text", "text": prompt}]}],
        )
        return _parse_json(response.content[0].text)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("extract_topology failed: %s", exc)
        return None


_DOCX_IMAGE_MIME: dict[str, str] = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif":  "image/gif",
    ".webp": "image/webp",
}


def _extract_docx_images(file_bytes: bytes) -> list[tuple[bytes, str]]:
    """Extract embedded images from a DOCX (ZIP) file.

    Returns list of (image_bytes, media_type) for formats Claude supports.
    EMF/WMF/BMP (Windows-only metafiles) are skipped.
    """
    import zipfile as _zipfile
    results: list[tuple[bytes, str]] = []
    try:
        with _zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            for name in z.namelist():
                if not name.startswith("word/media/"):
                    continue
                ext = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
                media_type = _DOCX_IMAGE_MIME.get(ext)
                if media_type:
                    results.append((z.read(name), media_type))
    except Exception:
        pass
    return results


def _extract_docx_text(file_bytes: bytes) -> str:
    import docx as _docx
    doc = _docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def review_design_document(
    document_text: str,
    target_pl: str,
    target_category: str,
    ra_hazard_ids: list[str] | None = None,
    file_bytes: bytes | None = None,
    file_name: str = "",
) -> dict[str, Any]:
    """
    Review a design/quote document for compliance completeness.

    When file_bytes is provided:
    - PDF  → sent as a Claude document block so both text and embedded images are visible.
    - DOCX → text extracted + embedded images sent as separate image blocks.
    - TXT / no file → document_text string used directly (capped at 120k chars).
    """
    client = _client()

    hazard_context = ""
    if ra_hazard_ids:
        hazard_context = f"\nRA hazard IDs to verify coverage for: {', '.join(ra_hazard_ids)}"

    _meta = f"""\
Target Performance Level: {target_pl}
Target Category: {target_category}
{hazard_context}"""

    _instructions = """\

Review this design/proposal document as a CEFS-qualified functional safety engineer.
Check whether the proposed design adequately addresses the required safety functions.

Return JSON:
{
  "safety_functions_identified": [
    {
      "name": "<safety function name>",
      "description": "<what it does>",
      "implementation": "<how it is implemented in this design>",
      "pl_claimed": "<PLa-PLe or not stated>",
      "category_claimed": "<Cat B/1/2/3/4 or not stated>"
    }
  ],
  "gaps": [
    {
      "severity": "<critical | major | minor>",
      "description": "<specific gap — what is missing or underspecified>",
      "clause_reference": "<standard and clause if applicable>",
      "recommendation": "<what needs to be added or clarified>"
    }
  ],
  "coverage_assessment": "<are all required safety functions addressed? What is missing?>",
  "overall_verdict": "<adequate | partially_adequate | inadequate>",
  "recommendations": ["<specific actionable recommendations>"]
}"""

    fname_lower = file_name.lower()
    is_pdf  = bool(file_bytes) and (file_bytes[:4] == b"%PDF" or fname_lower.endswith(".pdf"))
    is_docx = bool(file_bytes) and not is_pdf and (
        fname_lower.endswith(".docx") or "wordprocessingml" in fname_lower
    )

    content: list[dict[str, Any]]

    if is_pdf:
        b64 = base64.standard_b64encode(file_bytes).decode()  # type: ignore[arg-type]
        content = [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
            {"type": "text", "text": _meta + _instructions},
        ]

    elif is_docx:
        text_to_use = (document_text or _extract_docx_text(file_bytes))[:120_000]  # type: ignore[arg-type]
        images = _extract_docx_images(file_bytes)  # type: ignore[arg-type]
        prompt = _meta + f"\n\nDocument text:\n---\n{text_to_use}\n---\n" + _instructions
        content = [{"type": "text", "text": prompt}]
        for img_bytes, media_type in images[:20]:
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": base64.standard_b64encode(img_bytes).decode()},
            })

    else:
        text_to_use = document_text[:120_000]
        prompt = _meta + f"\n\nDocument text:\n---\n{text_to_use}\n---\n" + _instructions
        content = [{"type": "text", "text": prompt}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=[
            {
                "type": "text",
                "text": _COMPLIANCE_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": content}],
    )

    return _parse_json(response.content[0].text)
