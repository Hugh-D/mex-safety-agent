from __future__ import annotations

import logging
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import Any, Optional

from models.schemas import HRNParameters, HazardEntry, ProjectBrief, SafetyFunctionSpec, ReportDraftRequest
from services import claude_service, voice_service
from services.rate_limit import limiter

log = logging.getLogger(__name__)
router = APIRouter()

# In-memory job stores for async analysis. Jobs are pruned after _JOB_TTL_SECONDS
# so the stores cannot grow without bound. NOTE: these stores are per-process —
# the API must run as a single worker (current Dockerfile does) or polling breaks.
import time as _time

_JOB_TTL_SECONDS = 3600
_photo_jobs: dict[str, dict] = {}
_executor = ThreadPoolExecutor(max_workers=4)


def _prune_jobs(store: dict[str, dict]) -> None:
    cutoff = _time.time() - _JOB_TTL_SECONDS
    for jid in [j for j, v in store.items() if v.get("created", 0) < cutoff]:
        store.pop(jid, None)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class PhotoAnalysisResponse(BaseModel):
    observations: str
    hazard_types: list[str]
    suggested_mode: str
    suggested_task: str
    hrn_suggestions: dict[str, Any]
    flags: list[str]


class HRNValidationRequest(BaseModel):
    hrn_params: HRNParameters
    hazard_types: list[str]
    observations: str
    risk_reduction_measures: Optional[list[str]] = None


class HRNValidationResponse(BaseModel):
    valid: bool
    challenged_parameters: list[dict[str, Any]]
    flags: list[str]
    overall_comment: str


class RiskReductionRequest(BaseModel):
    location: str
    mode: str
    task: str
    hazard_types: list[str]
    hrn_score: float
    risk_band: str
    existing_measures: Optional[list[str]] = None


class RiskReductionResponse(BaseModel):
    measures: list[dict[str, Any]]
    target_hrn_achievable: bool
    notes: str


class VoiceTranscriptResponse(BaseModel):
    transcript: str
    suggested_mode: Optional[str]
    suggested_task: Optional[str]
    hazard_types: list[str]
    typed_notes: Optional[str]


class ConclusionRequest(BaseModel):
    project_brief: ProjectBrief
    hazards: list[HazardEntry]
    safety_functions: Optional[list[SafetyFunctionSpec]] = None


