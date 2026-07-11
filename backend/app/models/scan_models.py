from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceType(str, Enum):
    CODE = "code"
    FILE = "file"


class SuspiciousPattern(BaseModel):
    """Rule-based finding stored under analysis.suspicious_patterns."""

    pattern: str = Field(..., min_length=1, max_length=256)
    issue: str = Field(..., min_length=1, max_length=512)
    line: int = Field(..., ge=1)
    severity: str | None = Field(default=None, max_length=32)
    code: str | None = Field(default=None, max_length=512)

    model_config = ConfigDict(extra="forbid")


class PredictionResult(BaseModel):
    is_vulnerable: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., min_length=1, max_length=32)

    @field_validator("risk_level")
    @classmethod
    def normalize_risk_level(cls, value: str) -> str:
        return value.strip().upper()


class AnalysisResult(BaseModel):
    suspicious_patterns: list[SuspiciousPattern] = Field(default_factory=list)


class MetadataInfo(BaseModel):
    model_name: str | None = Field(default=None, max_length=128)
    model_version: str | None = Field(default=None, max_length=128)
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    checkpoint: str | None = Field(default=None, max_length=256)
    model_mode: str | None = Field(default=None, max_length=64)
    selected_checkpoint: str | None = Field(default=None, max_length=256)
    inference_used: bool = True
    analysis_mode: str | None = Field(default=None, max_length=64)
    findings_metrics: dict[str, Any] | None = None
    candidate_results: list[dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", protected_namespaces=())


class ScanCreate(BaseModel):
    """Payload used when persisting a completed scan."""

    source_type: SourceType
    language: str = Field(..., min_length=1, max_length=16)
    code: str = Field(..., min_length=1)
    filename: str | None = Field(default=None, max_length=255)
    user_id: str | None = Field(default=None, max_length=36)
    prediction: PredictionResult
    analysis: AnalysisResult
    metadata: MetadataInfo

    @field_validator("language")
    @classmethod
    def normalize_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("language is required")
        return normalized


class ScanDocument(ScanCreate):
    """Full document as stored in MongoDB."""

    scan_id: str = Field(..., min_length=36, max_length=36)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanHistoryFilters(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    filename: str | None = Field(default=None, max_length=255)
    language: str | None = Field(default=None, max_length=16)
    risk_level: str | None = Field(default=None, max_length=32)
    is_vulnerable: bool | None = None
    search: str | None = Field(default=None, max_length=255)
    user_id: str | None = Field(default=None, max_length=36)

    @field_validator("language")
    @classmethod
    def normalize_language_filter(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        return normalized or None

    @field_validator("risk_level")
    @classmethod
    def normalize_risk_filter(cls, value: str | None) -> str | None:
        if value is None or value.strip().upper() == "ALL":
            return None
        return value.strip().upper()


class ScanHistoryItemResponse(BaseModel):
    """List view — flat shape expected by the frontend."""

    id: str
    filename: str | None = None
    language: str
    is_vulnerable: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    created_at: str
    source_type: str | None = None


class PaginationResponse(BaseModel):
    items: list[ScanHistoryItemResponse]
    total: int
    page: int
    limit: int


class DashboardStats(BaseModel):
    total_scans: int
    vulnerable_scans: int
    safe_scans: int
    vulnerable_ratio: float = Field(..., ge=0.0, le=1.0)
    average_confidence: float = Field(..., ge=0.0, le=1.0)
    risk_distribution: dict[str, int]


class ScanDetailResponse(BaseModel):
    """Detail view — includes source code and findings for the result page."""

    scan_id: str
    user_id: str | None = None
    source_type: str
    filename: str | None = None
    language: str
    source_code: str
    is_vulnerable: bool
    confidence: float
    risk_level: str
    findings: list[dict[str, Any]]
    metadata: MetadataInfo | None = None
    created_at: str


class ScanResultResponse(BaseModel):
    """Immediate scan API response (no full document)."""

    scan_id: str
    is_vulnerable: bool
    confidence: float
    risk_level: str
    findings: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None
