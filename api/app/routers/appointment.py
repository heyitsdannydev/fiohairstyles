from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import require_auth
from app.controllers.appointment import (
    create_appointment,
    delete_appointment,
    list_appointments_by_month,
    list_appointments_for_income,
    update_appointment,
)
from app.models.appointment import Appointment

router = APIRouter(tags=["appointments"], dependencies=[Depends(require_auth)])


class AppointmentCreate(BaseModel):
    ClientId: str
    ClientName: str
    Address: str | None = None
    ServiceDateTime: datetime
    Service: str
    Comments: str | None = None
    ServicePrice: float = 0
    Transportation: float = 0
    DownPaymentPercentage: float = 0
    PaymentMethod: str | None = None
    DownPaymentDate: date | None = None
    RemainingPaymentDate: date | None = None


class AppointmentUpdate(AppointmentCreate):
    pass


@router.get("/appointments")
def get_appointments(
    month: int,
    year: int,
    order: Literal["asc", "desc"] = "desc",
    only_future: bool = False,
) -> list[Appointment]:
    return list_appointments_by_month(month, year, order=order, only_future=only_future)


@router.get("/appointments/income")
def get_appointments_income(
    month: int, year: int, order: Literal["asc", "desc"] = "desc"
) -> list[Appointment]:
    return list_appointments_for_income(month, year, order=order)


@router.post("/appointments")
def post_appointment(data: AppointmentCreate) -> Appointment:
    return create_appointment(data)


@router.put("/appointments/{sk}")
def put_appointment(sk: str, data: AppointmentUpdate) -> Appointment:
    updated = update_appointment(sk, data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated


@router.delete("/appointments/{sk}", status_code=204)
def delete_appointment_endpoint(sk: str) -> None:
    delete_appointment(sk)
