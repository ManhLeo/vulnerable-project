from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import USERS_COLLECTION
from app.models.user_models import UserInDB, UserCreate, Role


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db[USERS_COLLECTION]

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"email": email, "is_deleted": False})
        if doc:
            doc["_id"] = str(doc["_id"])
            return UserInDB(**doc)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(user_id), "is_deleted": False})
            if doc:
                doc["_id"] = str(doc["_id"])
                return UserInDB(**doc)
        except Exception:
            pass
        return None

    async def get_user_by_role(self, role: Role) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"role": role.value, "is_deleted": False})
        if doc:
            doc["_id"] = str(doc["_id"])
            return UserInDB(**doc)
        return None

    async def update_user_role(self, user_id: str, role: Role) -> bool:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id), "is_deleted": False},
                {"$set": {"role": role.value}},
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def create_user(self, user: UserInDB) -> UserInDB:
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        cursor = self.collection.find({"is_deleted": False}).skip(skip).limit(limit)
        users = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            users.append(UserInDB(**doc))
        return users

    async def get_users_count(self) -> int:
        return await self.collection.count_documents({"is_deleted": False})

    async def soft_delete_user(self, user_id: str) -> bool:
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def update_last_login(self, user_id: str) -> None:
        """Atomically record successful login timestamp and reset failure counters."""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "last_login_at": datetime.utcnow(),
                    "failed_login_attempts": 0,
                    "last_failed_login_at": None,
                }}
            )
        except Exception:
            pass  # Non-fatal — do not block login on stat update failure

    async def increment_failed_login(self, user_id: str) -> None:
        """Increment consecutive failure counter for brute-force tracking."""
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"failed_login_attempts": 1},
                 "$set": {"last_failed_login_at": datetime.utcnow()}}
            )
        except Exception:
            pass
