from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic

from models.schemas import AIInteractionLog, HazardEntry, HRNParameters, ProjectBrief, SafetyFunctionSpec
from services.standards import field_agent_standards_line
from services.hrn_plr import ALLOWED_VALUES as _HRN_ALLOWED

MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Standards doc loader — lazy, in-process cache
# ---------------------------------------------------------------------------
_DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "docs"

_DOC_FILES: dict[str, str] = {
    "1201": "AS4024_1201_safety_of_machines_general_principles_of_design.md",
    "1302": "AS4024_1302_safety_of_machines_risk_assesments_reduction_of_risk.md",
    "1303": "AS4024_1303_risk_assesment.md",
    "1501": "AS4024_1501_Safety_Related_Parts_Control_Systems.md",
    "1502": "AS4024_1502_Design_of_Safety_Related_Parts_Control_Systems_Validation.md",
    "1503": "AS4024_1503_Safety_Related_Parts_Control_Systems_Principles_For_Design.md",
    "1703": "AS4024_1703_access_openings.md",
    "1801": "AS4024_1801_safety_distances.md",
    "1803": "AS4024_1803_minimum_gaps.md",
}

_DOC_CACHE: dict[str, str] = {}


def _load_docs(*keys: str) -> str:
    parts = []
    for key in keys:
        if key not in _DOC_CACHE:
            path = _DOCS_DIR / _DOC_FILES[key]
            if path.exists():
                _DOC_CACHE[key] = path.read_text(encoding="utf-8")
            else:
                logging.warning("Standards doc missing — AI context degraded: %s", path)
        content = _DOC_CACHE.get(key)
        if content:
            parts.append(content)
    return "\n\n---\n\n".join(parts)


def _system_blocks(base_system: str, *doc_keys: str) -> list[dict]:
    """Build the system prompt block list, appending standards docs as a cached second block."""
    blocks: list[dict] = [
        {"type": "text", "text": base_system, "cache_control": {"type": "ephemeral"}}
    ]
    docs = _load_docs(*doc_keys)
    if docs:
        blocks.append(
            {"type": "text", "text": f"## AS/NZS 4024 Standards Reference\n\n{docs}", "cache_control": {"type": "ephemeral"}}
        )
    return blocks

# Standards line generated from api/data/standards_catalogue.json — do not edit inline.
_RISK_AGENT_SYSTEM = f"""\
You are a senior Certified Machinery Safety Expert (CMSE®) employed by MEX Engineering Group, \
an Australian machine safety consultancy. You apply {field_agent_standards_line()} to every assessment.

Your rules:
- Always cite specific clause numbers when referencing standards.
- Challenge HRN parameter selections when the evidence does not support them. \
  For example: no visible guard → LO must be ≥ 8; daily exposure → FE must be ≥ 2.5.
- Never reduce LO to 0.033 unless administrative controls are formally documented and verified.
- HRN risk bands (lower bound inclusive, upper bound exclusive): <1 Acceptable, 1–<4 Very Low \
  (both acceptable), 4–<6 Needs Review (engineer judgment required — not automatically acceptable), \
  6–<10 Low (action required), 10–<50 Significant, 50–<100 High, 100–<500 Very High, \
  500–<1000 Extreme, ≥1000 Unacceptable.
- Acceptance threshold: an HRN score is acceptable ONLY when strictly below 4. Never describe \
  a score of 4 or above as acceptable.
- Respond only with valid JSON that matches the requested schema exactly. No prose outside JSON.
"""

_CONCLUSION_SYSTEM = """\
You are a principal safety engineer at MEX Engineering Group writing the Conclusion section \
of a formal machine safety report. MEX Engineering Group is an Australian safety engineering \
consultancy (mexeng.com.au, Lic 141260C, ABN 68 101 789 584).

Style — match this exactly (based on real MEX reports):
- Formal, third-person, passive voice. Never use "I" or "we".
- Open with: "This Risk Assessment was conducted on [machine/line] at [site] in accordance with \
the principles of the AS/NZS 4024 series and relevant WHS requirements."
- Group findings by system type (guarding, control systems, energy isolation) — not hazard by hazard.
- Name specific HRN bands (e.g. "assessed as Significant and Very High using the HRN methodology").
- State that risk reduction measures were proposed in line with the hierarchy of controls.
- Where post-mitigation HRN is below 4, state residual risks were "reduced to very low or acceptable levels". Never describe an HRN of 4 or above as acceptable.
- For control system findings: reference specific deficiencies (e.g. non-compliant wiring, \
non-PL-rated functions) and the PLr/Category required to remediate.
- Close with: "Based on the findings of this assessment, a separate proposal will be developed \
as a subsequent phase to define and implement risk reduction measures necessary to reduce \
residual risks to an acceptable level and to ensure compliance with applicable AS/NZS 4024 \
and WHS requirements."
- Cite standards with full names and years (e.g. AS/NZS 4024.1801:2014, ISO 13849-1:2015).
- 4–6 paragraphs. No bullet points in the conclusion text itself.
- Respond only with valid JSON matching the requested schema exactly. No prose outside JSON.
"""


