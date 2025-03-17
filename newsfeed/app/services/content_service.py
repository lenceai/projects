from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import Content, ContentType, User
from .feed_service import FeedService

class ContentService:
    def __init__(self, db: Session):
        self.db = db
        self.feed_service = FeedService(db)

    async def create_post(
        self,
        user_id: int,
        content_type: ContentType,
        content: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Content:
        """Create a new post."""
        # Validate user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Create content
        post = Content(
            user_id=user_id,
            content_type=content_type,
            content=content,
            title=title,
            metadata=metadata or {}
        )
        
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        # Fan out to followers
        await self.feed_service.fan_out_post(post.id, user_id)

        return post

    def get_user_posts(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> List[Dict[str, Any]]:
        """Get posts created by a user with pagination."""
        offset = (page - 1) * page_size
        posts = (
            self.db.query(Content)
            .filter(Content.user_id == user_id)
            .order_by(Content.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return [self._format_post(post) for post in posts]

    def get_post(self, post_id: int) -> Dict[str, Any]:
        """Get a single post by ID."""
        post = self.db.query(Content).filter(Content.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        return self._format_post(post)

    async def update_post(
        self,
        post_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Content:
        """Update a post."""
        post = self.db.query(Content).filter(
            Content.id == post_id,
            Content.user_id == user_id
        ).first()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or unauthorized"
            )

        # Update allowed fields
        allowed_fields = {"title", "content", "metadata"}
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(post, field, value)

        post.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(post)

        return post

    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete a post."""
        post = self.db.query(Content).filter(
            Content.id == post_id,
            Content.user_id == user_id
        ).first()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or unauthorized"
            )

        # Delete associated feed items
        self.db.query(FeedItem).filter(FeedItem.content_id == post_id).delete()
        
        # Delete the post
        self.db.delete(post)
        self.db.commit()

        return True

    async def engage_with_post(
        self,
        post_id: int,
        user_id: int,
        engagement_type: str
    ) -> Dict[str, Any]:
        """Handle post engagement (like, comment, share)."""
        post = self.db.query(Content).filter(Content.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Update engagement metrics
        post.increment_engagement(engagement_type)
        self.db.commit()
        self.db.refresh(post)

        # Update feed item scores for this post
        await self._update_feed_item_scores(post)

        return self._format_post(post)

    async def _update_feed_item_scores(self, post: Content) -> None:
        """Update feed item scores when engagement changes."""
        feed_items = self.db.query(FeedItem).filter(FeedItem.content_id == post.id).all()
        
        for item in feed_items:
            # Recalculate score
            base_score = self.feed_service._calculate_content_score(post)
            item.score = self.feed_service._adjust_score_for_user(
                base_score,
                item.user_id,
                post.user_id
            )
            
            # Invalidate cache for affected users
            self.feed_service._invalidate_user_feed_cache(item.user_id)

        self.db.commit()

    def _format_post(self, post: Content) -> Dict[str, Any]:
        """Format a post for API response."""
        return {
            "id": post.id,
            "creator": {
                "id": post.creator.id,
                "username": post.creator.username
            },
            "content_type": post.content_type.value,
            "title": post.title,
            "content": post.content,
            "metadata": post.metadata,
            "engagement": {
                "likes": post.likes_count,
                "comments": post.comments_count,
                "shares": post.shares_count
            },
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat()
        } 