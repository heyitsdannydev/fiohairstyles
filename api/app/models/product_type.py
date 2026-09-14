from typing import Literal

from pydantic import BaseModel


class ProductType(BaseModel):
    pk: Literal["ProductType"] = "ProductType"
    sk: str

    Name: str
