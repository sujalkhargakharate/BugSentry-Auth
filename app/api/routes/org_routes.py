from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.github_auth import get_github_orgs
from app.auth.gitlab_auth import get_gitlab_groups
from app.core.security import get_current_user
from app.db.models import OrgItem, SelectOrgRequest, SetRoleRequest, WorkspaceResponse
from app.db.mongo import get_db
from app.services.org_service import assign_role, create_or_get_workspace, get_user_workspaces
from app.services.user_service import get_user_by_id

router = APIRouter(prefix="/auth", tags=["Organizations"])


@router.get("/orgs", summary="List GitHub/GitLab orgs for current user", response_model=list[OrgItem])
async def list_orgs(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    orgs: list[OrgItem] = []

    if user.get("github_token"):
        gh_orgs = get_github_orgs(user["github_token"])
        for o in gh_orgs:
            orgs.append(OrgItem(
                org_id=str(o["id"]),
                name=o["login"],
                provider="github",
                avatar_url=o.get("avatar_url"),
            ))

    if user.get("gitlab_token"):
        gl_groups = get_gitlab_groups(user["gitlab_token"])
        for g in gl_groups:
            orgs.append(OrgItem(
                org_id=str(g["id"]),
                name=g["name"],
                provider="gitlab",
                avatar_url=g.get("avatar_url"),
            ))

    return orgs


@router.post("/select-org", summary="Create workspace from selected org", response_model=WorkspaceResponse)
async def select_org(body: SelectOrgRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    workspace = await create_or_get_workspace(
        db,
        org_id=body.org_id,
        org_name=body.org_name,
        provider=body.provider,
        created_by=current_user["user_id"],
    )
    membership = await assign_role(db, user_id=current_user["user_id"], workspace_id=workspace["workspace_id"], role="developer")
    return WorkspaceResponse(**workspace, role=membership["role"])


@router.post("/set-role", summary="Set role in a workspace")
async def set_role(body: SetRoleRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    membership = await assign_role(db, user_id=current_user["user_id"], workspace_id=body.workspace_id, role=body.role)
    return {"workspace_id": body.workspace_id, "role": membership["role"]}


@router.get("/workspaces", summary="List user workspaces", response_model=list[WorkspaceResponse])
async def list_workspaces(current_user: dict = Depends(get_current_user)):
    db = get_db()
    workspaces = await get_user_workspaces(db, current_user["user_id"])
    return [WorkspaceResponse(**ws) for ws in workspaces]
