from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import settings


@dataclass
class LoadedModelInfo:
    model_name: str
    device: str
    loaded: bool
    active_checkpoint: str
    available_checkpoints: list[str]


class ModelManager:
    def __init__(self) -> None:
        self._loaded: bool = False
        self._model_name: str = settings.model_name_or_path
        self._device: str = (
            "cuda" if torch.cuda.is_available() and settings.model_device.lower() != "cpu" else "cpu"
        )
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger("app.ai.model_manager")

        self._tokenizer = None
        self._model = None
        self._active_checkpoint: str = "best_codebert_linevul.pt"

    def get_available_checkpoints(self) -> list[str]:
        backend_root = Path(__file__).resolve().parents[2]
        local_model_dir = backend_root / "models" / "codebert-base"
        if not local_model_dir.exists():
            return []
        return sorted([f.name for f in local_model_dir.glob("*.pt")])

    def _load_checkpoint_sync(self, checkpoint_name: str) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        local_model_dir = backend_root / "models" / "codebert-base"
        local_checkpoint = local_model_dir / checkpoint_name

        if local_model_dir.exists():
            self._logger.info("local_model_dir_detected path=%s", str(local_model_dir))
            
            # Initialize tokenizer if not already done
            if self._tokenizer is None:
                try:
                    self._tokenizer = AutoTokenizer.from_pretrained(str(local_model_dir), local_files_only=False)
                except Exception as local_dir_exc:
                    self._logger.warning(
                        "local_tokenizer_load_failed_fallback_to_hf path=%s error=%s",
                        str(local_model_dir),
                        str(local_dir_exc),
                    )
                    self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)

            # Initialize base model structure if not already done
            if self._model is None:
                try:
                    self._model = AutoModelForSequenceClassification.from_pretrained(
                        str(local_model_dir),
                        local_files_only=False,
                    )
                except Exception as local_dir_exc:
                    self._logger.warning(
                        "local_model_load_failed_fallback_to_hf path=%s error=%s",
                        str(local_model_dir),
                        str(local_dir_exc),
                    )
                    self._model = AutoModelForSequenceClassification.from_pretrained(self._model_name)

            if local_checkpoint.exists():
                self._logger.info("local_checkpoint_detected path=%s", str(local_checkpoint))
                try:
                    state = torch.load(str(local_checkpoint), map_location=self._device, weights_only=False)
                except TypeError:
                    state = torch.load(str(local_checkpoint), map_location=self._device)

                if isinstance(state, dict) and "state_dict" in state and isinstance(state["state_dict"], dict):
                    state = state["state_dict"]
                if not isinstance(state, dict):
                    raise RuntimeError(f"Invalid checkpoint format for {checkpoint_name}")

                cleaned_state: dict[str, torch.Tensor] = {}
                model_state = self._model.state_dict()
                for key, value in state.items():
                    new_key = key
                    if new_key.startswith("module."):
                        new_key = new_key[len("module.") :]
                    if new_key.startswith("model."):
                        new_key = new_key[len("model.") :]

                    if new_key in model_state and hasattr(value, "shape"):
                        if tuple(value.shape) != tuple(model_state[new_key].shape):
                            self._logger.warning(
                                "checkpoint_shape_mismatch_skip key=%s ckpt_shape=%s model_shape=%s",
                                new_key,
                                tuple(value.shape),
                                tuple(model_state[new_key].shape),
                            )
                            continue
                    cleaned_state[new_key] = value

                missing_keys, unexpected_keys = self._model.load_state_dict(cleaned_state, strict=False)
                if missing_keys:
                    self._logger.warning("checkpoint_missing_keys count=%s", len(missing_keys))
                if unexpected_keys:
                    self._logger.warning("checkpoint_unexpected_keys count=%s", len(unexpected_keys))
            else:
                raise FileNotFoundError(f"Checkpoint file '{checkpoint_name}' not found at {local_checkpoint}")
        else:
            if self._tokenizer is None:
                self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            if self._model is None:
                self._model = AutoModelForSequenceClassification.from_pretrained(self._model_name)
            self._logger.warning("local_model_dir not found, fallback to Hugging Face without custom checkpoint")

        self._model.to(self._device)
        self._model.eval()

    async def _load_sync(self) -> None:
        await asyncio.to_thread(self._load_checkpoint_sync, self._active_checkpoint)

    async def load(self) -> None:
        async with self._lock:
            if self._loaded:
                return
            try:
                await self._load_sync()
                self._loaded = True
                self._logger.info("model_loaded model=%s device=%s checkpoint=%s", self._model_name, self._device, self._active_checkpoint)
            except Exception as exc:
                self._loaded = False
                self._tokenizer = None
                self._model = None
                self._logger.exception("model_load_failed error=%s", str(exc))
                raise RuntimeError("Failed to load model") from exc

    async def change_checkpoint(self, checkpoint_name: str) -> None:
        async with self._lock:
            backend_root = Path(__file__).resolve().parents[2]
            local_model_dir = backend_root / "models" / "codebert-base"
            local_checkpoint = local_model_dir / checkpoint_name
            if not local_checkpoint.exists():
                raise FileNotFoundError(f"Checkpoint file '{checkpoint_name}' not found.")
            
            await asyncio.to_thread(self._load_checkpoint_sync, checkpoint_name)
            self._active_checkpoint = checkpoint_name
            self._loaded = True
            self._logger.info("Successfully switched to checkpoint: %s", checkpoint_name)

    async def unload(self) -> None:
        async with self._lock:
            self._loaded = False
            self._tokenizer = None
            self._model = None

    def is_loaded(self) -> bool:
        return self._loaded

    def get_tokenizer(self):
        return self._tokenizer

    def get_model(self):
        return self._model

    def get_device(self) -> str:
        return self._device

    def info(self) -> LoadedModelInfo:
        return LoadedModelInfo(
            model_name=self._model_name,
            device=self._device,
            loaded=self._loaded,
            active_checkpoint=self._active_checkpoint,
            available_checkpoints=self.get_available_checkpoints(),
        )


model_manager = ModelManager()
