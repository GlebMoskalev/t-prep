from pydantic import BaseModel
from typing import List
from datetime import datetime


class UpdateCardIntervalRepetitionRequest(BaseModel):
    TimeOfAnswer: datetime
    RightAnswer: bool

    class Config:
        from_attributes = True

class CardResponse(BaseModel):
    Id: str
    Question: str
    AnswerVariant: List[str]
    RightAnswer: int

    class Config:
        from_attributes = True

class GetInternalRepetitionCardResponse(BaseModel):
    Items: List[CardResponse]
    TotalCount: int

    class Config:
        from_attributes = True