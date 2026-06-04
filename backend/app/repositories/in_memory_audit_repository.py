from __future__ import annotations

from copy import deepcopy

from app.models.audit_models import AuditLogDocument


class InMemoryAuditRepository:
    """Non-persistent audit repository used when MongoDB is disabled."""

    def __init__(self) -> None:
        self._logs: list[AuditLogDocument] = []

    def clear(self) -> None:
        self._logs.clear()

    async def log_action(self, log: AuditLogDocument) -> None:
        self._logs.append(deepcopy(log))

    async def get_logs(self, skip: int = 0, limit: int = 100) -> list[AuditLogDocument]:
        logs = sorted(self._logs, key=lambda item: item.created_at, reverse=True)
        return [deepcopy(log) for log in logs[skip : skip + limit]]
