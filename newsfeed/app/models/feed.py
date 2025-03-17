from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class FeedItem(Base, TimestampMixin):
    __tablename__ = 'feed_items'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content_id = Column(Integer, ForeignKey('content.id'), nullable=False)
    score = Column(Float, default=0.0)  # Relevance score for ranking
    seen = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)  # Allow users to hide items
    
    # Relationships
    user = relationship('User', back_populates='feed_items')
    content = relationship('Content', back_populates='feed_items')

    def __repr__(self):
        return f"<FeedItem {self.id} for User {self.user_id}>"

    # Create composite index for efficient feed retrieval
    __table_args__ = (
        Index('idx_user_score', user_id, score.desc()),
        Index('idx_user_content', user_id, content_id, unique=True),
    ) 