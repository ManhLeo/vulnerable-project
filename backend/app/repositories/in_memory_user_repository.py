from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.models.user_models import Role, UserInDB


class InMemoryUserRepository:
    """Shared in-memory user repository for local development and tests."""

    def __init__(self) -> None:
        self._users: dict[str, UserInDB] = {}

    def clear(self) -> None:
        self._users.clear()

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        normalized = email.lower()
        for user in self._users.values():
            if user.email.lower() == normalized and not user.is_deleted:
                return deepcopy(user)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        user = self._users.get(user_id)
        if user and not user.is_deleted:
            return deepcopy(user)
        return None

    async def get_user_by_role(self, role: Role) -> Optional[UserInDB]:
        for user in self._users.values():
            if user.role == role and not user.is_deleted:
                return deepcopy(user)
        return None

    async def update_user_role(self, user_id: str, role: Role) -> bool:
        user = self._users.get(user_id)
        if not user or user.is_deleted:
            return False
        user.role = role
        return True

    async def create_user(self, user: UserInDB) -> UserInDB:
        created = deepcopy(user)
        created.id = str(uuid4())
        self._users[created.id] = created
        return deepcopy(created)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[UserInDB]:
        users = [user for user in self._users.values() if not user.is_deleted]
        users.sort(key=lambda item: item.created_at, reverse=True)
        return [deepcopy(user) for user in users[skip : skip + limit]]

    async def get_users_count(self) -> int:
        return sum(1 for user in self._users.values() if not user.is_deleted)

    async def soft_delete_user(self, user_id: str) -> bool:
        user = self._users.get(user_id)
        if not user or user.is_deleted:
            return False
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        return True

    async def update_last_login(self, user_id: str) -> None:
        user = self._users.get(user_id)
        if not user:
            return
        user.last_login_at = datetime.utcnow()
        user.failed_login_attempts = 0
        user.last_failed_login_at = None

    async def increment_failed_login(self, user_id: str) -> None:
        user = self._users.get(user_id)
        if not user:
            return
        user.failed_login_attempts += 1
        user.last_failed_login_at = datetime.utcnow()
