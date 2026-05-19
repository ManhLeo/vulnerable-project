from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    data: Any,
    message: str = "Request successful",
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "data": data,
            "message": message,
        },
    )


def error_response(
    message: str,
    error_code: str,
    status_code: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "error_code": error_code,
        },
    )
