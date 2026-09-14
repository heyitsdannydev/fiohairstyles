from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, field_validator


class Outcome(BaseModel):
    pk: Literal["Outcome"] = "Outcome"
    sk: str

    Money: float
    Date: date
    ProductType: str

    @field_validator("Date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> Any:
        if isinstance(v, str):
            return date.fromisoformat(v[:10])
        return v
