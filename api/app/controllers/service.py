from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.controllers import _table
from app.models.service import Service

if TYPE_CHECKING:
    from app.routers.service import ServiceCreate, ServiceUpdate


def list_services() -> list[Service]:
    """All services live under pk="Service", one per sk (a generated UUID)."""
    response = _table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "Service"},
    )
    return [Service(**item) for item in response.get("Items", [])]


def create_service(data: ServiceCreate) -> Service:
    item = {
        "pk": "Service",
        "sk": str(uuid.uuid4()),
        "Name": data.Name,
    }
    _table.put_item(Item=item)
    return Service(**item)


def update_service(service_id: str, data: ServiceUpdate) -> Service:
    item = {
        "pk": "Service",
        "sk": service_id,
        "Name": data.Name,
    }
    _table.put_item(Item=item)
    return Service(**item)


def delete_service(service_id: str) -> None:
    _table.delete_item(Key={"pk": "Service", "sk": service_id})