def _parse_json(text: str) -> Any:
    """Strip markdown code fences then parse JSON. If prose surrounds the JSON,
    fall back to the outermost {...} block. Raises ValueError with a clear
    message if no valid JSON is found — never returns a guess."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError("AI response was not valid JSON — result rejected, not guessed.")


_AUDIT_DIR = Path(__file__).resolve().parent.parent / "data" / "audit"
_AUDIT_FILE = _AUDIT_DIR / "ai_audit.jsonl"


def _persist_log(entry: AIInteractionLog) -> None:
    """Append the audit record to a JSONL file. Every AI interaction in a
    compliance product must leave a persistent trace — console logging alone
    is not an audit trail."""
    try:
        _AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        with open(_AUDIT_FILE, "a", encoding="utf-8") as fh:
            fh.write(entry.model_dump_json() + "\n")
    except OSError as exc:
        logging.error("AI audit log write FAILED — investigate immediately: %s", exc)


def _make_log(function: str, prompt_text: str, response: Any) -> AIInteractionLog:
    """Build and persist an audit log entry from a Claude API response."""
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()[:16]
    usage = response.usage
    entry = AIInteractionLog(
        function=function,
        model=response.model,
        response_id=response.id,
        prompt_hash=prompt_hash,
        timestamp=datetime.utcnow(),
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
    )
    _persist_log(entry)
    return entry


def _client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set.")
    return anthropic.Anthropic(api_key=api_key)


def _image_media_type(image_bytes: bytes) -> str:
    if image_bytes[:4] == b"\x89PNG":
        return "image/png"
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


# ---------------------------------------------------------------------------
# 1. Photo analysis
# ---------------------------------------------------------------------------
def analyse_photo(
    image_bytes: bytes,
    site_label: str,
    equipment_ref: str | None = None,
) -> tuple[dict[str, Any], AIInteractionLog]:
    """
    Analyse a field photo and return identified hazards, HRN parameter
    suggestions, and observations.

    Returns (result dict matching PhotoAnalysisResult schema, audit log).
    """
    client = _client()
    b64 = base64.standard_b64encode(image_bytes).decode()
    media_type = _image_media_type(image_bytes)

    prompt = f"""\
Site label: {site_label}
Equipment reference: {equipment_ref or "not specified"}

Analyse this machine/site photo as a CMSE® conducting a preliminary hazard identification.

Return JSON with this exact structure:
{{
  "observations": "<2-4 sentences describing what is visible — equipment, guards, access points, energy sources>",
  "hazard_types": ["<from the allowed list only>"],
  "suggested_mode": "<one of: Operation | Maintenance | Setup | Cleaning | Fault finding>",
  "suggested_task": "<brief task description, max 12 words>",
  "hrn_suggestions": {{
    "LO": {{"value": <float>, "justification": "<why>"}},
    "FE": {{"value": <float>, "justification": "<why>"}},
    "DPH": {{"value": <float>, "justification": "<why>"}},
    "NP": {{"value": <float>, "justification": "<why>"}}
  }},
  "flags": ["<any concerns — missing guards, obscured energy sources, etc>"]
}}

Allowed hazard_types (use exact strings):
Crushing, Impact, Entanglement, Drawing-in, Friction and abrasion, Burn/Scald,
Cutting, Shearing, Slipping, Tripping, Falling, Being run over, Ejection of parts,
Loss of stability, Electrical shock, Electrocution, Noise, Vibration, Radiation,
Dust/fume inhalation, Contact with hazardous substances

HRN value reference:
LO: 0.033=almost impossible, 1=highly unlikely, 1.5=unlikely, 2=possible, 5=even chance, 8=probable, 10=likely, 15=certain
FE: 0.5=annually, 1=monthly, 1.5=weekly, 2.5=daily, 4=hourly, 5=constantly
DPH: 0.1=scratch, 0.5=laceration, 1=minor fracture, 2=major fracture, 4=loss 1-2 digits, 8=amputation/partial sense loss, 10=double amputation, 12=critical illness, 15=fatality
NP: 1=1-2 persons, 2=3-7 persons, 4=8-15 persons, 8=16-50 persons, 12=50+ persons
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=_system_blocks(_RISK_AGENT_SYSTEM),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    log = _make_log("analyse_photo", prompt, response)
    result = _parse_json(response.content[0].text)
    _sanitise_hrn_suggestions(result)
    return result, log


