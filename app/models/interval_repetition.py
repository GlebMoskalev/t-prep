from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base


class RepetitionState(str, enum.Enum):
    Learning = "Learning"
    Review = "Review"
    Relearning = "Relearning"


class IntervalRepetition(Base):
    __tablename__ = "interval_repetitions"

    id = Column(Integer, Sequence('interval_repetitions_id_seq'), primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    state = Column(Enum(RepetitionState), nullable=False, default=RepetitionState.Learning)
    step = Column(Integer, nullable=False, default=0)
    stability = Column(Float, nullable=False, default=0.5)
    difficulty = Column(Float, nullable=False, default=0.3)
    due = Column(DateTime(timezone=True), nullable=False)
    last_review = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    card = relationship("Card", back_populates="repetitions")
    user = relationship("User", back_populates="repetitions")
    module = relationship("Module", back_populates="repetitions")
