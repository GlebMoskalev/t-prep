from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, asc
from fsrs import Scheduler, Card, Rating, State
import random
from ..models.interval_repetition import IntervalRepetition, RepetitionState
from ..models.card import Card as DBCard
from dataclasses import dataclass
from typing import List


@dataclass
class UpdateCardIntervalRepetitionRequest:
    TimeOfAnswer: datetime
    RightAnswer: bool

@dataclass
class CardResponse:
    Id: str
    Question: str
    AnswerVariant: List[str]
    RightAnswer: int

@dataclass
class GetInternalRepetitionCardResponse:
    Items: List[CardResponse]
    TotalCount: int


class RepetitionService:
    def __init__(self, db: Session, fsrs_optimizer=None):
        """
        Инициализация сервиса интервальных повторений.
        
        Args:
            db: Сессия SQLAlchemy
            fsrs_optimizer: Оптимизатор FSRS (опционально)
        """
        self.db = db
        self.fsrs = Scheduler()
        
    def enable_interval_repetitions(self, user_id: int, module_id: int) -> None:
        existing = self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.user_id == user_id,
                IntervalRepetition.module_id == module_id
            )
        ).first()
        
        if existing:
            return

        module_cards = self.db.query(DBCard).filter(
            DBCard.module_id == module_id,
        ).all()
        
        if not module_cards:
            return

        now = datetime.now()
        repetitions = []
        for card in module_cards:
            fsrs_card = Card()

            repetition = IntervalRepetition(
                user_id=user_id,
                module_id=int(module_id),
                card_id=card.id,
                state=self._get_repetition_state(fsrs_card.state),
                step=0,
                stability=fsrs_card.stability,
                difficulty=fsrs_card.difficulty,
                due=now,
                last_review=None
            )
            repetitions.append(repetition)
        
        self.db.bulk_save_objects(repetitions)  # ← Массовая вставка)
        self.db.commit()
        
    def disable_interval_repetitions(self, user_id: int, module_id: int) -> None:
        """
        Отключить интервальные повторения для модуля пользователя.
        
        Args:
            user_id: ID пользователя
            module_id: ID модуля
        """
        # Удаляем все записи о повторениях для этого модуля и пользователя
        self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.user_id == user_id,
                IntervalRepetition.module_id == module_id
            )
        ).delete()
        
        self.db.commit()
        
    def update_card_status(
        self,
        user_id: int,
        module_id: int,
        card_id: int,
        request: UpdateCardIntervalRepetitionRequest
    ) -> Dict[str, Any]:
        """
        Обновить статус карточки для интервального повторения.
        
        Args:
            user_id: ID пользователя
            module_id: ID модуля
            card_id: ID карточки
            request: Данные об ответе
            
        Returns:
            Обновленная информация о карточке
        """
        # Находим запись о повторении
        repetition = self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.user_id == user_id,
                IntervalRepetition.module_id == module_id,
                IntervalRepetition.card_id == card_id
            )
        ).first()
        
        if not repetition:
            raise ValueError("Card not found in interval repetitions")
    
        print('Ok')
        fsrs_card = self._deserialize_fsrs_card(repetition)
        print('Ok')
    
        rating = Rating.Good if request.RightAnswer else Rating.Again

        print('Ok')
        updated_fsrs_card = self.fsrs.review_card(fsrs_card, rating=rating, review_datetime=request.TimeOfAnswer.astimezone(timezone.utc))[0]
        print('ok')
        
        # Обновление записи в БД
        repetition.state = self._get_repetition_state(updated_fsrs_card.state)
        repetition.step = repetition.step + 1
        repetition.stability = updated_fsrs_card.stability
        repetition.difficulty = updated_fsrs_card.difficulty
        repetition.due = updated_fsrs_card.due
        repetition.last_review = request.TimeOfAnswer.astimezone(timezone.utc)
        repetition.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        
        return {
            "due_date": repetition.due,
            "status": repetition.state,
            "interval": updated_fsrs_card,
            "stability": repetition.stability,
            "difficulty": repetition.difficulty
        }
    
    def get_cards_for_repetition(
        self,
        user_id: int,
        module_id: int,
        skip: int = 0,
        take: int = 10,
        due_only: bool = False
    ) -> GetInternalRepetitionCardResponse:
        """
        Получить карточки для интервального повторения.
        
        Args:
            user_id: ID пользователя
            module_id: ID модуля
            skip: Число пропускаемых карточек
            take: Число взятых карточек
            due_only: Только карточки, готовые к повторению
            
        Returns:
            Ответ с карточками и общим количеством
        """
        # Явно используем DBCard для модели БД
        query = self.db.query(IntervalRepetition).filter(
            IntervalRepetition.user_id == user_id,
            IntervalRepetition.module_id == module_id
        )

        # Если нужны только готовые к повторению карточки
        if due_only:
            now = datetime.now()
            query = query.filter(IntervalRepetition.due <= now)
        
        # Получаем общее количество
        total_count = query.count()
        
        # Применяем сортировку и пагинацию
        # Сортируем по due_date (чем раньше должна быть повторена, тем выше)
        items = query.order_by(asc(IntervalRepetition.due))\
                    .offset(skip)\
                    .limit(take)\
                    .all()
        
        # Извлекаем только карточки из результатов
        all_cards = [card.card for card in items]
        
        # Конвертируем в ответ - здесь нужно использовать CardSchema
        card_responses = self._cardsdb_to_cards(all_cards)
        
        return GetInternalRepetitionCardResponse(
            Items=card_responses,
            TotalCount=total_count
        )

    def _cardsdb_to_cards(self, cardsdb: List[DBCard]) -> List[CardResponse]:
        all_answers = [card.answer for card in cardsdb]
        result = []
        for card in sorted(cardsdb, key=lambda x: x.id):
            ans, id = self._get_three_answer(all_answers, card.answer)
            result.append(CardResponse(Id=str(card.id),
                                    Question=card.question,
                                    AnswerVariant=ans,
                                    RightAnswer=id))
            
        return result

    def _get_three_answer(self, answers: List[str], right_answer: str):
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

    def _get_repetition_state(self, fsrs_state: State) -> RepetitionState:
        """Преобразовать состояние FSRS в RepetitionState."""
        state_mapping = {
            State.Learning: RepetitionState.Learning,
            State.Review: RepetitionState.Review,
            State.Relearning: RepetitionState.Relearning,
        }
        return state_mapping.get(fsrs_state, RepetitionState.Learning)

    def _get_fsrs_state(self, repetition_state: RepetitionState) -> State:
        """Преобразовать RepetitionState в состояние FSRS."""
        state_mapping = {
            RepetitionState.Learning: State.Learning,
            RepetitionState.Review: State.Review,
            RepetitionState.Relearning: State.Relearning,
        }
        return state_mapping.get(repetition_state)
    
    def _serialize_fsrs_card(self, fsrs_card: Card) -> Dict[str, Any]:
        return {
            "due": fsrs_card.due if fsrs_card.due else None,
            "stability": fsrs_card.stability,
            "difficulty": fsrs_card.difficulty,
            "state": fsrs_card.state.value,
            "last_review": fsrs_card.last_review if fsrs_card.last_review else None,
        }

    def _deserialize_fsrs_card(self, data: IntervalRepetition) -> Card:
        """Десериализовать FSRS карточку из JSON."""
        fsrs_card = Card()
        
        if data.due:
            fsrs_card.due = data.due
        fsrs_card.stability = data.stability
        fsrs_card.difficulty = data.difficulty
        fsrs_card.state = self._get_fsrs_state(data.state)
        if data.last_review:
            fsrs_card.last_review = data.last_review
    
        return fsrs_card