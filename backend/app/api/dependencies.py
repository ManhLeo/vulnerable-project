from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database
from app.db.repositories.in_memory_scan_repository import InMemoryScanRepository
from app.db.repositories.scan_repository import ScanRepository


def get_scan_repository() -> ScanRepository | InMemoryScanRepository:
    """Provide the active scan repository implementation."""
    if settings.use_in_memory_repository:
        return InMemoryScanRepository()
    return ScanRepository()


ScanRepositoryDep = Annotated[ScanRepository | InMemoryScanRepository, Depends(get_scan_repository)]
DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]
