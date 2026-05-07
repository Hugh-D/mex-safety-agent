# Data Model Reference

## HazardEntry (Core field data unit)
```python
HazardEntry:
    id: str                              # e.g., "4.1.1"
    location: str                        # e.g., "V1 Between Cylinder 1 and 2"
    asset_id: Optional[str]              # e.g., "004-SC-WS01"
    mode: str                            # Operation, Maintenance, Setup
    task: str                            # e.g., "Clean Jam during production"
    hazard_types: list[str]              # From hazard_types.json vocabulary
    photos: list[PhotoEntry]             # Geotagged, with optional annotations
    voice_notes: list[VoiceNote]
    typed_notes: Optional[str]
    measurements: Optional[dict]         # Guard height, reach distance, opening size

    # HRN before risk reduction
    hrn_before: HRNParameters            # LO, FE, DPH, NP + justification per param
    hrn_score_before: float
    risk_band_before: str

    # Risk reduction
    risk_reduction_measures: list[str]
    standards_references: list[str]

    # HRN after risk reduction
    hrn_after: HRNParameters
    hrn_score_after: float
    risk_band_after: str

    # AI flags
    ai_validation_flags: list[str]
    ai_recommendations: list[str]
```

## SafetyFunctionSpec (Bridge between Field Mode and Design Mode)
```python
SafetyFunctionSpec:
    function_name: str                   # e.g., "Emergency Stop — Group 1&2 Dryer"
    plr_required: str                    # a, b, c, d, e
    category_required: str               # B, 1, 2, 3, 4
    severity: str                        # S1 or S2
    frequency: str                       # F1 or F2
    avoidance: str                       # P1 or P2
    source_hazard_ids: list[str]         # Links to HazardEntry IDs
    notes: str
```

## ProjectBrief
```python
ProjectBrief:
    project_number: str
    client: str
    site: str
    machine_or_line: str
    assessment_date: date
    team: list[TeamMember]               # name, company, role
    scope_description: str
    standards_applicable: list[str]
    lifecycle_exclusions: list[str]
```

## PhotoEntry
```python
PhotoEntry:
    filepath: str
    timestamp: datetime
    gps_lat: Optional[float]
    gps_lon: Optional[float]
    site_label: str
    equipment_ref: Optional[str]
    annotations: list[Annotation]        # Measurements, arrows, text overlays
```
