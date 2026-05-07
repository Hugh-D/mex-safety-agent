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
all safety-relevant components AND trace the complete wiring topology.

Identify ALL components present, categorised as:
- estop         : E-stop pushbuttons (mushroom head, NC contact)
- safety_switch : Interlocked guard switches, limit switches, safety door switches
- light_curtain : Light curtains, AOPDs, ESPEs (Type 4 / Type 2)
- scanner       : Laser area scanners, safety laser scanners
- safety_relay  : Dedicated safety relay modules (e.g. Pilz PNOZ, SICK i10, Schmersal SRB)
- safety_plc    : Safety PLCs, safety controllers, safety I/O (e.g. Pilz PSS, Siemens F-CPU)
- contactor     : Contactors, motor starters, output switching devices
- vfd           : Variable frequency drives, soft starters, servo drives with STO
- terminal      : Wire labels, terminal blocks, cable IDs

For dual-channel safety circuits set "channel" to "CH1" or "CH2" for each component.
For components wired in series in a safety chain, set "series_group" to a shared label \
(e.g. "ch1_inputs", "ch2_inputs", "gate_chain").

ALSO trace every wiring connection between safety-relevant components. For each connection record:
- which output terminal of the source connects to which input terminal of the destination
- the wire type: 'safety'=main safety chain; 'feedback'=output contact feedback to relay; \
'power'=24VDC/0VDC supply; 'control'=reset/enable/mute signals
- the wire label or cable number if shown on the drawing

Return ONLY valid JSON — no preamble, no markdown fences:
{
  "drawing_type": "single line diagram|schematic|safety circuit|control panel layout|unknown",
  "page_count": <integer>,
  "summary": ["<sentence 1>", "<sentence 2>"],
  "components": [
    {
      "id": "<ref e.g. K1, ES1, X1>",
      "label": "<human readable name>",
      "type": "<estop|safety_switch|light_curtain|scanner|safety_relay|safety_plc|contactor|vfd|terminal>",
      "manufacturer": "<if identifiable, else null>",
      "model": "<if identifiable, else null>",
      "pl_rating": "<PLa-PLe or null>",
      "location": "<where on drawing>",
      "channel": "<CH1|CH2|null>",
      "series_group": "<shared label for series-wired group, else null>",
      "notes": "<wiring config, NC/NO contacts, channel count, concerns>"
    }
  ],
  "connections": [
    {
      "from_id": "<source component ID>",
      "from_port": "<terminal/pin on source e.g. '13','Q1' — null if not shown>",
      "to_id": "<destination component ID>",
      "to_port": "<terminal/pin on destination e.g. '14','I1' — null if not shown>",
      "wire_type": "<safety|power|control|feedback>",
      "label": "<wire number or cable label — null if not shown>"
    }
  ],
  "wiring_observations": ["<observation>"],
  "safety_concerns": ["<concern>"]
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
    result.setdefault("connections", [])
    result.setdefault("page_count", 1)
    # Normalise summary to list — split prose into sentences if Claude ignores array instruction
    if isinstance(result.get("summary"), str):
        result["summary"] = _to_sentences(result["summary"])
    result["components"] = [enrich_component(c) for c in result.get("components", [])]
    logger.info("Parse complete: %d components, %d connections",
                len(result["components"]), len(result["connections"]))
    return result
