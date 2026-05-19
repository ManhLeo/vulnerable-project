from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponseData(BaseModel):
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Current environment")
    uptime_seconds: float = Field(..., ge=0, description="Service uptime in seconds")
