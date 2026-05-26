from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from services.rate_limit import limiter
from routers.assessment import router as assessment_router
from routers.project import router as project_router
from routers.report import router as report_router
from routers.claude import router as claude_router
from routers.compliance import router as compliance_router
from services.auth import require_api_key

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="MEX Safety Platform API",
    version="0.1.0",
    description="Deterministic HRN, PLr, and report generation services for the MEX Safety Platform",
    dependencies=[],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8082",
    "http://localhost:19006",
    "http://localhost:19007",
]
_cors_env = os.environ.get("CORS_ORIGINS", "").strip()
_ORIGIN_RE = __import__("re").compile(r"^https?://[\w.\-]+(:\d+)?$")
_allowed_origins = (
    [o for o in (o.strip() for o in _cors_env.split(",")) if o and _ORIGIN_RE.match(o)]
    or _DEFAULT_ORIGINS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers — AI endpoints get stricter rate limit via dependency
# ---------------------------------------------------------------------------
_auth = [Depends(require_api_key)]

app.include_router(assessment_router, prefix="/api", tags=["assessment"], dependencies=_auth)
app.include_router(project_router, prefix="/api", tags=["project"], dependencies=_auth)
app.include_router(report_router, prefix="/api", tags=["report"], dependencies=_auth)
app.include_router(claude_router, prefix="/api", tags=["ai"], dependencies=_auth)
app.include_router(compliance_router, prefix="/api", tags=["compliance"], dependencies=_auth)

from services.project_store import PHOTOS_DIR  # noqa: E402
from services.storage import spaces_enabled       # noqa: E402
if not spaces_enabled():
    app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")


@app.get("/", tags=["health"])
def root() -> dict:
    return {
        "status": "ok",
        "service": "MEX Safety Platform API",
        "description": "Use /api/assessment and /api/report endpoints for HRN, PLr, and report workflows.",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
