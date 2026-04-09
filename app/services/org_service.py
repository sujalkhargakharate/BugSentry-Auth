from __future__ import annotations

import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_or_get_workspace(db: AsyncIOMotorDatabase, *, org_id: str, org_name: str, provider: str, created_by: str) -> dict:
    existing = await db["workspaces"].find_one({"org_id": org_id, "provider": provider})
    if existing:
        return existing

    workspace = {
        "workspace_id": str(uuid.uuid4()),
        "name": org_name,
        "provider": provider,
        "org_id": org_id,
        "created_by": created_by,
        "created_at": datetime.utcnow(),
    }
    await db["workspaces"].insert_one(workspace)
    return workspace


async def assign_role(db: AsyncIOMotorDatabase, *, user_id: str, workspace_id: str, role: str) -> dict:
    now = datetime.utcnow()

    # First user in workspace becomes CEO, rest are developers
    member_count = await db["memberships"].count_documents({"workspace_id": workspace_id})
    if member_count == 0:
        role = "ceo"

    membership = await db["memberships"].find_one_and_update(
        {"user_id": user_id, "workspace_id": workspace_id},
        {"$set": {"role": role, "updated_at": now}, "$setOnInsert": {"joined_at": now}},
        upsert=True,
        return_document=True,
    )
    return membership


async def get_user_workspaces(db: AsyncIOMotorDatabase, user_id: str) -> list[dict]:
    memberships = await db["memberships"].find({"user_id": user_id}).to_list(length=100)
    result = []
    for m in memberships:
        ws = await db["workspaces"].find_one({"workspace_id": m["workspace_id"]})
        if ws:
            result.append({**ws, "role": m["role"]})
    return result
