from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import require_auth
from app.controllers.client import create_client, delete_client, list_clients, update_client
from app.models.client import Client, SourceType

router = APIRouter(tags=["clients"], dependencies=[Depends(require_auth)])


class ClientCreate(BaseModel):
    Name: str
    Phone: str | None = None
    Instagram: str | None = None
    Source: SourceType = "Contacto"


class ClientUpdate(ClientCreate):
    pass


@router.get("/clients")
def get_clients() -> list[Client]:
    return list_clients()


@router.post("/clients")
def post_client(data: ClientCreate) -> Client:
    return create_client(data)


@router.put("/clients/{client_id}")
def put_client(client_id: str, data: ClientUpdate) -> Client:
    return update_client(client_id, data)


@router.delete("/clients/{client_id}", status_code=204)
def delete_client_endpoint(client_id: str) -> None:
    delete_client(client_id)
