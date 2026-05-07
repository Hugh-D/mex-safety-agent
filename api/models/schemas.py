from __future__ import annotations
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AIInteractionLog(BaseModel):
    """Audit record for a single Claude API call. Stored alongside AI-generated findings."""
    function: str
    model: str
    response_id: str
    prompt_hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_tokens: int
    output_tokens: int


class CamelModel(BaseModel):
    """Base model that accepts snake_case field names but serialises to camelCase."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TeamMember(CamelModel):
    name: str
    company: str
    role: str


class Annotation(CamelModel):
    type: str
    text: str
    x: Optional[float] = None
    y: Optional[float] = None


class PhotoEntry(CamelModel):
    filepath: str
    timestamp: datetime
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    site_label: str
    equipment_ref: Optional[str] = None
    annotations: List[Annotation] = []


class VoiceNote(CamelModel):
    filepath: str
    timestamp: datetime
    duration_seconds: Optional[float] = None
    transcript: Optional[str] = None


class HRNParameters(CamelModel):
    LO: float = Field(..., description="Likelihood of Occurrence")
    FE: float = Field(..., description="Frequency of Exposure")
    DPH: float = Field(..., description="Degree of Possible Harm")
    NP: float = Field(..., description="Number of Persons at Risk")
    justification: Optional[Dict[str, str]] = None


class RiskBand(CamelModel):
    min: float
    max: Optional[float]
    label: str
    acceptable: bool
    colour: str


class HazardEntry(CamelModel):
    id: str
    location: str
    asset_id: Optional[str] = None
    mode: str
    task: str
    hazard_types: List[str] = []
    photos: List[PhotoEntry] = []
    voice_notes: List[VoiceNote] = []
    typed_notes: Optional[str] = None
    measurements: Optional[Dict[str, Any]] = None
    hrn_before: HRNParameters
    hrn_score_before: float
    risk_band_before: str
    risk_reduction_measures: List[str] = []
    standards_references: List[str] = []
    hrn_after: Optional[HRNParameters] = None
    hrn_score_after: Optional[float] = None
    risk_band_after: Optional[str] = None
    ai_validation_flags: List[str] = []
    ai_recommendations: List[str] = []
    ai_logs: List[AIInteractionLog] = []


class SafetyFunctionSpec(CamelModel):
    function_name: str
    plr_required: str
    category_required: str
    severity: str
    frequency: str
    avoidance: str
    source_hazard_ids: List[str] = []
    notes: Optional[str] = None


class ProjectBrief(CamelModel):
    project_number: str
    client: str
    site: str
    machine_or_line: str
    assessment_date: date
    team: List[TeamMember] = []
    scope_description: str
    standards_applicable: List[str] = []
    lifecycle_exclusions: List[str] = []


class HRNScoreResponse(CamelModel):
    hrn_score: float
    risk_band: RiskBand
    acceptable: bool


class PLRRequest(CamelModel):
    severity: str = Field(..., pattern=r"^S[12]$")
    frequency: str = Field(..., pattern=r"^F[12]$")
    avoidance: str = Field(..., pattern=r"^P[12]$")


class PLRResultResponse(CamelModel):
    plr_required: str
    source_standard: str
    parameter_selection: Dict[str, str]


class ReportDraftRequest(CamelModel):
    project_brief: ProjectBrief
    hazards: List[HazardEntry]
    safety_functions: Optional[List[SafetyFunctionSpec]] = None
    notes: Optional[str] = None


class AssessmentProject(ReportDraftRequest):
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "draft"


class ProjectListResponse(CamelModel):
    project_numbers: List[str]


class HRNTableResponse(CamelModel):
    parameters: Dict[str, Dict[str, Any]]
    risk_bands: List[RiskBand]
    acceptance_threshold: float
    formula: str


class PLRParametersResponse(CamelModel):
    source_standard: str
    parameters: Dict[str, Any]
    risk_graph: Dict[str, str]
    performance_levels: Dict[str, Any]
