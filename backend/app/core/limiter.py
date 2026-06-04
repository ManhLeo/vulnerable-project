from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import jwt

from app.core.config import settings


def get_scan_rate_limit_key(request: Request) -> str:
    token = request.cookies.get("access_token")
    role = "guest"
    if token:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            role = payload.get("role", "guest") or "guest"
        except Exception:
            role = "guest"

    remote_address = get_remote_address(request)
    return f"{role}:{remote_address}"


def get_rate_limit(key: str) -> str:
    role = key.split(":", 1)[0] if isinstance(key, str) else "guest"
    if role == "admin":
        return "200/minute"
    if role == "user":
        return "30/minute"
    return "5/minute"


limiter = Limiter(key_func=get_remote_address)
