from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IntervalRepetitionBase(BaseModel):
    card_id: int
    state: str
    step: int
    stability: float
    difficulty: float
    due: datetime


class IntervalRepetitionCreate(IntervalRepetitionBase):
    user_id: int


class IntervalRepetitionUpdate(BaseModel):
    state: Optional[str] = None
    step: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    due: Optional[datetime] = None
    last_review: Optional[datetime] = None


class IntervalRepetitionInDB(IntervalRepetitionBase):
    id: int
    user_id: int
    last_review: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class IntervalRepetition(IntervalRepetitionInDB):
    pass
