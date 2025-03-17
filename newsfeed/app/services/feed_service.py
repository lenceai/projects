from datetime import datetime, timedelta
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..core.config import settings
from ..core.database import get_redis
from ..models import User, Content, FeedItem

class FeedService:
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis()
        
    async def get_user_feed(self, user_id: int, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """Get a user's feed items with pagination."""
        # Try to get from cache first
        cache_key = f"feed:{user_id}:page:{page}"
        cached_feed = self.redis.get(cache_key)
        
        if cached_feed:
            return json.loads(cached_feed)
            
        # If not in cache, generate from database
        offset = (page - 1) * page_size
        feed_items = (
            self.db.query(FeedItem)
            .filter(FeedItem.user_id == user_id, FeedItem.hidden == False)
            .order_by(desc(FeedItem.score), desc(FeedItem.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        # Convert to dictionary and include content details
        feed_data = []
        for item in feed_items:
            content = item.content
            feed_data.append({
                "id": item.id,
                "content_id": content.id,
                "content_type": content.content_type.value,
                "title": content.title,
                "content": content.content,
                "creator": content.creator.username,
                "score": item.score,
                "created_at": content.created_at.isoformat(),
                "engagement": {
                    "likes": content.likes_count,
                    "comments": content.comments_count,
                    "shares": content.shares_count
                }
            })
            
        # Cache the results
        self.redis.setex(
            cache_key,
            settings.FEED_CACHE_TTL,
            json.dumps(feed_data)
        )
        
        return feed_data
    
    async def fan_out_post(self, content_id: int, creator_id: int) -> None:
        """Fan out a new post to followers' feeds using hybrid approach."""
        # Get content creator's follower count
        creator = self.db.query(User).filter(User.id == creator_id).first()
        follower_count = len(creator.followers)
        
        # Decide on push vs pull strategy
        if follower_count <= settings.MAX_FANOUT_FOLLOWERS:
            await self._push_to_followers(content_id, creator_id)
        else:
            await self._mark_for_pull(content_id, creator_id)
    
    async def _push_to_followers(self, content_id: int, creator_id: int) -> None:
        """Push content to followers' feeds."""
        creator = self.db.query(User).filter(User.id == creator_id).first()
        content = self.db.query(Content).filter(Content.id == content_id).first()
        
        # Calculate base score for the content
        base_score = self._calculate_content_score(content)
        
        # Process followers in batches
        for i in range(0, len(creator.followers), settings.FANOUT_BATCH_SIZE):
            batch = creator.followers[i:i + settings.FANOUT_BATCH_SIZE]
            feed_items = []
            
            for follower in batch:
                # Create feed item
                feed_item = FeedItem(
                    user_id=follower.id,
                    content_id=content_id,
                    score=self._adjust_score_for_user(base_score, follower.id, creator_id)
                )
                feed_items.append(feed_item)
                
                # Invalidate follower's feed cache
                self._invalidate_user_feed_cache(follower.id)
            
            # Bulk insert feed items
            self.db.bulk_save_objects(feed_items)
            self.db.commit()
    
    async def _mark_for_pull(self, content_id: int, creator_id: int) -> None:
        """Mark content for pull-based delivery."""
        key = f"pull:content:{content_id}"
        self.redis.setex(
            key,
            timedelta(days=7),  # Keep for 7 days
            json.dumps({
                "creator_id": creator_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    
    def _calculate_content_score(self, content: Content) -> float:
        """Calculate content relevance score."""
        # Base time decay
        age_hours = (datetime.utcnow() - content.created_at).total_seconds() / 3600
        time_decay = 1 / (1 + age_hours/24)  # Decay over 24 hours
        
        # Engagement score
        engagement_score = (
            content.likes_count * 1.0 +
            content.comments_count * 2.0 +
            content.shares_count * 3.0
        )
        
        # Combine scores
        return (0.7 * time_decay + 0.3 * engagement_score)
    
    def _adjust_score_for_user(self, base_score: float, user_id: int, creator_id: int) -> float:
        """Adjust content score based on user-creator relationship."""
        # Get interaction history between user and creator
        interaction_score = self._get_interaction_score(user_id, creator_id)
        
        # Combine scores with weights
        return (0.8 * base_score + 0.2 * interaction_score)
    
    def _get_interaction_score(self, user_id: int, creator_id: int) -> float:
        """Calculate interaction score between user and creator."""
        # This would typically look at:
        # - Frequency of interactions
        # - Recency of interactions
        # - Types of interactions (likes, comments, shares)
        # For now, return a simple placeholder score
        return 1.0
    
    def _invalidate_user_feed_cache(self, user_id: int) -> None:
        """Invalidate all cached feed pages for a user."""
        pattern = f"feed:{user_id}:page:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys) 