from fastapi import APIRouter

from app.core.response import success_response
from app.services.health_service import health_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def get_health():
    data = await health_service.get_health()
    return success_response(data=data, message="Health check successful")
