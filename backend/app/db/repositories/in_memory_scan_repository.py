from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class InMemoryScanRepository:
    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    async def create_scan_record(self, payload: dict[str, Any]) -> str:
        record_id = str(uuid4())
        data = {
            "_id": record_id,
            **payload,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._items.insert(0, data)
        return record_id

    async def list_scan_history(self, page: int = 1, limit: int = 10) -> tuple[list[dict[str, Any]], int]:
        total = len(self._items)
        skip = (page - 1) * limit
        end = skip + limit
        return self._items[skip:end], total

    async def get_scan_record(self, record_id: str) -> dict[str, Any] | None:
        for item in self._items:
            if item.get("_id") == record_id:
                return item
        return None
