from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AuditEvent(str, Enum):
    """All named audit events. Use these constants — never raw strings."""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    ADMIN_LOGIN = "ADMIN_LOGIN"
    LOGOUT = "LOGOUT"
    REGISTER = "REGISTER"
    ACCESS_DENIED = "ACCESS_DENIED"
    SCAN_CREATED = "SCAN_CREATED"
    FILE_UPLOAD_REJECTED = "FILE_UPLOAD_REJECTED"
    RATE_LIMIT_TRIGGERED = "RATE_LIMIT_TRIGGERED"
    ADMIN_ACTION = "ADMIN_ACTION"
    USER_SOFT_DELETE = "USER_SOFT_DELETE"
    REPORT_EXPORT = "REPORT_EXPORT"


class AuditLogCreate(BaseModel):
    user_id: Optional[str] = None
    action: AuditEvent
    endpoint: str = Field(..., min_length=1)
    ip_address: Optional[str] = None
    status: str = Field(..., min_length=1)
    detail: Optional[str] = None  # Optional human-readable context


class AuditLogDocument(AuditLogCreate):
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)

