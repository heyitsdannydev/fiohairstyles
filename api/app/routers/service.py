from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import require_auth
from app.controllers.service import create_service, delete_service, list_services, update_service
from app.models.service import Service

router = APIRouter(tags=["services"], dependencies=[Depends(require_auth)])


class ServiceCreate(BaseModel):
    Name: str


class ServiceUpdate(ServiceCreate):
    pass


@router.get("/services")
def get_services() -> list[Service]:
    return list_services()


@router.post("/services")
def post_service(data: ServiceCreate) -> Service:
    return create_service(data)


@router.put("/services/{service_id}")
def put_service(service_id: str, data: ServiceUpdate) -> Service:
    return update_service(service_id, data)


@router.delete("/services/{service_id}", status_code=204)
def delete_service_endpoint(service_id: str) -> None:
    delete_service(service_id)
