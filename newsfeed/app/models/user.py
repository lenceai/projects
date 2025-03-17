from typing import List, Optional
from sqlalchemy import Column, Integer, String, JSON, Table, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

# Association table for user followers
followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    preferences = Column(JSON, default={})
    is_active = Column(Boolean, default=True)

    # Relationships
    followers = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        backref='following'
    )

    # Content created by the user
    posts = relationship('Content', back_populates='creator')

    # Feed items for this user
    feed_items = relationship('FeedItem', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>" 