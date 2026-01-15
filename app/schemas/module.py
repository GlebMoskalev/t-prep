from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .card import Card

class AccessLevel(str, Enum):
    ALL_USERS = "all_users"
    USERS_WITH_PASSWORD = "users_with_password"
    ONLY_ME = "only_me"


class ModuleBase(BaseModel):
    name: str
    description: Optional[str] = None


class ModuleCreate(ModuleBase):
    ViewAccess: AccessLevel
    EditAccess: AccessLevel
    PasswordHash: Optional[str] = None


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ViewAccess: Optional[AccessLevel] = None
    EditAccess: Optional[AccessLevel] = None


class ModuleInDB(ModuleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    ViewAccess: AccessLevel
    EditAccess: AccessLevel
    PasswordHash: str

    class Config:
        from_attributes = True


class Module(ModuleInDB):
    IsIntervalRepetitionsEnabled: bool
    TotalCards: int
    CardsToRepeatCount: int


# Forward reference будет разрешен после импорта card schemas
class ModuleWithCards(Module):
    cards: List["Card"] = []


class GetModulesResponse(BaseModel):
    items: List[Module]
    total_count: int

    class Config:
        from_attributes = True 


# Импортируем Card после определения классов чтобы избежать циклического импорта
from .card import Card  # noqa: E402

ModuleWithCards.model_rebuild()
