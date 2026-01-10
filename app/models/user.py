from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    oidc_sub = Column(String, unique=True, index=True, nullable=False)
    push_id = Column(String, nullable=True)

    # Relationships
    modules = relationship("Module", back_populates="owner", cascade="all, delete-orphan")
    module_accesses = relationship("ModuleAccess", back_populates="owner", cascade="all, delete-orphan")
    repetitions = relationship("IntervalRepetition", back_populates="user", cascade="all, delete-orphan")
