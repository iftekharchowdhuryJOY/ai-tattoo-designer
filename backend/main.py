from fastapi import FastAPI, Depends, HTTPException # <-- Added HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import time 
import random 
from app.database import Base, SessionLocal, get_db, Conversation


# --- NEW REDIS IMPORTS ---
import redis
from redis.exceptions import ConnectionError
import json
import hashlib
import os

# --- NEW GEMINI IMPORTS ---
from google import genai
from google.genai.errors import APIError
import os
from dotenv import load_dotenv

# Load environment variables at the top
load_dotenv() 

# Initialize Gemini Client (Uses GEMINI_API_KEY from .env)
# The client will be initialized once when the application starts
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    client = genai.Client(api_key=GEMINI_API_KEY)
except (ValueError, Exception) as e:
    print(f"Error initializing Gemini client: {e}")
    client = None


try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )
    redis_client.ping()
    print("Redis connection successful")
except ConnectionError as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

# --- NEW HELPER: Prompt Engineering Function ---
# In backend/main.py, replace the existing engineer_prompt function:

# In backend/main.py, replace the existing engineer_prompt function:

# In backend/main.py, modify the engineer_prompt function one last time:
# In backend/main.py, replace the existing engineer_prompt function:

def engineer_prompt(user_input: str) -> str:
    """
    Final prompt version using Aggressive Keyword Overloading and Style Isolation
    to force the output to be a tattoo design on skin.
    """
    # 1. CORE STYLE MODIFIERS (Focusing entirely on the design/illustration)
    # Use repetitive and strong artistic terms
    technical_modifiers = (
        ", **Highly Detailed Tattoo Illustration**, **Blackwork Style Tattoo**, "
        "Intricate Linework, **Digital Painting**, **Vector Art**, "
        "clean lines, high contrast, on human skin texture, studio lighting, "
        "isolated composition, no background elements." # Rejects scenery
    )
    
    # 2. ANTI-PROMPT TAGS (These explicitly tell the AI what NOT to draw)
    # The more detail we give the AI about what NOT to do, the better.
    anti_prompts = (
        " ::-1, " # Some models use this for negative weighting
        " **NOT** a photo, **NOT** a landscape, **NOT** scenery, "
        " **NOT** sunset, **NOT** rocks, **NOT** blurry, **NOT** watermark, "
        " **NOT** photography" 
    )
    
    # 3. FINAL COMPOSITE PROMPT
    final_prompt = (
        f"A **Blackwork Tattoo Illustration** of '{user_input}'. "
        f"The image must show the **fully inked design on the corresponding clean human body part** (e.g., bicep). "
        f"The focus must be 100% on the tattoo art. {technical_modifiers} {anti_prompts}"
    )
    
    return final_prompt


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
# In backend/main.py, modify the generate_tattoo endpoint:

# In backend/main.py, replace the entire generate_tattoo function:

@app.post("/api/generate_tattoo")
def generate_tattoo(request: PromptRequest, db: Session = Depends(get_db)):
    # 1. Check for AI Service Initialization
    if not client:
        raise HTTPException(status_code=500, detail="AI Service Initialization Error. GEMINI_API_KEY is likely missing or invalid.")
        
    prompt = request.user_prompt
    engineered_prompt = engineer_prompt(prompt)
    
    # --- 2. CACHE CHECK ---
    cache_key = None
    if redis_client:
        # Create a unique key from the engineered prompt using SHA256
        cache_key = hashlib.sha256(engineered_prompt.encode('utf-8')).hexdigest()
        cached_data = redis_client.hgetall(cache_key) # HGETALL retrieves the hash fields
        
        if cached_data and 'image_url' in cached_data:
            print("CACHE HIT: Serving response from Redis.")
            
            # Log the CACHE HIT in the database
            ai_message_cache = Conversation(
                role='ai', 
                prompt_text=f"(CACHED) {cached_data['ai_text']}", 
                generated_image_url=cached_data['image_url'], 
                engineered_prompt=engineered_prompt
            )
            db.add(ai_message_cache)
            db.commit()
            
            # Return the cached response instantly
            return {
                "status": "success",
                "ai_text": cached_data['ai_text'],
                "image_url": cached_data['image_url'],
                "engineered_prompt": engineered_prompt
            }
    
    # --- 3. CACHE MISS: LOG USER MESSAGE (DB Write) ---
    user_message = Conversation(
        role='user', 
        prompt_text=prompt, 
        generated_image_url=None, 
        engineered_prompt=None
    )
    db.add(user_message)
    db.commit() 
    db.refresh(user_message)
    
    # --- 4. CACHE MISS: GEMINI API CALL (High Latency Operation) ---
    try:
        print(f"CACHE MISS: Calling Gemini with prompt: {engineered_prompt}")

        # Call the Gemini API for image generation
        gemini_response = client.models.generate_images(
            model='imagen-4.0-generate-001', 
            prompt=engineered_prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio='1:1'
            )
        )
        
        if not gemini_response.generated_images:
            raise APIError("Gemini generated no images for the prompt.")
            
        # Get the placeholder URL for the successful generation
        image_url = 'https://picsum.photos/400/400?random=' + str(random.randint(1, 100))
        ai_response_text = f"Analyzing your request for '{prompt}'... Here is your high-resolution AI-designed tattoo concept!"

    except APIError as e:
        # Log failure
        ai_message_fail = Conversation(
            role='ai', 
            prompt_text=f"🚨 Gemini API Failed: {e}", 
            generated_image_url=None, 
            engineered_prompt=engineered_prompt
        )
        db.add(ai_message_fail)
        db.commit()
        raise HTTPException(status_code=500, detail=f"AI Generation Failed: {e}")

    # --- 5. CACHE WRITE (DB Write & Redis Write) ---
    
    # DB Write (Log successful AI response)
    ai_message_success = Conversation(
        role='ai', 
        prompt_text=ai_response_text, 
        generated_image_url=image_url, 
        engineered_prompt=engineered_prompt
    )
    db.add(ai_message_success)
    db.commit() 
    
    # Redis Write (Store the result for 24 hours)
    if redis_client and cache_key:
        cache_data = {
            "ai_text": ai_response_text,
            "image_url": image_url,
        }
        redis_client.hset(cache_key, mapping=cache_data)
        redis_client.expire(cache_key, 60 * 60 * 24) # TTL: 24 hours
        print("CACHE WRITE: Stored successful response in Redis.")

    # 6. Return Final Response
    return {
        "status": "success",
        "ai_text": ai_response_text,
        "image_url": image_url,
        "engineered_prompt": engineered_prompt
    }