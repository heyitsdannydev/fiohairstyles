from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.auth import authenticate, require_auth
from app.controllers.session import create_session, invalidate_session

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    Code: str


class LoginResponse(BaseModel):
    Token: str


@router.post("/login")
def login(data: LoginRequest) -> LoginResponse:
    if not authenticate(data.Code):
        raise HTTPException(status_code=401, detail="Invalid code")
    return LoginResponse(Token=create_session())


@router.post("/logout", status_code=204)
def logout(request: Request) -> None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        invalidate_session(auth_header.removeprefix("Bearer "))


# Used by the UI on load to check whether a locally-stored token is still
# valid, before deciding whether to bounce to /login.
@router.get("/session", status_code=204)
def check_session(_: None = Depends(require_auth)) -> None:
    pass
