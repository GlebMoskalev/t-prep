from pydantic import BaseModel
from typing import List
from datetime import datetime


class UpdateCardIntervalRepetitionRequest(BaseModel):
    time_of_answer: datetime
    right_answer: bool

    class Config:
        from_attributes = True

class CardResponse(BaseModel):
    id: str
    question: str
    answer_variant: List[str]
    right_answer: int

    class Config:
        from_attributes = True

class GetInternalRepetitionCardResponse(BaseModel):
    items: List[CardResponse]
    total_count: int

    class Config:
        from_attributes = True