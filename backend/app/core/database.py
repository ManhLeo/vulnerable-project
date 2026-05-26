from __future__ import annotations

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

from app.core.config import settings

logger = logging.getLogger("app.core.database")

SCANS_COLLECTION = "scans"


class DatabaseManager:
    """Async MongoDB connection manager for MongoDB Atlas and local instances."""

    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None
        self._indexes_ready: bool = False

    async def connect(self) -> None:
        if self._client is not None:
            return

        self._client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
            connectTimeoutMS=settings.mongodb_connect_timeout_ms,
            socketTimeoutMS=settings.mongodb_socket_timeout_ms,
            maxPoolSize=settings.mongodb_max_pool_size,
            retryWrites=True,
        )
        self._db = self._client[settings.mongodb_db_name]

        # Fail fast when Atlas/URI is unreachable.
        await self._client.admin.command("ping")
        logger.info("mongodb_connected db=%s", settings.mongodb_db_name)

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            self._indexes_ready = False
            logger.info("mongodb_disconnected")

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("MongoDB is not connected")
        return self._db

    def get_collection(self, name: str = SCANS_COLLECTION):
        return self.db[name]

    async def ensure_indexes(self) -> None:
        """Create production indexes on the scans collection (idempotent)."""
        if self._indexes_ready:
            return

        collection = self.get_collection(SCANS_COLLECTION)
        index_models = [
            IndexModel([("scan_id", ASCENDING)], name="idx_scan_id", unique=True),
            IndexModel([("created_at", DESCENDING)], name="idx_created_at"),
            IndexModel([("language", ASCENDING)], name="idx_language"),
            IndexModel(
                [("prediction.is_vulnerable", ASCENDING)],
                name="idx_prediction_is_vulnerable",
            ),
            IndexModel(
                [("prediction.risk_level", ASCENDING)],
                name="idx_prediction_risk_level",
            ),
            # Compound index for common history queries
            IndexModel(
                [
                    ("created_at", DESCENDING),
                    ("language", ASCENDING),
                    ("prediction.risk_level", ASCENDING),
                ],
                name="idx_history_compound",
            ),
        ]

        try:
            await collection.create_indexes(index_models)
            self._indexes_ready = True
            logger.info("mongodb_indexes_ensured collection=%s", SCANS_COLLECTION)
        except OperationFailure as exc:
            logger.exception("mongodb_index_creation_failed error=%s", str(exc))
            raise

    async def ping(self) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("MongoDB is not connected")
        return await self._client.admin.command("ping")


# Singleton used across the application lifecycle.
database_manager = DatabaseManager()

# Backward-compatible alias for existing imports.
mongo_manager = database_manager


async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency — returns the active database handle."""
    return database_manager.db


def is_mongo_connection_error(exc: BaseException) -> bool:
    return isinstance(exc, (ConnectionFailure, ServerSelectionTimeoutError))
