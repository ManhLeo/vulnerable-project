from __future__ import annotations

from app.ai.model_manager import ModelManager


def test_model_manager_lists_checkpoints_without_loading_model() -> None:
    manager = ModelManager()
    checkpoints = manager.get_available_checkpoints()

    assert isinstance(checkpoints, list)
    assert manager.is_loaded() is False
