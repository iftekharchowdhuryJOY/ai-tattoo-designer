# Save this as backend/app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker # <-- NEW ASYNC IMPORTS
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base # ORM base remains the same
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# --- 1. Database Setup (MODIFIED FOR ASYNC) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables.")

# CHANGE 1: Use 'postgresql+asyncpg' driver instead of 'postgresql'
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create the ASYNC engine
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Create an ASYNC session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False # Ensures objects can be accessed outside the session block
)

# Base class for model definitions
Base = declarative_base()


# --- 2. Database Model Definition (Model remains the same) ---
class Conversation(Base):
    __tablename__ = "conversations"
    # ... (Model columns remain the same) ...
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    role = Column(String(10), nullable=False)
    prompt_text = Column(Text, nullable=False)
    generated_image_url = Column(String(512), nullable=True) 
    engineered_prompt = Column(Text, nullable=True) 


# --- 3. Database Utility (Async Dependency) ---
# Function to get an asynchronous database session (Dependency for FastAPI)
async def get_db_async(): # <-- FUNCTION IS NOW ASYNCHRONOUS
    async with AsyncSessionLocal() as session:
        yield session