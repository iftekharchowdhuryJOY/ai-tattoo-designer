// Save this as frontend/src/components/ChatWindow.jsx

import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

const ChatWindow = ({ chatHistory, isLoading }) => {
    const messagesEndRef = useRef(null);

    // Auto-scroll to the bottom when history updates
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatHistory]);

    const loadingBubble = {
        role: 'ai',
        text: 'Generating your custom tattoo concept... Please wait, this may take a moment while the AI designs!',
        image_url: null,
    };

    return (
        <div style={{
            height: '500px',
            overflowY: 'auto',
            padding: '15px',
            border: '1px solid #ccc',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#f9f9f9'
        }}>
            {/* Map over the historical messages */}
            {chatHistory.map((message) => (
                <MessageBubble key={message.id} message={message} />
            ))}

            {/* Show a loading message while waiting for API response */}
            {isLoading && <MessageBubble message={loadingBubble} />}

            <div ref={messagesEndRef} />
        </div>
    );
};

export default ChatWindow;