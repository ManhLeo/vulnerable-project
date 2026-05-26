from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.models.scan_models import (
    AnalysisResult,
    MetadataInfo,
    PredictionResult,
    ScanCreate,
    ScanDetailResponse,
    ScanHistoryItemResponse,
    SuspiciousPattern,
)


def new_scan_id() -> str:
    return str(uuid4())


def findings_to_patterns(findings: list[dict[str, Any]]) -> list[SuspiciousPattern]:
    patterns: list[SuspiciousPattern] = []
    for item in findings:
        patterns.append(
            SuspiciousPattern(
                pattern=str(item.get("pattern", "")),
                issue=str(item.get("issue", "")),
                line=int(item.get("line", 1)),
                severity=item.get("severity"),
                code=item.get("code"),
            )
        )
    return patterns


def patterns_to_findings(patterns: list[dict[str, Any]] | list[SuspiciousPattern]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in patterns:
        if isinstance(item, SuspiciousPattern):
            findings.append(item.model_dump(exclude_none=True))
        else:
            findings.append(
                {
                    "pattern": item.get("pattern", ""),
                    "issue": item.get("issue", ""),
                    "severity": item.get("severity", "MEDIUM"),
                    "line": item.get("line", 1),
                    "code": item.get("code", ""),
                }
            )
    return findings


def scan_create_to_document(scan: ScanCreate, scan_id: str) -> dict[str, Any]:
    """Convert a validated ScanCreate into a MongoDB document."""
    created_at = datetime.now(timezone.utc).isoformat()
    return {
        "_id": scan_id,
        "scan_id": scan_id,
        "source_type": scan.source_type.value,
        "language": scan.language,
        "filename": scan.filename,
        "code": scan.code,
        "prediction": scan.prediction.model_dump(),
        "analysis": {
            "suspicious_patterns": [
                pattern.model_dump(exclude_none=True) for pattern in scan.analysis.suspicious_patterns
            ],
        },
        "metadata": scan.metadata.model_dump(exclude_none=True),
        "created_at": created_at,
    }


def _extract_prediction(doc: dict[str, Any]) -> dict[str, Any]:
    if "prediction" in doc and isinstance(doc["prediction"], dict):
        return doc["prediction"]
    return {
        "is_vulnerable": bool(doc.get("is_vulnerable", False)),
        "confidence": float(doc.get("confidence", 0.0)),
        "risk_level": str(doc.get("risk_level", "LOW")).upper(),
    }


def _extract_patterns(doc: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = doc.get("analysis")
    if isinstance(analysis, dict):
        patterns = analysis.get("suspicious_patterns")
        if isinstance(patterns, list):
            return patterns_to_findings(patterns)

    findings = doc.get("findings")
    if isinstance(findings, list):
        return patterns_to_findings(findings)

    return []


def document_to_history_item(doc: dict[str, Any]) -> ScanHistoryItemResponse:
    prediction = _extract_prediction(doc)
    scan_id = str(doc.get("scan_id") or doc.get("_id", ""))
    created_at = doc.get("created_at", "")
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

    return ScanHistoryItemResponse(
        id=scan_id,
        filename=doc.get("filename"),
        language=str(doc.get("language", "")),
        is_vulnerable=bool(prediction["is_vulnerable"]),
        confidence=float(prediction["confidence"]),
        risk_level=str(prediction["risk_level"]),
        created_at=str(created_at),
        source_type=doc.get("source_type"),
    )


def document_to_detail(doc: dict[str, Any]) -> ScanDetailResponse:
    prediction = _extract_prediction(doc)
    scan_id = str(doc.get("scan_id") or doc.get("_id", ""))
    created_at = doc.get("created_at", "")
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

    metadata_raw = doc.get("metadata")
    metadata = MetadataInfo.model_validate(metadata_raw) if isinstance(metadata_raw, dict) else None

    return ScanDetailResponse(
        scan_id=scan_id,
        source_type=str(doc.get("source_type", "code")),
        filename=doc.get("filename"),
        language=str(doc.get("language", "")),
        source_code=str(doc.get("code") or doc.get("source_code", "")),
        is_vulnerable=bool(prediction["is_vulnerable"]),
        confidence=float(prediction["confidence"]),
        risk_level=str(prediction["risk_level"]),
        findings=_extract_patterns(doc),
        metadata=metadata,
        created_at=str(created_at),
    )


def document_to_scan_result(doc: dict[str, Any]) -> dict[str, Any]:
    detail = document_to_detail(doc)
    return {
        "scan_id": detail.scan_id,
        "is_vulnerable": detail.is_vulnerable,
        "confidence": detail.confidence,
        "risk_level": detail.risk_level,
        "findings": detail.findings,
    }
