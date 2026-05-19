from __future__ import annotations

from app.ai.model_manager import model_manager


class ModelService:
    async def get_model_info(self) -> dict[str, str | bool]:
        info = model_manager.info()
        return {
            "model_name": info.model_name,
            "model_loaded": info.loaded,
            "device": info.device,
            "supports_gpu": info.device.lower() in {"cuda", "gpu"},
        }


model_service = ModelService()
