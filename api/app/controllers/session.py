import secrets
import time
from datetime import datetime, timezone

from app.controllers import _table
from app.models.session import Session

SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 1 week


def _session_key(token: str) -> dict[str, str]:
    # Own partition per token (pk=Session#{token}, fixed sk) rather than
    # nesting under some User# — a get_item on this key is a direct O(1)
    # lookup. There's only one user in this app, so no UserId is stored.
    return {"pk": f"Session#{token}", "sk": "Session"}


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    item = {
        **_session_key(token),
        "Token": token,
        "CreatedAt": now.isoformat(),
        "Ttl": int(now.timestamp()) + SESSION_MAX_AGE_SECONDS,
    }
    _table.put_item(Item=item)
    return token


def is_valid_token(token: str) -> bool:
    response = _table.get_item(Key=_session_key(token))
    raw_item = response.get("Item")
    if raw_item is None:
        return False

    session = Session(**raw_item)
    if session.Ttl < int(time.time()):
        # Expired but not yet swept by DynamoDB TTL (which can lag up to
        # 48h) — delete eagerly so a stale token can't keep working.
        invalidate_session(token)
        return False
    return True


def invalidate_session(token: str) -> None:
    _table.delete_item(Key=_session_key(token))
