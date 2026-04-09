from __future__ import annotations

import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase


async def upsert_user(db: AsyncIOMotorDatabase, *, email: str, name: str | None, picture: str | None, provider: str, github_token: str | None = None, gitlab_token: str | None = None) -> dict:
    now = datetime.utcnow()
    update: dict = {
        "$set": {
            "name": name,
            "picture": picture,
            "provider": provider,
            "updated_at": now,
        },
        "$setOnInsert": {
            "user_id": str(uuid.uuid4()),
            "email": email,
            "created_at": now,
        },
    }
    if github_token:
        update["$set"]["github_token"] = github_token
    if gitlab_token:
        update["$set"]["gitlab_token"] = gitlab_token

    user = await db["users"].find_one_and_update(
        {"email": email},
        update,
        upsert=True,
        return_document=True,
    )
    return user


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> dict | None:
    return await db["users"].find_one({"user_id": user_id})
