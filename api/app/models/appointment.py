import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, computed_field, field_validator

from app.models.client import SourceType


class ClientRef(BaseModel):
    ClientId: str
    ClientName: str


class AppointmentFile(BaseModel):
    # A document attached to the appointment. Only the S3 key is stored on
    # the item; the bytes live in the DOCUMENTS_BUCKET. Downloads go
    # through a short-lived presigned URL minted by the API.
    Label: str
    S3Path: str


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
    CanvaProposal: str | None = None
    # Always "Profesora" today (see create_appointment() in
    # controllers/appointment.py) — there's no Source field on the
    # appointment form, unlike Client.Source, which the client picker does
    # expose.
    Source: SourceType | None = None
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
    # The seña (deposit) amount, in whatever currency the appointment is
    # priced in — a plain recorded amount, not derived from a percentage.
    DownPayment: float = 0.0

    # Attached documents. Managed through the dedicated
    # /appointments/{sk}/documents endpoints, not the appointment form.
    Files: list[AppointmentFile] = []

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
