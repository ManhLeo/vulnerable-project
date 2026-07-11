from __future__ import annotations

import logging
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.core.config import settings
from app.core.database import database_manager, is_mongo_connection_error
from app.core.exceptions import ConflictException, InternalServerException
from app.db.document_mapper import (
    document_to_detail,
    document_to_history_item,
    scan_create_to_document,
)
from app.db.security import build_safe_regex_filter, sanitize_filter_string, validate_scan_id
from app.models.scan_models import (
    DashboardStats,
    PaginationResponse,
    ScanCreate,
    ScanDetailResponse,
    ScanHistoryFilters,
    ScanHistoryItemResponse,
)

logger = logging.getLogger("app.db.scan_repository")


class ScanRepository:
    """MongoDB repository for the `scans` collection."""

    def __init__(self, collection_name: str | None = None) -> None:
        self.collection_name = collection_name or settings.mongodb_scans_collection

    @property
    def collection(self):
        return database_manager.get_collection(self.collection_name)

    def _build_history_query(self, filters: ScanHistoryFilters) -> dict[str, Any]:
        query: dict[str, Any] = {}

        language = sanitize_filter_string(filters.language, "language")
        if language:
            query["language"] = language.lower()

        risk_level = sanitize_filter_string(filters.risk_level, "risk_level")
        if risk_level:
            query["prediction.risk_level"] = risk_level.upper()

        if filters.is_vulnerable is not None:
            query["prediction.is_vulnerable"] = filters.is_vulnerable

        filename = sanitize_filter_string(filters.filename, "filename")
        if filename:
            query.update(build_safe_regex_filter("filename", filename))

        search = sanitize_filter_string(filters.search, "search")
        if search:
            query["$or"] = [
                build_safe_regex_filter("filename", search),
                build_safe_regex_filter("language", search),
            ]

        if filters.user_id:
            query["user_id"] = filters.user_id

        return query

    async def create_scan(self, scan: ScanCreate, scan_id: str) -> str:
        document = scan_create_to_document(scan, scan_id)
        try:
            await self.collection.insert_one(document)
            return scan_id
        except DuplicateKeyError as exc:
            raise ConflictException(
                message="Scan record with this identifier already exists",
                error_code="DUPLICATE_SCAN_ID",
            ) from exc
        except PyMongoError as exc:
            if is_mongo_connection_error(exc):
                logger.exception("mongodb_connection_error")
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def get_scan_by_id(self, scan_id: str) -> ScanDetailResponse | None:
        validated_id = validate_scan_id(scan_id)
        try:
            document = await self.collection.find_one({"scan_id": validated_id})
            if document is None and ObjectId.is_valid(validated_id):
                document = await self.collection.find_one({"_id": ObjectId(validated_id)})
            if document is None:
                # Legacy flat documents keyed only by _id string
                document = await self.collection.find_one({"_id": validated_id})
            if document is None:
                return None
            return document_to_detail(document)
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def get_scan_history(self, filters: ScanHistoryFilters) -> PaginationResponse:
        query = self._build_history_query(filters)
        skip = (filters.page - 1) * filters.limit

        try:
            cursor = (
                self.collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(filters.limit)
            )
            raw_items = await cursor.to_list(length=filters.limit)
            total = await self.collection.count_documents(query)

            items: list[ScanHistoryItemResponse] = [
                document_to_history_item(item) for item in raw_items
            ]
            return PaginationResponse(
                items=items,
                total=total,
                page=filters.page,
                limit=filters.limit,
            )
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def get_dashboard_stats(self, user_id: str | None = None) -> DashboardStats:
        """Aggregate dashboard metrics server-side."""
        base_query: dict[str, Any] = {"user_id": user_id} if user_id else {}
        try:
            total_scans = await self.collection.count_documents(base_query)
            vulnerable_scans = await self.collection.count_documents(
                {**base_query, "prediction.is_vulnerable": True}
            )
            safe_scans = max(0, total_scans - vulnerable_scans)

            avg_pipeline = [
                {"$match": base_query},
                {
                    "$group": {
                        "_id": None,
                        "average_confidence": {"$avg": "$prediction.confidence"},
                    }
                }
            ]
            avg_cursor = self.collection.aggregate(avg_pipeline)
            avg_result = await avg_cursor.to_list(length=1)
            average_confidence = float(avg_result[0]["average_confidence"]) if avg_result else 0.0

            risk_pipeline = [
                {"$match": base_query},
                {"$group": {"_id": "$prediction.risk_level", "count": {"$sum": 1}}},
            ]
            risk_cursor = self.collection.aggregate(risk_pipeline)
            risk_rows = await risk_cursor.to_list(length=20)

            risk_distribution: dict[str, int] = {
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0,
                "CRITICAL": 0,
            }
            for row in risk_rows:
                level = str(row.get("_id") or "LOW").upper()
                risk_distribution[level] = risk_distribution.get(level, 0) + int(row.get("count", 0))

            vulnerable_ratio = (vulnerable_scans / total_scans) if total_scans else 0.0

            return DashboardStats(
                total_scans=total_scans,
                vulnerable_scans=vulnerable_scans,
                safe_scans=safe_scans,
                vulnerable_ratio=round(vulnerable_ratio, 4),
                average_confidence=round(average_confidence, 4),
                risk_distribution=risk_distribution,
            )
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def list_all_for_export(self) -> list[dict[str, Any]]:
        """Return raw scan documents for the admin CSV export."""
        projection = {
            "scan_id": 1,
            "user_id": 1,
            "created_at": 1,
            "filename": 1,
            "language": 1,
            "code": 1,
            "source_code": 1,
            "prediction": 1,
            "metadata": 1,
        }
        try:
            cursor = self.collection.find({}, projection).sort("created_at", -1)
            rows: list[dict[str, Any]] = []
            async for document in cursor:
                rows.append(document)
            return rows
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def delete_scan(self, scan_id: str) -> bool:
        validated_id = validate_scan_id(scan_id)
        try:
            result = await self.collection.delete_one({"scan_id": validated_id})
            if result.deleted_count > 0:
                return True

            if ObjectId.is_valid(validated_id):
                legacy_result = await self.collection.delete_one({"_id": ObjectId(validated_id)})
                return legacy_result.deleted_count > 0

            legacy_result = await self.collection.delete_one({"_id": validated_id})
            return legacy_result.deleted_count > 0
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc
