from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    oidc_sub: str


class UserUpdate(BaseModel):
    name: Optional[str] = None


class User(UserBase):
    id: int
    oidc_sub: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    oidc_sub: Optional[str] = None
