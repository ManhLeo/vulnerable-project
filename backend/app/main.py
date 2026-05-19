from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.model_manager import model_manager
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import RequestLoggingMiddleware, setup_logging
from app.core.response import error_response
from app.db.mongo import mongo_manager
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded



setup_logging()
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup_begin")
    await mongo_manager.connect()
    await model_manager.load()
    logger.info("application_startup_complete")
    yield
    logger.info("application_shutdown_begin")
    await model_manager.unload()
    await mongo_manager.disconnect()
    logger.info("application_shutdown_complete")


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_exception(_: Request, exc: RateLimitExceeded):
    logger.warning("rate_limit_exceeded details=%s", str(exc))
    return error_response(
        message="Too many requests, please try again later",
        error_code="RATE_LIMIT_EXCEEDED",
        status_code=429,
    )


@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException):
    return error_response(
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError):
    logger.warning("validation_error details=%s", exc.errors())
    return error_response(
        message="Validation error",
        error_code="VALIDATION_ERROR",
        status_code=422,
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(_: Request, exc: Exception):
    logger.exception("unhandled_exception error=%s", str(exc))
    return error_response(
        message="Internal server error",
        error_code="INTERNAL_SERVER_ERROR",
        status_code=500,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(api_router)


@app.get("/")
async def root():
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {"service": settings.app_name},
            "message": "Service is running",
        },
    )
