from typing import Optional
from sqlalchemy.orm import Session

from ..database.models import User
from ..database.schemas import UserCreate
from .utils import get_password_hash, verify_password


class UserService:
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, username: str, password: str) -> User:
        """Create a new user with hashed password"""
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user