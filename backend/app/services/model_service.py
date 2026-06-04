from typing import Any

from app.ai.model_manager import model_manager
from app.core.exceptions import NotFoundException, ServiceUnavailableException


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
        try:
            await model_manager.change_checkpoint(checkpoint_name)
        except FileNotFoundError as exc:
            raise NotFoundException(
                message="Checkpoint not found",
                error_code="CHECKPOINT_NOT_FOUND",
            ) from exc
        except RuntimeError as exc:
            raise ServiceUnavailableException(
                message="Unable to load checkpoint",
                error_code="CHECKPOINT_LOAD_FAILED",
            ) from exc
        return await self.get_model_info()


model_service = ModelService()
