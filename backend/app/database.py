# Save this as backend/app/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- 1. Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables.")

# Create the engine
engine = create_engine(DATABASE_URL)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model definitions
Base = declarative_base()


# --- 2. Database Model Definition ---
class Conversation(Base):
    """
    Database model to store each turn of the conversation.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    role = Column(String(10), nullable=False)       # 'user' or 'ai'
    prompt_text = Column(Text, nullable=False)     # The user's input OR AI's response text
    
    # URL of the generated image (only set for 'ai' role)
    generated_image_url = Column(String(512), nullable=True) 
    
    # The final prompt sent to the external AI (useful for debugging)
    engineered_prompt = Column(Text, nullable=True) 

# --- 3. Database Utility ---
# Function to get a database session (Dependency for FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()