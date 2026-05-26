from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppException(Exception):
    message: str
    error_code: str
    status_code: int

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"


class BadRequestException(AppException):
    def __init__(self, message: str = "Invalid request", error_code: str = "BAD_REQUEST") -> None:
        super().__init__(message=message, error_code=error_code, status_code=400)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(message=message, error_code=error_code, status_code=404)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", error_code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message=message, error_code=error_code, status_code=422)


class ConflictException(AppException):
    def __init__(
        self,
        message: str = "Resource already exists",
        error_code: str = "CONFLICT",
    ) -> None:
        super().__init__(message=message, error_code=error_code, status_code=409)


class InternalServerException(AppException):
    def __init__(
        self,
        message: str = "Internal server error",
        error_code: str = "INTERNAL_SERVER_ERROR",
    ) -> None:
        super().__init__(message=message, error_code=error_code, status_code=500)
