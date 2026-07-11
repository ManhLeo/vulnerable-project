import csv
import io
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.api.dependencies import UserRepositoryDep, AuditRepositoryDep, ScanRepositoryDep
from app.core.auth_dependencies import require_role, CurrentUserDep
from app.core.exceptions import BadRequestException
from app.models.audit_models import AuditEvent, AuditLogCreate, AuditLogDocument
from app.models.user_models import Role

logger = logging.getLogger("app.routes.admin")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role([Role.ADMIN.value]))]
)


class UserListResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    is_deleted: bool
    created_at: str
    last_login_at: str | None = None
    failed_login_attempts: int = 0


async def _audit(
    audit_repo: AuditRepositoryDep,
    *,
    action: AuditEvent,
    endpoint: str,
    user_id: str | None,
    ip: str | None,
    detail: str | None = None,
) -> None:
    """Write a non-fatal admin audit event."""
    try:
        log = AuditLogCreate(
            user_id=user_id,
            action=action,
            endpoint=endpoint,
            ip_address=ip,
            status="SUCCESS",
            detail=detail,
        )
        await audit_repo.log_action(AuditLogDocument(**log.model_dump()))
    except Exception:
        logger.exception("admin_audit_write_failed action=%s", action)


def _role_value(role: Any) -> str:
    return str(getattr(role, "value", role))


def _extract_csv_value(row: dict[str, Any], path: tuple[str, ...], default: Any = "") -> Any:
    current: Any = row
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


@router.get("/users")
async def list_users(
    request: Request,
    current_user: CurrentUserDep,
    user_repo: UserRepositoryDep,
    audit_repo: AuditRepositoryDep,
):
    """List all active users."""
    users = await user_repo.get_users(limit=100)
    await _audit(
        audit_repo,
        action=AuditEvent.ADMIN_ACTION,
        endpoint="/admin/users",
        user_id=current_user.id,
        ip=request.client.host if request.client else None,
        detail="LIST_USERS",
    )
    return [
        UserListResponse(
            id=u.id,
            email=u.email,
            role=u.role.value,
            is_active=u.is_active,
            is_deleted=u.is_deleted,
            created_at=u.created_at.isoformat(),
            last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
            failed_login_attempts=u.failed_login_attempts,
        )
        for u in users
    ]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: CurrentUserDep,
    user_repo: UserRepositoryDep,
    audit_repo: AuditRepositoryDep,
):
    """Soft delete a user."""
    if user_id == current_user.id:
        raise BadRequestException(
            message="Cannot delete your own admin account",
            error_code="CANNOT_DELETE_SELF",
        )

    target_user = await user_repo.get_user_by_id(user_id)
    if target_user and _role_value(target_user.role) == Role.ADMIN.value:
        users = await user_repo.get_users(limit=10000)
        active_admins = [
            user
            for user in users
            if _role_value(user.role) == Role.ADMIN.value
            and user.is_active
            and not user.is_deleted
        ]
        if len(active_admins) <= 1:
            raise BadRequestException(
                message="Cannot delete the last admin account",
                error_code="CANNOT_DELETE_LAST_ADMIN",
            )

    success = await user_repo.soft_delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    await _audit(
        audit_repo,
        action=AuditEvent.USER_SOFT_DELETE,
        endpoint=f"/admin/users/{user_id}",
        user_id=current_user.id,
        ip=request.client.host if request.client else None,
        detail=f"target_user_id={user_id}",
    )
    return {"message": "User soft deleted successfully"}


@router.get("/stats")
async def get_dashboard_stats(
    request: Request,
    current_user: CurrentUserDep,
    user_repo: UserRepositoryDep,
    scan_repo: ScanRepositoryDep,
    audit_repo: AuditRepositoryDep,
):
    """Get system-wide statistics for the admin dashboard."""
    total_users = await user_repo.get_users_count()
    stats = await scan_repo.get_dashboard_stats()

    await _audit(
        audit_repo,
        action=AuditEvent.ADMIN_ACTION,
        endpoint="/admin/stats",
        user_id=current_user.id,
        ip=request.client.host if request.client else None,
        detail="VIEW_DASHBOARD_STATS",
    )
    return {
        "users": {"total_active": total_users},
        "scans": stats.model_dump(),
    }


@router.get("/scan-sources/export.csv")
async def export_scan_sources_csv(
    request: Request,
    current_user: CurrentUserDep,
    user_repo: UserRepositoryDep,
    scan_repo: ScanRepositoryDep,
    audit_repo: AuditRepositoryDep,
):
    """Export raw scanned source code as CSV for administrators only."""
    rows = await scan_repo.list_all_for_export()
    users = await user_repo.get_users(limit=10000)
    user_email_by_id = {user.id: user.email for user in users}

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    columns = [
        "scan_id",
        "user_id",
        "user_email",
        "created_at",
        "filename",
        "language",
        "risk_level",
        "vulnerable",
        "confidence",
        "model_mode",
        "selected_checkpoint",
        "source_code",
    ]
    writer.writerow(columns)

    for row in rows:
        user_id = str(row.get("user_id") or "")
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        is_vulnerable = bool(_extract_csv_value(row, ("prediction", "is_vulnerable"), False))
        vulnerable = 1 if is_vulnerable else 0
        writer.writerow(
            [
                str(row.get("scan_id") or row.get("_id") or ""),
                user_id,
                user_email_by_id.get(user_id, "guest" if not user_id else ""),
                str(row.get("created_at") or ""),
                str(row.get("filename") or ""),
                str(row.get("language") or ""),
                str(_extract_csv_value(row, ("prediction", "risk_level"))),
                vulnerable,
                str(_extract_csv_value(row, ("prediction", "confidence"))),
                str(metadata.get("model_mode") or ""),
                str(metadata.get("selected_checkpoint") or metadata.get("checkpoint") or ""),
                str(row.get("code") or row.get("source_code") or ""),
            ]
        )

    await _audit(
        audit_repo,
        action=AuditEvent.ADMIN_ACTION,
        endpoint="/admin/scan-sources/export.csv",
        user_id=current_user.id,
        ip=request.client.host if request.client else None,
        detail="EXPORT_SCAN_SOURCES_CSV",
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="scan_sources_export_{timestamp}.csv"',
        },
    )
