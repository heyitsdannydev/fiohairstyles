from pydantic import BaseModel


class Session(BaseModel):
    Token: str
    CreatedAt: str
    # Epoch seconds. Also DynamoDB's TTL attribute if TTL is enabled on the
    # table for this attribute name — auto-purges expired items server-side,
    # on top of the explicit expiry check in controllers/session.py.
    Ttl: int
