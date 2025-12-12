// Save this as frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatWindow from './components/ChatWindow';
import PromptInput from './components/PromptInput';

// Define the URL for your Python FastAPI backend
const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  // --- STATE MANAGEMENT ---
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // --- 1. HISTORY LOADING (useEffect) ---
  // Fetches conversation history from the FastAPI database on component mount
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/history`);
        const historyData = response.data;

        // Add a welcome message if the database is truly empty
        if (historyData.length === 0) {
          historyData.push({
            id: 0,
            role: 'ai',
            text: 'Welcome to the AI Tattoo Designer! Tell me what kind of tattoo you want (e.g., "fierce lion on my chest, black and white").',
            image_url: null
          });
        }

        setChatHistory(historyData);

      } catch (error) {
        console.error("Failed to fetch chat history:", error);
        // Fallback for a connection error
        setChatHistory([{
          id: -1,
          role: 'ai',
          text: 'Connection Error: Could not reach the backend API. Please ensure FastAPI server is running.',
          image_url: null
        }]);
      }
    };

    fetchHistory();
  }, []);

  // --- 2. PROMPT SUBMISSION HANDLER ---
  const handleSubmitPrompt = async (promptText) => {
    // 1. Validation and Setup
    if (!promptText.trim()) return;

    // Add user message to history immediately for quick UI feedback
    const newUserMessage = {
      id: Date.now() + 1, // Use timestamp for unique key
      role: 'user',
      text: promptText,
      image_url: null
    };
    setChatHistory(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // --- API CALL to FastAPI endpoint ---
      const response = await axios.post(`${API_BASE_URL}/api/generate_tattoo`, {
        user_prompt: promptText // Structure matches the Pydantic model
      });

      const responseData = response.data;

      // 2. Process and Format AI Response
      const aiResponse = {
        id: Date.now() + 2,
        role: 'ai',
        text: responseData.ai_text,
        image_url: responseData.image_url,
      };

      // 3. Update history with the final AI response (including image URL)
      setChatHistory(prev => [...prev, aiResponse]);

    } catch (error) {
      console.error("Image Generation API Failed:", error);

      // Add an error message to the chat history if the API fails
      const errorMessage = {
        id: Date.now() + 2,
        role: 'ai',
        text: "🚨 Error: Image generation failed. Check backend logs for API key or generation error.",
        image_url: null,
      };
      setChatHistory(prev => [...prev, errorMessage]);

    } finally {
      // 4. Always set loading to false when done
      setIsLoading(false);
    }
  };


  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px', backgroundColor: 'white', boxShadow: '0 0 10px rgba(0,0,0,0.1)' }}>
      <h1>AI Tattoo Designer</h1>

      {/* 1. Chat History Area */}
      <ChatWindow chatHistory={chatHistory} isLoading={isLoading} />

      {/* 2. Input Field (Passes the handler and loading state) */}
      <PromptInput handleSubmitPrompt={handleSubmitPrompt} isLoading={isLoading} />

    </div>
  );
}

export default App;