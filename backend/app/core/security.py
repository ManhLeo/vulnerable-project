from __future__ import annotations

from datetime import datetime, timedelta
import re
from passlib.context import CryptContext
import jwt

from app.core.config import settings


def _build_pwd_context() -> CryptContext:
    """Build CryptContext with configurable bcrypt rounds from settings."""
    return CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=settings.bcrypt_rounds,
    )


pwd_context = _build_pwd_context()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time password verification. Never logs inputs."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password with bcrypt at configured cost factor. Never log the return value."""
    return pwd_context.hash(password)


def validate_password_policy(password: str) -> bool:
    """Enforce: min 8 chars, 1 lowercase, 1 uppercase, 1 digit."""
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create signed JWT. Caller must never log the returned token."""
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

