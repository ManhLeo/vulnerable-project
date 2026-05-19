from __future__ import annotations

import time

from app.core.config import settings

START_TIME = time.time()


class HealthService:
    async def get_health(self) -> dict[str, str | float]:
        uptime = max(0.0, time.time() - START_TIME)
        return {
            "service": settings.app_name,
            "version": "v1",
            "environment": settings.app_env,
            "uptime_seconds": round(uptime, 2),
        }


health_service = HealthService()
