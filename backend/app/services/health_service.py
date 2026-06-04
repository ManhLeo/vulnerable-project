from __future__ import annotations

import time
from datetime import datetime, timezone

from app.ai.model_manager import model_manager
from app.core.config import settings
from app.core.database import database_manager

START_TIME = time.time()


class HealthService:
    async def get_health(self) -> dict[str, str | float | bool | dict[str, str | bool | None]]:
        uptime = max(0.0, time.time() - START_TIME)
        database_status = (
            "skipped"
            if settings.use_in_memory_repository
            else "connected"
            if database_manager.is_connected
            else "disconnected"
        )
        model_info = model_manager.info()
        degraded = database_status == "disconnected" or not model_info.loaded
        return {
            "status": "degraded" if degraded else "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": settings.app_name,
            "version": "v1",
            "environment": settings.app_env,
            "uptime": round(uptime, 2),
            "uptime_seconds": round(uptime, 2),
            "database": {
                "status": database_status,
                "mode": "in_memory" if settings.use_in_memory_repository else "mongodb",
            },
            "model": {
                "status": "loaded" if model_info.loaded else "not_loaded",
                "loaded": model_info.loaded,
                "name": model_info.model_name,
                "device": model_info.device,
                "checkpoint": model_info.active_checkpoint,
            },
            "degraded": degraded,
        }


health_service = HealthService()
