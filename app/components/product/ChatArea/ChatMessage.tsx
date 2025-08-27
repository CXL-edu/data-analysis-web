'use client';

import React from 'react';
import Icon from '../common/Icon';

export interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  contentType?: 'text' | 'thought' | 'image' | 'tool_call' | 'error';
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const renderContent = () => {
    const { content, contentType = 'text', isStreaming } = message;
    
    switch (contentType) {
      case 'thought':
        return (
          <div className="italic text-gray-600 flex items-center">
            <Icon name="thinking" className="mr-2" size={16} />
            {content}
            {isStreaming && <span className="inline-block w-2 h-5 bg-current animate-pulse ml-1" />}
          </div>
        );
        
      case 'image':
        return content ? (
          <div>
            <img 
              src={`data:image/png;base64,${content}`} 
              alt="Generated chart" 
              className="max-w-full h-auto rounded border"
            />
          </div>
        ) : null;
        
      case 'tool_call':
        return (
          <div className="bg-gray-100 p-3 rounded border-l-4 border-blue-500">
            <div className="flex items-center mb-2">
              <Icon name="tool" className="mr-2 text-blue-600" size={16} />
              <span className="font-medium text-gray-700">工具调用</span>
            </div>
            <pre className="text-sm text-gray-600 whitespace-pre-wrap">{content}</pre>
          </div>
        );
        
      case 'error':
        return (
          <div className="bg-red-50 p-3 rounded border-l-4 border-red-500">
            <div className="flex items-center">
              <Icon name="error" className="mr-2 text-red-600" size={16} />
              <span className="text-red-700">{content}</span>
            </div>
          </div>
        );
        
      default:
        return (
          <div className="whitespace-pre-wrap">
            {content}
            {isStreaming && <span className="inline-block w-2 h-5 bg-current animate-pulse ml-1" />}
          </div>
        );
    }
  };

  // Different styling for thought messages
  const isThought = message.contentType === 'thought';
  
  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-3xl`}>
        {!isThought && (
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            message.type === 'user' ? 'bg-blue-600' : 'bg-gray-300'
          }`}>
            {message.type === 'user' ? (
              <Icon name="user" className="text-white" size={16} />
            ) : (
              <Icon name="ai" className="text-gray-600" size={16} />
            )}
          </div>
        )}
        <div className={`px-4 py-3 rounded-lg ${
          isThought
            ? 'bg-gray-50 border border-gray-100'
            : message.type === 'user' 
              ? 'bg-blue-600 text-white' 
              : 'bg-white border border-gray-200 text-gray-800'
        }`}>
          {renderContent()}
          <div className={`text-xs mt-2 ${
            isThought
              ? 'text-gray-400'
              : message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
          }`}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;