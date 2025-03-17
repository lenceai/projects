from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(BigInteger, primary_key=True, index=True)
    original_url = Column(String, index=True)
    short_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    click_count = Column(Integer, default=0) 