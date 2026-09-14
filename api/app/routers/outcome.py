from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import require_auth
from app.controllers.outcome import create_outcome, delete_outcome, list_outcomes, update_outcome
from app.models.outcome import Outcome

router = APIRouter(tags=["outcomes"], dependencies=[Depends(require_auth)])


class OutcomeCreate(BaseModel):
    Money: float
    Date: date | None = None
    ProductType: str


class OutcomeUpdate(OutcomeCreate):
    pass


@router.get("/outcomes")
def get_outcomes() -> list[Outcome]:
    return list_outcomes()


@router.post("/outcomes")
def post_outcome(data: OutcomeCreate) -> Outcome:
    return create_outcome(data)


@router.put("/outcomes/{outcome_id}")
def put_outcome(outcome_id: str, data: OutcomeUpdate) -> Outcome:
    return update_outcome(outcome_id, data)


@router.delete("/outcomes/{outcome_id}", status_code=204)
def delete_outcome_endpoint(outcome_id: str) -> None:
    delete_outcome(outcome_id)
