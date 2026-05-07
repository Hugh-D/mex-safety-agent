from fastapi import APIRouter, HTTPException
from models.schemas import (
    HRNParameters,
    HRNScoreResponse,
    HRNTableResponse,
    PLRParametersResponse,
    PLRRequest,
    PLRResultResponse,
)
from services.hrn_plr import calculate_hrn, risk_band_for_score, get_hrn_tables, calculate_plr, get_plr_parameters

router = APIRouter()


@router.get("/assessment/lookup", response_model=HRNTableResponse)
def get_lookup_tables() -> dict:
    return get_hrn_tables()


@router.post("/assessment/hrn", response_model=HRNScoreResponse)
def score_hrn(parameters: HRNParameters) -> dict:
    score = calculate_hrn(parameters.LO, parameters.FE, parameters.DPH, parameters.NP)
    band = risk_band_for_score(score)
    return HRNScoreResponse(hrn_score=score, risk_band=band, acceptable=band.get("acceptable", False)).model_dump(by_alias=True)


@router.get("/assessment/plr/lookup", response_model=PLRParametersResponse)
def get_plr_lookup() -> dict:
    return get_plr_parameters()


@router.post("/assessment/plr", response_model=PLRResultResponse)
def determine_plr(request: PLRRequest) -> dict:
    try:
        plr_required = calculate_plr(request.severity, request.frequency, request.avoidance)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return PLRResultResponse(
        plr_required=plr_required,
        source_standard=get_plr_parameters()["source_standard"],
        parameter_selection={
            "severity": request.severity,
            "frequency": request.frequency,
            "avoidance": request.avoidance,
        },
    ).model_dump(by_alias=True)
