from __future__ import annotations

import asyncio
import io
import logging
from typing import Any, Optional

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel

from services import compliance_service, dxf_parser

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------
class ComponentIdentified(BaseModel):
    component: str
    type: str
    location: str
    safetyRelevant: bool


class ArchitectureAssessment(BaseModel):
    detectedCategory: str
    detectedPl: str
    channelCount: str
    hasFeedbackMonitoring: Optional[bool]
    hasCrossMonitoring: Optional[bool]
    summary: str


class Conformance(BaseModel):
    description: str
    clauseReference: str


class NonConformance(BaseModel):
    severity: str
    description: str
    clauseReference: str
    remediation: str


class TopologyComponent(BaseModel):
    id: str
    channel: Optional[str]
    seriesGroup: Optional[str]


class TopologyConnection(BaseModel):
    fromId: str
    toId: str
    fromPort: Optional[str]
    toPort: Optional[str]
    wireType: str
    label: Optional[str]


class TopologyResult(BaseModel):
    components: list[TopologyComponent]
    connections: list[TopologyConnection]


class DrawingAnalysisResponse(BaseModel):
    drawingType: str
    componentsIdentified: list[ComponentIdentified]
    architectureAssessment: ArchitectureAssessment
    conformances: list[Conformance]
    nonConformances: list[NonConformance]
    gapToTarget: str
    gapSummary: str
    overallVerdict: str
    topology: Optional[TopologyResult] = None
    svgDiagram: Optional[str] = None


class SafetyFunctionFound(BaseModel):
    name: str
    description: str
    implementation: str
    plClaimed: str
    categoryClaimed: str


class DesignGap(BaseModel):
    severity: str
    description: str
    clauseReference: str
    recommendation: str


class DesignReviewRequest(BaseModel):
    documentText: str
    targetPl: str
    targetCategory: str
    raHazardIds: Optional[list[str]] = None


class DesignReviewResponse(BaseModel):
    safetyFunctionsIdentified: list[SafetyFunctionFound]
    gaps: list[DesignGap]
    coverageAssessment: str
    overallVerdict: str
    recommendations: list[str]


class ComplianceReportRequest(BaseModel):
    drawingTitle: str
    targetPl: str
    targetCategory: str
    format: str = "pdf"
    analysis: dict[str, Any]
    svgDiagram: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/compliance/drawing", response_model=DrawingAnalysisResponse)
