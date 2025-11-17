from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.database import get_db
from ...models.user import User
from ...schemas.user import User as UserSchema, UserUpdate
from ...core.deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    user = current_user
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_Not_Found,
            detail=f"UserNotFound"
        )
        
    return user


@router.put("/users", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user
