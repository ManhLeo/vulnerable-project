from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    status: str = Field(default="success")
    data: T
    message: str = Field(default="Request successful")


class ErrorResponse(BaseModel):
    status: str = Field(default="error")
    message: str
    error_code: str


class HealthData(BaseModel):
    service: str
    version: str
    environment: str
    uptime_seconds: float


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int


class PaginatedData(BaseModel):
    items: list[Any]
    total: int
    page: int
    limit: int
