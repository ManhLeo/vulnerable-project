from typing import Any

from app.ai.model_manager import model_manager
from app.core.exceptions import NotFoundException, ServiceUnavailableException


class ModelService:
    async def get_model_info(self) -> dict[str, Any]:
        info = model_manager.info()
        available_checkpoints = info.available_checkpoints
        available_model_options = []
        for checkpoint_name in available_checkpoints:
            if checkpoint_name == "best_graphcodebert_linevul.pt":
                label = "GraphCodeBERT LineVul"
                description = "Line-level vulnerability model"
            elif checkpoint_name == "best_codebert_linevul.pt":
                label = "CodeBERT Vulnerability Model"
                description = "Default vulnerability classifier"
            else:
                label = checkpoint_name
                description = "Available model checkpoint"
            available_model_options.append(
                {
                    "checkpoint_name": checkpoint_name,
                    "label": label,
                    "description": description,
                    "loaded": model_manager.is_checkpoint_loaded(checkpoint_name),
                }
            )

        if len(available_checkpoints) >= 2:
            available_model_options.append(
                {
                    "checkpoint_name": "__ensemble_best_confidence__",
                    "label": "Best Confidence Ensemble",
                    "description": "Run multiple checkpoints and use the highest-confidence result",
                    "loaded": all(model_manager.is_checkpoint_loaded(name) for name in available_checkpoints[:2]),
                }
            )

        return {
            "model_name": info.model_name,
            "model_loaded": info.loaded,
            "device": info.device,
            "supports_gpu": info.device.lower() in {"cuda", "gpu"},
            "active_checkpoint": info.active_checkpoint,
            "available_checkpoints": available_checkpoints,
            "available_model_options": available_model_options,
            "supported_modes": ["single", "best_confidence"],
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
