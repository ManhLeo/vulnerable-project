#!/usr/bin/env python
"""Manual model status script. Safe to import during pytest collection."""

from __future__ import annotations

from app.ai.model_manager import model_manager


def test_default_model_manager_starts_unloaded() -> None:
    assert model_manager.is_loaded() is False


def main() -> None:
    print("=" * 60)
    print("Model Manager Check")
    print("=" * 60)
    print(f"Available checkpoints: {model_manager.get_available_checkpoints()}")
    print(f"Active checkpoint (default): {model_manager.info().active_checkpoint}")
    print(f"Model name: {model_manager.info().model_name}")
    print(f"Device: {model_manager.info().device}")
    print(f"Loaded status: {model_manager.info().loaded}")
    print("=" * 60)


if __name__ == "__main__":
    main()
