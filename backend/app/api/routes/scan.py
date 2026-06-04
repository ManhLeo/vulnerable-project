import os
import logging

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile

from app.api.dependencies import ScanRepositoryDep, AuditRepositoryDep
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.limiter import limiter, get_rate_limit, get_scan_rate_limit_key
from app.core.response import success_response
from app.core.auth_dependencies import CurrentUserDep, OptionalUserDep, require_role
from app.models.audit_models import AuditEvent, AuditLogCreate, AuditLogDocument
from app.models.user_models import Role
from app.schemas.scan import ScanCodeRequest
from app.services.scan_service import ScanService

logger = logging.getLogger("app.routes.scan")

router = APIRouter(prefix="/scan", tags=["scan"])

# Extensions that must never be accepted regardless of MIME type
_BLOCKED_EXTENSIONS: frozenset[str] = frozenset({
    ".exe", ".dll", ".so", ".bin", ".bat", ".cmd", ".sh", ".ps1",
    ".msi", ".com", ".scr", ".vbs", ".jar", ".py", ".rb", ".php",
    ".pl", ".js", ".ts",  # Script types not part of C/C++ analysis
})


def get_scan_service(repository: ScanRepositoryDep) -> ScanService:
    return ScanService(repository=repository)


async def _log_file_rejection(
    audit_repo,
    reason: str,
    ip: str | None,
    user_id: str | None,
    endpoint: str,
) -> None:
    """Non-fatal audit log for rejected uploads."""
    try:
        log = AuditLogCreate(
            user_id=user_id,
            action=AuditEvent.FILE_UPLOAD_REJECTED,
            endpoint=endpoint,
            ip_address=ip,
            status="REJECTED",
            detail=reason,
        )
        await audit_repo.log_action(AuditLogDocument(**log.model_dump()))
    except Exception:
        logger.exception("audit_file_rejection_failed")


def _validate_upload_filename(filename: str) -> None:
    """
    Reject:
    - Null-byte injections
    - Path traversal attempts
    - Double extensions (e.g. file.cpp.exe)
    - Blocked extension types
    """
    if "\x00" in filename:
        raise BadRequestException("Invalid filename: null byte detected", "INVALID_FILENAME")

    safe_name = os.path.basename(filename.replace("\\", "/"))
    if not safe_name:
        raise BadRequestException("Invalid filename", "INVALID_FILENAME")

    # Detect double extensions — only the last extension matters for allowlisting
    # but we reject if ANY extension in the name is in the blocked set
    parts = safe_name.split(".")
    if len(parts) > 2:
        # e.g. "evil.cpp.exe" → extensions are [".cpp", ".exe"]
        all_exts = {"." + p.lower() for p in parts[1:]}
        if all_exts & _BLOCKED_EXTENSIONS:
            raise BadRequestException(
                "File contains a disallowed extension",
                "INVALID_FILE_EXTENSION",
            )

    _, ext = os.path.splitext(safe_name.lower())
    if ext in _BLOCKED_EXTENSIONS:
        raise BadRequestException(
            "File type not allowed",
            "INVALID_FILE_EXTENSION",
        )


@router.post("/code")
@limiter.limit(get_rate_limit, key_func=get_scan_rate_limit_key)
async def scan_code(
    request: Request,
    payload: ScanCodeRequest,
    service: ScanService = Depends(get_scan_service),
    current_user: OptionalUserDep = None,
):
    data = await service.scan_code(
        source_code=payload.source_code,
        language=payload.language,
        user_id=current_user.id if current_user else None,
    )
    return success_response(data=data, message="Analysis completed")


@router.post("/file")
@limiter.limit(get_rate_limit, key_func=get_scan_rate_limit_key)
async def scan_file(
    request: Request,
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    service: ScanService = Depends(get_scan_service),
    audit_repo: AuditRepositoryDep = None,
    current_user: OptionalUserDep = None,
):
    ip = request.client.host if request.client else None
    uid = current_user.id if current_user else None
    filename = file.filename or "uploaded_file"

    # --- filename security checks ---
    try:
        _validate_upload_filename(filename)
    except BadRequestException as exc:
        await _log_file_rejection(audit_repo, exc.message, ip, uid, "/scan/file")
        raise

    # --- size check via Content-Length header (fast path) ---
    if file.size and file.size > 5 * 1024 * 1024:
        await _log_file_rejection(audit_repo, "file_too_large_header", ip, uid, "/scan/file")
        raise BadRequestException("File too large", "FILE_TOO_LARGE")

    content = await file.read()

    # --- size check on actual body (cannot be spoofed) ---
    if len(content) > 5 * 1024 * 1024:
        await _log_file_rejection(audit_repo, "file_too_large_body", ip, uid, "/scan/file")
        raise BadRequestException("File too large", "FILE_TOO_LARGE")

    data = await service.scan_file(
        filename=filename,
        content_bytes=content,
        language_hint=language,
        user_id=uid,
    )
    return success_response(data=data, message="Analysis completed")


@router.get("/history")
async def scan_history(
    current_user: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    filename: str | None = Query(default=None),
    language: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    is_vulnerable: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    service: ScanService = Depends(get_scan_service),
):
    # Admins see all; regular users see only their own scans
    owner_filter = None if current_user.role == Role.ADMIN else current_user.id
    data = await service.get_scan_history(
        page=page,
        limit=limit,
        filename=filename,
        language=language,
        risk_level=risk_level,
        is_vulnerable=is_vulnerable,
        search=search,
        user_id=owner_filter,
    )
    return success_response(data=data, message="Scan history retrieved successfully")


@router.get("/stats")
async def scan_stats(
    current_user: CurrentUserDep,
    service: ScanService = Depends(get_scan_service),
):
    owner_filter = None if current_user.role == Role.ADMIN else current_user.id
    data = await service.get_dashboard_stats(user_id=owner_filter)
    return success_response(data=data, message="Scan stats retrieved successfully")


@router.get("/{record_id}")
async def get_scan_record(
    record_id: str,
    current_user: CurrentUserDep,
    service: ScanService = Depends(get_scan_service),
):
    data = await service.get_scan_record(record_id)

    # Return 404 for both "not found" and "not owned" — prevents ID enumeration
    if not data:
        raise NotFoundException(message="Scan record not found", error_code="SCAN_NOT_FOUND")

    if current_user.role != Role.ADMIN:
        record_owner = data.get("user_id") if isinstance(data, dict) else getattr(data, "user_id", None)
        if record_owner != current_user.id:
            # Deliberate 404 — do not reveal that the record exists
            raise NotFoundException(message="Scan record not found", error_code="SCAN_NOT_FOUND")

    return success_response(data=data, message="Scan record retrieved successfully")


@router.delete("/{record_id}", dependencies=[Depends(require_role([Role.ADMIN.value]))])
async def delete_scan_record(
    record_id: str,
    service: ScanService = Depends(get_scan_service),
):
    await service.delete_scan(record_id)
    return success_response(data={"deleted": True}, message="Scan record deleted successfully")
