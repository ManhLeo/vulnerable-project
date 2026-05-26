from __future__ import annotations

import re
from typing import Any

from app.core.exceptions import BadRequestException

# UUID v4 (canonical string form)
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# MongoDB field names must not contain $ or . at top-level keys we control
FORBIDDEN_KEY_CHARS = re.compile(r"[\$\.]")

MAX_FILTER_STRING_LENGTH = 255


def sanitize_source_code(source_code: str, max_bytes: int) -> str:
    """Remove null bytes and enforce maximum encoded size."""
    if not source_code or not source_code.strip():
        raise BadRequestException(message="Source code is empty", error_code="EMPTY_SOURCE_CODE")

    cleaned = source_code.replace("\x00", "")
    encoded_size = len(cleaned.encode("utf-8"))
    if encoded_size > max_bytes:
        raise BadRequestException(
            message=f"Source code exceeds maximum size of {max_bytes} bytes",
            error_code="SOURCE_CODE_TOO_LARGE",
        )
    return cleaned


def sanitize_filter_string(value: str | None, field_name: str) -> str | None:
    """Sanitize user-provided filter strings to reduce injection surface."""
    if value is None:
        return None

    trimmed = value.strip()
    if not trimmed:
        return None

    if len(trimmed) > MAX_FILTER_STRING_LENGTH:
        raise BadRequestException(
            message=f"Filter value for {field_name} is too long",
            error_code="INVALID_FILTER",
        )

    if FORBIDDEN_KEY_CHARS.search(trimmed):
        raise BadRequestException(
            message=f"Invalid characters in {field_name}",
            error_code="INVALID_FILTER",
        )

    return trimmed


def validate_scan_id(scan_id: str) -> str:
    """Accept UUID scan_id; reject malformed identifiers."""
    trimmed = scan_id.strip()
    if not trimmed:
        raise BadRequestException(message="scan_id is required", error_code="INVALID_SCAN_ID")

    if len(trimmed) > 64:
        raise BadRequestException(message="scan_id is too long", error_code="INVALID_SCAN_ID")

    if FORBIDDEN_KEY_CHARS.search(trimmed):
        raise BadRequestException(message="Invalid scan_id", error_code="INVALID_SCAN_ID")

    if UUID_PATTERN.match(trimmed):
        return trimmed

    # Legacy ObjectId hex (24 chars) from older records
    if re.fullmatch(r"^[0-9a-fA-F]{24}$", trimmed):
        return trimmed

    raise BadRequestException(message="Invalid scan_id format", error_code="INVALID_SCAN_ID")


def build_safe_regex_filter(field: str, value: str) -> dict[str, Any]:
    """Build a case-insensitive substring regex filter with escaped input."""
    escaped = re.escape(value)
    return {field: {"$regex": escaped, "$options": "i"}}
