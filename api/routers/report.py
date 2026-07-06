from fastapi import APIRouter, Response, HTTPException, Query
from models.schemas import AssessmentProject, ReportDraftRequest
from services.project_store import load_project
from services.report_generator import build_risk_assessment_pdf, build_risk_assessment_docx
from services.hrn_plr import verify_hazards

router = APIRouter()

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.post("/report/draft", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def create_report(request: ReportDraftRequest) -> Response:
    errors = verify_hazards(request.hazards)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "HRN verification failed — report blocked.", "errors": errors})
    pdf_bytes = build_risk_assessment_pdf(request)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.get("/report/project/{project_number}", response_class=Response)
def create_report_from_project(
    project_number: str,
    format: str = Query(default="pdf", pattern="^(pdf|docx)$"),
) -> Response:
    project = load_project(project_number)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    errors = verify_hazards(project.hazards)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "HRN verification failed — report blocked.", "errors": errors})
    safe_name = project_number.replace(" ", "_").replace("/", "-")
    if format == "docx":
        docx_bytes = build_risk_assessment_docx(project)
        return Response(
            content=docx_bytes,
            media_type=DOCX_MIME,
            headers={"Content-Disposition": f'attachment; filename="{safe_name}_RA.docx"'},
        )
    pdf_bytes = build_risk_assessment_pdf(project)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_RA.pdf"'},
    )
