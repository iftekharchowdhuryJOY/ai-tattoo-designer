from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks # <-- Added HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import time 
import random 
from app.database import Base, AsyncSessionLocal, get_db_async, Conversation


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



async def log_ai_response_in_background(
    ai_response_text: str, 
    image_url: str, 
    engineered_prompt: str, 
    is_cache_hit: bool
):
    """
    Asynchronously handles the database logging. Executed by FastAPI 
    in the background after the main HTTP response is sent.
    """
    async with AsyncSessionLocal() as db:
        try:
            if is_cache_hit:
                response_text = f"(CACHED) {ai_response_text}"
            else:
                response_text = ai_response_text

            ai_message_log = Conversation(
                role='ai', 
                prompt_text=response_text, 
                generated_image_url=image_url, 
                engineered_prompt=engineered_prompt
            )
            db.add(ai_message_log)
            await db.commit()
            print(f"Background Task Complete: Successfully logged AI response. Cache Hit: {is_cache_hit}")
        except Exception as e:
            # Crucial to catch errors in background tasks
            print(f"Background Task Error: Failed to log AI response to DB: {e}")




# In backend/main.py (Find the create_tables function and replace it)

app = FastAPI()

async def create_tables(): # <-- FUNCTION IS NOW ASYNCHRONOUS
    from app.database import engine, Base
    # Use the async engine to run the table creation command
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Call the function once at startup using a standard event handler
@app.on_event("startup")
async def startup_event():
    await create_tables()


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

from app.database import get_db_async
# --- History Retrieval Endpoint ---
@app.get("/api/history", response_model=List[dict])
async def get_chat_history(db: AsyncSession = Depends(get_db_async)): # <-- Use async dependency
    """
    Fetches the entire chat history from the database asynchronously.
    """
    # Use async ORM commands
    result = await db.execute(select(Conversation).order_by(Conversation.timestamp))
    history = result.scalars().all()
    
    # ... (return formatting remains the same) ...
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
# In backend/main.py, replace the entire generate_tattoo function:

@app.post("/api/generate_tattoo")
async def generate_tattoo(
    request: PromptRequest,     
    background_tasks: BackgroundTasks, # <-- Accepts background task handler
    db: AsyncSession = Depends(get_db_async)
):
    # 1. Check for AI Service Initialization
    if not client:
        raise HTTPException(status_code=500, detail="AI Service Initialization Error. GEMINI_API_KEY is missing.")
        
    prompt = request.user_prompt
    engineered_prompt = engineer_prompt(prompt)
    
    # --- 2. CACHE CHECK (Redis) ---
    cache_key = None
    if redis_client:
        cache_key = hashlib.sha256(engineered_prompt.encode('utf-8')).hexdigest()
        cached_data = redis_client.hgetall(cache_key)
        
        if cached_data and 'image_url' in cached_data:
            print("CACHE HIT: Serving response from Redis.")
            
            # Log the CACHE HIT in the BACKGROUND
            background_tasks.add_task(
                log_ai_response_in_background,
                ai_response_text=cached_data['ai_text'],
                image_url=cached_data['image_url'],
                engineered_prompt=engineered_prompt,
                is_cache_hit=True
            )
            
            # Return INSTANTLY
            return {
                "status": "success",
                "ai_text": cached_data['ai_text'],
                "image_url": cached_data['image_url'],
                "engineered_prompt": engineered_prompt
            }
    
    # --- 3. CACHE MISS: LOG USER MESSAGE (Synchronous Write) ---
    # Must be synchronous so the user's message appears in history before AI response
    user_message = Conversation(
        role='user', 
        prompt_text=prompt, 
        generated_image_url=None, 
        engineered_prompt=None
    )
    db.add(user_message)
    await db.commit() 
    await db.refresh(user_message)
    
    # --- 4. CACHE MISS: GEMINI API CALL (High Latency Operation) ---
    try:
        print(f"CACHE MISS: Calling Gemini with prompt: {engineered_prompt}")

        # Gemini API call (takes several seconds)
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
            
        # Using placeholder URL for successful generation (replace with actual image upload logic later)
        image_url = 'https://picsum.photos/400/400?random=' + str(random.randint(1, 100))
        ai_response_text = f"Analyzing your request for '{prompt}'... Here is your high-resolution AI-designed tattoo concept!"

    except APIError as e:
        # Log failure synchronously before raising the exception
        ai_message_fail = Conversation(
            role='ai', 
            prompt_text=f"🚨 Gemini API Failed: {e}", 
            generated_image_url=None, 
            engineered_prompt=engineered_prompt
        )
        db.add(ai_message_fail)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"AI Generation Failed: {e}")

    # --- 5. CACHE WRITE & DB LOGGING (Background Tasks) ---
    
    # Redis Write (Store the result for 24 hours) - Must be done BEFORE response is sent
    if redis_client and cache_key:
        cache_data = {"ai_text": ai_response_text, "image_url": image_url,}
        redis_client.hset(cache_key, mapping=cache_data)
        redis_client.expire(cache_key, 60 * 60 * 24)
        print("CACHE WRITE: Stored successful response in Redis.")

    # Log successful AI response in the BACKGROUND
    background_tasks.add_task(
        log_ai_response_in_background,
        ai_response_text=ai_response_text,
        image_url=image_url,
        engineered_prompt=engineered_prompt,
        is_cache_hit=False
    )
    
    # --- 6. Return Final Response (Instantaneous) ---
    return {
        "status": "success",
        "ai_text": ai_response_text,
        "image_url": image_url,
        "engineered_prompt": engineered_prompt
    }