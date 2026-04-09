from __future__ import annotations

from app.core.security import create_access_token
from app.db.models import TokenResponse


def issue_token(user_id: str, provider: str) -> TokenResponse:
    token, expires_in = create_access_token({"user_id": user_id, "provider": provider})
    return TokenResponse(access_token=token, expires_in=expires_in)
