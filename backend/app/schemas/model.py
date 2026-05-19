from __future__ import annotations

from pydantic import BaseModel


class ModelInfoData(BaseModel):
    model_name: str
    model_loaded: bool
    device: str
    supports_gpu: bool
