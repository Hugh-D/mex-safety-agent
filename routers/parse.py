"""
/api/parse  — Drawing parser endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser_service import parse_drawing
from models import ParseResult

router = APIRouter()


@router.post("/drawing", response_model=ParseResult, summary="Parse an electrical drawing PDF")
async def parse_drawing_endpoint(file: UploadFile = File(...)):
    """
    Upload a PDF electrical drawing (single line diagram, schematic, or safety circuit).
    Returns identified components, wiring observations, and safety concerns.

    Accepts: PDF (vector or scanned/raster)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum 20 MB.")

    try:
        result = await parse_drawing(pdf_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {str(e)}")
