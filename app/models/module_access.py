from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..db.database import Base
import enum


class AccessLevel(str, enum.Enum):
    ALL_USERS = "all_users"
    USERS_WITH_PASSWORD = "users_with_password"
    ONLY_ME = "only_me"


class ModuleAccess(Base):
    __tablename__ = "module_accesses"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    view_access = Column(Enum(AccessLevel), nullable=False, default=AccessLevel.ONLY_ME)
    edit_access = Column(Enum(AccessLevel), nullable=False, default=AccessLevel.ONLY_ME)
    password_hash = Column(String, nullable=True)

    # Relationships
    module = relationship("Module", back_populates="access")
    owner = relationship("User", back_populates="module_accesses")