def _sanitise_hrn_suggestions(result: dict) -> None:
    """AI-suggested HRN values must come from the published tables. Any invalid
    value is snapped UP to the next allowed value (conservative — never
    understate risk) and flagged so the engineer sees the correction."""
    suggestions = result.get("hrn_suggestions")
    if not isinstance(suggestions, dict):
        return
    flags = result.setdefault("flags", [])
    for name, allowed in _HRN_ALLOWED.items():
        entry = suggestions.get(name)
        if not isinstance(entry, dict) or "value" not in entry:
            continue
        try:
            value = float(entry["value"])
        except (TypeError, ValueError):
            entry["value"] = max(allowed)
            flags.append(f"AI suggested a non-numeric {name} — replaced with the maximum table value {max(allowed)} (conservative). Engineer must review.")
            continue
        if any(abs(value - a) < 1e-9 for a in allowed):
            continue
        higher = [a for a in allowed if a > value]
        snapped = min(higher) if higher else max(allowed)
        entry["value"] = snapped
        flags.append(f"AI suggested {name}={value}, which is not a valid table value — snapped UP to {snapped} (conservative). Engineer must review.")


# ---------------------------------------------------------------------------
# 2. HRN validation
# ---------------------------------------------------------------------------
def validate_hrn(
    hrn_params: HRNParameters,
    hazard_types: list[str],
    observations: str,
    risk_reduction_measures: list[str] | None = None,
) -> tuple[dict[str, Any], AIInteractionLog]:
    """
    Validate HRN parameter selections against the described scene.
    Returns flags, challenged parameters, and recommended corrections.

    Returns (result dict matching HRNValidationResult schema, audit log).
    """
    client = _client()

    context = f"""\
Scene observations: {observations}
Hazard types identified: {", ".join(hazard_types)}
HRN parameters entered by engineer:
  LO = {hrn_params.LO}  ({hrn_params.justification.get("LO", "") if hrn_params.justification else ""})
  FE = {hrn_params.FE}  ({hrn_params.justification.get("FE", "") if hrn_params.justification else ""})
  DPH = {hrn_params.DPH}  ({hrn_params.justification.get("DPH", "") if hrn_params.justification else ""})
  NP = {hrn_params.NP}  ({hrn_params.justification.get("NP", "") if hrn_params.justification else ""})
HRN score: {hrn_params.LO * hrn_params.FE * hrn_params.DPH * hrn_params.NP:.2f}
Risk reduction measures: {", ".join(risk_reduction_measures) if risk_reduction_measures else "none yet"}
"""

    prompt = f"""\
{context}

Review the entered HRN parameters as a CMSE® and return JSON:
{{
  "valid": <true if all parameters are well-supported, false if any need challenge>,
  "challenged_parameters": [
    {{
      "parameter": "<LO|FE|DPH|NP>",
      "entered_value": <float>,
      "recommended_value": <float>,
      "reason": "<standards-referenced explanation>"
    }}
  ],
  "flags": ["<any issues — e.g. LO too optimistic given no guard visible>"],
  "overall_comment": "<1-2 sentences summarising the validation outcome>"
}}

If all parameters are well-supported, return an empty challenged_parameters array.
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=_system_blocks(_RISK_AGENT_SYSTEM, "1302", "1303", "1501", "1801", "1803"),
        messages=[{"role": "user", "content": prompt}],
    )

    log = _make_log("validate_hrn", prompt, response)
    return _parse_json(response.content[0].text), log


# ---------------------------------------------------------------------------
# 3. Risk reduction recommendations
# ---------------------------------------------------------------------------
def recommend_risk_reduction(
    location: str,
    mode: str,
    task: str,
    hazard_types: list[str],
    hrn_score: float,
    risk_band: str,
    existing_measures: list[str] | None = None,
) -> tuple[dict[str, Any], AIInteractionLog]:
    """
    Recommend risk reduction measures with standards references.

    Returns (result dict matching RiskReductionResult schema, audit log).
    """
    client = _client()

    prompt = f"""\
Location: {location}
Mode: {mode}
Task: {task}
Hazard types: {", ".join(hazard_types)}
Current HRN score: {hrn_score} ({risk_band})
Existing measures: {", ".join(existing_measures) if existing_measures else "none"}

Recommend up to 6 risk reduction measures following ISO 12100 hierarchy \
(eliminate > guard > safeguard > warning > training/PPE). Group related hazard types under one measure where possible.
Target: bring HRN below 4 (Very Low or Acceptable band).

