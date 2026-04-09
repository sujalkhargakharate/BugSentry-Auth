from __future__ import annotations

from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import settings


def verify_google_token(token: str) -> dict:
    try:
        id_info = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {exc}",
        )

    email = id_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="No email in Google token.")

    return {
        "google_id": id_info["sub"],
        "email": email,
        "name": id_info.get("name"),
        "picture": id_info.get("picture"),
    }
