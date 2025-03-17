from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...services.user_service import UserService
from ...schemas import UserProfile, UserUpdate
from ...models import User
from ..deps import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    user_service = UserService(db)
    return user_service.get_user_profile(current_user.id)

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user profile by ID."""
    user_service = UserService(db)
    return user_service.get_user_profile(user_id)

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    user_service = UserService(db)
    if user_update.preferences:
        user_service.update_user_preferences(current_user.id, user_update.preferences)
    return user_service.get_user_profile(current_user.id)

@router.post("/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user."""
    user_service = UserService(db)
    if user_service.follow_user(current_user.id, user_id):
        return {"message": "Successfully followed user"}
    return {"message": "Already following user"}

@router.post("/{user_id}/unfollow")
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user."""
    user_service = UserService(db)
    if user_service.unfollow_user(current_user.id, user_id):
        return {"message": "Successfully unfollowed user"}
    return {"message": "Not following user"} 