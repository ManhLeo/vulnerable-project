from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

import torch

from app.ai.model_manager import model_manager
from app.ai.preprocessing import preprocess_source_code
from app.core.config import settings
from app.core.exceptions import NotFoundException, ServiceUnavailableException


@dataclass
class InferenceOutput:
    is_vulnerable: bool
    confidence: float
    vulnerability_probability: float


@dataclass
class CandidatePrediction:
    checkpoint_name: str
    confidence: float
    risk_level: str
    is_vulnerable: bool


@dataclass
class EnsembleInferenceOutput:
    selected_checkpoint: str
    selected_output: InferenceOutput
    candidate_results: list[CandidatePrediction]


class InferenceService:
    def __init__(self, threshold: float | None = None) -> None:
        self.threshold = settings.model_vulnerability_threshold if threshold is None else threshold
        self._logger = logging.getLogger("app.ai.inference")

    def _forward_pass_sync(self, source_code: str, checkpoint_name: str | None = None) -> InferenceOutput:
        tokenizer = model_manager.get_tokenizer()
        model = (
            model_manager.get_model_for_checkpoint(checkpoint_name)
            if checkpoint_name
            else model_manager.get_model()
        )
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
                prob_vulnerable = torch.sigmoid(logits).squeeze().item()
            else:
                probs = torch.softmax(logits, dim=-1)
                prob_vulnerable = (
                    probs[..., 1].squeeze().item() if logits.shape[-1] > 1 else probs.squeeze().item()
                )

        prob_vulnerable = float(max(0.0, min(1.0, prob_vulnerable)))
        is_vulnerable = prob_vulnerable >= self.threshold
        confidence = prob_vulnerable if is_vulnerable else 1.0 - prob_vulnerable
        return InferenceOutput(
            is_vulnerable=is_vulnerable,
            confidence=round(confidence, 4),
            vulnerability_probability=round(prob_vulnerable, 4),
        )

    async def predict(self, source_code: str, language: str) -> InferenceOutput:
        if not model_manager.is_loaded():
            raise ServiceUnavailableException(
                message="AI model is currently unavailable",
                error_code="MODEL_NOT_LOADED",
            )

        prepared = preprocess_source_code(source_code)
        if not prepared:
            prepared = f"// empty input ({language})"

        started = time.perf_counter()
        result = await asyncio.to_thread(self._forward_pass_sync, prepared)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        self._logger.info("inference_completed language=%s duration_ms=%s", language, elapsed_ms)

        return result

    async def predict_with_checkpoint(
        self,
        source_code: str,
        language: str,
        checkpoint_name: str,
    ) -> InferenceOutput:
        try:
            await model_manager.get_or_load_model(checkpoint_name)
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

        prepared = preprocess_source_code(source_code)
        if not prepared:
            prepared = f"// empty input ({language})"

        started = time.perf_counter()
        result = await asyncio.to_thread(self._forward_pass_sync, prepared, checkpoint_name)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        self._logger.info(
            "checkpoint_inference_completed language=%s checkpoint=%s duration_ms=%s",
            language,
            checkpoint_name,
            elapsed_ms,
        )
        return result

    @staticmethod
    def _normalize_confidence(value: float) -> float:
        if value <= 1:
            return max(0.0, min(1.0, value))
        return max(0.0, min(1.0, value / 100.0))

    @staticmethod
    def _risk_rank(risk_level: str | None) -> int:
        order = {
            "UNKNOWN": 0,
            "SAFE": 0,
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }
        return order.get((risk_level or "UNKNOWN").upper(), 0)

    async def predict_best_confidence(
        self,
        source_code: str,
        language: str,
        checkpoint_names: list[str],
        risk_levels_by_checkpoint: dict[str, str],
        vulnerability_by_checkpoint: dict[str, bool],
        active_checkpoint: str | None = None,
    ) -> EnsembleInferenceOutput:
        candidates: list[CandidatePrediction] = []
        outputs_by_checkpoint: dict[str, InferenceOutput] = {}

        for checkpoint_name in checkpoint_names:
            output = await self.predict_with_checkpoint(source_code, language, checkpoint_name)
            outputs_by_checkpoint[checkpoint_name] = output
            candidates.append(
                CandidatePrediction(
                    checkpoint_name=checkpoint_name,
                    confidence=output.confidence,
                    risk_level=risk_levels_by_checkpoint.get(checkpoint_name, "UNKNOWN"),
                    is_vulnerable=vulnerability_by_checkpoint.get(checkpoint_name, output.is_vulnerable),
                )
            )

        # Tie-break order:
        # 1. higher normalized confidence
        # 2. higher vulnerability severity
        # 3. active checkpoint, if present
        # 4. first checkpoint in the request list
        selected = max(
            candidates,
            key=lambda candidate: (
                self._normalize_confidence(candidate.confidence),
                self._risk_rank(candidate.risk_level),
                1 if active_checkpoint and candidate.checkpoint_name == active_checkpoint else 0,
                -checkpoint_names.index(candidate.checkpoint_name),
            ),
        )
        return EnsembleInferenceOutput(
            selected_checkpoint=selected.checkpoint_name,
            selected_output=outputs_by_checkpoint[selected.checkpoint_name],
            candidate_results=candidates,
        )


inference_service = InferenceService()
