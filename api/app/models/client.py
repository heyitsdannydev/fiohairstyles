from typing import Literal

from pydantic import BaseModel

# Matches the pre-existing Streamlit app's SourceEnum values exactly (see
# models/source.py in the old app) — a fixed closed set, not an open catalog.
SourceType = Literal["Instagram", "Profesora", "Contacto"]


class Client(BaseModel):
    pk: Literal["Client"] = "Client"
    sk: str

    Name: str
    Instagram: str | None = None
    Phone: str | None = None
    Source: SourceType = "Contacto"
