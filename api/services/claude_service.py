from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime
from typing import Any

import anthropic

from models.schemas import AIInteractionLog, HazardEntry, HRNParameters, ProjectBrief, SafetyFunctionSpec
from services.standards import field_agent_standards_line

MODEL = "claude-sonnet-4-6"

# Standards line generated from api/data/standards_catalogue.json — do not edit inline.
_RISK_AGENT_SYSTEM = f"""\
You are a senior Certified Machinery Safety Expert (CMSE®) employed by MEX Engineering Group, \
an Australian machine safety consultancy. You apply {field_agent_standards_line()} to every assessment.

Your rules:
- Always cite specific clause numbers when referencing standards.
- Challenge HRN parameter selections when the evidence does not support them. \
  For example: no visible guard → LO must be ≥ 8; daily exposure → FE must be ≥ 2.5.
- Never reduce LO to 0.033 unless administrative controls are formally documented and verified.
- HRN acceptance threshold is ≤ 5 (LO × FE × DPH × NP).
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
- Where post-mitigation HRN ≤ 5, state residual risks were "reduced to very low or acceptable levels".
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
    """Strip markdown code fences then parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _make_log(function: str, prompt_text: str, response: Any) -> AIInteractionLog:
    """Build an audit log entry from a Claude API response."""
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()[:16]
    usage = response.usage
    return AIInteractionLog(
        function=function,
        model=response.model,
        response_id=response.id,
        prompt_hash=prompt_hash,
        timestamp=datetime.utcnow(),
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
    )


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
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": _RISK_AGENT_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
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
    return _parse_json(response.content[0].text), log


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
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": _RISK_AGENT_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
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

Recommend risk reduction measures following ISO 12100 hierarchy \
(eliminate > guard > safeguard > warning > training/PPE).
Target: bring HRN to ≤ 5.

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
        max_tokens=768,
        system=[
            {
                "type": "text",
                "text": _RISK_AGENT_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    log = _make_log("recommend_risk_reduction", prompt, response)
    return _parse_json(response.content[0].text), log


# ---------------------------------------------------------------------------
# 4. Conclusion synthesis
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

    unacceptable = [h for h in hazards if not h.hrn_score_after or h.hrn_score_after > 5]

    prompt = f"""\
Project: {project_brief.project_number} — {project_brief.client}
Site: {project_brief.site}
Machine / Line: {project_brief.machine_or_line}
Assessment date: {project_brief.assessment_date}
Standards: {", ".join(project_brief.standards_applicable)}

Hazard findings:
{hazard_summary}
{sf_summary}

Hazards still above HRN 5 after mitigation: {len(unacceptable)}

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
        system=[
            {
                "type": "text",
                "text": _CONCLUSION_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    log = _make_log("synthesise_conclusion", prompt, response)
    return _parse_json(response.content[0].text), log
