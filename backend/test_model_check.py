#!/usr/bin/env python
"""Quick test script to check model loading."""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.ai.model_manager import model_manager

print("=" * 60)
print("Model Manager Check")
print("=" * 60)

# Check available checkpoints
checkpoints = model_manager.get_available_checkpoints()
print(f"Available checkpoints: {checkpoints}")
print(f"Active checkpoint (default): {model_manager._active_checkpoint}")
print(f"Model name: {model_manager._model_name}")
print(f"Device: {model_manager._device}")
print(f"Loaded status: {model_manager._loaded}")

print("=" * 60)
