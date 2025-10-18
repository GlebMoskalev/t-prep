from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base


class RepetitionState(str, enum.Enum):
    LEARNING = "Learning"
    REVIEW = "Review"
    RELEARNING = "Relearning"


class IntervalRepetition(Base):
    __tablename__ = "interval_repetitions"

    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state = Column(Enum(RepetitionState), nullable=False, default=RepetitionState.LEARNING)
    step = Column(Integer, nullable=False, default=0)
    stability = Column(Float, nullable=False, default=2.5)
    difficulty = Column(Float, nullable=False, default=5.0)
    due = Column(DateTime(timezone=True), nullable=False)
    last_review = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    card = relationship("Card", back_populates="interval_repetitions")
    user = relationship("User", back_populates="interval_repetitions")
