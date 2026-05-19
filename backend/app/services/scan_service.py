from __future__ import annotations

import os
from typing import Any

from app.ai.inference import inference_service
from app.analysis.detectors import detect_findings
from app.analysis.risk import calculate_risk_score, classify_risk_level
from app.core.constants import MAX_UPLOAD_SIZE_BYTES, SUPPORTED_FILE_EXTENSIONS
from app.core.exceptions import BadRequestException
from app.core.config import settings
from app.db.repositories.in_memory_scan_repository import InMemoryScanRepository
from app.db.repositories.scan_repository import ScanRepository


class ScanService:
    def __init__(self, repository: ScanRepository | InMemoryScanRepository | None = None) -> None:
        if repository is not None:
            self.repository = repository
        elif settings.use_in_memory_repository:
            self.repository = InMemoryScanRepository()
        else:
            self.repository = ScanRepository()

    async def scan_code(self, source_code: str, language: str, filename: str | None = None) -> dict[str, Any]:
        normalized_language = language.strip().lower()
        language_aliases = {
            "python": "py",
            "c++": "cpp",
        }
        normalized_language = language_aliases.get(normalized_language, normalized_language)

        if normalized_language not in {"c", "cpp", "py", "java"}:
            raise BadRequestException(message="Unsupported language", error_code="INVALID_LANGUAGE")

        inference = await inference_service.predict(source_code=source_code, language=normalized_language)
        findings = detect_findings(source_code=source_code, language=normalized_language)
        risk_score = calculate_risk_score(inference.confidence, findings)
        risk_level = classify_risk_level(risk_score, findings)

        # Final verdict unification:
        # if there is any HIGH/CRITICAL finding, force vulnerable=True.
        high_or_critical_present = any(
            finding.severity in {"HIGH", "CRITICAL"} for finding in findings
        )
        final_is_vulnerable = inference.is_vulnerable or high_or_critical_present

        payload = {
            "filename": filename,
            "language": normalized_language,
            "source_code": source_code,
            "is_vulnerable": final_is_vulnerable,
            "confidence": inference.confidence,
            "risk_level": risk_level,
            "findings": [finding.to_dict() for finding in findings],
        }
        record_id = await self.repository.create_scan_record(payload)

        return {
            "scan_id": record_id,
            "is_vulnerable": payload["is_vulnerable"],
            "confidence": payload["confidence"],
            "risk_level": payload["risk_level"],
            "findings": payload["findings"],
        }

    async def scan_file(
        self,
        filename: str,
        content_bytes: bytes,
        language_hint: str | None = None,
    ) -> dict[str, Any]:
        if not content_bytes:
            raise BadRequestException(message="Empty file upload", error_code="EMPTY_FILE")

        if len(content_bytes) > MAX_UPLOAD_SIZE_BYTES:
            raise BadRequestException(message="File too large", error_code="FILE_TOO_LARGE")

        safe_name = os.path.basename(filename)
        _, ext = os.path.splitext(safe_name.lower())
        if ext not in SUPPORTED_FILE_EXTENSIONS:
            raise BadRequestException(
                message="Invalid file extension",
                error_code="INVALID_FILE_EXTENSION",
            )

        source_code = content_bytes.decode("utf-8", errors="ignore")
        normalized_language = (language_hint or ext.replace(".", "")).lower()
        return await self.scan_code(source_code=source_code, language=normalized_language, filename=safe_name)

    async def get_scan_history(self, page: int = 1, limit: int = 10) -> dict[str, Any]:
        if page < 1 or limit < 1:
            raise BadRequestException(message="Invalid pagination params", error_code="INVALID_PAGINATION")

        items, total = await self.repository.list_scan_history(page=page, limit=limit)
        normalized_items: list[dict[str, Any]] = []
        for item in items:
            normalized_items.append(
                {
                    "id": str(item.get("_id", "")),
                    "filename": item.get("filename"),
                    "language": item.get("language", ""),
                    "is_vulnerable": item.get("is_vulnerable", False),
                    "confidence": item.get("confidence", 0.0),
                    "risk_level": item.get("risk_level", "LOW"),
                    "created_at": item.get("created_at", ""),
                }
            )

        return {
            "items": normalized_items,
            "total": total,
            "page": page,
            "limit": limit,
        }

    async def get_scan_record(self, record_id: str) -> dict[str, Any] | None:
        item = await self.repository.get_scan_record(record_id)
        if not item:
            return None
        return {
            "scan_id": str(item.get("_id", "")),
            "filename": item.get("filename"),
            "language": item.get("language", ""),
            "source_code": item.get("source_code", ""),
            "is_vulnerable": item.get("is_vulnerable", False),
            "confidence": item.get("confidence", 0.0),
            "risk_level": item.get("risk_level", "LOW"),
            "findings": item.get("findings", []),
            "created_at": item.get("created_at", ""),
        }


scan_service = ScanService()
