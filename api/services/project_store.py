from __future__ import annotations
from pathlib import Path
import json
import threading
from typing import Any, Dict, List, Optional

from models.schemas import AssessmentProject

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROJECTS_DIR = DATA_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Per-project locks prevent concurrent writes corrupting a JSON file.
_locks: dict[str, threading.Lock] = {}
_locks_meta = threading.Lock()


def _get_lock(project_number: str) -> threading.Lock:
    with _locks_meta:
        if project_number not in _locks:
            _locks[project_number] = threading.Lock()
        return _locks[project_number]


def _project_file(project_number: str) -> Path:
    safe_name = project_number.replace("/", "_").replace("\\", "_")
    return PROJECTS_DIR / f"{safe_name}.json"


def save_project(project: AssessmentProject) -> AssessmentProject:
    project.updated_at = project.updated_at or project.created_at
    project_number = project.project_brief.project_number
    path = _project_file(project_number)
    with _get_lock(project_number):
        path.write_text(project.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
    return project


def load_project(project_number: str) -> Optional[AssessmentProject]:
    path = _project_file(project_number)
    if not path.exists():
        return None
    with _get_lock(project_number):
        data = json.loads(path.read_text(encoding="utf-8"))
    return AssessmentProject.model_validate(data)


def list_projects() -> List[str]:
    return [path.stem for path in PROJECTS_DIR.glob("*.json")]
