"""
API key authentication — MEX Safety Agent
All /api/* routes require X-API-Key header matching MEX_API_KEY in .env.
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=_KEY_NAME, auto_error=False)


def require_api_key(key: str = Security(_api_key_header)):
    expected = os.environ.get("MEX_API_KEY", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: MEX_API_KEY not set",
        )
    if key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return key
