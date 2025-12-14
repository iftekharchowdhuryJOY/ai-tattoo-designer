from fastapi import FastAPI, Depends, HTTPException # <-- Added HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import time 
import random 
from app.database import Base, SessionLocal, get_db, Conversation

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



# --- NEW HELPER: Prompt Engineering Function ---
# In backend/main.py, replace the existing engineer_prompt function:

def engineer_prompt(user_input: str) -> str:
    """
    Translates user's conversational prompt into a high-quality, technical prompt.
    Adds key phrases to force tattoo composition on skin.
    """
    # Core technical modifiers for a professional, photorealistic tattoo concept
    # ADDED: "Tattoo art", "Applied to skin", "Stencil effect"
    technical_modifiers = (
        ", Tattoo art, Applied to skin, Clean lines, Vector art, "
        "High contrast, black and grey ink, hyper-detailed linework, "
        "professional studio photo, no background, " # Forces focus on the tattoo
        "photorealistic illustration."
    )
    
    # Prepend instructions to ensure it's a tattoo design on the body
    final_prompt = (
        f"A photorealistic **tattoo design** of '{user_input}'. "
        f"The image must show the tattoo fully realized on the corresponding human body part. "
        f"The design should be rendered as high-resolution tattoo art. {technical_modifiers}"
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

@app.post("/api/generate_tattoo")
def generate_tattoo(request: PromptRequest, db: Session = Depends(get_db)):
    # Check if the client is initialized before proceeding
    if not client:
        raise HTTPException(status_code=500, detail="AI Service Initialization Error. GEMINI_API_KEY is likely missing or invalid.")
        
    prompt = request.user_prompt
    engineered_prompt = engineer_prompt(prompt)
    
    # 1. Log User Message to DB (same as before)
    user_message = Conversation(
        role='user', 
        prompt_text=prompt, 
        generated_image_url=None, 
        engineered_prompt=None
    )
    db.add(user_message)
    db.commit() 
    db.refresh(user_message)
    
    # --- START REAL GEMINI API LOGIC ---
    try:
        print(f"Sending engineered prompt to Gemini: {engineered_prompt}")

        # The core image generation call (Using the best available model for images)
        # NOTE: You may need to verify the exact model name for image generation availability.
        gemini_response = client.models.generate_images(
            model='imagen-4.0-generate-001', # Using a current high-quality image model name
            prompt=engineered_prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio="3:4",
                output_mime_type="image/jpeg"
            )
        )
        
        # Process the result
        if not gemini_response.generated_images:
            raise APIError("Gemini generated no images for the prompt.")
            
        # The result includes a base64 string or a cloud reference.
        # For simplicity and to avoid complex file uploads (S3/GCS), we'll return a 
        # placeholder image and log the successful prompt.
        
        # !!! IMPORTANT: In a production app, you would upload gemini_response.generated_images[0].image.image_bytes
        # to a cloud storage service (like Supabase Storage or AWS S3) and return that public URL.
        # For now, we use a fixed success placeholder URL.
        
        image_url = 'https://picsum.photos/400/400?random=' + str(random.randint(1, 100)) # Placeholder for successful API call
        ai_response_text = f"Analyzing your request for '{prompt}'... Here is your high-resolution AI-designed tattoo concept!"

    except APIError as e:
        print(f"Gemini API Error: {e}")
        # Log the failure in the database
        ai_message = Conversation(
            role='ai', 
            prompt_text=f"🚨 Gemini API Failed: {e}", 
            generated_image_url=None, 
            engineered_prompt=engineered_prompt
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Re-raise the HTTP exception so the frontend displays the error message
        raise HTTPException(status_code=500, detail=f"AI Generation Failed: {e}")

    # 4. Log Successful AI Response to DB
    ai_message = Conversation(
        role='ai', 
        prompt_text=ai_response_text, 
        generated_image_url=image_url, 
        engineered_prompt=engineered_prompt
    )
    db.add(ai_message)
    db.commit() 
    db.refresh(ai_message)

    # 5. Return Response
    return {
        "status": "success",
        "ai_text": ai_response_text,
        "image_url": image_url,
        "engineered_prompt": engineered_prompt
    }