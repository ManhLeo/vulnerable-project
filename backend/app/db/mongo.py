"""Backward-compatible re-export — prefer app.core.database."""

from app.core.database import database_manager, get_database, mongo_manager

__all__ = ["database_manager", "get_database", "mongo_manager"]
