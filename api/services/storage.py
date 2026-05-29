from __future__ import annotations

import mimetypes
import os
from pathlib import Path

# DigitalOcean Spaces config — all optional; falls back to local filesystem when not set.
_SPACES_KEY      = os.environ.get("SPACES_KEY", "")
_SPACES_SECRET   = os.environ.get("SPACES_SECRET", "")
_SPACES_BUCKET   = os.environ.get("SPACES_BUCKET", "")
_SPACES_REGION   = os.environ.get("SPACES_REGION", "syd1")
_SPACES_ENDPOINT = os.environ.get("SPACES_ENDPOINT", f"https://{_SPACES_REGION}.digitaloceanspaces.com")

_spaces_enabled = bool(_SPACES_KEY and _SPACES_SECRET and _SPACES_BUCKET)

_s3_client = None

def _get_s3():
    global _s3_client
    if _s3_client is None:
        import boto3
        _s3_client = boto3.client(
            "s3",
            region_name=_SPACES_REGION,
            endpoint_url=_SPACES_ENDPOINT,
            aws_access_key_id=_SPACES_KEY,
            aws_secret_access_key=_SPACES_SECRET,
        )
    return _s3_client


def upload_photo(data: bytes, key: str, filename: str = "photo.jpg") -> str:
    """Upload photo bytes and return a URL (Spaces) or filepath (local fallback).

    key: relative path used as the Spaces object key, e.g. 'J27010/H05/abc_photo.jpg'
    """
    content_type = mimetypes.guess_type(filename)[0] or "image/jpeg"

    if _spaces_enabled:
        client = _get_s3()
        client.put_object(
            Bucket=_SPACES_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        client.put_object_acl(
            Bucket=_SPACES_BUCKET,
            Key=key,
            ACL="public-read",
        )
        # Subdomain-style URL required for public access; path-style requires auth.
        return f"https://{_SPACES_BUCKET}.{_SPACES_REGION}.digitaloceanspaces.com/{key}"

    # Local fallback — write to PHOTOS_DIR and return the relative filepath
    from services.project_store import PHOTOS_DIR
    dest = PHOTOS_DIR / Path(key)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return key  # relative path; served by StaticFiles at /photos/<key>


def spaces_enabled() -> bool:
    return _spaces_enabled
