"""Repository layer re-export (clean architecture entry point)."""

from app.db.repositories.scan_repository import ScanRepository

__all__ = ["ScanRepository"]
