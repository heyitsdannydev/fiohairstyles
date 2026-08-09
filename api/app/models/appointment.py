import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, computed_field, field_validator, model_validator

from app.models.client import SourceType


class ClientRef(BaseModel):
    ClientId: str
    ClientName: str


class Appointment(BaseModel):
    # extra="allow": some production items may carry attributes added by
    # hand (e.g. via the AWS console) that aren't modeled below — same
    # tolerance the old Streamlit app's Appointment model had.
    model_config = ConfigDict(extra="allow")

    pk: str
    sk: str

    Client: ClientRef
    Address: str | None = None
    ServiceDateTime: datetime
    Service: str
    Comments: str | None = None
    PaymentMethod: str | None = None
    # Always "Profesora" today (see create_appointment() in
    # controllers/appointment.py) — there's no Source field on the
    # appointment form, unlike Client.Source, which the client picker does
    # expose.
    Source: SourceType | None = None
    DownPaymentPercentage: float = 0.0
    ServicePrice: float = 0
    Transportation: float = 0

    # Set once a client actually pays — the Incomes page reads them to
    # decide which month a payment counts toward. Kept as real typed dates
    # (not left as untyped extras) since the old incomes.py already relied
    # on them being date-like (.month/.year/.strftime()).
    DownPaymentDate: date | None = None
    RemainingPaymentDate: date | None = None
    # Set by hand — no UI writes this yet.
    Remaining: float | None = None
    # A real stored field (not purely computed from DownPaymentPercentage)
    # because production data shows it's sometimes recorded by hand once a
    # client actually pays a down payment that doesn't match the
    # percentage on file (e.g. DownPaymentPercentage=0 but a real
    # DownPayment was still collected and noted). Falls back to the
    # percentage-based estimate below only when nothing's been recorded yet
    # — see _default_down_payment.
    DownPayment: float = 0.0

    @model_validator(mode="before")
    @classmethod
    def _default_down_payment(cls, data: Any) -> Any:
        if not isinstance(data, dict) or data.get("DownPayment") not in (None, ""):
            return data
        service_price = float(data.get("ServicePrice", 0) or 0)
        transportation = float(data.get("Transportation", 0) or 0)
        percentage = float(data.get("DownPaymentPercentage", 0) or 0)
        estimated = round((service_price + transportation) * percentage / 100)
        return {**data, "DownPayment": estimated}

    @field_validator("Client", mode="before")
    @classmethod
    def parse_client(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Old DynamoDB-JSON string encoding some legacy records may
            # still have (see the old app's models/appointment.py) rather
            # than a native Map.
            data = json.loads(v)
            return {
                "ClientId": data["ClientId"]["S"],
                "ClientName": data["ClientName"]["S"],
            }
        return v

    @field_validator("ServiceDateTime", mode="before")
    @classmethod
    def parse_service_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

    @field_validator("DownPaymentDate", "RemainingPaymentDate", mode="before")
    @classmethod
    def parse_payment_dates(cls, v: Any) -> Any:
        if isinstance(v, str) and v:
            return date.fromisoformat(v[:10])
        return v or None

    @computed_field
    @property
    def Total(self) -> float:
        return self.ServicePrice + self.Transportation
