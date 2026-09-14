from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import require_auth
from app.controllers.product_type import (
    create_product_type,
    delete_product_type,
    list_product_types,
    update_product_type,
)
from app.models.product_type import ProductType

router = APIRouter(tags=["product-types"], dependencies=[Depends(require_auth)])


class ProductTypeCreate(BaseModel):
    Name: str


class ProductTypeUpdate(ProductTypeCreate):
    pass


@router.get("/product-types")
def get_product_types() -> list[ProductType]:
    return list_product_types()


@router.post("/product-types")
def post_product_type(data: ProductTypeCreate) -> ProductType:
    return create_product_type(data)


@router.put("/product-types/{product_type_id}")
def put_product_type(product_type_id: str, data: ProductTypeUpdate) -> ProductType:
    return update_product_type(product_type_id, data)


@router.delete("/product-types/{product_type_id}", status_code=204)
def delete_product_type_endpoint(product_type_id: str) -> None:
    delete_product_type(product_type_id)
