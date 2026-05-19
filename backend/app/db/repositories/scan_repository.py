from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.errors import PyMongoError

from app.core.exceptions import InternalServerException
from app.db.mongo import mongo_manager


class ScanRepository:
    def __init__(self, collection_name: str = "scan_history") -> None:
        self.collection_name = collection_name

    @property
    def collection(self):
        return mongo_manager.db[self.collection_name]

    async def create_scan_record(self, payload: dict[str, Any]) -> str:
        data = {
            **payload,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            result = await self.collection.insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def list_scan_history(self, page: int = 1, limit: int = 10) -> tuple[list[dict[str, Any]], int]:
        skip = (page - 1) * limit
        try:
            cursor = self.collection.find({}).sort("created_at", -1).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            total = await self.collection.count_documents({})
            return items, total
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc

    async def get_scan_record(self, record_id: str) -> dict[str, Any] | None:
        from bson import ObjectId
        try:
            try:
                query_id: Any = ObjectId(record_id)
            except Exception:
                query_id = record_id
            return await self.collection.find_one({"_id": query_id})
        except PyMongoError as exc:
            raise InternalServerException(
                message="Database operation failed",
                error_code="DATABASE_UNAVAILABLE",
            ) from exc
