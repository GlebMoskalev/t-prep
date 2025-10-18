from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import HTTPException, status
from ..core.config import settings
from ..core.security import create_access_token
from ..models.user import User
from ..schemas.user import Token, UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, google_id: Optional[str] = None) -> Optional[User]:
        """Authenticate user by email and optionally google_id"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if google_id and user.google_id != google_id:
            return None
            
        return user

    def create_user_from_google(self, email: str, name: str, google_id: str) -> User:
        """Create new user from Google OAuth data"""
        user_data = UserCreate(
            name=name,
            email=email,
            google_id=google_id
        )
        
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            google_id=user_data.google_id,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def get_or_create_user(self, email: str, name: str, google_id: str) -> User:
        """Get existing user or create new one from Google OAuth"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if user:
            # Update google_id if not set
            if not user.google_id:
                user.google_id = google_id
                self.db.commit()
                self.db.refresh(user)
            return user
        
        return self.create_user_from_google(email, name, google_id)

    def create_access_token_for_user(self, user: User) -> Token:
        """Create JWT access token for user"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return email"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        email = self.verify_token(token)
        if email is None:
            return None
        
        user = self.db.query(User).filter(User.email == email).first()
        return user
