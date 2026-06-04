import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.api.dependencies import UserRepositoryDep, AuditRepositoryDep, ScanRepositoryDep
from app.core.auth_dependencies import require_role, CurrentUserDep
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

