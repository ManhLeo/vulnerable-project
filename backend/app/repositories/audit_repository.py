from __future__ import annotations

from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import AUDIT_LOGS_COLLECTION
from app.models.audit_models import AuditLogDocument


class AuditRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db[AUDIT_LOGS_COLLECTION]

    async def log_action(self, log: AuditLogDocument) -> None:
        """Persist an audit event. Returns nothing — callers must not depend on the inserted ID."""
        log_dict = log.model_dump()
        await self.collection.insert_one(log_dict)

    async def get_logs(self, skip: int = 0, limit: int = 100) -> List[AuditLogDocument]:
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        logs = []
        async for doc in cursor:
            doc.pop("_id", None)  # Strip MongoDB internal _id before parsing
            logs.append(AuditLogDocument(**doc))
        return logs

