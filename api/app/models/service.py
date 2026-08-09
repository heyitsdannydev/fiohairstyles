from typing import Literal

from pydantic import BaseModel


class Service(BaseModel):
    pk: Literal["Service"] = "Service"
    sk: str

    Name: str
