from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime, date
import json


class ClientModel(BaseModel):
    ClientId: str
    ClientName: str

    def __repr__(self):
        return f"Client(ClientId={self.ClientId}, ClientName={self.ClientName})"


class Appointment(BaseModel):
    model_config = ConfigDict(extra="allow")
    pk: str
    sk: datetime

    Address: Optional[str] = None
    Client: ClientModel

    ServiceDateTime: datetime

    Service: str

    PaymentMethod: Optional[str] = None

    Source: Optional[str] = None

    DownPaymentPercentage: float = 0.0

    ServicePrice: int = 0
    Transportation: int = 0

    @property
    def Total(self):
        return self.ServicePrice + self.Transportation

    @property
    def DownPayment(self):
        return round(self.Total * self.DownPaymentPercentage / 100)

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

    @field_validator("sk", "ServiceDateTime", mode="before")
    @classmethod
    def parse_datetimes(cls, v):
        return datetime.fromisoformat(v)

    def __repr__(self):
        return f"Appointment(Client={self.Client}, Service={self.Service}, ServiceDateTime={self.ServiceDateTime}, Total={self.Total})"
