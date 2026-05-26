from __future__ import annotations

import os
from typing import Any

from app.ai.inference import inference_service
from app.ai.model_manager import model_manager
from app.analysis.detectors import detect_findings
from app.analysis.risk import calculate_risk_score, classify_risk_level
from app.core.config import settings
from app.core.constants import MAX_UPLOAD_SIZE_BYTES, SUPPORTED_FILE_EXTENSIONS
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.document_mapper import findings_to_patterns, new_scan_id
from app.db.repositories.in_memory_scan_repository import InMemoryScanRepository
from app.db.repositories.scan_repository import ScanRepository
from app.db.security import sanitize_source_code
from app.models.scan_models import (
    AnalysisResult,
    MetadataInfo,
    PredictionResult,
    ScanCreate,
    ScanHistoryFilters,
    SourceType,
)


class ScanService:
    def __init__(self, repository: ScanRepository | InMemoryScanRepository | None = None) -> None:
        if repository is not None:
            self.repository = repository
        elif settings.use_in_memory_repository:
            self.repository = InMemoryScanRepository()
        else:
            self.repository = ScanRepository()

    def _build_metadata(self) -> MetadataInfo:
        info = model_manager.info()
        checkpoint = info.active_checkpoint or "default"
        return MetadataInfo(
            model_name=info.model_name,
            model_version=checkpoint,
            threshold=settings.model_vulnerability_threshold,
            checkpoint=checkpoint,
        )

    async def scan_code(
        self,
        source_code: str,
        language: str,
        filename: str | None = None,
        source_type: SourceType = SourceType.CODE,
    ) -> dict[str, Any]:
        normalized_language = language.strip().lower()
        language_aliases = {
            "c++": "cpp",
            "c_cpp": "cpp",
            "h": "c",
            "hpp": "cpp",
        }
        normalized_language = language_aliases.get(normalized_language, normalized_language)

        if normalized_language not in {"c", "cpp"}:
            raise BadRequestException(message="Unsupported language", error_code="INVALID_LANGUAGE")

        sanitized_code = sanitize_source_code(source_code, settings.max_upload_size_bytes)

        inference = await inference_service.predict(
            source_code=sanitized_code,
            language=normalized_language,
        )
        findings = detect_findings(source_code=sanitized_code, language=normalized_language)
        risk_score = calculate_risk_score(inference.vulnerability_probability, findings)
        risk_level = classify_risk_level(risk_score, findings)

        high_or_critical_present = any(
            finding.severity in {"HIGH", "CRITICAL"} for finding in findings
        )
        final_is_vulnerable = inference.is_vulnerable or high_or_critical_present

        confidence = inference.confidence
        if final_is_vulnerable and not inference.is_vulnerable:
            confidence = max(inference.vulnerability_probability, risk_score)

        finding_dicts = [finding.to_dict() for finding in findings]
        scan_id = new_scan_id()

        scan_create = ScanCreate(
            source_type=source_type,
            language=normalized_language,
            code=sanitized_code,
            filename=filename,
            prediction=PredictionResult(
                is_vulnerable=final_is_vulnerable,
                confidence=round(confidence, 4),
                risk_level=risk_level,
            ),
            analysis=AnalysisResult(suspicious_patterns=findings_to_patterns(finding_dicts)),
            metadata=self._build_metadata(),
        )

        await self.repository.create_scan(scan_create, scan_id)

        return {
            "scan_id": scan_id,
            "is_vulnerable": final_is_vulnerable,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "findings": finding_dicts,
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
        return await self.scan_code(
            source_code=source_code,
            language=normalized_language,
            filename=safe_name,
            source_type=SourceType.FILE,
        )

    async def get_scan_history(
        self,
        page: int = 1,
        limit: int = 10,
        filename: str | None = None,
        language: str | None = None,
        risk_level: str | None = None,
        is_vulnerable: bool | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        filters = ScanHistoryFilters(
            page=page,
            limit=limit,
            filename=filename,
            language=language,
            risk_level=risk_level,
            is_vulnerable=is_vulnerable,
            search=search,
        )
        pagination = await self.repository.get_scan_history(filters)
        return pagination.model_dump()

    async def get_dashboard_stats(self) -> dict[str, Any]:
        stats = await self.repository.get_dashboard_stats()
        return stats.model_dump()

    async def get_scan_record(self, record_id: str) -> dict[str, Any] | None:
        detail = await self.repository.get_scan_by_id(record_id)
        if detail is None:
            return None

        return {
            "scan_id": detail.scan_id,
            "filename": detail.filename,
            "language": detail.language,
            "source_code": detail.source_code,
            "is_vulnerable": detail.is_vulnerable,
            "confidence": detail.confidence,
            "risk_level": detail.risk_level,
            "findings": detail.findings,
            "created_at": detail.created_at,
            "source_type": detail.source_type,
            "metadata": detail.metadata.model_dump() if detail.metadata else None,
        }

    async def delete_scan(self, record_id: str) -> None:
        deleted = await self.repository.delete_scan(record_id)
        if not deleted:
            raise NotFoundException(message="Scan record not found", error_code="SCAN_NOT_FOUND")


scan_service = ScanService()
