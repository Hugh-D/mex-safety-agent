from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Any, Optional

from models.schemas import HRNParameters, HazardEntry, ProjectBrief, SafetyFunctionSpec, ReportDraftRequest
from services import claude_service

log = logging.getLogger(__name__)
router = APIRouter()


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
    log.info("AI audit: %s", ai_log.model_dump_json())
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
