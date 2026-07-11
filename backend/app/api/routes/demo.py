from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.core.response import success_response
from app.services.demo_scan_service import demo_scan_service


router = APIRouter(prefix="/demo", tags=["demo"])


class DemoScanRequest(BaseModel):
    sample_id: str = Field(..., min_length=1)


@router.get("/samples")
async def list_demo_samples():
    return success_response(
        data=demo_scan_service.list_samples(),
        message="Demo samples retrieved successfully",
    )


@router.post("/scan")
async def scan_demo_sample(payload: DemoScanRequest):
    return success_response(
        data=demo_scan_service.scan_sample(payload.sample_id),
        message="Demo scan completed",
    )
