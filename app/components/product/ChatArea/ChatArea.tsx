'use client';

import React, { useState, useEffect } from 'react';
import ChatMessage, { Message } from './ChatMessage';
import ChatInput from './ChatInput';
import Icon from '../common/Icon';

interface ChatAreaProps {
  onFileUpload: (file: File) => void;
  sessionId: string | null;
  isBackendConnected: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({ onFileUpload, sessionId, isBackendConnected }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Listen for new chat events to clear messages
  useEffect(() => {
    const handleNewChat = () => {
      setMessages([]);
      setIsLoading(false);
    };
    
    window.addEventListener('newChat', handleNewChat);
    
    return () => {
      window.removeEventListener('newChat', handleNewChat);
    };
  }, []);

  const handleSendMessage = async (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);

    if (!isBackendConnected || !sessionId) {
      // Fallback to mock response if backend is not connected
      setTimeout(() => {
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: '我正在分析您的数据，请稍等...',
          timestamp: new Date(),
          isStreaming: true
        };
        setMessages(prev => [...prev, aiResponse]);
        
        setTimeout(() => {
          setMessages(prev => prev.map(msg => 
            msg.id === aiResponse.id 
              ? { ...msg, content: '分析完成！我已为您生成相关图表和数据洞察。', isStreaming: false }
              : msg
          ));
          setIsLoading(false);
        }, 2000);
      }, 1000);
      return;
    }

    try {
      // Use real backend API
      const { apiService } = await import('../services/api');
      const response = await apiService.chatWithData(sessionId, content);
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: response.ai_response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
      
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '抱歉，处理您的请求时出现了错误。请稍后再试。',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleFileUpload = (file: File) => {
    onFileUpload(file);
    const uploadMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: `已上传文件: ${file.name}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, uploadMessage]);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <h2 className="text-lg font-semibold text-gray-800">AI数据分析助手</h2>
        <p className="text-sm text-gray-600">上传数据文件开始智能分析</p>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 min-h-0">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Icon name="message" className="text-blue-600" size={32} />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">开始新的对话</h3>
              <p className="text-gray-600 mb-4">上传您的数据文件，我会帮您进行智能分析</p>
              <button
                onClick={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                上传数据文件
              </button>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start space-x-3 max-w-3xl">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    <Icon name="ai" className="text-gray-600" size={16} />
                  </div>
                  <div className="px-4 py-3 bg-white border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input area */}
      <ChatInput 
        onSendMessage={handleSendMessage}
        onFileUpload={handleFileUpload}
        isLoading={isLoading}
      />
    </div>
  );
};

export default ChatArea;