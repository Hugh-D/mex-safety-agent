from __future__ import annotations

import json
import logging
import time
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Any, Optional

from models.schemas import HRNParameters, HazardEntry, ProjectBrief, SafetyFunctionSpec, ReportDraftRequest
from services import claude_service, voice_service

log = logging.getLogger(__name__)
router = APIRouter()

# In-memory job store for async photo analysis
_photo_jobs: dict[str, dict] = {}
_executor = ThreadPoolExecutor(max_workers=4)


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
    t0 = time.time()
    try:
        result, ai_log = claude_service.analyse_photo(image_bytes, site_label, equipment_ref)
        log.debug("analyse_photo OK in %.1fs", time.time() - t0)
        _photo_jobs[job_id] = {"status": "complete", "result": result}
    except Exception as exc:
        log.debug("analyse_photo FAILED after %.1fs: %s", time.time() - t0, exc)
        _photo_jobs[job_id] = {"status": "error", "detail": str(exc)}


@router.post("/ai/photo/start")
async def analyse_photo_start(
    file: UploadFile = File(...),
    site_label: str = Form(...),
    equipment_ref: Optional[str] = Form(None),
) -> dict:
    """Accept a photo and start analysis in the background. Returns a job_id to poll."""
    image_bytes = await file.read()
    job_id = str(uuid.uuid4())
    _photo_jobs[job_id] = {"status": "pending"}
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
    t0 = time.time()
    try:
        result, ai_log = voice_service.transcribe_voice(audio_bytes, filename, site_label)
        log.debug("transcribe_voice OK in %.1fs", time.time() - t0)
        _voice_jobs[job_id] = {"status": "complete", "result": result}
    except Exception as exc:
        log.debug("transcribe_voice FAILED after %.1fs: %s", time.time() - t0, exc)
        _voice_jobs[job_id] = {"status": "error", "detail": str(exc)}


@router.post("/ai/voice/start")
async def transcribe_voice_start(
    file: UploadFile = File(...),
    site_label: str = Form(...),
) -> dict:
    """Accept audio and start transcription in the background. Returns a job_id to poll."""
    audio_bytes = await file.read()
    filename = file.filename or "voice.m4a"
    job_id = str(uuid.uuid4())
    _voice_jobs[job_id] = {"status": "pending"}
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
async def analyse_photo(
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
def validate_hrn(request: HRNValidationRequest) -> HRNValidationResponse:
    """Validate HRN parameter selections against observed scene context."""
    try:
        result, ai_log = claude_service.validate_hrn(
            request.hrn_params,
            request.hazard_types,
            request.observations,
            request.risk_reduction_measures,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    log.info("AI audit: %s", ai_log.model_dump_json())
    return HRNValidationResponse(**result)


@router.post("/ai/risk-reduction", response_model=RiskReductionResponse)
def recommend_risk_reduction(request: RiskReductionRequest) -> RiskReductionResponse:
    """Get standards-referenced risk reduction recommendations for a hazard."""
    try:
        result, ai_log = claude_service.recommend_risk_reduction(
            request.location,
            request.mode,
            request.task,
            request.hazard_types,
            request.hrn_score,
            request.risk_band,
            request.existing_measures,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    log.info("AI audit: %s", ai_log.model_dump_json())
    return RiskReductionResponse(**result)


@router.post("/ai/voice", response_model=VoiceTranscriptResponse)
async def transcribe_voice_note(
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
def synthesise_conclusion(request: ConclusionRequest) -> ConclusionResponse:
    """Synthesise a conclusion section from a completed assessment."""
    try:
        result, ai_log = claude_service.synthesise_conclusion(
            request.project_brief,
            request.hazards,
            request.safety_functions,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    log.info("AI audit: %s", ai_log.model_dump_json())
    return ConclusionResponse(**result)
