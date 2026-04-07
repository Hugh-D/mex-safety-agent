"""
Drawing parser service — MEX Safety Agent
Accepts PDF bytes, returns structured ParseResult.
"""

import ast
import json
import logging
import re
from services.claude_client import call_claude, pdf_to_base64
from services.library_service import enrich_component

logger = logging.getLogger(__name__)

PARSER_SYSTEM_PROMPT = """You are an expert electrical engineer specialising in machine safety systems \
compliant with AS4024, ISO 13849-1, and IEC 62061. You analyse electrical drawings — \
single line diagrams, safety circuit schematics, and control system layouts — to identify \
and catalogue all components relevant to a safety review.

Identify ALL components present, categorised as:
- estop      : E-stops, light curtains, safety mats, safety switches, interlock guards
- safety_plc : Safety PLCs, safety relays, safety controllers
- contactor  : Contactors, motor starters, output switching devices, safety outputs
- vfd        : Variable frequency drives, soft starters, motor drives
- terminal   : Wire labels, terminal numbers, cable IDs, circuit references

Return ONLY valid JSON in exactly this structure — no preamble, no markdown fences:
{
  "drawing_type": "single line diagram|schematic|safety circuit|control panel layout|unknown",
  "page_count": <integer>,
  "summary": ["<sentence 1 about drawing scope>", "<sentence 2 about key safety elements>"],
  "components": [
    {
      "id": "<ref from drawing e.g. K1, ES1, X1>",
      "label": "<human readable name>",
      "type": "<estop|safety_plc|contactor|vfd|terminal>",
      "manufacturer": "<if identifiable, else null>",
      "model": "<if identifiable, else null>",
      "pl_rating": "<PLa-PLe or null>",
      "location": "<where on drawing>",
      "notes": "<wiring config, NC/NO contacts, channel count, concerns>"
    }
  ],
  "wiring_observations": ["<observation 1>", "..."],
  "safety_concerns": ["<concern 1>", "..."]
}"""


def _to_sentences(text: str) -> list:
    """Split a prose string into individual sentences for bullet rendering."""
    if not text or not text.strip():
        return []
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _requote(s: str) -> str:
    """Rewrite single-quote-delimited JSON strings as double-quote-delimited.

    A candidate closing single-quote is treated as a true delimiter only when
    the next non-whitespace character is a valid JSON continuation token
    (, } ] :).  Otherwise it is kept as a literal apostrophe in the value.

    Example: {'label': 'Garlo's Pies'} → {"label": "Garlo's Pies"}
    """
    out = []
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]

        if ch == '"':
            # Already double-quoted string — copy verbatim
            out.append(ch)
            i += 1
            while i < n:
                c = s[i]
                if c == '\\':
                    out.append(c)
                    i += 1
                    if i < n:
                        out.append(s[i])
                        i += 1
                elif c == '"':
                    out.append(c)
                    i += 1
                    break
                else:
                    out.append(c)
                    i += 1

        elif ch == "'":
            # Single-quoted string — convert delimiter to double-quote
            out.append('"')
            i += 1
            while i < n:
                c = s[i]
                if c == '\\' and i + 1 < n and s[i + 1] == "'":
                    # \' → plain apostrophe (no escaping needed inside "…")
                    out.append("'")
                    i += 2
                elif c == '"':
                    # Bare double-quote inside → escape it
                    out.append('\\"')
                    i += 1
                elif c == "'":
                    # Peek ahead: closing delimiter or mid-value apostrophe?
                    j = i + 1
                    while j < n and s[j] in ' \t\r\n':
                        j += 1
                    if j >= n or s[j] in ',}]:':
                        out.append('"')   # genuine close
                        i += 1
                        break
                    else:
                        out.append("'")   # apostrophe inside value
                        i += 1
                else:
                    out.append(c)
                    i += 1

        else:
            out.append(ch)
            i += 1

    return ''.join(out)


def clean_json(raw: str) -> str:
    """Strip markdown fences, isolate the JSON object, and fix apostrophe
    encoding issues so json.loads() succeeds regardless of how the LLM
    delimited its strings."""
    raw = raw.strip()

    # Strip markdown code fences
    raw = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"^```\s*",     "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```$",        "", raw, flags=re.MULTILINE)

    # Isolate the outermost JSON object
    start = raw.find("{")
    end   = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end + 1]
    raw = raw.strip()

    # Fast path — already valid
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass

    # Fix \' (not a valid JSON escape) inside double-quoted strings
    raw = raw.replace("\\'", "'")
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass

    # LLM used single-quote delimiters, possibly with bare apostrophes in
    # values (e.g. {'label': 'Garlo's Pies'}).  Use structural lookahead to
    # tell a genuine closing quote from a mid-value apostrophe.
    requoted = _requote(raw)
    try:
        json.loads(requoted)
        return requoted
    except json.JSONDecodeError:
        pass

    # Final fallback: Python literal eval handles single-quoted dicts and
    # Python literals (None, True, False) that Claude sometimes emits.
    # ast.literal_eval is safe — it never executes code.
    try:
        obj = ast.literal_eval(raw)
        return json.dumps(obj)
    except (ValueError, SyntaxError):
        pass

    # Nothing worked — log the raw text so it can be inspected, then raise.
    logger.error("clean_json: all parse attempts failed.\nRaw Claude output:\n%s", raw)
    raise ValueError(f"Could not parse Claude response as JSON. Raw output logged above.")


async def parse_drawing(pdf_bytes: bytes) -> dict:
    """
    Main entry point. Accepts raw PDF bytes, returns parsed drawing dict.
    """
    b64 = pdf_to_base64(pdf_bytes)

    user_msg = (
        "Analyse this electrical drawing and identify all safety-relevant components. "
        "Return the structured JSON as specified."
    )

    raw = call_claude(
        system_prompt=PARSER_SYSTEM_PROMPT,
        user_message=user_msg,
        pdf_base64=b64,
        max_tokens=16384,
    )

    logger.info("Raw Claude response (%d chars):\n%s", len(raw), raw)
    cleaned = clean_json(raw)
    result = json.loads(cleaned)
    result.setdefault("wiring_observations", [])
    result.setdefault("safety_concerns", [])
    result.setdefault("page_count", 1)
    # Normalise summary to list — split prose into sentences if Claude ignores array instruction
    if isinstance(result.get("summary"), str):
        result["summary"] = _to_sentences(result["summary"])
    result["components"] = [enrich_component(c) for c in result.get("components", [])]
    return result
