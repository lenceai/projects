import os
from sqlalchemy import create_engine
from models.base import Base
from models.models import User, Driver, Trip
from dotenv import load_dotenv

load_dotenv()

def init_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 