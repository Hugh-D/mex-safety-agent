from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.schemas import AssessmentProject, ProjectListResponse
from services.project_store import save_project, load_project, list_projects

router = APIRouter()


@router.post("/assessment/project", response_model=AssessmentProject)
def create_or_update_project(project: AssessmentProject) -> dict:
    project.updated_at = datetime.utcnow()
    project.created_at = project.created_at or project.updated_at
    saved = save_project(project)
    return saved.model_dump(by_alias=True)


@router.get("/assessment/project/{project_number}", response_model=AssessmentProject)
def get_project(project_number: str) -> dict:
    project = load_project(project_number)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.model_dump(by_alias=True)


@router.get("/assessment/projects", response_model=ProjectListResponse)
def get_project_list() -> dict:
    return ProjectListResponse(project_numbers=list_projects()).model_dump(by_alias=True)
