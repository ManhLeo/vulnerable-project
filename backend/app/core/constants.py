from __future__ import annotations

SUPPORTED_FILE_EXTENSIONS: set[str] = {".c", ".cpp", ".py", ".java"}
MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5MB

API_V1_PREFIX: str = "/api/v1"
DEFAULT_SUCCESS_MESSAGE: str = "Request successful"
INTERNAL_SERVER_ERROR_MESSAGE: str = "Internal server error"
