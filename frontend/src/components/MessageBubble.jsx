// Save this as frontend/src/components/MessageBubble.jsx

import React from 'react';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    // Base styles for the bubble
    const bubbleStyle = {
        padding: '10px 15px',
        borderRadius: '15px',
        maxWidth: '70%',
        margin: '10px 0',
        alignSelf: isUser ? 'flex-end' : 'flex-start',
        backgroundColor: isUser ? '#1a73e8' : '#e0e0e0', // Google Blue for user, light gray for AI
        color: isUser ? 'white' : 'black',
    };

    const imageStyle = {
        maxWidth: '100%',
        borderRadius: '8px',
        marginTop: '10px',
        border: '3px solid #000', // Making the tattoo stand out!
    };

    return (
        <div style={{ display: 'flex', width: '100%', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
            <div style={bubbleStyle}>
                <strong>{isUser ? 'You:' : 'AI Tattoo Artist:'}</strong>
                <p style={{ margin: '5px 0' }}>{message.text}</p>

                {/* Conditional rendering for the image output */}
                {message.image_url && (
                    <div>
                        <p style={{ marginTop: '10px', fontWeight: 'bold' }}>Your Design:</p>
                        <img src={message.image_url} alt="Generated Tattoo Design" style={imageStyle} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default MessageBubble;