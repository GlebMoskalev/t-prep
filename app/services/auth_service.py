from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..core.config import settings
from ..core.security import create_access_token
from ..models.user import User
from ..schemas.user import Token, UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, oidc_sub: str) -> Optional[User]:
        """Authenticate user by oidc_sub"""
        user = self.db.query(User).filter(User.oidc_sub == oidc_sub).first()
        return user

    def create_user_from_oidc(self, name: str, oidc_sub: str) -> User:
        """Create new user from OIDC data"""
        user_data = UserCreate(
            name=name,
            oidc_sub=oidc_sub
        )
        
        db_user = User(
            name=user_data.name,
            oidc_sub=user_data.oidc_sub
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def get_or_create_user(self, name: str, oidc_sub: str) -> User:
        """Get existing user or create new one from OIDC"""
        user = self.db.query(User).filter(User.oidc_sub == oidc_sub).first()
        
        if user:
            return user
        
        return self.create_user_from_oidc(name, oidc_sub)

    def create_access_token_for_user(self, user: User) -> Token:
        """Create JWT access token for user"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            subject=user.oidc_sub, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return oidc_sub"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            oidc_sub: str = payload.get("sub")
            if oidc_sub is None:
                return None
            return oidc_sub
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        oidc_sub = self.verify_token(token)
        if oidc_sub is None:
            return None
        
        user = self.db.query(User).filter(User.oidc_sub == oidc_sub).first()
        return user
