from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

import torch

from app.ai.model_manager import model_manager
from app.ai.preprocessing import preprocess_source_code
from app.core.config import settings


@dataclass
class InferenceOutput:
    is_vulnerable: bool
    confidence: float


class InferenceService:
    def __init__(self, threshold: float | None = None) -> None:
        self.threshold = settings.model_vulnerability_threshold if threshold is None else threshold
        self._logger = logging.getLogger("app.ai.inference")

    def _forward_pass_sync(self, source_code: str) -> InferenceOutput:
        tokenizer = model_manager.get_tokenizer()
        model = model_manager.get_model()
        device = model_manager.get_device()

        encoded = tokenizer(
            source_code,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        encoded = {k: v.to(device) for k, v in encoded.items()}

        with torch.no_grad():
            outputs = model(**encoded)
            logits = outputs.logits

            if logits.shape[-1] == 1:
                prob = torch.sigmoid(logits).squeeze().item()
            else:
                probs = torch.softmax(logits, dim=-1)
                prob = probs[..., 1].squeeze().item() if logits.shape[-1] > 1 else probs.squeeze().item()

        confidence = float(max(0.0, min(1.0, prob)))
        is_vulnerable = confidence >= self.threshold
        return InferenceOutput(is_vulnerable=is_vulnerable, confidence=round(confidence, 4))

    async def predict(self, source_code: str, language: str) -> InferenceOutput:
        if not model_manager.is_loaded():
            raise RuntimeError("Model is not loaded")

        prepared = preprocess_source_code(source_code)
        if not prepared:
            prepared = f"// empty input ({language})"

        started = time.perf_counter()
        result = await asyncio.to_thread(self._forward_pass_sync, prepared)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        self._logger.info("inference_completed language=%s duration_ms=%s", language, elapsed_ms)

        return result


inference_service = InferenceService()
