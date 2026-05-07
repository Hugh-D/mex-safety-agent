from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, List, Optional

from models.schemas import AssessmentProject

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROJECTS_DIR = DATA_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _project_file(project_number: str) -> Path:
    safe_name = project_number.replace("/", "_").replace("\\", "_")
    return PROJECTS_DIR / f"{safe_name}.json"


def save_project(project: AssessmentProject) -> AssessmentProject:
    project.updated_at = project.updated_at or project.created_at
    path = _project_file(project.project_brief.project_number)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(project.model_dump_json(indent=2, exclude_none=True))
    return project


def load_project(project_number: str) -> Optional[AssessmentProject]:
    path = _project_file(project_number)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return AssessmentProject.model_validate(data)


def list_projects() -> List[str]:
    return [path.stem for path in PROJECTS_DIR.glob("*.json")]
