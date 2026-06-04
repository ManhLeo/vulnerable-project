from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.response import success_response
from app.services.model_service import model_service

router = APIRouter(prefix="/model", tags=["model"])


class SelectModelRequest(BaseModel):
    checkpoint_name: str = Field(..., description="Name of the checkpoint file, e.g. best_codebert_v3.pt")


@router.get("/info")
async def get_model_info():
    data = await model_service.get_model_info()
    return success_response(data=data, message="Model info retrieved successfully")


@router.post("/select")
async def select_model(payload: SelectModelRequest):
    data = await model_service.select_model(payload.checkpoint_name)
    return success_response(data=data, message="Model checkpoint switched successfully")
