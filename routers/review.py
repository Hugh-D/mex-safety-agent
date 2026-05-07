"""
/api/review  — Compliance review endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models import ProjectInput, ParseResult, ReviewResult
from services.review_service import run_review

router = APIRouter()


class ReviewRequest(BaseModel):
    project:      ProjectInput
    parse_result: Optional[ParseResult] = None


@router.post("/", response_model=ReviewResult, summary="Run a PLd/Cat compliance review")
async def compliance_review(req: ReviewRequest):
    """
    Submit project data + equipment list (and optional parsed drawing data)
    to receive a full compliance review against AS4024 / ISO 13849-1.

    The parse_result field is optional — if provided, the review agent will
    also analyse the parsed drawing topology.
    """
    try:
        result = await run_review(req.project, req.parse_result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")
