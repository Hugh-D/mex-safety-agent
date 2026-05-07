"""
/api/export  — Redline PDF export endpoints
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from models import ExportRequest
from services.export_service import generate_pdf

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/pdf", summary="Generate branded redline compliance report PDF")
async def export_pdf(req: ExportRequest):
    """
    Accepts a project input + review result (and optional parse result),
    returns a branded MEX redline PDF report for engineer review.
    """
    logger.info("PDF export request received — parse_result present: %s, components: %s",
                req.parse_result is not None,
                len(req.parse_result.components) if req.parse_result else 0)
    try:
        pdf_bytes = generate_pdf(req)
        filename  = f"{req.project.project_number}_Compliance_Review_Redline.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
