'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../contexts/AuthContext';
import Icon from '../common/Icon';
import { Session, apiService } from '../services/api';

interface SessionManagerProps {
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
  onSessionCreated?: (sessionId: string) => void;
}

const SessionManager: React.FC<SessionManagerProps> = ({ 
  currentSessionId, 
  onSessionSelect, 
  onNewSession,
  onSessionCreated
}) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const { isAuthenticated, user, logout } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      loadSessions();
    }
  }, [isAuthenticated]);

  // Listen for session creation events
  useEffect(() => {
    if (onSessionCreated) {
      const handleSessionCreated = (sessionId: string) => {
        // Reload sessions to include the new one
        loadSessions();
      };
      
      // Listen for custom session created event
      const handleCustomSessionCreated = (event: CustomEvent) => {
        handleSessionCreated(event.detail.sessionId);
      };
      
      window.addEventListener('sessionCreated', handleCustomSessionCreated as EventListener);
      
      return () => {
        window.removeEventListener('sessionCreated', handleCustomSessionCreated as EventListener);
      };
    }
  }, [onSessionCreated]);

  const loadSessions = async () => {
    if (!isAuthenticated) return;
    
    setIsLoading(true);
    setError('');
    try {
      const userSessions = await apiService.getUserSessions();
      setSessions(userSessions);
    } catch (error) {
      setError('加载会话失败');
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSession = () => {
    if (!isAuthenticated) return;

    // Clear current session and let ChatArea create new session when user sends message/uploads file
    onNewSession();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else if (diffDays === 1) {
      return '昨天';
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      return date.toLocaleDateString('zh-CN');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="w-80 bg-white border-r border-gray-200 p-4">
        <div className="text-center">
          <Icon name="user" className="mx-auto mb-2 text-gray-400" size={32} />
          <p className="text-sm text-gray-600">请先登录查看您的会话</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center">
            <Icon name="user" className="mr-2 text-gray-600" size={20} />
            <span className="font-medium text-gray-900">{user?.username}</span>
          </div>
          <button
            onClick={logout}
            className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            title="登出"
          >
            <Icon name="logout" size={16} />
          </button>
        </div>
        
        <button
          onClick={handleNewSession}
          className="w-full flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          disabled={isLoading}
        >
          <Icon name="plus" className="mr-2" size={16} />
          新建对话
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {error && (
          <div className="p-4">
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">
              {error}
              <button
                onClick={loadSessions}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                重试
              </button>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="p-4 text-center">
            <div className="inline-flex items-center">
              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
              加载中...
            </div>
          </div>
        ) : (
          <div className="p-2">
            {sessions.length === 0 ? (
              <div className="text-center p-4">
                <Icon name="message" className="mx-auto mb-2 text-gray-400" size={32} />
                <p className="text-sm text-gray-600">还没有会话记录</p>
                <p className="text-xs text-gray-500 mt-1">点击"新建对话"开始</p>
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.uuid || session.id}
                  onClick={() => onSessionSelect(session.uuid)}
                  className={`p-3 mb-2 rounded-lg cursor-pointer transition-colors ${
                    currentSessionId === session.uuid
                      ? 'bg-blue-50 border border-blue-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {session.title || '未命名对话'}
                      </h4>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(session.updated_at)}
                      </p>
                    </div>
                    {session.is_active && (
                      <div className="w-2 h-2 bg-green-500 rounded-full ml-2 mt-1 flex-shrink-0"></div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* User Status */}
      {user && !user.isEmailVerified && (
        <div className="p-4 border-t border-gray-200 bg-yellow-50">
          <div className="flex items-start">
            <Icon name="warning" className="text-yellow-600 mr-2 mt-0.5" size={16} />
            <div>
              <p className="text-xs text-yellow-800 font-medium">邮箱未验证</p>
              <p className="text-xs text-yellow-700 mt-1">
                请检查您的邮箱并点击验证链接
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionManager;