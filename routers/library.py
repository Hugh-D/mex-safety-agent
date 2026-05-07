"""
/api/library  — Equipment library read-only endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.library_service import get_all, get_by_id, search

router = APIRouter()


@router.get("/devices", summary="List all devices in the equipment library")
def list_devices(
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer (partial match)"),
    device_type:  Optional[str] = Query(None, description="Filter by type: estop, safety_relay, safety_plc, interlock, light_curtain, scanner, safety_switch"),
):
    return get_all(manufacturer=manufacturer, device_type=device_type)


@router.get("/devices/{device_id}", summary="Get a single device by ID")
def get_device(device_id: int):
    row = get_by_id(device_id)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    return row


@router.get("/search", summary="Fuzzy search devices by model string")
def search_devices(q: str = Query(..., min_length=2, description="Model name or partial string")):
    results = search(q)
    return [
        {"device": row, "match_type": match_type, "match_score": round(score, 3)}
        for row, match_type, score in results
    ]
