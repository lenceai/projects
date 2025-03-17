from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...services.feed_service import FeedService
from ...schemas import FeedResponse, FeedItem
from ...models import User
from ..deps import get_current_active_user

router = APIRouter()

@router.get("", response_model=FeedResponse)
async def get_feed(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's feed."""
    feed_service = FeedService(db)
    items = await feed_service.get_user_feed(current_user.id, page, page_size)
    
    # Get total items count for pagination
    total_items = len(items)  # This should be replaced with actual count from database
    total_pages = (total_items + page_size - 1) // page_size
    
    return FeedResponse(
        items=items,
        page=page,
        total_pages=total_pages,
        total_items=total_items
    )

@router.post("/{feed_item_id}/hide")
async def hide_feed_item(
    feed_item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Hide a feed item."""
    feed_item = db.query(FeedItem).filter(
        FeedItem.id == feed_item_id,
        FeedItem.user_id == current_user.id
    ).first()
    
    if not feed_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed item not found"
        )
    
    feed_item.hidden = True
    db.commit()
    return {"message": "Feed item hidden successfully"}

@router.post("/{feed_item_id}/mark-seen")
async def mark_feed_item_seen(
    feed_item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a feed item as seen."""
    feed_item = db.query(FeedItem).filter(
        FeedItem.id == feed_item_id,
        FeedItem.user_id == current_user.id
    ).first()
    
    if not feed_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed item not found"
        )
    
    feed_item.seen = True
    db.commit()
    return {"message": "Feed item marked as seen"} 