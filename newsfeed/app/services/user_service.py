from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from ..core.config import settings
from ..models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, password: str, full_name: str = None) -> User:
        """Create a new user."""
        try:
            user = User(
                username=username,
                email=email,
                hashed_password=self._get_password_hash(password),
                full_name=full_name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user and return user object if valid."""
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not self._verify_password(password, user.hashed_password):
            return None
        return user

    def follow_user(self, follower_id: int, followed_id: int) -> bool:
        """Make one user follow another."""
        if follower_id == followed_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users cannot follow themselves"
            )

        follower = self.db.query(User).filter(User.id == follower_id).first()
        followed = self.db.query(User).filter(User.id == followed_id).first()

        if not follower or not followed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if followed in follower.following:
            return False  # Already following

        follower.following.append(followed)
        self.db.commit()
        return True

    def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        """Make one user unfollow another."""
        follower = self.db.query(User).filter(User.id == follower_id).first()
        followed = self.db.query(User).filter(User.id == followed_id).first()

        if not follower or not followed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if followed not in follower.following:
            return False  # Not following

        follower.following.remove(followed)
        self.db.commit()
        return True

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile with following/follower counts."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "followers_count": len(user.followers),
            "following_count": len(user.following),
            "posts_count": len(user.posts),
            "created_at": user.created_at.isoformat()
        }

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> User:
        """Update user preferences."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.preferences.update(preferences)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_access_token(self, user: User) -> str:
        """Create JWT access token for user."""
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "exp": expire
        }
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

    def _get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password) 