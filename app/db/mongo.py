from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=100,
            serverSelectionTimeoutMS=5000,
        )
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.MONGO_DB_NAME]


async def close_client():
    global _client
    if _client:
        _client.close()
        _client = None


async def create_indexes():
    db = get_db()
    await db["users"].create_index("email", unique=True, background=True)
    await db["users"].create_index("user_id", unique=True, background=True)
    await db["workspaces"].create_index("workspace_id", unique=True, background=True)
    await db["workspaces"].create_index("org_id", background=True)
    await db["memberships"].create_index([("user_id", 1), ("workspace_id", 1)], unique=True, background=True)
