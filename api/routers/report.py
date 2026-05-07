from fastapi import APIRouter, Response, HTTPException
from models.schemas import AssessmentProject, ReportDraftRequest
from services.project_store import load_project
from services.report_generator import build_risk_assessment_pdf

router = APIRouter()


@router.post("/report/draft", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def create_report(request: ReportDraftRequest) -> Response:
    pdf_bytes = build_risk_assessment_pdf(request)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.get("/report/project/{project_number}", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def create_report_from_project(project_number: str) -> Response:
    project = load_project(project_number)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    pdf_bytes = build_risk_assessment_pdf(project)
    return Response(content=pdf_bytes, media_type="application/pdf")
