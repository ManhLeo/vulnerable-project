from __future__ import annotations

import logging
from fastapi import HTTPException, status
from app.models.user_models import UserCreate, UserLogin, UserInDB, Role, UserResponse
from app.models.audit_models import AuditLogCreate, AuditLogDocument, AuditEvent
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.core.security import get_password_hash, verify_password, validate_password_policy, create_access_token

logger = logging.getLogger("app.services.auth")


class AuthService:
    def __init__(self, user_repo: UserRepository, audit_repo: AuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def log_audit(
        self,
        *,
        action: AuditEvent,
        endpoint: str,
        status: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        detail: str | None = None,
    ) -> None:
        """Persist an audit event. Failure is non-fatal and must never bubble up."""
        try:
            log = AuditLogCreate(
                user_id=user_id,
                action=action,
                endpoint=endpoint,
                ip_address=ip_address,
                status=status,
                detail=detail,
            )
            await self.audit_repo.log_action(AuditLogDocument(**log.model_dump()))
        except Exception:
            # Audit logging must never crash the main request path
            logger.exception("audit_log_write_failed action=%s", action)

    async def register(self, user_in: UserCreate) -> UserResponse:
        existing_user = await self.user_repo.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        if not validate_password_policy(user_in.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, and a digit",
            )

        user = UserInDB(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            role=Role.USER,
            _id="temp",  # overridden by db
        )
        created_user = await self.user_repo.create_user(user)
        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            role=created_user.role,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
        )

    async def authenticate(self, user_in: UserLogin, ip_address: str | None = None) -> str:
        """
        Validate credentials and return a signed JWT.
        Always returns the same generic error to prevent user enumeration.
        """
        _GENERIC_ERROR = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = await self.user_repo.get_user_by_email(user_in.email)

        # --- check user exists and has password ---
        if not user or not user.has_password():
            # Same generic error to prevent user enumeration
            raise _GENERIC_ERROR

        # --- wrong password ---
        if not verify_password(user_in.password, user.password_hash):
            await self.user_repo.increment_failed_login(user.id)
            await self.log_audit(
                action=AuditEvent.LOGIN_FAILED,
                endpoint="/auth/login",
                ip_address=ip_address,
                status="FAILED_INVALID_CREDENTIALS",
                user_id=user.id,
            )
            raise _GENERIC_ERROR

        # --- inactive / soft-deleted account ---
        if not user.is_active or user.is_deleted:
            await self.log_audit(
                action=AuditEvent.LOGIN_FAILED,
                endpoint="/auth/login",
                ip_address=ip_address,
                status="FAILED_INACTIVE_USER",
                user_id=user.id,
            )
            raise _GENERIC_ERROR  # Same generic message — do not reveal account status

        # --- success ---
        access_token = create_access_token(data={"user_id": user.id, "role": user.role.value})
        await self.user_repo.update_last_login(user.id)

        # Distinguish admin logins for extra observability
        audit_event = AuditEvent.ADMIN_LOGIN if user.role == Role.ADMIN else AuditEvent.LOGIN_SUCCESS
        await self.log_audit(
            action=audit_event,
            endpoint="/auth/login",
            ip_address=ip_address,
            status="SUCCESS",
            user_id=user.id,
        )
        return access_token
