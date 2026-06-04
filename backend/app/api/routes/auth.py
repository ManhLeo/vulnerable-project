from typing import Annotated

from fastapi import APIRouter, Depends, Response, Request
from app.models.user_models import UserCreate, UserLogin, UserResponse
from app.models.audit_models import AuditEvent
from app.services.auth_service import AuthService
from app.api.dependencies import UserRepositoryDep, AuditRepositoryDep
from app.core.auth_dependencies import CurrentUserDep
from app.core.config import settings
from app.core.limiter import limiter
from app.core.response import success_response

COOKIE_SECURE = settings.app_env == "production"
COOKIE_SAMESITE = "lax"

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(user_repo: UserRepositoryDep, audit_repo: AuditRepositoryDep) -> AuthService:
    return AuthService(user_repo, audit_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, user_in: UserCreate, auth_service: AuthServiceDep):
    """Register a new user. Rate-limited: 3 attempts/minute/IP."""
    user = await auth_service.register(user_in)
    return success_response(data=user, message="Registration successful")


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, response: Response, user_in: UserLogin, auth_service: AuthServiceDep):
    """Authenticate and set HttpOnly cookie. Rate-limited: 5 attempts/minute/IP."""
    ip = request.client.host if request.client else None
    token = await auth_service.authenticate(user_in, ip)
    result = success_response(data={"authenticated": True}, message="Successfully logged in")
    result.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=24 * 60 * 60,
        path="/",
    )
    return result


@router.post("/logout")
async def logout(request: Request, response: Response, current_user: CurrentUserDep, auth_service: AuthServiceDep):
    """Clear HttpOnly cookie and write audit log."""
    await auth_service.log_audit(
        action=AuditEvent.LOGOUT,
        endpoint="/auth/logout",
        ip_address=request.client.host if request.client else None,
        status="SUCCESS",
        user_id=current_user.id,
    )
    result = success_response(data={"authenticated": False}, message="Successfully logged out")
    result.delete_cookie(
        key="access_token",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )
    return result


@router.get("/me")
async def get_me(current_user: CurrentUserDep):
    """Get current authenticated user."""
    return success_response(
        data=UserResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            last_login_at=current_user.last_login_at,
        ),
        message="Current user retrieved successfully",
    )
