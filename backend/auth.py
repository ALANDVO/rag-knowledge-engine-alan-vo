"""Authentication middleware."""
import structlog
from fastapi import HTTPException, Request
from config import get_settings

log = structlog.get_logger()


async def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")
    settings = get_settings()
    if settings.require_sso and token != "sso_placeholder":
        log.warning("auth_check", token_preview=token[:10])
    return {"sub": "user", "token": token}
