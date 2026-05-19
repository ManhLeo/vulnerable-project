from __future__ import annotations

from pydantic import BaseModel, Field, model_validator, field_validator


class ScanCodeRequest(BaseModel):
    source_code: str = Field(..., min_length=1, description="Raw source code to scan")
    language: str = Field(..., description="Programming language, e.g. py, c, cpp, java")

    @model_validator(mode="before")
    @classmethod
    def map_legacy_code_field(cls, data):
        if isinstance(data, dict):
            has_source = bool(data.get("source_code"))
            if not has_source and data.get("code") is not None:
                data["source_code"] = data.get("code")
        return data

    @field_validator("language")
    @classmethod
    def normalize_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("language is required")

        language_aliases = {
            "python": "py",
            "c++": "cpp",
        }
        return language_aliases.get(normalized, normalized)


class FindingItem(BaseModel):
    pattern: str
    issue: str
    severity: str
    line: int = Field(..., ge=1)
    code: str


class ScanResultData(BaseModel):
    is_vulnerable: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    findings: list[FindingItem] = Field(default_factory=list)


class ScanHistoryItem(BaseModel):
    id: str
    filename: str | None = None
    language: str
    is_vulnerable: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    created_at: str


class ScanHistoryData(BaseModel):
    items: list[ScanHistoryItem]
    total: int
    page: int
    limit: int
