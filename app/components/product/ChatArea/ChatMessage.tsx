'use client';

import React from 'react';
import Icon from '../common/Icon';

export interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-3xl`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          message.type === 'user' ? 'bg-blue-600' : 'bg-gray-300'
        }`}>
          {message.type === 'user' ? (
            <Icon name="user" className="text-white" size={16} />
          ) : (
            <Icon name="ai" className="text-gray-600" size={16} />
          )}
        </div>
        <div className={`px-4 py-3 rounded-lg ${
          message.type === 'user' 
            ? 'bg-blue-600 text-white' 
            : 'bg-white border border-gray-200 text-gray-800'
        }`}>
          <div className="whitespace-pre-wrap">
            {message.content}
            {message.isStreaming && (
              <span className="inline-block w-2 h-5 bg-current animate-pulse ml-1" />
            )}
          </div>
          <div className={`text-xs mt-2 ${
            message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
          }`}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;