// Save this as frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatWindow from './components/ChatWindow';
import PromptInput from './components/PromptInput'; // Will be defined next

// Temporary sample data for testing the UI layout
const initialChatHistory = [
  { id: 1, role: 'ai', text: 'Welcome! Tell me what kind of tattoo you want. (e.g., "I want a fierce lion on my chest, black and white")', image_url: null },
  { id: 2, role: 'user', text: 'I want a tattoo of a geometric wolf on my forearm.', image_url: null },
  { id: 3, role: 'ai', text: 'Analyzing... Here is a concept!', image_url: 'https://via.placeholder.com/400x400/0000FF/FFFFFF?text=Generated+Wolf+Tattoo' },
];


function App() {
  // Central state to manage the entire conversation
  const [chatHistory, setChatHistory] = useState(initialChatHistory);
  const [isLoading, setIsLoading] = useState(false);

  // Placeholder function for handling the actual API call (defined next)
  // Save this as frontend/src/App.jsx

  // ... imports and initial state remains the same ...

  const handleSubmitPrompt = async (promptText) => {
    // 1. Add user message to history immediately
    const newUserMessage = {
      id: Date.now() + 1,
      role: 'user',
      text: promptText,
      image_url: null
    };
    setChatHistory(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // --- REAL API CALL ---
      const response = await axios.post('http://127.0.0.1:8000/api/generate_tattoo', {
        user_prompt: promptText // Matches the Pydantic model structure
      });

      const responseData = response.data;

      // 2. Process AI Response
      const aiResponse = {
        id: Date.now() + 2,
        role: 'ai',
        text: responseData.ai_text,
        image_url: responseData.image_url,
      };

      // 3. Update history with the AI response
      setChatHistory(prev => [...prev, aiResponse]);

    } catch (error) {
      console.error("Image Generation API Failed:", error);
      // Add an error message to the chat history if the API fails
      const errorMessage = {
        id: Date.now() + 2,
        role: 'ai',
        text: "🚨 Error: The AI service failed to generate the image. Please check the backend server logs.",
        image_url: null,
      };
      setChatHistory(prev => [...prev, errorMessage]);

    } finally {
      // 4. Always set loading to false when done
      setIsLoading(false);
    }
  };

  // ... rest of the App component remains the same ...


  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px', backgroundColor: 'white', boxShadow: '0 0 10px rgba(0,0,0,0.1)' }}>
      <h1>AI Tattoo Designer</h1>

      {/* 1. Chat History Area */}
      <ChatWindow chatHistory={chatHistory} isLoading={isLoading} />

      {/* 2. Input Field (Passing the handler) */}
      <PromptInput handleSubmitPrompt={handleSubmitPrompt} isLoading={isLoading} />

    </div>
  );
}

export default App;