async def analyse_drawing(
    file: UploadFile = File(...),
    drawing_title: str = Form(...),
    target_pl: str = Form(...),
    target_category: str = Form(...),
    context: Optional[str] = Form(None),
    dxf_file: Optional[UploadFile] = File(None),
) -> DrawingAnalysisResponse:
    """
    Upload a safety drawing image (PNG/JPG/PDF) and analyse it against a PLr/Category target.
    When a DXF is also provided, topology extraction runs in parallel with the compliance
    analysis so there is no additional wait time.
    """
    image_bytes = await file.read()
    parsed_dxf = None
    dxf_context: Optional[str] = None
    dxf_safety_components: list[dict] = []

    if dxf_file is not None:
        try:
            dxf_bytes = await dxf_file.read()
            parsed_dxf = dxf_parser.parse_dxf(dxf_bytes, dxf_file.filename or "drawing.dxf")
            dxf_context = parsed_dxf.as_context_text()
            dxf_safety_components = [
                {
                    "id":              c.tag or c.block_name,
                    "tag":             c.tag,
                    "compliance_type": c.compliance_type,
                    "component_type":  c.component_type,
                }
                for c in parsed_dxf.safety_components
            ]
        except Exception as exc:
            logger.warning("DXF parse failed in drawing analysis — continuing without DXF context: %s", exc, exc_info=True)

    # Run compliance analysis + topology in parallel when DXF components are available
    topology_raw: Optional[dict] = None
    try:
        if dxf_safety_components:
            raw, topology_raw = await asyncio.gather(
                asyncio.to_thread(
                    compliance_service.analyse_drawing,
                    image_bytes, drawing_title, target_pl, target_category, context, dxf_context,
                ),
                asyncio.to_thread(
                    compliance_service.extract_topology,
                    image_bytes, dxf_safety_components,
                ),
            )
        else:
            raw = await asyncio.to_thread(
                compliance_service.analyse_drawing,
                image_bytes, drawing_title, target_pl, target_category, context, dxf_context,
            )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    # Generate SLD if topology + DXF both available
    svg_diagram: Optional[str] = None
    if topology_raw and parsed_dxf:
        try:
            from services import diagram_service
            non_conformances = raw.get("non_conformances", [])
            svg_diagram = diagram_service.build_diagram_svg(parsed_dxf, topology_raw, non_conformances)
        except Exception as exc:
            logger.warning("SVG diagram generation failed: %s", exc, exc_info=True)

    # Map topology raw dict to response model
    topology_result: Optional[TopologyResult] = None
    if topology_raw:
        try:
            topology_result = TopologyResult(
                components=[
                    TopologyComponent(
                        id=c.get("id", ""),
                        channel=c.get("channel"),
                        seriesGroup=c.get("series_group"),
                    )
                    for c in topology_raw.get("components", [])
                ],
                connections=[
                    TopologyConnection(
                        fromId=c.get("from_id", ""),
                        toId=c.get("to_id", ""),
                        fromPort=c.get("from_port"),
                        toPort=c.get("to_port"),
                        wireType=c.get("wire_type", "safety"),
                        label=c.get("label"),
                    )
                    for c in topology_raw.get("connections", [])
                ],
            )
        except Exception as exc:
            logger.warning("Topology model mapping failed: %s", exc, exc_info=True)

    def _map_component(c: dict) -> ComponentIdentified:
        return ComponentIdentified(
            component=c.get("component", ""),
            type=c.get("type", ""),
            location=c.get("location", ""),
            safetyRelevant=c.get("safety_relevant", True),
        )

    arch = raw.get("architecture_assessment", {})
    return DrawingAnalysisResponse(
        drawingType=raw.get("drawing_type", ""),
        componentsIdentified=[_map_component(c) for c in raw.get("components_identified", [])],
        architectureAssessment=ArchitectureAssessment(
            detectedCategory=arch.get("detected_category", "unknown"),
            detectedPl=arch.get("detected_pl", "unknown"),
            channelCount=arch.get("channel_count", "unknown"),
            hasFeedbackMonitoring=arch.get("has_feedback_monitoring"),
            hasCrossMonitoring=arch.get("has_cross_monitoring"),
            summary=arch.get("summary", ""),
        ),
        conformances=[
            Conformance(description=c.get("description", ""), clauseReference=c.get("clause_reference", ""))
            for c in raw.get("conformances", [])
        ],
        nonConformances=[
            NonConformance(
                severity=nc.get("severity", ""),
                description=nc.get("description", ""),
                clauseReference=nc.get("clause_reference", ""),
                remediation=nc.get("remediation", ""),
            )
            for nc in raw.get("non_conformances", [])
        ],
        gapToTarget=raw.get("gap_to_target", ""),
        gapSummary=raw.get("gap_summary", ""),
        overallVerdict=raw.get("overall_verdict", ""),
        topology=topology_result,
        svgDiagram=svg_diagram,
    )


