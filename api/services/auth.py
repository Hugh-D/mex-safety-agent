from __future__ import annotations

import os
from fastapi import Header, HTTPException, status

_raw = os.environ.get("API_KEYS", "").strip()
_VALID_KEYS: set[str] = {k.strip() for k in _raw.split(",") if k.strip()} if _raw else set()


def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """FastAPI dependency — validates X-API-Key header against API_KEYS env var."""
    if not _VALID_KEYS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEYS environment variable is not configured.",
        )
    if x_api_key not in _VALID_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return x_api_key
