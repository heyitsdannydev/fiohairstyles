from __future__ import annotations

import calendar
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal

from boto3.dynamodb.conditions import Attr, Key

from app.controllers import _table
from app.models.appointment import Appointment

if TYPE_CHECKING:
    from app.routers.appointment import AppointmentCreate, AppointmentUpdate


_PK = "Appointment"


def _key_from_sk(sk: str) -> dict[str, str]:
    # pk is a constant for every appointment (same "one flat partition,
    # unique sk per item" shape as Client's pk="Client") — Callers only ever
    # need to pass sk to address one specific appointment.
    return {"pk": _PK, "sk": sk}


def list_appointments_by_month(
    month: int,
    year: int,
    order: Literal["asc", "desc"] = "desc",
    only_future: bool = False,
) -> list[Appointment]:
    prefix = f"{year:04d}-{month:02d}"
    response = _table.query(
        KeyConditionExpression=Key("pk").eq(_PK) & Key("sk").begins_with(prefix),
        ScanIndexForward=(order == "asc"),
    )
    appointments = [Appointment(**item) for item in response.get("Items", [])]

    # Only show future appointments if we're looking at the current month/year.
    now = datetime.now()
    if only_future and month == now.month and year == now.year:
        appointments = [a for a in appointments if a.ServiceDateTime >= now]

    return appointments


def list_appointments_for_income(
    month: int, year: int, order: Literal["asc", "desc"] = "desc"
) -> list[Appointment]:
    """Scans every appointment for ones with a DownPaymentDate or
    RemainingPaymentDate falling in the requested month — those dates are
    set by hand once a client actually pays (see models/appointment.py),
    so this can't be a Query against the pk/sk key like
    list_appointments_by_month() above."""
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # begins_with (not eq) so this still picks up any pre-migration item
    # left behind under the old "Appointment#YYYY-MM" pk format, alongside
    # the new constant "Appointment" pk.
    filter_expression = Attr("pk").begins_with("Appointment") & (
        Attr("RemainingPaymentDate").between(start_str, end_str)
        | Attr("DownPaymentDate").between(start_str, end_str)
    )

    items: list[dict[str, Any]] = []
    response = _table.scan(FilterExpression=filter_expression)
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = _table.scan(
            FilterExpression=filter_expression,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))

    appointments = [Appointment(**item) for item in items]
    appointments.sort(key=lambda a: a.ServiceDateTime, reverse=(order == "desc"))
    return appointments


def create_appointment(data: AppointmentCreate) -> Appointment:
    service_datetime = data.ServiceDateTime
    item = {
        "pk": _PK,
        "sk": service_datetime.isoformat(),
        "Client": {"ClientId": data.ClientId, "ClientName": data.ClientName},
        "Address": data.Address,
        "ServiceDateTime": service_datetime.isoformat(),
        "Service": data.Service,
        "Comments": data.Comments,
        "CanvaProposal": data.CanvaProposal,
        "ServicePrice": Decimal(str(data.ServicePrice)),
        "Transportation": Decimal(str(data.Transportation)),
        "DownPayment": Decimal(str(data.DownPayment)),
        "PaymentMethod": data.PaymentMethod,
        "Source": "Profesora",
        "DownPaymentDate": data.DownPaymentDate.isoformat() if data.DownPaymentDate else None,
        "RemainingPaymentDate": data.RemainingPaymentDate.isoformat()
        if data.RemainingPaymentDate
        else None,
    }
    _table.put_item(Item=item)
    return Appointment(**item)


def update_appointment(old_sk: str, data: AppointmentUpdate) -> Appointment | None:
    old_key = _key_from_sk(old_sk)
    existing = _table.get_item(Key=old_key).get("Item")
    if existing is None:
        return None

    service_datetime = data.ServiceDateTime
    new_sk = service_datetime.isoformat()

    item = {
        # Preserve anything the edit form doesn't touch — Remaining in
        # particular, which is set by hand once a client pays and must
        # survive a later date/price edit.
        **existing,
        "pk": _PK,
        "sk": new_sk,
        "Client": {"ClientId": data.ClientId, "ClientName": data.ClientName},
        "Address": data.Address,
        "ServiceDateTime": new_sk,
        "Service": data.Service,
        "Comments": data.Comments,
        "CanvaProposal": data.CanvaProposal,
        "ServicePrice": Decimal(str(data.ServicePrice)),
        "Transportation": Decimal(str(data.Transportation)),
        "DownPayment": Decimal(str(data.DownPayment)),
        "PaymentMethod": data.PaymentMethod,
        "DownPaymentDate": data.DownPaymentDate.isoformat() if data.DownPaymentDate else None,
        "RemainingPaymentDate": data.RemainingPaymentDate.isoformat()
        if data.RemainingPaymentDate
        else None,
    }

    # sk changes whenever the date/time moves — delete the old key
    # explicitly rather than relying on put_item, which only ever writes
    # under the *new* key.
    if old_sk != new_sk:
        _table.delete_item(Key=old_key)
    _table.put_item(Item=item)
    return Appointment(**item)


def delete_appointment(sk: str) -> None:
    _table.delete_item(Key=_key_from_sk(sk))
