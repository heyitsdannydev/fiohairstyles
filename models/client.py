from pydantic import BaseModel, Field
from typing import Optional

from models.source import SourceEnum


class Client(BaseModel):
    pk: str
    sk: str

    Name: str = None
    Instagram: str = None
    Phone: str = None
    Source: Optional[SourceEnum] = Field(default=SourceEnum.Contacto)

    def __repr__(self):
        return (
            f"Client(Name={self.Name}, Instagram={self.Instagram}, Phone={self.Phone})"
        )
