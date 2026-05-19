from __future__ import annotations

from fastapi import APIRouter

from app.core.response import success_response
from app.services.model_service import model_service

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/info")
async def get_model_info():
    data = await model_service.get_model_info()
    return success_response(data=data, message="Model info retrieved successfully")
