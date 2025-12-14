from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Tuple
from ...db.database import get_db
from ...models.user import User
from ...models.module import Module
from ...models.card import Card
from ...schemas.card import Card as CardSchema, CreateCardRequest, PatchCardRequest, GetCardResponse, CardInDB
from ...core.deps import get_current_active_user
import random

router = APIRouter()


@router.get("/", response_model=GetCardResponse)
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
    
    correct_cards = cardsdb_to_cards(cards)

    return GetCardResponse(
        items=correct_cards[skip:max(skip+take, len(correct_cards))],
        total_count=min(take, len(correct_cards) - skip)
    )

def cardsdb_to_cards(cardsdb: List[Card]) -> List[CardSchema]:
    all_answers = [card.answer for card in cardsdb]
    result = []
    for card in sorted(cardsdb, key=lambda x: x.id):
        ans, id = get_three_answer(all_answers, card.answer)
        result.append(CardSchema(id=str(card.id),
                                 question=card.question,
                                 answer_variant=ans,
                                 right_answer=id))
        
    return result

def get_three_answer(answers: List[str], right_answer: str):
    i = 0
    result = []
    for answer in random.sample(answers, len(answers)):
        result.append(answer)
        i += 1
        if i == 4:
            break
        
    if right_answer in result:
        return result, result.index(right_answer)
    
    result.pop()
    result.insert(len(result) // 2, answer)
    return result, (len(result) // 2)


@router.post("/", response_model=CardInDB)
async def create_card(
    module_id: int,
    card: CreateCardRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new card"""
    # Check if user owns the module
    module = db.query(Module).filter(
        Module.id == module_id,
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
        module_id=module_id
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    return db_card


@router.get("/{card_id}", response_model=CardInDB)
async def get_card(
    module_id: int,
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get card by ID"""
    card = db.query(Card).join(Module).filter(
        Card.id == card_id,
        Module.owner_id == current_user.id,
        Module.id == module_id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )

    return card


@router.patch("/{card_id}", response_model=CardInDB)
async def update_card(
    module_id: int,
    card_id: int,
    card_update: PatchCardRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update card"""
    card = db.query(Card).join(Module).filter(
        Card.id == card_id,
        Module.owner_id == current_user.id,
        Module.id == module_id
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
    module_id: int,
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete card"""
    card = db.query(Card).join(Module).filter(
        Card.id == card_id,
        Module.owner_id == current_user.id,
        Module.id == module_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    db.delete(card)
    db.commit()

    return {"message": "Card deleted successfully"}