@router.post("/compliance/report")
async def generate_compliance_report(req: ComplianceReportRequest) -> Response:
    """
    Generate a branded PDF or DOCX compliance report from a drawing analysis result.
    format: "pdf" (default) or "docx"
    """
    fmt = req.format.lower().strip()
    if fmt not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail='format must be "pdf" or "docx"')

    try:
        from services import compliance_report
        if fmt == "pdf":
            data = await asyncio.to_thread(
                compliance_report.generate_pdf,
                req.drawingTitle, req.targetPl, req.targetCategory,
                req.analysis, req.svgDiagram,
            )
            safe_title = req.drawingTitle.replace(" ", "_").replace("/", "-")[:40]
            filename = f"{safe_title}_Compliance_Review.pdf"
            return Response(
                content=data,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        else:
            data = await asyncio.to_thread(
                compliance_report.generate_docx,
                req.drawingTitle, req.targetPl, req.targetCategory,
                req.analysis, req.svgDiagram,
            )
            safe_title = req.drawingTitle.replace(" ", "_").replace("/", "-")[:40]
            filename = f"{safe_title}_Compliance_Review.docx"
            return Response(
                content=data,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")


class ParsedComponentOut(BaseModel):
    blockName: str
    tag: str
    description: str
    location: str
    x: float
    y: float
    componentType: str
    complianceType: str
    safetyRelevant: bool
    safetyNote: Optional[str]
    orientation: str


class DxfParseResponse(BaseModel):
    sourceFilename: str
    dxfVersion: str
    totalInserts: int
    recognisedCount: int
    safetyCount: int
    unknownBlockCount: int
    components: list[ParsedComponentOut]
    unknownBlocks: list[str]
    libraryGaps: list[str]
    contextText: str


@router.post("/compliance/dxf", response_model=DxfParseResponse)
async def parse_dxf_drawing(file: UploadFile = File(...)) -> DxfParseResponse:
    """Parse a DXF file using the MEX symbol library."""
    data = await file.read()
    fname = file.filename or "drawing.dxf"
    try:
        parsed = dxf_parser.parse_dxf(data, fname)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse DXF: {exc}")

    return DxfParseResponse(
        sourceFilename=parsed.source_filename,
        dxfVersion=parsed.dxf_version,
        totalInserts=parsed.total_inserts,
        recognisedCount=len(parsed.components),
        safetyCount=len(parsed.safety_components),
        unknownBlockCount=len(set(parsed.unknown_blocks)),
        components=[
            ParsedComponentOut(
                blockName=c.block_name, tag=c.tag, description=c.description,
                location=c.location, x=c.x, y=c.y,
                componentType=c.component_type, complianceType=c.compliance_type,
                safetyRelevant=c.safety_relevant, safetyNote=c.safety_note,
                orientation=c.orientation,
            )
            for c in parsed.components
        ],
        unknownBlocks=sorted(set(parsed.unknown_blocks)),
        libraryGaps=parsed.library_gaps,
        contextText=parsed.as_context_text(),
    )


@router.post("/compliance/extract-text")
async def extract_document_text(file: UploadFile = File(...)) -> dict:
    """Extract plain text from a PDF or Word document for use in design review."""
    data = await file.read()
    fname = (file.filename or "").lower()
    try:
        if fname.endswith(".pdf") or file.content_type == "application/pdf":
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif fname.endswith(".docx") or "wordprocessingml" in (file.content_type or ""):
            import docx
            doc = docx.Document(io.BytesIO(data))
            text = "\n".join(p.text for p in doc.paragraphs)
        elif fname.endswith(".txt") or (file.content_type or "").startswith("text/"):
            text = data.decode("utf-8", errors="replace")
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type. Upload a PDF, DOCX, or TXT file.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not extract text: {exc}")
    return {"text": text, "characters": len(text)}


@router.post("/compliance/design-review", response_model=DesignReviewResponse)
def review_design(request: DesignReviewRequest) -> DesignReviewResponse:
    """Review a design document (text) for safety function completeness."""
    try:
        raw = compliance_service.review_design_document(
            request.documentText, request.targetPl, request.targetCategory, request.raHazardIds,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    return DesignReviewResponse(
        safetyFunctionsIdentified=[
            SafetyFunctionFound(
                name=sf.get("name", ""), description=sf.get("description", ""),
                implementation=sf.get("implementation", ""),
                plClaimed=sf.get("pl_claimed", ""), categoryClaimed=sf.get("category_claimed", ""),
            )
            for sf in raw.get("safety_functions_identified", [])
        ],
        gaps=[
            DesignGap(
                severity=g.get("severity", ""), description=g.get("description", ""),
                clauseReference=g.get("clause_reference", ""),
                recommendation=g.get("recommendation", ""),
            )
            for g in raw.get("gaps", [])
        ],
        coverageAssessment=raw.get("coverage_assessment", ""),
        overallVerdict=raw.get("overall_verdict", ""),
        recommendations=raw.get("recommendations", []),
    )
