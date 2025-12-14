from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    question: str
    answer: str


class CardCreateRequest(CardBase):
    pass


class CardUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None


class CardInDB(CardBase):
    id: int
    module_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Card(CardInDB):
    pass

class GetCardsResponse(BaseModel):
    Items: list[Card]
    TotalCount: int

    class Config:
        from_attributes = True