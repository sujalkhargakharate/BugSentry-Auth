from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


Provider = Literal["github", "gitlab", "google"]
Role = Literal["developer", "ceo"]


# ── DB Models ──────────────────────────────────────────────────────────────

class UserInDB(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: Provider
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceInDB(BaseModel):
    workspace_id: str
    name: str
    provider: Literal["github", "gitlab"]
    org_id: str
    created_by: str  # user_id


class MembershipInDB(BaseModel):
    user_id: str
    workspace_id: str
    role: Role = "developer"


# ── Request / Response Schemas ─────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    id_token: str


class SelectOrgRequest(BaseModel):
    org_id: str
    org_name: str
    provider: Literal["github", "gitlab"]


class SetRoleRequest(BaseModel):
    workspace_id: str
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str
    created_at: datetime


class OrgItem(BaseModel):
    org_id: str
    name: str
    provider: str
    avatar_url: Optional[str] = None


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str
    provider: str
    org_id: str
    role: str
