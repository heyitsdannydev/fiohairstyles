from pydantic import BaseModel, Field
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date
import json


class ClientModel(BaseModel):
    ClientId: str
    ClientName: str

    def __repr__(self):
        return f"Client(ClientId={self.ClientId}, ClientName={self.ClientName})"


class Appointment(BaseModel):
    pk: str
    sk: datetime

    Address: Optional[str] = None
    Client: ClientModel

    DownPayment: int
    DownPaymentDate: Optional[date] = None

    PaymentMethod: Optional[str] = None

    Remaining: int
    RemainingPaymentDate: Optional[date] = None

    Service: str
    ServiceDateTime: datetime

    Total: int

    # -------- Validators --------

    @field_validator("Client", mode="before")
    @classmethod
    def parse_client(cls, v):
        if isinstance(v, str):
            # Convert DynamoDB JSON string → dict
            data = json.loads(v)
            return {
                "ClientId": data["ClientId"]["S"],
                "ClientName": data["ClientName"]["S"],
            }
        return v

    @field_validator(
        "DownPayment",
        "Remaining",
        "Total",
        mode="before",
    )
    @classmethod
    def parse_numbers(cls, v):
        if v == "" or v is None:
            return 0.0
        return float(v)

    @field_validator(
        "DownPaymentDate",
        "RemainingPaymentDate",
        mode="before",
    )
    @classmethod
    def parse_dates(cls, v):
        if not v:
            return None
        return datetime.fromisoformat(v).date()

    @field_validator("sk", "ServiceDateTime", mode="before")
    @classmethod
    def parse_datetimes(cls, v):
        return datetime.fromisoformat(v)

    def __repr__(self):
        return f"Appointment(Client={self.Client}, Service={self.Service}, ServiceDateTime={self.ServiceDateTime}, Total={self.Total})"
