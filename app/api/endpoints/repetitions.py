from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Tuple
from ...db.database import get_db
from ...models.user import User
from ...models.module import Module
from ...models.card import Card
from ...schemas.card import Card as CardSchema, CreateCardRequest, PatchCardRequest, GetCardResponse, CardInDB
from ...core.deps import get_current_active_user
from ...schemas.interval_repetition import GetInternalRepetitionCardResponse, UpdateCardIntervalRepetitionRequest
import random
from typing import Optional
from pydantic import BaseModel
from datetime import timedelta
from ...services.repetition_service import RepetitionService


router = APIRouter()


@router.post("/")
async def enable_interval_repetitions(
    module_id: str,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        service = RepetitionService(db)
        service.enable_interval_repetitions(user.id, module_id)
        return {"message": "Interval repetitions enabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
async def disable_interval_repetitions(
    module_id: str,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        service = RepetitionService(db)
        service.disable_interval_repetitions(user.id, module_id)
        return {"message": "Interval repetitions disabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{card_id}")
async def update_card_status(
    module_id: str,
    card_id: str,
    request: UpdateCardIntervalRepetitionRequest,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        service = RepetitionService(db)
        result = service.update_card_status(user.id, module_id, card_id, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_cards_for_repetition(
    module_id: str,
    skip: int = Query(0, ge=0),
    take: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> GetInternalRepetitionCardResponse:
    try:
        service = RepetitionService(db)
        return service.get_cards_for_repetition(user.id, module_id, skip, take)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
