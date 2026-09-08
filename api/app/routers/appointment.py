from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.auth import require_auth
from app.controllers.appointment import (
    create_appointment,
    delete_appointment,
    list_appointments_by_month,
    list_appointments_for_income,
    update_appointment,
)
from app.controllers.document import (
    add_appointment_document,
    appointment_document_url,
    delete_appointment_document,
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
    CanvaProposal: str | None = None
    ServicePrice: float = 0
    Transportation: float = 0
    DownPayment: float = 0
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


# --- Documents -------------------------------------------------------------
#
# Each appointment carries a Files list ([{Label, S3Path}, ...]); the bytes
# live in DOCUMENTS_BUCKET. The API owns both sides — S3 and DynamoDB.

# The API runs behind a Lambda Function URL, whose request payload tops
# out at 6 MB (and multipart bodies arrive base64-encoded in the event),
# so keep the accepted file well under that.
_MAX_DOCUMENT_BYTES = 4 * 1024 * 1024


class DocumentUrl(BaseModel):
    Url: str


@router.post("/appointments/{sk}/documents")
async def upload_appointment_document(
    sk: str,
    label: str = Form(...),
    file: UploadFile = File(...),
) -> Appointment:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > _MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 4 MB)")

    appointment = add_appointment_document(
        sk,
        label=label.strip() or (file.filename or "Document"),
        filename=file.filename or "document",
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.get("/appointments/{sk}/documents/url")
def get_appointment_document_url(sk: str, s3_path: str) -> DocumentUrl:
    url = appointment_document_url(sk, s3_path)
    if url is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentUrl(Url=url)


@router.delete("/appointments/{sk}/documents")
def delete_appointment_document_endpoint(sk: str, s3_path: str) -> Appointment:
    appointment = delete_appointment_document(sk, s3_path)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment
