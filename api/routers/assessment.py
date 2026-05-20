from fastapi import APIRouter, HTTPException
from models.schemas import (
    HRNParameters,
    HRNScoreResponse,
    HRNTableResponse,
    ImpedeLowerLimbsRequest,
    ImpedeLowerLimbsResponse,
    LowerLimbThroughRequest,
    LowerLimbThroughResponse,
    PLRParametersResponse,
    PLRRequest,
    PLRResultResponse,
    ReachingOverRequest,
    ReachingOverResponse,
    ReachingThroughRequest,
    ReachingThroughResponse,
)
from services.hrn_plr import calculate_hrn, risk_band_for_score, get_hrn_tables, calculate_plr, get_plr_parameters
from services.safety_distance import (
    get_safety_distances_data,
    reaching_over,
    reaching_through_adults,
    reaching_through_children,
    lower_limb_through,
    impede_lower_limbs,
)

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


# ---------------------------------------------------------------------------
# Safety distance endpoints (AS/NZS 4024.1801 — ISO 13857:2008)
# ---------------------------------------------------------------------------

@router.get("/assessment/safety-distances/lookup")
def get_safety_distances_lookup() -> dict:
    return get_safety_distances_data()


@router.post("/assessment/safety-distances/reaching-over", response_model=ReachingOverResponse)
def safety_distance_reaching_over(request: ReachingOverRequest) -> dict:
    result = reaching_over(request.a_mm, request.b_mm, request.risk_level)
    return ReachingOverResponse(**result).model_dump(by_alias=True)


@router.post("/assessment/safety-distances/reaching-through", response_model=ReachingThroughResponse)
def safety_distance_reaching_through(request: ReachingThroughRequest) -> dict:
    try:
        if request.age_group == "children":
            result = reaching_through_children(request.e_mm, request.shape)
        else:
            result = reaching_through_adults(request.e_mm, request.shape)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return ReachingThroughResponse(**result, age_group=request.age_group).model_dump(by_alias=True)


@router.post("/assessment/safety-distances/lower-limbs", response_model=LowerLimbThroughResponse)
def safety_distance_lower_limb_through(request: LowerLimbThroughRequest) -> dict:
    try:
        result = lower_limb_through(request.e_mm, request.shape)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return LowerLimbThroughResponse(**result).model_dump(by_alias=True)


@router.post("/assessment/safety-distances/impede-lower-limbs", response_model=ImpedeLowerLimbsResponse)
def safety_distance_impede_lower_limbs(request: ImpedeLowerLimbsRequest) -> dict:
    try:
        result = impede_lower_limbs(request.h_mm, request.case)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return ImpedeLowerLimbsResponse(**result).model_dump(by_alias=True)
