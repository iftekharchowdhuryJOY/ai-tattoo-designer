# Save this file as backend/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import time
import random
from app.database import Base, SessionLocal, get_db, Conversation
# Note: We will add the Gemini imports (google.genai, os, dotenv) in the next step!


# Utility function to create the database tables
def create_tables():
    from app.database import engine
    # This will create the 'conversations' table if it doesn't already exist
    Base.metadata.create_all(bind=engine)

# Call the function once at startup
create_tables()

app = FastAPI()

# --- Pydantic Model ---
class PromptRequest(BaseModel):
    user_prompt: str

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Existing Test Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Tattoo Designer Backend!"}

@app.get("/api/test")
def test_connection():
    return {"status": "Success", "data": "Backend is running and talking to FastAPI!"}


# --- History Retrieval Endpoint ---
@app.get("/api/history", response_model=List[dict])
def get_chat_history(db: Session = Depends(get_db)):
    """
    Fetches the entire chat history from the database, ordered by timestamp.
    """
    history = db.query(Conversation).order_by(Conversation.timestamp).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "text": msg.prompt_text,
            "image_url": msg.generated_image_url,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in history
    ]

# --- UNIFIED IMAGE GENERATION ENDPOINT ---
@app.post("/api/generate_tattoo")
def generate_tattoo(request: PromptRequest, db: Session = Depends(get_db)):
    prompt = request.user_prompt
    print(f"Received prompt from frontend: {prompt}")

    # 1. --- LOG USER MESSAGE TO DB ---
    user_message = Conversation(
        role='user', 
        prompt_text=prompt, 
        generated_image_url=None, 
        engineered_prompt=None
    )
    db.add(user_message)
    db.commit() 
    db.refresh(user_message)
    
    # --- START OF PLACEHOLDER LOGIC ---
    time.sleep(3) # Simulate AI generation delay

    # 2. --- PLACEHOLDER IMAGE URLS (Fixed UnboundLocalError) ---
    placeholders = [
        "https://via.placeholder.com/400x400/007bff/FFFFFF?text=AI+Concept+Blue", 
        "https://via.placeholder.com/400x400/FF5733/FFFFFF?text=AI+Concept+Orange",
        "https://via.placeholder.com/400x400/33FF57/FFFFFF?text=AI+Concept+Green"
    ]
    
    placeholder_url = random.choice(placeholders)
    ai_response_text = f"Analyzing your request for '{prompt}'... Here is a high-resolution concept design for your tattoo!"
    # --- END OF PLACEHOLDER LOGIC ---
    
    # 3. --- LOG AI RESPONSE TO DB ---
    ai_message = Conversation(
        role='ai', 
        prompt_text=ai_response_text, 
        generated_image_url=placeholder_url, 
        engineered_prompt=f"Technical prompt based on: {prompt}" # Placeholder for real prompt later
    )
    db.add(ai_message)
    db.commit() # Commit the AI response
    db.refresh(ai_message)

    # 4. --- RETURN RESPONSE ---
    return {
        "status": "success",
        "ai_text": ai_response_text,
        "image_url": placeholder_url,
        "engineered_prompt": ai_message.engineered_prompt
    }