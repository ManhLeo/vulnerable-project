from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.db.document_mapper import (
    document_to_detail,
    document_to_history_item,
    scan_create_to_document,
)
from app.models.scan_models import (
    DashboardStats,
    PaginationResponse,
    ScanCreate,
    ScanDetailResponse,
    ScanHistoryFilters,
)


class InMemoryScanRepository:
    """In-memory repository for local development without MongoDB."""

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    async def create_scan(self, scan: ScanCreate, scan_id: str) -> str:
        if any(item.get("scan_id") == scan_id for item in self._items):
            from app.core.exceptions import ConflictException

            raise ConflictException(
                message="Scan record with this identifier already exists",
                error_code="DUPLICATE_SCAN_ID",
            )

        document = scan_create_to_document(scan, scan_id)
        self._items.insert(0, document)
        return scan_id

    async def get_scan_by_id(self, scan_id: str) -> ScanDetailResponse | None:
        for item in self._items:
            if str(item.get("scan_id")) == scan_id or str(item.get("_id")) == scan_id:
                return document_to_detail(item)
        return None

    async def get_scan_history(self, filters: ScanHistoryFilters) -> PaginationResponse:
        query_items = self._filter_items(filters)
        total = len(query_items)
        skip = (filters.page - 1) * filters.limit
        page_items = query_items[skip : skip + filters.limit]
        return PaginationResponse(
            items=[document_to_history_item(item) for item in page_items],
            total=total,
            page=filters.page,
            limit=filters.limit,
        )

    async def get_dashboard_stats(self) -> DashboardStats:
        items = [document_to_history_item(doc) for doc in self._items]
        total = len(items)
        vulnerable = sum(1 for item in items if item.is_vulnerable)
        safe = total - vulnerable
        average = (
            round(sum(item.confidence for item in items) / total, 4) if total else 0.0
        )
        risk_distribution: dict[str, int] = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0,
        }
        for item in items:
            risk_distribution[item.risk_level] = risk_distribution.get(item.risk_level, 0) + 1

        return DashboardStats(
            total_scans=total,
            vulnerable_scans=vulnerable,
            safe_scans=safe,
            vulnerable_ratio=round(vulnerable / total, 4) if total else 0.0,
            average_confidence=average,
            risk_distribution=risk_distribution,
        )

    async def delete_scan(self, scan_id: str) -> bool:
        before = len(self._items)
        self._items = [
            item
            for item in self._items
            if str(item.get("scan_id")) != scan_id and str(item.get("_id")) != scan_id
        ]
        return len(self._items) < before

    def _filter_items(self, filters: ScanHistoryFilters) -> list[dict[str, Any]]:
        items = deepcopy(self._items)
        items.sort(key=lambda doc: str(doc.get("created_at", "")), reverse=True)

        if filters.language:
            items = [doc for doc in items if doc.get("language") == filters.language]

        if filters.risk_level:
            items = [
                doc
                for doc in items
                if document_to_history_item(doc).risk_level == filters.risk_level
            ]

        if filters.is_vulnerable is not None:
            items = [
                doc
                for doc in items
                if document_to_history_item(doc).is_vulnerable == filters.is_vulnerable
            ]

        if filters.filename:
            needle = filters.filename.lower()
            items = [
                doc
                for doc in items
                if needle in str(doc.get("filename", "")).lower()
            ]

        if filters.search:
            needle = filters.search.lower()
            items = [
                doc
                for doc in items
                if needle in str(doc.get("filename", "")).lower()
                or needle in str(doc.get("language", "")).lower()
            ]

        return items
