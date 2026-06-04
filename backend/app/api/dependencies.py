from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database
from app.db.repositories.in_memory_scan_repository import InMemoryScanRepository
from app.db.repositories.scan_repository import ScanRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.in_memory_audit_repository import InMemoryAuditRepository
from app.repositories.in_memory_user_repository import InMemoryUserRepository
from app.repositories.user_repository import UserRepository


_in_memory_scan_repository = InMemoryScanRepository()
_in_memory_user_repository = InMemoryUserRepository()
_in_memory_audit_repository = InMemoryAuditRepository()


def reset_in_memory_repositories() -> None:
    """Clear shared in-memory state. Intended for tests and local resets."""
    _in_memory_scan_repository.clear()
    _in_memory_user_repository.clear()
    _in_memory_audit_repository.clear()


def get_scan_repository() -> ScanRepository | InMemoryScanRepository:
    """Provide the active scan repository implementation."""
    if settings.use_in_memory_repository:
        return _in_memory_scan_repository
    return ScanRepository()


ScanRepositoryDep = Annotated[ScanRepository | InMemoryScanRepository, Depends(get_scan_repository)]
DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]


def get_user_repository() -> UserRepository | InMemoryUserRepository:
    if settings.use_in_memory_repository:
        return _in_memory_user_repository
    return UserRepository(get_database_handle())


def get_audit_repository() -> AuditRepository | InMemoryAuditRepository:
    if settings.use_in_memory_repository:
        return _in_memory_audit_repository
    return AuditRepository(get_database_handle())


def get_database_handle() -> AsyncIOMotorDatabase:
    from app.core.database import database_manager

    return database_manager.db

UserRepositoryDep = Annotated[UserRepository | InMemoryUserRepository, Depends(get_user_repository)]
AuditRepositoryDep = Annotated[AuditRepository | InMemoryAuditRepository, Depends(get_audit_repository)]
