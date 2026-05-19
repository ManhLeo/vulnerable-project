from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoManager:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
                connectTimeoutMS=settings.mongodb_connect_timeout_ms,
                socketTimeoutMS=settings.mongodb_socket_timeout_ms,
            )
            self._db = self._client[settings.mongodb_db_name]

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("MongoDB is not connected")
        return self._db


mongo_manager = MongoManager()
