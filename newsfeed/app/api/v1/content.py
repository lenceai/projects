from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...services.content_service import ContentService
from ...schemas import ContentCreate, ContentResponse, ContentUpdate, ContentEngagement
from ...models import User, ContentType
from ..deps import get_current_active_user

router = APIRouter()

@router.post("", response_model=ContentResponse)
async def create_post(
    content_in: ContentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post."""
    content_service = ContentService(db)
    try:
        content_type = ContentType[content_in.content_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type. Must be one of: {[t.value for t in ContentType]}"
        )
    
    post = await content_service.create_post(
        user_id=current_user.id,
        content_type=content_type,
        content=content_in.content,
        title=content_in.title,
        metadata=content_in.metadata
    )
    return post

@router.get("", response_model=List[ContentResponse])
async def get_posts(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Get posts by user ID."""
    content_service = ContentService(db)
    return content_service.get_user_posts(user_id, page, page_size)

@router.get("/{post_id}", response_model=ContentResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get a post by ID."""
    content_service = ContentService(db)
    return content_service.get_post(post_id)

@router.put("/{post_id}", response_model=ContentResponse)
async def update_post(
    post_id: int,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post."""
    content_service = ContentService(db)
    return await content_service.update_post(
        post_id=post_id,
        user_id=current_user.id,
        updates=content_update.dict(exclude_unset=True)
    )

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post."""
    content_service = ContentService(db)
    if await content_service.delete_post(post_id, current_user.id):
        return {"message": "Post deleted successfully"}
    return {"message": "Failed to delete post"}

@router.post("/{post_id}/engage", response_model=ContentResponse)
async def engage_with_post(
    post_id: int,
    engagement: ContentEngagement,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Engage with a post (like, comment, share)."""
    content_service = ContentService(db)
    return await content_service.engage_with_post(
        post_id=post_id,
        user_id=current_user.id,
        engagement_type=engagement.engagement_type
    ) 