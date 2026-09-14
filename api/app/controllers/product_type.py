from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.controllers import _table
from app.models.product_type import ProductType

if TYPE_CHECKING:
    from app.routers.product_type import ProductTypeCreate, ProductTypeUpdate


def list_product_types() -> list[ProductType]:
    """All product types live under pk="ProductType", one per sk (a generated UUID)."""
    response = _table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "ProductType"},
    )
    return [ProductType(**item) for item in response.get("Items", [])]


def create_product_type(data: ProductTypeCreate) -> ProductType:
    item = {
        "pk": "ProductType",
        "sk": str(uuid.uuid4()),
        "Name": data.Name,
    }
    _table.put_item(Item=item)
    return ProductType(**item)


def update_product_type(product_type_id: str, data: ProductTypeUpdate) -> ProductType:
    item = {
        "pk": "ProductType",
        "sk": product_type_id,
        "Name": data.Name,
    }
    _table.put_item(Item=item)
    return ProductType(**item)


def delete_product_type(product_type_id: str) -> None:
    _table.delete_item(Key={"pk": "ProductType", "sk": product_type_id})
