// Save this as frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Assuming default CSS

function App() {
  const [backendStatus, setBackendStatus] = useState('Loading...');
  const [backendData, setBackendData] = useState('N/A');

  useEffect(() => {
    // The backend runs on http://127.0.0.1:8000, while the frontend runs on port 5173 (Vite default)
    axios.get('http://127.0.0.1:8000/api/test')
      .then(response => {
        // Success: FastAPI responded
        setBackendStatus('✅ Connection Successful!');
        setBackendData(response.data.data); // Grabs the "Backend is running..." message
      })
      .catch(error => {
        // Failure: Likely a CORS error or server is down
        console.error("API Connection Error:", error);
        setBackendStatus('❌ Connection Failed! Check console for errors. (Likely CORS Issue)');
        setBackendData('Try running the backend server or fixing CORS.');
      });
  }, []);

  return (
    <div className="App">
      <h1>AI Tattoo Designer - Full-Stack Test</h1>
      <p>Backend Status: <strong>{backendStatus}</strong></p>
      <p>Backend Message: <em>{backendData}</em></p>

      {/* Placeholder for the main UI */}
      <div style={{ padding: '20px', border: '1px solid #ccc', marginTop: '20px' }}>
        <p>Frontend UI will go here.</p>
      </div>
    </div>
  );
}

export default App;