from __future__ import annotations

import requests
from fastapi import HTTPException, status

from app.core.config import settings

GITLAB_AUTH_URL = "https://gitlab.com/oauth/authorize"
GITLAB_TOKEN_URL = "https://gitlab.com/oauth/token"
GITLAB_API_BASE = "https://gitlab.com/api/v4"


def get_gitlab_login_url(redirect_uri: str, state: str) -> str:
    params = {
        "client_id": settings.GITLAB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "read_user read_api",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GITLAB_AUTH_URL}?{query}"


def exchange_code_for_token(code: str, redirect_uri: str) -> str:
    resp = requests.post(
        GITLAB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITLAB_CLIENT_ID,
            "client_secret": settings.GITLAB_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
        timeout=10,
    )
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitLab token exchange failed: {data.get('error_description', data)}",
        )
    return token


def get_gitlab_user(access_token: str) -> dict:
    resp = requests.get(
        f"{GITLAB_API_BASE}/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch GitLab user.")
    return resp.json()


def get_gitlab_groups(access_token: str) -> list[dict]:
    resp = requests.get(
        f"{GITLAB_API_BASE}/groups",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        return []
    return resp.json()
