// Save this as frontend/src/components/MessageBubble.jsx

import React from 'react';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={`message-wrapper ${isUser ? 'user' : 'ai'}`}>
            <div className={`message-bubble ${isUser ? 'user' : 'ai'}`}>
                <span className="sender-name">{isUser ? 'You' : 'AI Artist'}</span>
                <p style={{ margin: 0 }}>{message.text}</p>

                {/* Conditional rendering for the image output */}
                {message.image_url && (
                    <div className="tattoo-image-container">
                        <img
                            src={message.image_url}
                            alt="Generated Tattoo Design"
                            className="tattoo-image"
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default MessageBubble;