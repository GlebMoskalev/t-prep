from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    question: str
    answer: str


class CardCreate(CardBase):
    module_id: int


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
