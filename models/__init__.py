"""
Data models — MEX Safety Agent
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Union
from enum import Enum
import re


def _coerce_to_list(v) -> List[str]:
    """Accept List[str] or a plain string — split prose into sentences if needed."""
    if isinstance(v, list):
        return [str(s).strip() for s in v if str(s).strip()]
    if isinstance(v, str) and v.strip():
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', v.strip())
        return [p.strip() for p in parts if p.strip()]
    return []


class PLRating(str, Enum):
    PLa = "PLa"
    PLb = "PLb"
    PLc = "PLc"
    PLd = "PLd"
    PLe = "PLe"


class SILRating(str, Enum):
    SIL1 = "SIL1"
    SIL2 = "SIL2"
    SIL3 = "SIL3"


class Category(str, Enum):
    B  = "B"
    C1 = "1"
    C2 = "2"
    C3 = "3"
    C4 = "4"


class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR    = "MAJOR"
    MINOR    = "MINOR"


class OverallStatus(str, Enum):
    pass_   = "pass"
    warn    = "warn"
    fail    = "fail"


# ── Equipment ──────────────────────────────────────────────────────────────────

class EquipmentItem(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    manufacturer: str = Field(..., example="SICK")
    model:        str = Field(..., example="deTec4 Core")
    pl_rating:    Optional[PLRating] = None
    qty:          int = Field(default=1, ge=1)
    function:     Optional[str] = None
    notes:        Optional[str] = None


# ── Project ────────────────────────────────────────────────────────────────────

class ProjectInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    project_number: str   = Field(..., example="MEX-2025-047")
    client:         str   = Field(..., example="Acme Manufacturing")
    machine:        str   = Field(..., example="Robotic palletiser cell")
    target_pl:      PLRating
    target_category: Category
    target_sil:     Optional[SILRating] = None
    redundancy:     Optional[str] = None   # "single", "dual", "dual-monitor"
    dc:             Optional[str] = None   # "none", "low", "med", "high"
    mttfd:          Optional[float] = None
    proof_test:     Optional[str] = None
    equipment:      List[EquipmentItem]
    standards:      List[str] = Field(
        default=["AS4024", "ISO 13849-1"],
        example=["AS4024", "ISO 13849-1", "IEC 62061"]
    )


# ── Parser output ──────────────────────────────────────────────────────────────

class ComponentType(str, Enum):
    estop         = "estop"
    safety_switch = "safety_switch"   # interlocked guard switch, limit switch actuator
    light_curtain = "light_curtain"   # ESPE, AOPDs
    scanner       = "scanner"         # laser area scanner
    safety_relay  = "safety_relay"    # dedicated safety relay module (e.g. Pilz PNOZ, SICK i10)
    safety_plc    = "safety_plc"      # safety PLC / safety controller (e.g. Pilz PSS, B&R SafeIO)
    contactor     = "contactor"       # contactors, motor starters, safety output contacts
    vfd           = "vfd"             # VFDs, soft starters, servo drives
    terminal      = "terminal"        # wire labels, terminal blocks, cable refs
    unknown       = "unknown"


class ParsedComponent(BaseModel):
    id:           str
    label:        str
    type:         ComponentType
    manufacturer: Optional[str] = None
    model:        Optional[str] = None
    pl_rating:    Optional[PLRating] = None
    location:     Optional[str] = None
    notes:        Optional[str] = None


class Connection(BaseModel):
    """A directed connection between two components in the safety circuit."""
    from_id:   str
    to_id:     str
    from_port: Optional[str] = None   # terminal/pin label on the source (e.g. "Q1", "13")
    to_port:   Optional[str] = None   # terminal/pin label on the destination (e.g. "I1", "A1")
    wire_type: str = "control"        # "safety" | "power" | "control" | "feedback"
    label:     Optional[str] = None   # wire number or cable label from drawing


class ParseResult(BaseModel):
    drawing_type:         str
    page_count:           int
    summary:              List[str]
    components:           List[ParsedComponent]
    connections:          List[Connection] = Field(default_factory=list)
    wiring_observations:  List[str]
    safety_concerns:      List[str]
    raw_text_extracted:   Optional[str] = None

    @field_validator('summary', mode='before')
    @classmethod
    def coerce_summary(cls, v): return _coerce_to_list(v)


# ── Compliance review output ───────────────────────────────────────────────────

class ChangeItem(BaseModel):
    id:          int
    priority:    Priority
    description: List[str]
    reference:   str
    action:      str

    @field_validator('description', mode='before')
    @classmethod
    def coerce_description(cls, v): return _coerce_to_list(v)


class EquipmentNote(BaseModel):
    item:  str
    note:  str
    status: str   # "ok", "warn", "fail"


class ReviewResult(BaseModel):
    project_number:  str
    overall_status:  str
    summary:         List[str]
    pl_achievable:   bool
    pl_reasoning:    List[str]
    changes:         List[ChangeItem]
    equipment_notes: List[EquipmentNote]
    standards_checked: List[str]

    @field_validator('summary', 'pl_reasoning', mode='before')
    @classmethod
    def coerce_list_fields(cls, v): return _coerce_to_list(v)


# ── Export request ─────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    project:       ProjectInput
    review_result: ReviewResult
    parse_result:  Optional[ParseResult] = None
