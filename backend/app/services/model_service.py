from typing import Any

from app.ai.model_manager import model_manager


class ModelService:
    async def get_model_info(self) -> dict[str, Any]:
        info = model_manager.info()
        return {
            "model_name": info.model_name,
            "model_loaded": info.loaded,
            "device": info.device,
            "supports_gpu": info.device.lower() in {"cuda", "gpu"},
            "active_checkpoint": info.active_checkpoint,
            "available_checkpoints": info.available_checkpoints,
        }

    async def select_model(self, checkpoint_name: str) -> dict[str, Any]:
        await model_manager.change_checkpoint(checkpoint_name)
        return await self.get_model_info()


model_service = ModelService()
