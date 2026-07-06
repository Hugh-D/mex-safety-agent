from __future__ import annotations

import os
from fastapi import Header, HTTPException, status

def _valid_keys() -> set[str]:
    raw = os.environ.get("API_KEYS", "").strip()
    return {k.strip() for k in raw.split(",") if k.strip()} if raw else set()


def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """FastAPI dependency — validates X-API-Key header against API_KEYS env var."""
    valid = _valid_keys()
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEYS environment variable is not configured.",
        )
    if x_api_key not in valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return x_api_key
