from __future__ import annotations

import logging
import os
from io import BytesIO
from typing import Any

from openai import OpenAI

from models.schemas import AIInteractionLog
from services import claude_service

log = logging.getLogger(__name__)

# Context hint for OpenAI transcription — improves accuracy on safety vocabulary.
_TRANSCRIPTION_PROMPT = (
    "Machine safety field notes from an Australian industrial site. "
    "May reference: AS/NZS 4024 series, ISO 13849-1, IEC 62061, HRN scoring "
    "(LO likelihood of occurrence, FE frequency of exposure, DPH degree of possible harm, "
    "NP number of persons at risk), Performance Level PLa through PLe, safety categories "
    "Category 1 through 4, components such as light curtains, interlocks, e-stops, "
    "two-hand controls, and hazard types: entanglement, crushing, electrical, thermal, noise."
)


def transcribe_voice(
    audio_bytes: bytes,
    filename: str,
    site_label: str,
) -> tuple[dict[str, Any], AIInteractionLog]:
    """
    Transcribe a voice note then extract structured hazard form fields.

    Stage 1 — OpenAI gpt-4o-mini-transcribe: raw audio → text.
    Stage 2 — Claude: text → {suggested_mode, suggested_task, hazard_types, typed_notes}.

    Returns (merged result dict, Claude audit log). HRN parameters are never
    auto-populated; the engineer must set those themselves.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

    oai = OpenAI(api_key=api_key)

    # Determine MIME type from filename extension for OpenAI multipart upload.
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    mime_map = {"m4a": "audio/mp4", "mp4": "audio/mp4", "wav": "audio/wav", "webm": "audio/webm"}
    mime = mime_map.get(ext, "audio/webm")

    transcript_obj = oai.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=(filename, BytesIO(audio_bytes), mime),
        prompt=_TRANSCRIPTION_PROMPT,
    )
    raw_transcript = transcript_obj.text
    log.info("Voice transcription: %d chars from %s", len(raw_transcript), filename)

    extracted, ai_log = claude_service.extract_voice_fields(raw_transcript, site_label)
    extracted["transcript"] = raw_transcript
    return extracted, ai_log
