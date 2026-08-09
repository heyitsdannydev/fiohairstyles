from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.controllers import _table
from app.models.client import Client

if TYPE_CHECKING:
    from app.routers.client import ClientCreate, ClientUpdate


def list_clients() -> list[Client]:
    """All clients live under pk="Client", one per sk (a generated UUID)."""
    response = _table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "Client"},
    )
    return [Client(**item) for item in response.get("Items", [])]


def create_client(data: ClientCreate) -> Client:
    item = {
        "pk": "Client",
        "sk": str(uuid.uuid4()),
        "Name": data.Name,
        "Phone": data.Phone,
        "Instagram": data.Instagram,
        "Source": data.Source,
    }
    _table.put_item(Item=item)
    return Client(**item)


def update_client(client_id: str, data: ClientUpdate) -> Client:
    item = {
        "pk": "Client",
        "sk": client_id,
        "Name": data.Name,
        "Phone": data.Phone,
        "Instagram": data.Instagram,
        "Source": data.Source,
    }
    _table.put_item(Item=item)
    return Client(**item)


def delete_client(client_id: str) -> None:
    _table.delete_item(Key={"pk": "Client", "sk": client_id})
