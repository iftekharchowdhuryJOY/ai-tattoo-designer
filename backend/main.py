# Save this file as backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize the FastAPI application
app = FastAPI()

origins = [
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

# 2. Define a simple test endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Tattoo Designer Backend!"}

# 3. Define the first API endpoint for the frontend to test connectivity
@app.get("/api/test")
def test_connection():
    return {"status": "Success", "data": "Backend is running and talking to FastAPI!"}

# Note: We will add the CORS configuration here in the next step.