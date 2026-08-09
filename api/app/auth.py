import os
import secrets

from fastapi import HTTPException, Request

from app.controllers.session import is_valid_token


def authenticate(code: str) -> bool:
    return secrets.compare_digest(os.environ["AUTH_CODE"], code)


def require_auth(request: Request) -> None:
    # Cross-site cookies (CloudFront UI domain -> Lambda Function URL API
    # domain) get silently dropped by Safari/Chrome's third-party cookie
    # blocking regardless of SameSite=None; Secure — so the session token
    # travels as a plain bearer token instead, stored client-side by the UI.
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ") if auth_header.startswith("Bearer ") else None
    if token is None or not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Not authenticated")
