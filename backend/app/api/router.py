from __future__ import annotations

from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.model import router as model_router
from app.api.routes.scan import router as scan_router
from app.core.constants import API_V1_PREFIX

api_router = APIRouter(prefix=API_V1_PREFIX)
api_router.include_router(health_router)
api_router.include_router(scan_router)
api_router.include_router(model_router)
