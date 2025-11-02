from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.interval_repetition import IntervalRepetition, RepetitionState
from ..models.card import Card
from ..models.user import User
import math


class RepetitionService:
    """Сервис для работы с интервальными повторениями (SFRS-подобный алгоритм)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_repetition(self, card_id: int, user_id: int) -> IntervalRepetition:
        """
        Создать новую запись интервального повторения для карточки и пользователя.
        Начальные параметры согласно ТЗ:
        - state = Learning
        - step = 0
        - stability = 0.5
        - difficulty = 0.3
        - due = now + 20 минут
        """
        # Проверяем, существует ли уже запись
        existing = self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.card_id == card_id,
                IntervalRepetition.user_id == user_id
            )
        ).first()
        
        if existing:
            return existing
        
        now = datetime.now()
        repetition = IntervalRepetition(
            card_id=card_id,
            user_id=user_id,
            state=RepetitionState.Learning,
            step=0,
            stability=0.5,
            difficulty=0.3,
            due=now + timedelta(minutes=20),
            last_review=None
        )
        
        self.db.add(repetition)
        self.db.commit()
        self.db.refresh(repetition)
        
        return repetition
    
    def update_repetition_on_answer(
        self, 
        repetition_id: int, 
        is_correct: bool
    ) -> IntervalRepetition:
        """
        Обновить параметры повторения на основе ответа пользователя.
        
        Если ответ правильный:
        - Увеличить stability
        - Уменьшить difficulty
        - Увеличить step
        - Пересчитать due (экспоненциально: +8ч, +1д, +3д, +7д, +14д, +30д...)
        - Перевести в Review при достаточном количестве правильных ответов
        
        Если ответ неправильный:
        - Уменьшить stability
        - Увеличить difficulty
        - Сбросить step = 0
        - due = now + 10 минут
        - state = Relearning
        """
        repetition = self.db.query(IntervalRepetition).filter(
            IntervalRepetition.id == repetition_id
        ).first()
        
        if not repetition:
            raise ValueError(f"Repetition with id {repetition_id} not found")
        
        now = datetime.now()
        repetition.last_review = now
        
        if is_correct:
            # Правильный ответ
            # Увеличиваем стабильность (максимум 10.0)
            repetition.stability = min(10.0, repetition.stability * 1.3 + 0.1)
            
            # Уменьшаем сложность (минимум 0.1)
            repetition.difficulty = max(0.1, repetition.difficulty - 0.05)
            
            # Увеличиваем шаг
            repetition.step += 1
            
            # Переводим в Review после 3 правильных ответов подряд
            if repetition.state == RepetitionState.Learning and repetition.step >= 3:
                repetition.state = RepetitionState.Review
            elif repetition.state == RepetitionState.Relearning and repetition.step >= 2:
                repetition.state = RepetitionState.Review
            
            # Рассчитываем следующий интервал (экспоненциальный рост)
            interval = self._calculate_next_interval(repetition.step, repetition.stability)
            repetition.due = now + timedelta(hours=interval)
            
        else:
            # Неправильный ответ
            # Уменьшаем стабильность (минимум 0.1)
            repetition.stability = max(0.1, repetition.stability * 0.5)
            
            # Увеличиваем сложность (максимум 1.0)
            repetition.difficulty = min(1.0, repetition.difficulty + 0.1)
            
            # Сбрасываем шаг
            repetition.step = 0
            
            # Переводим в Relearning
            repetition.state = RepetitionState.Relearning
            
            # Устанавливаем короткий интервал
            repetition.due = now + timedelta(minutes=10)
        
        self.db.commit()
        self.db.refresh(repetition)
        
        return repetition
    
    def _calculate_next_interval(self, step: int, stability: float) -> float:
        """
        Рассчитать следующий интервал повторения в часах.
        Интервалы растут экспоненциально с учетом стабильности.
        
        Базовые интервалы:
        - step 0-1: 8 часов
        - step 2: 24 часа (1 день)
        - step 3: 72 часа (3 дня)
        - step 4+: экспоненциальный рост
        """
        # Базовые интервалы для первых шагов
        base_intervals = [8, 8, 24, 72]
        
        if step < len(base_intervals):
            base_interval = base_intervals[step]
        else:
            # Экспоненциальный рост для последующих шагов
            # Формула: 72 * 2^(step - 3)
            base_interval = 72 * (2 ** (step - 3))
        
        # Корректируем интервал на основе стабильности
        # Стабильность влияет как множитель (0.1 - 10.0)
        adjusted_interval = base_interval * (0.5 + stability / 2)
        
        # Ограничиваем максимальный интервал (6 месяцев = 4320 часов)
        return min(adjusted_interval, 4320)
    
    def get_due_cards_for_user(
        self, 
        user_id: int, 
        hours_ahead: float = 12.0
    ) -> List[IntervalRepetition]:
        """
        Получить карточки, которые нужно повторить в ближайшие N часов.
        По умолчанию - 12 часов.
        """
        threshold = datetime.now() + timedelta(hours=hours_ahead)
        
        repetitions = self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.user_id == user_id,
                IntervalRepetition.due <= threshold
            )
        ).order_by(IntervalRepetition.due.asc()).all()
        
        return repetitions
    
    def get_overdue_cards_for_user(self, user_id: int) -> List[IntervalRepetition]:
        """Получить просроченные карточки (due < now)"""
        now = datetime.now()
        
        repetitions = self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.user_id == user_id,
                IntervalRepetition.due < now
            )
        ).order_by(IntervalRepetition.due.asc()).all()
        
        return repetitions
    
    def get_repetition_by_card_and_user(
        self, 
        card_id: int, 
        user_id: int
    ) -> Optional[IntervalRepetition]:
        """Получить запись повторения по card_id и user_id"""
        return self.db.query(IntervalRepetition).filter(
            and_(
                IntervalRepetition.card_id == card_id,
                IntervalRepetition.user_id == user_id
            )
        ).first()
    
    def get_user_statistics(self, user_id: int) -> dict:
        """Получить статистику по повторениям пользователя"""
        all_repetitions = self.db.query(IntervalRepetition).filter(
            IntervalRepetition.user_id == user_id
        ).all()
        
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        stats = {
            "total_cards": len(all_repetitions),
            "learning": sum(1 for r in all_repetitions if r.state == RepetitionState.Learning),
            "review": sum(1 for r in all_repetitions if r.state == RepetitionState.Review),
            "relearning": sum(1 for r in all_repetitions if r.state == RepetitionState.Relearning),
            "due_today": sum(1 for r in all_repetitions if r.due < now + timedelta(days=1)),
            "overdue": sum(1 for r in all_repetitions if r.due < now),
        }
        
        return stats
    
    def initialize_user_cards(self, user_id: int, module_id: int) -> List[IntervalRepetition]:
        """
        Инициализировать интервальные повторения для всех карточек модуля.
        Создает записи для карточек, у которых их еще нет.
        """
        # Получаем все карточки модуля
        cards = self.db.query(Card).filter(Card.module_id == module_id).all()
        
        created_repetitions = []
        
        for card in cards:
            # Проверяем, есть ли уже запись
            existing = self.get_repetition_by_card_and_user(card.id, user_id)
            
            if not existing:
                # Создаем новую запись
                repetition = self.create_repetition(card.id, user_id)
                created_repetitions.append(repetition)
        
        return created_repetitions

