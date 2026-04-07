"""
Anthropic API service — MEX Safety Agent
Handles all calls to Claude. Import this in routers, never call anthropic directly.
"""

import logging
import os
import base64
import anthropic
from typing import Optional

logger = logging.getLogger(__name__)

# Initialise once — reused across all requests
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# claude-sonnet-4-6 supports up to 64K output tokens — essential for large
# multi-page drawings that generate long component lists.
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192


def call_claude(
    system_prompt: str,
    user_message:  str,
    pdf_base64:    Optional[str] = None,
    max_tokens:    int = MAX_TOKENS,
) -> str:
    """
    Call Claude with an optional PDF attachment.
    Returns the text content of the response.
    """
    content = []

    if pdf_base64:
        content.append({
            "type": "document",
            "source": {
                "type":       "base64",
                "media_type": "application/pdf",
                "data":       pdf_base64,
            },
        })

    content.append({"type": "text", "text": user_message})

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )

    logger.info("Claude stop_reason=%s  model=%s  input_tokens=%s  output_tokens=%s",
                response.stop_reason, response.model,
                response.usage.input_tokens, response.usage.output_tokens)
    if response.stop_reason == "max_tokens":
        logger.warning("Response was TRUNCATED — increase max_tokens (used %d)", max_tokens)

    return "".join(
        block.text for block in response.content if hasattr(block, "text")
    )


def pdf_to_base64(file_bytes: bytes) -> str:
    """Convert raw PDF bytes to base64 string for the API."""
    return base64.standard_b64encode(file_bytes).decode("utf-8")
