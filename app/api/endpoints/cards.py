from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.database import get_db
from ...models.user import User
from ...models.module import Module
from ...models.card import Card
from ...schemas.card import Card as CardSchema, CardCreate, CardUpdate
from ...core.deps import get_current_active_user

router = APIRouter()


@router.get("/{module_id}/cards", response_model=List[CardSchema])
async def get_module_cards(
    module_id: int,
    skip: int = 0,
    take: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.owner_id == current_user.id
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    cards = db.query(Card).filter(Card.module_id == module_id).all()
    return cards


@router.post("/", response_model=CardSchema)
async def create_card(
    card: CardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new card"""
    # Check if user owns the module
    module = db.query(Module).filter(
        Module.id == card.module_id,
        Module.owner_id == current_user.id
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    db_card = Card(
        question=card.question,
        answer=card.answer,
        module_id=card.module_id
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    return db_card


@router.get("/{card_id}", response_model=CardSchema)
async def get_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get card by ID"""
    card = db.query(Card).join(Module).filter(
        Card.id == card_id,
        Module.owner_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return card


@router.put("/{card_id}", response_model=CardSchema)
async def update_card(
    card_id: int,
    card_update: CardUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update card"""
    card = db.query(Card).join(Module).filter(
        Card.id == card_id,
        Module.owner_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    for field, value in card_update.dict(exclude_unset=True).items():
        setattr(card, field, value)
    
    db.commit()
    db.refresh(card)
    
    return card


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete card"""
    card = db.query(Card).join(Module).filter(
        Card.id == card_id,
        Module.owner_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    db.delete(card)
    db.commit()
    
    return {"message": "Card deleted successfully"}
