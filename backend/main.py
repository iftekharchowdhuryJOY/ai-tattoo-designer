# Save this file as backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # <-- NEW IMPORT (for data validation)
import time # <-- NEW IMPORT (for simulating AI delay)
import random # <-- NEW IMPORT (for placeholder images)

app = FastAPI()

# --- NEW Pydantic Model ---
# Defines the structure of the data expected from the React frontend
class PromptRequest(BaseModel):
    user_prompt: str

# CORS configuration (already done in Step 3)
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
# --- END CORS CONFIGURATION ---


# Existing test endpoints...
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Tattoo Designer Backend!"}

@app.get("/api/test")
def test_connection():
    return {"status": "Success", "data": "Backend is running and talking to FastAPI!"}
# ...

# --- NEW IMAGE GENERATION ENDPOINT ---
@app.post("/api/generate_tattoo")
def generate_tattoo(request: PromptRequest):
    """
    Receives a prompt from the frontend and simulates image generation.
    """
    prompt = request.user_prompt
    print(f"Received prompt from frontend: {prompt}")

    # 1. --- PLACEHOLDER LOGIC ---
    # We simulate the long wait of the external AI service
    time.sleep(3) # Simulate a 3-second generation time

    # 2. --- PLACEHOLDER IMAGE URL ---
    # Use different placeholder colors based on the time for a visual change
    placeholders = [
        "https://via.placeholder.com/400x400/007bff/FFFFFF?text=AI+Concept+Blue", 
        "https://via.placeholder.com/400x400/FF5733/FFFFFF?text=AI+Concept+Orange",
        "https://via.placeholder.com/400x400/33FF57/FFFFFF?text=AI+Concept+Green"
    ]
    
    # In a real app, this would be the URL to the image saved in S3/GCS
    placeholder_url = random.choice(placeholders)

    # 3. --- PLACEHOLDER PROMPT ENGINEERING ---
    # We will replace this with real logic later
    ai_response_text = f"Analyzing your request for '{prompt}'... Here is a high-resolution concept design for your tattoo!"
    
    # 4. --- RETURN RESPONSE ---
    return {
        "status": "success",
        "ai_text": ai_response_text,
        "image_url": placeholder_url,
        "engineered_prompt": f"Technical prompt based on: {prompt}" # Placeholder for later use
    }