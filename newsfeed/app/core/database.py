from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import redis
from typing import Generator

from .config import settings
from ..models.base import Base

# PostgreSQL setup
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

# MongoDB setup
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
mongodb = mongo_client[settings.MONGODB_DB]

def init_db() -> None:
    """Initialize the database with all models."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis() -> redis.Redis:
    """Get Redis client."""
    return redis_client

def get_mongodb():
    """Get MongoDB database."""
    return mongodb 