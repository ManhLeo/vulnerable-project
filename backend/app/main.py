from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.ai.model_manager import model_manager
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import RequestLoggingMiddleware, setup_logging
from app.core.response import error_response
from app.core.database import database_manager
from app.core.limiter import limiter
from app.core.security import get_password_hash, validate_password_policy
from app.core.security_headers import SecurityHeadersMiddleware
from app.models.user_models import Role, UserInDB
from app.repositories.user_repository import UserRepository
from slowapi.errors import RateLimitExceeded


setup_logging()
logger = logging.getLogger("app.main")


# ---------------------------------------------------------------------------
# Request body size guard (global — not just on upload endpoints)
# ---------------------------------------------------------------------------
class ContentSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose body exceeds the configured maximum."""

    def __init__(self, app, max_body_size: int) -> None:
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        try:
            parsed_content_length = int(content_length) if content_length else 0
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid Content-Length header",
                    "error_code": "INVALID_CONTENT_LENGTH",
                    "request_id": str(uuid.uuid4()),
                },
            )

        if parsed_content_length > self.max_body_size:
            return JSONResponse(
                status_code=413,
                content={
                    "status": "error",
                    "message": "Request body too large",
                    "error_code": "PAYLOAD_TOO_LARGE",
                    "request_id": str(uuid.uuid4()),
                },
            )
        return await call_next(request)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup_begin")
    if settings.use_in_memory_repository:
        logger.info("repository_mode=in_memory mongodb_skipped")
    else:
        await database_manager.connect()
        await database_manager.ensure_indexes()

    await ensure_admin_account()

    try:
        await model_manager.load()
        app.state.model_manager_load_failed = False
    except RuntimeError as exc:
        logger.warning("model_manager_load_failed startup error=%s", str(exc))
        app.state.model_manager_load_failed = True

    logger.info("application_startup_complete")
    yield
    logger.info("application_shutdown_begin")
    await model_manager.unload()
    if not settings.use_in_memory_repository:
        await database_manager.disconnect()
    logger.info("application_shutdown_complete")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    debug=False,  # Always False — never expose tracebacks regardless of env
    lifespan=lifespan,
    # Hide internal FastAPI/Starlette server header
    openapi_url="/api/openapi.json" if settings.app_env != "production" else None,
)
app.state.limiter = limiter


async def ensure_admin_account() -> None:
    if not settings.admin_email or not settings.admin_password:
        return

    if settings.use_in_memory_repository:
        from app.api.dependencies import get_user_repository

        repo = get_user_repository()
    else:
        repo = UserRepository(database_manager.db)
    existing_admin = await repo.get_user_by_role(Role.ADMIN)
    if existing_admin:
        return

    existing_user = await repo.get_user_by_email(settings.admin_email)
    if existing_user:
        if existing_user.role != Role.ADMIN:
            promoted = await repo.update_user_role(existing_user.id, Role.ADMIN)
            if promoted:
                logger.info("default_admin_promoted email=%s", settings.admin_email)
        return

    if not validate_password_policy(settings.admin_password):
        logger.warning("default_admin_not_created invalid password for ADMIN_PASSWORD")
        return

    admin_user = UserInDB(
        email=settings.admin_email,
        password_hash=get_password_hash(settings.admin_password),
        role=Role.ADMIN,
        _id="temp",
    )
    await repo.create_user(admin_user)
    logger.info("default_admin_created email=%s", settings.admin_email)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
def _request_id() -> str:
    return str(uuid.uuid4())


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_exception(request: Request, exc: RateLimitExceeded):
    rid = _request_id()
    logger.warning("rate_limit_exceeded request_id=%s path=%s", rid, request.url.path)
    return error_response(
        message="Too many requests, please try again later",
        error_code="RATE_LIMIT_EXCEEDED",
        status_code=429,
        request_id=rid,
    )


@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    rid = _request_id()
    logger.info(
        "app_exception request_id=%s error_code=%s status=%s",
        rid, exc.error_code, exc.status_code,
    )
    return error_response(
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        request_id=rid,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    rid = _request_id()
    logger.warning("validation_error request_id=%s", rid)
    return error_response(
        message="Validation error",
        error_code="VALIDATION_ERROR",
        status_code=422,
        request_id=rid,
    )


def _http_exception_error_code(status_code: int) -> str:
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
    }
    return mapping.get(status_code, "HTTP_ERROR")


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    rid = _request_id()
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    logger.info(
        "http_exception request_id=%s status=%s path=%s",
        rid,
        exc.status_code,
        request.url.path,
    )
    return error_response(
        message=detail,
        error_code=_http_exception_error_code(exc.status_code),
        status_code=exc.status_code,
        request_id=rid,
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    rid = _request_id()
    # Log the full traceback internally but NEVER return it to the client
    logger.exception("unhandled_exception request_id=%s", rid)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "request_id": rid,  # Allows support to correlate with server logs
        },
    )


# ---------------------------------------------------------------------------
# Middleware  (applied in reverse order — last added = outermost)
# ---------------------------------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ContentSizeLimitMiddleware, max_body_size=settings.max_request_body_size)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router)


# ---------------------------------------------------------------------------
# Health probe
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {"service": settings.app_name},
            "message": "Service is running",
        },
    )
