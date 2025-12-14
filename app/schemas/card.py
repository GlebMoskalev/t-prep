from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CardBase(BaseModel):
    question: str
    answer: str


class CreateCardRequest(CardBase):
    pass


class PatchCardRequest(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None


class CardInDB(CardBase):
    id: int
    module_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Card(BaseModel):
    id: str
    question: str
    answer_variant: List[str]
    right_answer: int

    class Config:
        from_attributes = True    

class GetCardResponse(BaseModel):
    items: list[Card]
    total_count: int

    class Config:
        from_attributes = True