"""
Compliance review service — MEX Safety Agent
Accepts project + equipment data (+ optional parse result),
returns structured ReviewResult.
"""

import json
import logging
import re
from models import ProjectInput, ParseResult
from services.claude_client import call_claude
from services.library_service import enrich_equipment_item

logger = logging.getLogger(__name__)

REVIEW_SYSTEM_PROMPT = """You are a certified machine safety engineer (CMSE) and expert in:
- AS4024 (Australian Machine Safety Standard)
- ISO 13849-1:2015 (Safety-related parts of control systems)
- IEC 62061 (Functional safety of SRECS)
- IEC 61800-5-2 (Safe Torque Off and drive safety functions)
- EN ISO 14119 (Interlocking devices)
- Australian WHS legislation and codes of practice

You review electrical safety system designs and equipment selections against target \
Performance Level (PL) and Category requirements.

For each finding you must:
1. Identify the specific non-conformance
2. Reference the exact standard clause
3. Provide a concrete, actionable redline instruction for the engineer

Priority definitions:
- CRITICAL : Must be resolved before any PLd claim can be made
- MAJOR    : Required for a compliant design — not safety-critical blocker but necessary
- MINOR    : Documentation, verification, or annotation items

Output constraints — be thorough but concise:
- Report ALL findings — do not omit any non-conformance regardless of count
- Each finding in "changes" must be its own separate object — do NOT combine multiple concerns into one change item
- description: array of 1-3 short sentences — each sentence is its own string in the array
- action: 1 sentence max — direct and specific
- summary: array of 2-4 short sentences — each sentence is its own string in the array
- pl_reasoning: array of 2-3 short sentences — each sentence is its own string in the array
- equipment_notes: ONLY include components with warn or fail status, and any new components that need to be added or replaced — omit compliant (ok) components entirely. This section is an action list, not an inventory.

Return ONLY valid JSON in exactly this structure — no preamble, no markdown fences:
{
  "overall_status": "pass|warn|fail",
  "summary": ["<sentence 1>", "<sentence 2>", "<sentence 3>"],
  "pl_achievable": true|false,
  "pl_reasoning": ["<sentence 1>", "<sentence 2>", "<sentence 3>"],
  "changes": [
    {
      "id": <integer>,
      "priority": "CRITICAL|MAJOR|MINOR",
      "description": ["<sentence 1: what is wrong — always reference specific component IDs (e.g. ES01, K01) and terminal numbers (e.g. terminals 13/14) involved>", "<sentence 2: why it matters>"],
      "reference": "<standard and clause e.g. ISO 13849-1:2015 cl.6.2.4>",
      "action": "<1 sentence: specific redline instruction — always reference the specific component IDs (e.g. ES01, K01) and terminal numbers (e.g. terminals 13/14) involved in the finding>"
    }
  ],
  "equipment_notes": [
    {
      "item": "<ID or Manufacturer Model>",
      "note": "<1 sentence compliance observation>",
      "status": "ok|warn|fail"
    }
  ],
  "standards_checked": ["<standard 1>", "..."]
}"""


def _to_sentences(text: str) -> list:
    """Split a prose string into individual sentences for bullet rendering."""
    if not text or not text.strip():
        return []
    # Split on sentence-ending punctuation followed by whitespace + capital letter
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [p.strip() for p in parts if p.strip()]


def clean_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"^```\s*",     "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```$",        "", raw, flags=re.MULTILINE)
    start = raw.find("{")
    end   = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    raw = raw.strip()
    raw = raw.replace("\\'", "'")
    return raw


def build_user_message(project: ProjectInput, parse_result: ParseResult | None) -> str:
    lines = [
        "## Project data",
        f"Project number : {project.project_number}",
        f"Client         : {project.client}",
        f"Machine        : {project.machine}",
        f"Target PL      : {project.target_pl}",
        f"Target Category: {project.target_category}",
    ]
    if project.target_sil:
        lines.append(f"Target SIL     : {project.target_sil}")
    if project.redundancy:
        lines.append(f"Redundancy     : {project.redundancy}")
    if project.dc:
        lines.append(f"Diagnostic cov : {project.dc}")
    if project.mttfd:
        lines.append(f"MTTFd target   : {project.mttfd} years")

    lines += [
        "",
        "## Standards to review against",
        *[f"- {s}" for s in project.standards],
        "",
        "## Equipment list",
    ]
    for eq in project.equipment:
        eq = enrich_equipment_item(eq)
        pl = eq.pl_rating or "unrated"
        fn = f" ({eq.function})" if eq.function else ""
        notes = f" — {eq.notes}" if eq.notes else ""
        lines.append(f"- {eq.manufacturer} {eq.model}{fn}  PL:{pl}  Qty:{eq.qty}{notes}")

    if parse_result:
        lines += [
            "",
            "## Parsed drawing data",
            f"Drawing type: {parse_result.drawing_type}",
            f"Summary: {parse_result.summary}",
            "",
            "Components identified:",
        ]
        for c in parse_result.components:
            pl = c.pl_rating or "unrated"
            mfr = f"{c.manufacturer} {c.model}" if c.manufacturer else c.label
            notes = f" — {c.notes}" if c.notes else ""
            lines.append(f"  {c.id} ({c.type}): {mfr}  PL:{pl}  @ {c.location}{notes}")

        if parse_result.wiring_observations:
            lines += ["", "Wiring observations:"]
            lines += [f"  - {w}" for w in parse_result.wiring_observations]

        if parse_result.safety_concerns:
            lines += ["", "Pre-identified concerns from drawing:"]
            lines += [f"  - {s}" for s in parse_result.safety_concerns]

    lines += [
        "",
        "## Task",
        f"Perform a full compliance review for {project.target_pl} / Category {project.target_category}.",
        "Identify all non-conformances, missing elements, and documentation gaps.",
        "Return the structured JSON review result.",
    ]

    return "\n".join(lines)


async def run_review(project: ProjectInput, parse_result: ParseResult | None = None) -> dict:
    """
    Main entry point. Returns compliance review as dict.
    """
    user_msg = build_user_message(project, parse_result)

    raw = call_claude(
        system_prompt=REVIEW_SYSTEM_PROMPT,
        user_message=user_msg,
        max_tokens=16384,
    )

    logger.info("Raw review response (%d chars):\n%s", len(raw), raw)
    cleaned = clean_json(raw)
    result  = json.loads(cleaned)

    # Inject project number for downstream use
    result["project_number"] = project.project_number
    result["standards_checked"] = result.get("standards_checked", project.standards)

    # Normalise list fields — split prose strings into sentences
    for key in ("summary", "pl_reasoning"):
        if isinstance(result.get(key), str):
            result[key] = _to_sentences(result[key])
    for ch in result.get("changes", []):
        if isinstance(ch.get("description"), str):
            ch["description"] = _to_sentences(ch["description"])

    return result
