from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile

from app.api.dependencies import ScanRepositoryDep
from app.core.exceptions import NotFoundException
from app.core.limiter import limiter
from app.core.response import success_response
from app.schemas.scan import ScanCodeRequest
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scan", tags=["scan"])


def get_scan_service(repository: ScanRepositoryDep) -> ScanService:
    return ScanService(repository=repository)


@router.post("/code")
@limiter.limit("10/minute")
async def scan_code(
    request: Request,
    payload: ScanCodeRequest,
    service: ScanService = Depends(get_scan_service),
):
    data = await service.scan_code(
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
    service: ScanService = Depends(get_scan_service),
):
    content = await file.read()
    data = await service.scan_file(
        filename=file.filename or "uploaded_file",
        content_bytes=content,
        language_hint=language,
    )
    return success_response(data=data, message="Analysis completed")


@router.get("/dashboard/stats")
async def dashboard_stats(service: ScanService = Depends(get_scan_service)):
    data = await service.get_dashboard_stats()
    return success_response(data=data, message="Dashboard statistics retrieved successfully")


@router.get("/history")
async def scan_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    filename: str | None = Query(default=None),
    language: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    is_vulnerable: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    service: ScanService = Depends(get_scan_service),
):
    data = await service.get_scan_history(
        page=page,
        limit=limit,
        filename=filename,
        language=language,
        risk_level=risk_level,
        is_vulnerable=is_vulnerable,
        search=search,
    )
    return success_response(data=data, message="Scan history retrieved successfully")


@router.get("/{record_id}")
async def get_scan_record(
    record_id: str,
    service: ScanService = Depends(get_scan_service),
):
    data = await service.get_scan_record(record_id)
    if not data:
        raise NotFoundException(message="Scan record not found", error_code="SCAN_NOT_FOUND")
    return success_response(data=data, message="Scan record retrieved successfully")


@router.delete("/{record_id}")
async def delete_scan_record(
    record_id: str,
    service: ScanService = Depends(get_scan_service),
):
    await service.delete_scan(record_id)
    return success_response(data={"deleted": True}, message="Scan record deleted successfully")
