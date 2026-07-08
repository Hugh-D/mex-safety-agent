from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from models.schemas import AssessmentProject, ProjectListResponse
from services.project_store import save_project, load_project, list_projects, delete_project
from services.hrn_plr import verify_hazards
from services import storage

router = APIRouter()


@router.post("/assessment/project", response_model=AssessmentProject)
def create_or_update_project(project: AssessmentProject) -> dict:
    errors = verify_hazards(project.hazards)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "HRN verification failed — scores/bands must match the server calculation.", "errors": errors})
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


@router.delete("/assessment/project/{project_number}", status_code=204)
def remove_project(project_number: str) -> None:
    if not delete_project(project_number):
        raise HTTPException(status_code=404, detail="Project not found")


def _safe_name(project_number: str) -> str:
    name = project_number
    for ch in '/\\<>:"|?*# ':
        name = name.replace(ch, "_")
    return name.rstrip(". ") or "unnamed"


@router.post("/assessment/project/{project_number}/photo")
async def upload_hazard_photo(
    project_number: str,
    hazard_id: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    safe_proj = _safe_name(project_number)
    original = Path(file.filename or "photo.jpg").name
    safe_filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in original)
    unique_name = f"{uuid4().hex[:8]}_{safe_filename}"
    key = f"{safe_proj}/{hazard_id}/{unique_name}"

    data = await file.read()
    filepath = storage.upload_photo(data, key, filename=original)

    return {"filepath": filepath}
