from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    role: Role = Role.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(UserBase):
    id: str = Field(..., alias="_id")
    password_hash: Optional[str] = Field(default=None, serialization_alias="password_hash")
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    last_failed_login_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)

    def has_password(self) -> bool:
        """Check if user has a password set."""
        return bool(self.password_hash)


class UserResponse(UserBase):
    """Public-facing user representation. password_hash is intentionally absent."""
    id: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[Role] = None
