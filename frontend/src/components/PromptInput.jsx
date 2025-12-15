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
        <div className="input-area">
            <form onSubmit={handleSend} className="input-form">
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={isLoading ? "Please wait for the AI..." : "Describe your tattoo idea in detail..."}
                    disabled={isLoading}
                    className="prompt-input"
                />
                <button
                    type="submit"
                    disabled={isLoading}
                    className="send-button"
                >
                    {isLoading ? <span className="loading-dots">Designing</span> : 'Generate'}
                </button>
            </form>
        </div>
    );
};

export default PromptInput;