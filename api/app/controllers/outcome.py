from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from app.controllers import _table
from app.models.outcome import Outcome

if TYPE_CHECKING:
    from app.routers.outcome import OutcomeCreate, OutcomeUpdate


def list_outcomes() -> list[Outcome]:
    """All outcomes live under pk="Outcome", one per sk (a generated UUID)."""
    response = _table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "Outcome"},
    )
    return [Outcome(**item) for item in response.get("Items", [])]


def create_outcome(data: OutcomeCreate) -> Outcome:
    item = {
        "pk": "Outcome",
        "sk": str(uuid.uuid4()),
        "Money": Decimal(str(data.Money)),
        "Date": (data.Date or date.today()).isoformat(),
        "ProductType": data.ProductType,
    }
    _table.put_item(Item=item)
    return Outcome(**item)


def update_outcome(outcome_id: str, data: OutcomeUpdate) -> Outcome:
    item = {
        "pk": "Outcome",
        "sk": outcome_id,
        "Money": Decimal(str(data.Money)),
        "Date": (data.Date or date.today()).isoformat(),
        "ProductType": data.ProductType,
    }
    _table.put_item(Item=item)
    return Outcome(**item)


def delete_outcome(outcome_id: str) -> None:
    _table.delete_item(Key={"pk": "Outcome", "sk": outcome_id})
