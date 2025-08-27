'use client';

import React, { useState, useEffect } from 'react';
import ChatMessage, { Message } from './ChatMessage';
import ChatInput from './ChatInput';
import Icon from '../common/Icon';
import { useAuth } from '../../../contexts/AuthContext';
import AuthModal from '../../auth/AuthModal';

interface ChatAreaProps {
  onFileUpload?: (file: File) => void;
  onFileUploadComplete?: (data: any, sessionId: string) => void;
  sessionId: string | null;
  isBackendConnected: boolean;
  onChartGenerated?: (chartData: string) => void;
  onSessionCreated?: (sessionId: string) => void;
}

const ChatArea: React.FC<ChatAreaProps> = ({ onFileUpload, onFileUploadComplete, sessionId, isBackendConnected, onChartGenerated, onSessionCreated }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { isAuthenticated, user } = useAuth();

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
    // Check authentication first
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    // Create session if none exists
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      try {
        const { apiService } = await import('../services/api');
        const newSession = await apiService.createSession('新对话');
        console.log('ChatArea: Created session for sendMessage:', newSession);
        currentSessionId = newSession.uuid;
        console.log('ChatArea: Using sessionId for sendMessage:', currentSessionId);
        onSessionCreated?.(currentSessionId);
        
        // Trigger event to notify SessionManager
        window.dispatchEvent(new CustomEvent('sessionCreated', { 
          detail: { sessionId: currentSessionId } 
        }));
      } catch (error) {
        console.error('Failed to create session:', error);
        const errorMessage: Message = {
          id: Date.now().toString(),
          type: 'ai',
          content: '创建会话失败，请重试',
          timestamp: new Date(),
          contentType: 'error'
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }
    }

    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);

    if (!isBackendConnected) {
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
      // Use SSE streaming API
      const { apiService } = await import('../services/api');
      
      await apiService.streamChat(currentSessionId, content, (streamMessage) => {
        const { type, content: streamContent } = streamMessage;
        
        if (type === 'done') {
          setIsLoading(false);
          // Update any streaming message to not streaming
          setMessages(prev => prev.map(msg => 
            msg.isStreaming ? { ...msg, isStreaming: false } : msg
          ));
          return;
        }
        
        if (type === 'error') {
          setMessages(prev => [...prev, {
            id: (Date.now() + Math.random()).toString(),
            type: 'ai',
            content: streamContent,
            timestamp: new Date(),
            contentType: 'error'
          }]);
          setIsLoading(false);
          return;
        }
        
        // Handle image charts - notify parent component
        if (type === 'image' && streamContent && onChartGenerated) {
          onChartGenerated(streamContent);
        }
        
        // Create a new message for each stream chunk
        const newMessage: Message = {
          id: (Date.now() + Math.random()).toString(),
          type: 'ai',
          content: streamContent,
          timestamp: new Date(),
          contentType: type as any,
          isStreaming: false
        };
        
        setMessages(prev => [...prev, newMessage]);
      });
      
    } catch (error) {
      console.error('Streaming chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `抱歉，处理您的请求时出现了错误：${error}`,
        timestamp: new Date(),
        contentType: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    // Check authentication first
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    // Create session if none exists
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      try {
        const { apiService } = await import('../services/api');
        const newSession = await apiService.createSession('新对话');
        console.log('ChatArea: Created session for fileUpload:', newSession);
        currentSessionId = newSession.uuid;
        console.log('ChatArea: Using sessionId for fileUpload:', currentSessionId);
        onSessionCreated?.(currentSessionId);
        
        // Trigger event to notify SessionManager
        window.dispatchEvent(new CustomEvent('sessionCreated', { 
          detail: { sessionId: currentSessionId } 
        }));
        
        // Wait a bit to ensure parent state is updated
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error('Failed to create session:', error);
        const errorMessage: Message = {
          id: Date.now().toString(),
          type: 'ai',
          content: '创建会话失败，请重试',
          timestamp: new Date(),
          contentType: 'error'
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }
    }

    try {
      // Pass the current session ID directly to the upload handler
      const uploadResponse = await handleFileUploadWithSession(file, currentSessionId);
      
      // Notify parent component about successful upload
      onFileUploadComplete?.(uploadResponse, currentSessionId);
      
      const uploadMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: `已上传文件: ${file.name}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, uploadMessage]);
    } catch (error) {
      console.error('File upload failed:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'ai',
        content: '文件上传失败，请重试',
        timestamp: new Date(),
        contentType: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleFileUploadWithSession = async (file: File, sessionId: string) => {
    console.log('ChatArea: handleFileUploadWithSession called', { 
      fileName: file.name, 
      sessionId 
    });
    
    const { apiService } = await import('../services/api');
    const result = await apiService.uploadFile(file, sessionId);
    
    console.log('ChatArea: Upload completed', result);
    return result;
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">AI数据分析助手</h2>
            <p className="text-sm text-gray-600">
              {isAuthenticated ? '上传数据文件开始智能分析' : '请先登录使用分析功能'}
            </p>
          </div>
          {isAuthenticated && user && (
            <div className="text-right">
              <p className="text-sm text-gray-600">欢迎, {user.username}</p>
              {!user.isEmailVerified && (
                <p className="text-xs text-yellow-600">请验证您的邮箱</p>
              )}
            </div>
          )}
        </div>
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
              <p className="text-gray-600 mb-4">
                {isAuthenticated ? '上传您的数据文件，我会帮您进行智能分析' : '请先登录使用分析功能'}
              </p>
              {isAuthenticated ? (
                <button
                  onClick={() => document.querySelector<HTMLInputElement>('input[type="file"]')?.click()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  上传数据文件
                </button>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  登录开始使用
                </button>
              )}
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
        disabled={!isAuthenticated}
      />
      
      {/* Authentication Modal */}
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
        initialMode="login"
      />
    </div>
  );
};

export default ChatArea;