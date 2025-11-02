from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ...db.database import get_db
from ...models.user import User
from ...models.card import Card
from ...models.interval_repetition import IntervalRepetition, RepetitionState
from ...schemas.interval_repetition import IntervalRepetition as RepetitionSchema
from ...core.deps import get_current_active_user
from ...services.repetition_service import RepetitionService

router = APIRouter()


class AnswerRequest(BaseModel):
    """Запрос для отправки ответа на карточку"""
    is_correct: bool


class RepetitionWithCard(BaseModel):
    """Повторение с информацией о карточке"""
    id: int
    card_id: int
    user_id: int
    state: str
    step: int
    stability: float
    difficulty: float
    due: datetime
    last_review: datetime | None
    question: str
    answer: str
    module_id: int
    
    class Config:
        from_attributes = True


class UserStatistics(BaseModel):
    """Статистика пользователя по повторениям"""
    total_cards: int
    learning: int
    review: int
    relearning: int
    due_today: int
    overdue: int


@router.post("/card/{card_id}/start", response_model=RepetitionSchema)
async def start_card_repetition(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Начать повторение карточки (создать запись IntervalRepetition).
    Если запись уже существует, вернуть её.
    """
    # Проверяем, что карточка существует и доступна пользователю
    card = db.query(Card).join(Card.module).filter(
        Card.id == card_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Создаем или получаем повторение
    service = RepetitionService(db)
    repetition = service.create_repetition(card_id, current_user.id)
    
    return repetition


@router.post("/card/{card_id}/answer", response_model=RepetitionSchema)
async def answer_card(
    card_id: int,
    answer: AnswerRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Отправить ответ на карточку.
    Обновляет параметры интервального повторения на основе правильности ответа.
    """
    service = RepetitionService(db)
    
    # Получаем запись повторения
    repetition = service.get_repetition_by_card_and_user(card_id, current_user.id)
    
    if not repetition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repetition not found. Start the card first."
        )
    
    # Обновляем повторение на основе ответа
    updated_repetition = service.update_repetition_on_answer(
        repetition.id, 
        answer.is_correct
    )
    
    return updated_repetition


@router.get("/due", response_model=List[RepetitionWithCard])
async def get_due_cards(
    hours_ahead: float = 12.0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить карточки, которые нужно повторить в ближайшие N часов.
    По умолчанию - 12 часов.
    """
    service = RepetitionService(db)
    repetitions = service.get_due_cards_for_user(current_user.id, hours_ahead)
    
    # Обогащаем данными карточек
    result = []
    for rep in repetitions:
        card = db.query(Card).filter(Card.id == rep.card_id).first()
        if card:
            result.append(RepetitionWithCard(
                id=rep.id,
                card_id=rep.card_id,
                user_id=rep.user_id,
                state=rep.state.value,
                step=rep.step,
                stability=rep.stability,
                difficulty=rep.difficulty,
                due=rep.due,
                last_review=rep.last_review,
                question=card.question,
                answer=card.answer,
                module_id=card.module_id
            ))
    
    return result


@router.get("/overdue", response_model=List[RepetitionWithCard])
async def get_overdue_cards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить просроченные карточки (due < now).
    """
    service = RepetitionService(db)
    repetitions = service.get_overdue_cards_for_user(current_user.id)
    
    # Обогащаем данными карточек
    result = []
    for rep in repetitions:
        card = db.query(Card).filter(Card.id == rep.card_id).first()
        if card:
            result.append(RepetitionWithCard(
                id=rep.id,
                card_id=rep.card_id,
                user_id=rep.user_id,
                state=rep.state.value,
                step=rep.step,
                stability=rep.stability,
                difficulty=rep.difficulty,
                due=rep.due,
                last_review=rep.last_review,
                question=card.question,
                answer=card.answer,
                module_id=card.module_id
            ))
    
    return result


@router.get("/statistics", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику по повторениям текущего пользователя.
    """
    service = RepetitionService(db)
    stats = service.get_user_statistics(current_user.id)
    
    return UserStatistics(**stats)


@router.post("/module/{module_id}/initialize", response_model=List[RepetitionSchema])
async def initialize_module_repetitions(
    module_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Инициализировать интервальные повторения для всех карточек модуля.
    Создает записи для карточек, у которых их еще нет.
    """
    # Проверяем доступ к модулю
    from ...models.module import Module
    module = db.query(Module).filter(
        Module.id == module_id
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    service = RepetitionService(db)
    repetitions = service.initialize_user_cards(current_user.id, module_id)
    
    return repetitions


@router.get("/card/{card_id}", response_model=RepetitionSchema)
async def get_card_repetition(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить информацию о повторении конкретной карточки.
    """
    service = RepetitionService(db)
    repetition = service.get_repetition_by_card_and_user(card_id, current_user.id)
    
    if not repetition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repetition not found for this card"
        )
    
    return repetition