Return JSON:
{{
  "measures": [
    {{
      "description": "<specific, actionable measure>",
      "hierarchy_level": "<elimination|engineering|safeguarding|warning|administrative|PPE>",
      "standards_references": ["<e.g. ISO 14120:2015 cl 5.3>"],
      "estimated_hrn_factor_reduction": "<e.g. reduces LO from 8 to 1.5>"
    }}
  ],
  "target_hrn_achievable": <true|false>,
  "notes": "<any caveats or follow-up actions required>"
}}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=_system_blocks(_RISK_AGENT_SYSTEM, "1201", "1501", "1503", "1703", "1801", "1803"),
        messages=[{"role": "user", "content": prompt}],
    )

    log = _make_log("recommend_risk_reduction", prompt, response)
    return _parse_json(response.content[0].text), log


# ---------------------------------------------------------------------------
# 4. Voice field extraction
# ---------------------------------------------------------------------------
def extract_voice_fields(
    transcript: str,
    site_label: str,
) -> tuple[dict[str, Any], AIInteractionLog]:
    """
    Extract structured hazard form fields from a voice note transcript.
    HRN parameters are intentionally excluded — engineer must set those.

    Returns (result dict matching VoiceExtractionResult schema, audit log).
    """
    client = _client()

    prompt = f"""\
Site: {site_label}
Voice note transcript: {transcript}

Extract structured fields from this field engineer's voice note.

Allowed modes (use exact string or null): Operation, Maintenance, Setup, Cleaning, Fault finding
Allowed hazard_types (use exact strings only):
Crushing, Impact, Entanglement, Drawing-in, Friction and abrasion, Burn/Scald,
Cutting, Shearing, Slipping, Tripping, Falling, Being run over, Ejection of parts,
Loss of stability, Electrical shock, Electrocution, Noise, Vibration, Radiation,
Dust/fume inhalation, Contact with hazardous substances

Return JSON:
{{
  "suggested_mode": "<mode string or null if not mentioned>",
  "suggested_task": "<brief task description max 12 words, or null if not clear>",
  "hazard_types": ["<only types explicitly mentioned or clearly implied>"],
  "typed_notes": "<anything in the transcript that doesn't fit the above fields — verbatim context, observations, measurements, names — or null if nothing left>"
}}

Do not invent information not present in the transcript.
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": _RISK_AGENT_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    log = _make_log("extract_voice_fields", prompt, response)
    return _parse_json(response.content[0].text), log


# ---------------------------------------------------------------------------
# 5. Conclusion synthesis
# ---------------------------------------------------------------------------
def synthesise_conclusion(
    project_brief: ProjectBrief,
    hazards: list[HazardEntry],
    safety_functions: list[SafetyFunctionSpec] | None = None,
) -> tuple[dict[str, Any], AIInteractionLog]:
    """
    Synthesise a conclusion section from the complete assessment.

    Returns (result dict matching ConclusionResult schema, audit log).
    """
    client = _client()

    hazard_summary = "\n".join(
        f"- {h.id} ({h.location}): HRN {h.hrn_score_before} ({h.risk_band_before})"
        + (f" → {h.hrn_score_after} ({h.risk_band_after}) after mitigation" if h.hrn_score_after else "")
        for h in hazards
    )

    sf_summary = ""
    if safety_functions:
        sf_summary = "\nSafety functions:\n" + "\n".join(
            f"- {sf.function_name}: PLr {sf.plr_required}, Category {sf.category_required}"
            for sf in safety_functions
        )

    unacceptable = [h for h in hazards if h.hrn_score_after is None or h.hrn_score_after >= 4]

    prompt = f"""\
Project: {project_brief.project_number} — {project_brief.client}
Site: {project_brief.site}
Machine / Line: {project_brief.machine_or_line}
Assessment date: {project_brief.assessment_date}
Standards: {", ".join(project_brief.standards_applicable)}

Hazard findings:
{hazard_summary}
{sf_summary}

Hazards not yet acceptable (HRN missing or >= 4) after mitigation: {len(unacceptable)}

Write the Conclusion section for this risk assessment report.

Return JSON:
{{
  "conclusion_text": "<4-8 paragraph conclusion in MEX report style>",
  "systemic_issues": ["<grouped findings, e.g. 'E-stops absent on all conveyor lines'>"],
  "overall_plr_recommendation": "<e.g. PLd Category 3>",
  "immediate_actions_required": ["<actions needed before machine can operate>"],
  "follow_up_actions": ["<recommendations for next stage>"]
}}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=_system_blocks(_CONCLUSION_SYSTEM, "1201", "1302", "1303", "1501", "1502", "1503", "1703", "1801", "1803"),
        messages=[{"role": "user", "content": prompt}],
    )

    log = _make_log("synthesise_conclusion", prompt, response)
    return _parse_json(response.content[0].text), log
