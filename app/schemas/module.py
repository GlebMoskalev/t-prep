from pydantic import BaseModel
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .card import Card


class ModuleBase(BaseModel):
    name: str
    description: Optional[str] = None


class ModuleCreate(ModuleBase):
    ViewAccess: str
    EditAccess: str
    PasswordHash: Optional[str] = None


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ViewAccess: Optional[str] = None
    EditAccess: Optional[str] = None


class ModuleInDB(ModuleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Module(ModuleInDB):
    pass


class ModuleAccess(BaseModel):
    view_access: str
    edit_access: str
    password_hash: Optional[str] = None


class ModuleWithAccess(Module):
    access: Optional[ModuleAccess] = None


# Forward reference будет разрешен после импорта card schemas
class ModuleWithCards(Module):
    cards: List["Card"] = []


# Импортируем Card после определения классов чтобы избежать циклического импорта
from .card import Card  # noqa: E402

ModuleWithCards.model_rebuild()