class ConclusionResponse(BaseModel):
    conclusion_text: str
    systemic_issues: list[str]
    overall_plr_recommendation: str
    immediate_actions_required: list[str]
    follow_up_actions: list[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
def _run_photo_job(job_id: str, image_bytes: bytes, site_label: str, equipment_ref: Optional[str]) -> None:
    try:
        result, ai_log = claude_service.analyse_photo(image_bytes, site_label, equipment_ref)
        _photo_jobs[job_id] = {"status": "complete", "result": result, "created": _time.time()}
    except Exception as exc:
        log.error("analyse_photo failed: %s", exc)
        _photo_jobs[job_id] = {"status": "error", "detail": str(exc), "created": _time.time()}


@router.post("/ai/photo/start")
@limiter.limit("20/minute")
async def analyse_photo_start(
    request: Request,
    file: UploadFile = File(...),
    site_label: str = Form(...),
    equipment_ref: Optional[str] = Form(None),
) -> dict:
    """Accept a photo and start analysis in the background. Returns a job_id to poll."""
    image_bytes = await file.read()
    _prune_jobs(_photo_jobs)
    job_id = str(uuid.uuid4())
    _photo_jobs[job_id] = {"status": "pending", "created": _time.time()}
    loop = asyncio.get_event_loop()
    loop.run_in_executor(_executor, _run_photo_job, job_id, image_bytes, site_label, equipment_ref)
    return {"job_id": job_id, "status": "pending"}


@router.get("/ai/photo/{job_id}")
def analyse_photo_poll(job_id: str) -> dict:
    """Poll for the result of a photo analysis job."""
    job = _photo_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------------------------------------------------------------------
# Voice — async job pattern (same OkHttp timeout problem as photo)
# ---------------------------------------------------------------------------
_voice_jobs: dict[str, dict] = {}


def _run_voice_job(job_id: str, audio_bytes: bytes, filename: str, site_label: str) -> None:
    try:
        result, ai_log = voice_service.transcribe_voice(audio_bytes, filename, site_label)
        _voice_jobs[job_id] = {"status": "complete", "result": result, "created": _time.time()}
    except Exception as exc:
        log.error("transcribe_voice failed: %s", exc)
        _voice_jobs[job_id] = {"status": "error", "detail": str(exc), "created": _time.time()}


@router.post("/ai/voice/start")
@limiter.limit("20/minute")
async def transcribe_voice_start(
    request: Request,
    file: UploadFile = File(...),
    site_label: str = Form(...),
) -> dict:
    """Accept audio and start transcription in the background. Returns a job_id to poll."""
    audio_bytes = await file.read()
    filename = file.filename or "voice.m4a"
    _prune_jobs(_voice_jobs)
    job_id = str(uuid.uuid4())
    _voice_jobs[job_id] = {"status": "pending", "created": _time.time()}
    loop = asyncio.get_event_loop()
    loop.run_in_executor(_executor, _run_voice_job, job_id, audio_bytes, filename, site_label)
    return {"job_id": job_id, "status": "pending"}


@router.get("/ai/voice/{job_id}")
def transcribe_voice_poll(job_id: str) -> dict:
    """Poll for the result of a voice transcription job."""
    job = _voice_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/ai/photo", response_model=PhotoAnalysisResponse)
@limiter.limit("20/minute")
async def analyse_photo(
    request: Request,
    file: UploadFile = File(...),
    site_label: str = Form(...),
    equipment_ref: Optional[str] = Form(None),
) -> PhotoAnalysisResponse:
    """Upload a field photo and get hazard identification + HRN suggestions."""
    image_bytes = await file.read()
    try:
        result, ai_log = claude_service.analyse_photo(image_bytes, site_label, equipment_ref)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    return PhotoAnalysisResponse(**result)


@router.post("/ai/hrn/validate", response_model=HRNValidationResponse)
@limiter.limit("20/minute")
def validate_hrn(request: Request, body: HRNValidationRequest) -> HRNValidationResponse:
    """Validate HRN parameter selections against observed scene context."""
    try:
        result, ai_log = claude_service.validate_hrn(
            body.hrn_params,
            body.hazard_types,
            body.observations,
            body.risk_reduction_measures,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    log.info("AI audit: %s", ai_log.model_dump_json())
    return HRNValidationResponse(**result)


@router.post("/ai/risk-reduction", response_model=RiskReductionResponse)
@limiter.limit("20/minute")
def recommend_risk_reduction(request: Request, body: RiskReductionRequest) -> RiskReductionResponse:
    """Get standards-referenced risk reduction recommendations for a hazard."""
    try:
        result, ai_log = claude_service.recommend_risk_reduction(
            body.location,
            body.mode,
            body.task,
            body.hazard_types,
            body.hrn_score,
            body.risk_band,
            body.existing_measures,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    log.info("AI audit: %s", ai_log.model_dump_json())
    return RiskReductionResponse(**result)


@router.post("/ai/voice", response_model=VoiceTranscriptResponse)
@limiter.limit("20/minute")
async def transcribe_voice_note(
    request: Request,
    file: UploadFile = File(...),
    site_label: str = Form(...),
) -> VoiceTranscriptResponse:
    """Transcribe a voice note and extract structured hazard form fields."""
    audio_bytes = await file.read()
    filename = file.filename or "voice.webm"
    try:
        result, ai_log = voice_service.transcribe_voice(audio_bytes, filename, site_label)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Voice service error: {exc}")
    log.info("AI audit (voice): %s", ai_log.model_dump_json())
    return VoiceTranscriptResponse(
        transcript=result.get("transcript", ""),
        suggested_mode=result.get("suggested_mode"),
        suggested_task=result.get("suggested_task"),
        hazard_types=result.get("hazard_types", []),
        typed_notes=result.get("typed_notes"),
    )


@router.post("/ai/conclusion", response_model=ConclusionResponse)
@limiter.limit("20/minute")
def synthesise_conclusion(request: Request, body: ConclusionRequest) -> ConclusionResponse:
    """Synthesise a conclusion section from a completed assessment."""
    try:
        result, ai_log = claude_service.synthesise_conclusion(
            body.project_brief,
            body.hazards,
            body.safety_functions,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    log.info("AI audit: %s", ai_log.model_dump_json())
    return ConclusionResponse(**result)
