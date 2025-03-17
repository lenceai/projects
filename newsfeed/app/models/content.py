from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base, TimestampMixin

class ContentType(enum.Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"

class Content(Base, TimestampMixin):
    __tablename__ = 'content'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    title = Column(String(200))
    content = Column(String)  # For text content or media URLs
    metadata = Column(JSON, default={})  # For storing tags, location, etc.
    
    # Relationships
    creator = relationship('User', back_populates='posts')
    feed_items = relationship('FeedItem', back_populates='content')
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Content {self.id} by User {self.user_id}>"

    def increment_engagement(self, engagement_type: str):
        """Increment engagement metrics."""
        if engagement_type == 'like':
            self.likes_count += 1
        elif engagement_type == 'comment':
            self.comments_count += 1
        elif engagement_type == 'share':
            self.shares_count += 1 