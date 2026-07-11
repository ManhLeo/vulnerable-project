from __future__ import annotations

import os
from typing import Any

from app.ai.inference import inference_service
from app.ai.model_manager import model_manager
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
from app.services.findings_metrics_service import findings_metrics_service


class ScanService:
    def __init__(self, repository: ScanRepository | InMemoryScanRepository | None = None) -> None:
        if repository is not None:
            self.repository = repository
        elif settings.use_in_memory_repository:
            self.repository = InMemoryScanRepository()
        else:
            self.repository = ScanRepository()

    def _build_metadata(
        self,
        *,
        checkpoint: str | None = None,
        model_mode: str = "single",
        candidate_results: list[dict[str, Any]] | None = None,
    ) -> MetadataInfo:
        info = model_manager.info()
        resolved_checkpoint = checkpoint or info.active_checkpoint or "default"
        return MetadataInfo(
            model_name=info.model_name,
            model_version=resolved_checkpoint,
            threshold=settings.model_vulnerability_threshold,
            checkpoint=resolved_checkpoint,
            model_mode=model_mode,
            selected_checkpoint=resolved_checkpoint,
            candidate_results=candidate_results or [],
            inference_used=True,
            analysis_mode="metrics_plus_ai",
        )

    @staticmethod
    def _build_guest_metrics_metadata(findings_metrics: dict[str, Any]) -> MetadataInfo:
        return MetadataInfo(
            model_name=None,
            model_version=None,
            threshold=None,
            checkpoint=None,
            model_mode="findings_metrics_only",
            selected_checkpoint=None,
            inference_used=False,
            analysis_mode="guest_metrics",
            findings_metrics=findings_metrics,
            candidate_results=[],
        )

    @staticmethod
    def _public_findings_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
        return {
            "is_vulnerable_by_metrics": bool(metrics["is_vulnerable_by_metrics"]),
            "findings_count": int(metrics["findings_count"]),
            "risk_score": float(metrics["risk_score"]),
            "risk_level": str(metrics["risk_level"]),
            "severity_counts": metrics["severity_counts"],
        }

    @staticmethod
    def _normalize_language(language: str) -> str:
        normalized_language = language.strip().lower()
        language_aliases = {
            "c++": "cpp",
            "c_cpp": "cpp",
            "h": "c",
            "hpp": "cpp",
        }
        return language_aliases.get(normalized_language, normalized_language)

    @staticmethod
    def _summarize_candidate(
        *,
        checkpoint_name: str,
        confidence: float,
        risk_level: str,
        is_vulnerable: bool,
    ) -> dict[str, Any]:
        return {
            "checkpoint_name": checkpoint_name,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "is_vulnerable": is_vulnerable,
        }

    @staticmethod
    def _normalize_confidence_for_compare(value: float) -> float:
        if value <= 1:
            return max(0.0, min(1.0, value))
        return max(0.0, min(1.0, value / 100.0))

    @staticmethod
    def _severity_rank(risk_level: str | None) -> int:
        order = {
            "UNKNOWN": 0,
            "SAFE": 0,
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }
        return order.get((risk_level or "UNKNOWN").upper(), 0)

    def _resolve_best_confidence_checkpoints(
        self,
        checkpoint_names: list[str] | None,
        active_checkpoint: str,
    ) -> list[str]:
        requested = checkpoint_names or [active_checkpoint, "best_graphcodebert_linevul.pt"]
        deduped: list[str] = []
        for checkpoint_name in requested:
            if checkpoint_name and checkpoint_name not in deduped:
                deduped.append(checkpoint_name)

        if len(deduped) < 2:
            for checkpoint_name in model_manager.get_available_checkpoints():
                if checkpoint_name not in deduped:
                    deduped.append(checkpoint_name)
                if len(deduped) >= 2:
                    break

        if len(deduped) < 2:
            raise BadRequestException(
                message="Best confidence mode requires at least two checkpoints",
                error_code="INVALID_MODEL_MODE",
            )
        return deduped

    @staticmethod
    def _select_best_candidate(
        candidates: list[dict[str, Any]],
        *,
        active_checkpoint: str,
        checkpoint_order: list[str],
    ) -> dict[str, Any]:
        # Tie-break order:
        # 1. higher normalized confidence
        # 2. higher severity
        # 3. active checkpoint
        # 4. first checkpoint in request order
        return max(
            candidates,
            key=lambda candidate: (
                ScanService._normalize_confidence_for_compare(float(candidate["confidence"])),
                ScanService._severity_rank(str(candidate["risk_level"])),
                1 if candidate["checkpoint_name"] == active_checkpoint else 0,
                -checkpoint_order.index(candidate["checkpoint_name"]),
            ),
        )

    async def scan_code(
        self,
        source_code: str,
        language: str,
        filename: str | None = None,
        source_type: SourceType = SourceType.CODE,
        user_id: str | None = None,
        model_mode: str | None = None,
        checkpoint_name: str | None = None,
        checkpoint_names: list[str] | None = None,
        use_ai: bool = True,
    ) -> dict[str, Any]:
        normalized_language = self._normalize_language(language)
        if normalized_language not in {"c", "cpp"}:
            raise BadRequestException(message="Unsupported language", error_code="INVALID_LANGUAGE")

        sanitized_code = sanitize_source_code(source_code, settings.max_upload_size_bytes)
        base_metrics = findings_metrics_service.analyze(
            source_code=sanitized_code,
            language=normalized_language,
            base_confidence=0.0,
        )
        base_metrics_public = self._public_findings_metrics(base_metrics)

        if not use_ai:
            findings = base_metrics["findings"]
            finding_dicts = base_metrics["suspicious_patterns"]
            risk_score = float(base_metrics["risk_score"])
            risk_level = str(base_metrics["risk_level"])
            final_is_vulnerable = bool(base_metrics["is_vulnerable_by_metrics"])
            confidence = findings_metrics_service.confidence_from_metrics(
                risk_score=risk_score,
                risk_level=risk_level,
                findings=findings,
            )
            scan_id = new_scan_id()
            metadata = self._build_guest_metrics_metadata(base_metrics_public)

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
                metadata=metadata,
                user_id=user_id,
            )
            await self.repository.create_scan(scan_create, scan_id)

            return {
                "scan_id": scan_id,
                "is_vulnerable": final_is_vulnerable,
                "confidence": round(confidence, 4),
                "risk_level": risk_level,
                "findings": finding_dicts,
                "findings_metrics": base_metrics_public,
                "analysis_mode": "guest_metrics",
                "metadata": metadata.model_dump(),
            }

        active_checkpoint = model_manager.get_active_checkpoint()
        requested_mode = (model_mode or "single").strip().lower()

        if requested_mode == "best_confidence":
            selected_checkpoints = self._resolve_best_confidence_checkpoints(
                checkpoint_names=checkpoint_names,
                active_checkpoint=active_checkpoint,
            )
            candidates: list[dict[str, Any]] = []
            for candidate_checkpoint in selected_checkpoints:
                candidate_inference = await inference_service.predict_with_checkpoint(
                    source_code=sanitized_code,
                    language=normalized_language,
                    checkpoint_name=candidate_checkpoint,
                )
                candidate_findings = base_metrics["findings"]
                candidate_risk_score = calculate_risk_score(
                    candidate_inference.vulnerability_probability,
                    candidate_findings,
                )
                candidate_risk_level = classify_risk_level(candidate_risk_score, candidate_findings)
                high_or_critical_present = any(
                    finding.severity in {"HIGH", "CRITICAL"} for finding in candidate_findings
                )
                candidate_is_vulnerable = candidate_inference.is_vulnerable or high_or_critical_present
                candidate_confidence = candidate_inference.confidence
                if candidate_is_vulnerable and not candidate_inference.is_vulnerable:
                    candidate_confidence = max(candidate_inference.vulnerability_probability, candidate_risk_score)

                candidates.append(
                    {
                        "checkpoint_name": candidate_checkpoint,
                        "inference": candidate_inference,
                        "findings": candidate_findings,
                        "risk_score": candidate_risk_score,
                        "risk_level": candidate_risk_level,
                        "is_vulnerable": candidate_is_vulnerable,
                        "confidence": round(candidate_confidence, 4),
                    }
                )

            selected_candidate = self._select_best_candidate(
                candidates,
                active_checkpoint=active_checkpoint,
                checkpoint_order=selected_checkpoints,
            )
            inference = selected_candidate["inference"]
            findings = selected_candidate["findings"]
            risk_score = float(selected_candidate["risk_score"])
            risk_level = str(selected_candidate["risk_level"])
            final_is_vulnerable = bool(selected_candidate["is_vulnerable"])
            confidence = float(selected_candidate["confidence"])
            selected_checkpoint = str(selected_candidate["checkpoint_name"])
            candidate_results = [
                self._summarize_candidate(
                    checkpoint_name=str(candidate["checkpoint_name"]),
                    confidence=float(candidate["confidence"]),
                    risk_level=str(candidate["risk_level"]),
                    is_vulnerable=bool(candidate["is_vulnerable"]),
                )
                for candidate in candidates
            ]
        else:
            selected_checkpoint = checkpoint_name or active_checkpoint
            if checkpoint_name:
                inference = await inference_service.predict_with_checkpoint(
                    source_code=sanitized_code,
                    language=normalized_language,
                    checkpoint_name=selected_checkpoint,
                )
            else:
                inference = await inference_service.predict(
                    source_code=sanitized_code,
                    language=normalized_language,
                )

            findings = base_metrics["findings"]
            risk_score = calculate_risk_score(inference.vulnerability_probability, findings)
            risk_level = classify_risk_level(risk_score, findings)
            high_or_critical_present = any(
                finding.severity in {"HIGH", "CRITICAL"} for finding in findings
            )
            final_is_vulnerable = inference.is_vulnerable or high_or_critical_present
            confidence = inference.confidence
            if final_is_vulnerable and not inference.is_vulnerable:
                confidence = max(inference.vulnerability_probability, risk_score)
            candidate_results = []

        finding_dicts = [finding.to_dict() for finding in findings]
        findings_metrics_public = self._public_findings_metrics(
            {
                **base_metrics,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "is_vulnerable_by_metrics": bool(base_metrics["is_vulnerable_by_metrics"]),
            }
        )
        scan_id = new_scan_id()
        metadata = self._build_metadata(
            checkpoint=selected_checkpoint,
            model_mode=requested_mode,
            candidate_results=candidate_results,
        )

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
            metadata=metadata,
            user_id=user_id,
        )

        await self.repository.create_scan(scan_create, scan_id)

        return {
            "scan_id": scan_id,
            "is_vulnerable": final_is_vulnerable,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "findings": finding_dicts,
            "findings_metrics": findings_metrics_public,
            "analysis_mode": "metrics_plus_ai",
            "metadata": metadata.model_dump(exclude_none=True),
        }

    async def scan_file(
        self,
        filename: str,
        content_bytes: bytes,
        language_hint: str | None = None,
        user_id: str | None = None,
        model_mode: str | None = None,
        checkpoint_name: str | None = None,
        checkpoint_names: list[str] | None = None,
        use_ai: bool = True,
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
            user_id=user_id,
            model_mode=model_mode,
            checkpoint_name=checkpoint_name,
            checkpoint_names=checkpoint_names,
            use_ai=use_ai,
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
        user_id: str | None = None,
    ) -> dict[str, Any]:
        filters = ScanHistoryFilters(
            page=page,
            limit=limit,
            filename=filename,
            language=language,
            risk_level=risk_level,
            is_vulnerable=is_vulnerable,
            search=search,
            user_id=user_id,
        )
        pagination = await self.repository.get_scan_history(filters)
        return pagination.model_dump()

    async def get_dashboard_stats(self, user_id: str | None = None) -> dict[str, Any]:
        stats = await self.repository.get_dashboard_stats(user_id=user_id)
        return stats.model_dump()

    async def get_scan_record(self, record_id: str) -> dict[str, Any] | None:
        detail = await self.repository.get_scan_by_id(record_id)
        if detail is None:
            return None

        return {
            "scan_id": detail.scan_id,
            "user_id": detail.user_id,
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
