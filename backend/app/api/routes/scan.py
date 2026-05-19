from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile, Request

from app.core.response import success_response
from app.schemas.scan import ScanCodeRequest
from app.services.scan_service import scan_service
from app.core.limiter import limiter

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("/code")
@limiter.limit("10/minute")
async def scan_code(request: Request, payload: ScanCodeRequest):
    data = await scan_service.scan_code(
        source_code=payload.source_code,
        language=payload.language,
    )
    return success_response(data=data, message="Analysis completed")


@router.post("/file")
@limiter.limit("10/minute")
async def scan_file(
    request: Request,
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
):
    content = await file.read()
    data = await scan_service.scan_file(
        filename=file.filename or "uploaded_file",
        content_bytes=content,
        language_hint=language,
    )
    return success_response(data=data, message="Analysis completed")


@router.get("/history")
async def scan_history(page: int = 1, limit: int = 10):
    data = await scan_service.get_scan_history(page=page, limit=limit)
    return success_response(data=data, message="Scan history retrieved successfully")


@router.get("/{record_id}")
async def get_scan_record(record_id: str):
    from app.core.exceptions import NotFoundException
    data = await scan_service.get_scan_record(record_id)
    if not data:
        raise NotFoundException(message="Scan record not found", error_code="SCAN_NOT_FOUND")
    return success_response(data=data, message="Scan record retrieved successfully")
