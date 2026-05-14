from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.assessment import router as assessment_router
from routers.project import router as project_router
from routers.report import router as report_router
from routers.claude import router as claude_router
from routers.compliance import router as compliance_router

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="MEX Safety Platform API",
    version="0.1.0",
    description="Deterministic HRN, PLr, and report generation services for the MEX Safety Platform",
)

_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:19006",
    "http://localhost:19007",
]
_cors_env = os.environ.get("CORS_ORIGINS", "").strip()
_allowed_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or _DEFAULT_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assessment_router, prefix="/api", tags=["assessment"])
app.include_router(project_router, prefix="/api", tags=["project"])
app.include_router(report_router, prefix="/api", tags=["report"])
app.include_router(claude_router, prefix="/api", tags=["ai"])
app.include_router(compliance_router, prefix="/api", tags=["compliance"])


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
