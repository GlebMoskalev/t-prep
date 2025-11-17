from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    password_hash = Column(String, nulable=True)

    # Relationships
    owner = relationship("User", back_populates="modules")
    cards = relationship("Card", back_populates="module", cascade="all, delete-orphan")
    access = relationship("ModuleAccess", back_populates="module", cascade="all, delete-orphan")
    edit_access = relationship("EditAccess", back_populates="module", cascade="all, delete-orphan")
    view_access = relationship("ViewAccess", back_populates="module", cascade="all, delete-orphan")