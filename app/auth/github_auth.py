from __future__ import annotations

import requests
from fastapi import HTTPException, status

from app.core.config import settings

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_BASE = "https://api.github.com"


def get_github_login_url(redirect_uri: str, state: str) -> str:
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "repo read:org user:email",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GITHUB_AUTH_URL}?{query}"


def exchange_code_for_token(code: str, redirect_uri: str) -> str:
    resp = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        },
        timeout=10,
    )
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub token exchange failed: {data.get('error_description', data)}",
        )
    return token


def get_github_user(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    user_resp = requests.get(f"{GITHUB_API_BASE}/user", headers=headers, timeout=10)
    if user_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch GitHub user.")
    user = user_resp.json()

    # Fetch primary email if not public
    if not user.get("email"):
        email_resp = requests.get(f"{GITHUB_API_BASE}/user/emails", headers=headers, timeout=10)
        if email_resp.status_code == 200:
            emails = email_resp.json()
            primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
            user["email"] = primary

    return user


def get_github_orgs(access_token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    resp = requests.get(f"{GITHUB_API_BASE}/user/orgs", headers=headers, timeout=10)
    if resp.status_code != 200:
        return []
    return resp.json()
