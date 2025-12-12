// Save this as frontend/src/components/PromptInput.jsx

import React, { useState } from 'react';

const PromptInput = ({ handleSubmitPrompt, isLoading }) => {
    const [prompt, setPrompt] = useState('');

    const handleSend = (e) => {
        e.preventDefault();
        if (!prompt.trim() || isLoading) return;

        // Call the handler passed from App.jsx
        handleSubmitPrompt(prompt.trim());
        setPrompt(''); // Clear the input field
    };

    return (
        <form onSubmit={handleSend} style={{ display: 'flex', marginTop: '10px' }}>
            <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={isLoading ? "Please wait for the AI..." : "Enter your tattoo idea..."}
                disabled={isLoading}
                style={{
                    flexGrow: 1,
                    padding: '12px',
                    fontSize: '16px',
                    border: '1px solid #ccc',
                    borderRadius: '5px 0 0 5px'
                }}
            />
            <button
                type="submit"
                disabled={isLoading}
                style={{
                    padding: '12px 20px',
                    fontSize: '16px',
                    backgroundColor: isLoading ? '#888' : '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0 5px 5px 0',
                    cursor: isLoading ? 'not-allowed' : 'pointer'
                }}
            >
                {isLoading ? 'Designing...' : 'Send'}
            </button>
        </form>
    );
};

export default PromptInput;