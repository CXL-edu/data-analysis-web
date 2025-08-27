'use client';

import React, { useState, useEffect } from 'react';
import Icon from '../common/Icon';
import { Session, apiService } from '../services/api';
import { useAuth } from '../../../contexts/AuthContext';

interface SidebarHistoryProps {
  isCollapsed: boolean;
  currentSessionId?: string | null;
  onSessionSelect?: (sessionId: string) => void;
}

const SidebarHistory: React.FC<SidebarHistoryProps> = ({ isCollapsed, currentSessionId, onSessionSelect }) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      loadSessions();
    } else {
      setSessions([]);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    const handleNewChat = () => {
      if (isAuthenticated) {
        loadSessions();
      }
    };

    const handleSessionCreated = () => {
      if (isAuthenticated) {
        loadSessions();
      }
    };

    window.addEventListener('newChat', handleNewChat);
    window.addEventListener('sessionCreated', handleSessionCreated);

    return () => {
      window.removeEventListener('newChat', handleNewChat);
      window.removeEventListener('sessionCreated', handleSessionCreated);
    };
  }, [isAuthenticated]);

  const loadSessions = async () => {
    if (!isAuthenticated) return;
    
    setLoading(true);
    setError(null);
    try {
      const userSessions = await apiService.getUserSessions();
      setSessions(userSessions);
    } catch (err) {
      console.error('Failed to load sessions:', err);
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const sessionDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    if (sessionDate.getTime() === today.getTime()) {
      return `今天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (sessionDate.getTime() === today.getTime() - 24 * 60 * 60 * 1000) {
      return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
    } else {
      return date.toLocaleString('zh-CN', { 
        month: 'numeric', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      }).replace(/\//g, '月').replace(' ', '日 ');
    }
  };

  const handleSessionClick = (sessionId: string) => {
    onSessionSelect?.(sessionId);
  };

  return (
    <div className={`${isCollapsed ? 'flex-shrink-0' : 'flex-1 min-h-0 flex flex-col'}`}>
      <div className={`${isCollapsed ? 'px-2' : 'px-4'}`}>
        {!isCollapsed && (
          <div className="text-sm font-medium text-gray-600 mb-4 flex items-center space-x-2 flex-shrink-0">
            <Icon name="history" size={16} />
            <span>历史聊天记录</span>
          </div>
        )}
      </div>
      <div className={`${isCollapsed ? '' : 'px-4 flex-1 min-h-0'}`}>
        <div 
          className={`${isCollapsed ? '' : 'space-y-2 overflow-y-auto hide-scrollbar'}`} 
          style={!isCollapsed ? { maxHeight: 'calc(100vh - 300px)' } : {}}
        >
            {!isAuthenticated ? (
              <div className="text-xs text-gray-500 text-center py-4">
                请登录查看历史记录
              </div>
            ) : loading ? (
              <div className="text-xs text-gray-500 text-center py-4">
                加载中...
              </div>
            ) : error ? (
              <div className="text-xs text-red-500 text-center py-4">
                {error}
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-xs text-gray-500 text-center py-4">
                暂无历史记录
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.uuid}
                  onClick={() => handleSessionClick(session.uuid)}
                  className={`${
                    isCollapsed ? 'p-2 flex justify-center items-center w-10 h-10 mb-2 flex-shrink-0' : 'px-3 py-3'
                  } ${
                    currentSessionId === session.uuid 
                      ? (isCollapsed ? 'bg-blue-100 text-blue-700' : 'bg-blue-100 border border-blue-200')
                      : (isCollapsed ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' : 'bg-gray-50 hover:bg-gray-100')
                  } rounded-lg cursor-pointer transition-colors`}
                >
                  {isCollapsed ? (
                    <Icon name="chat" size={16} />
                  ) : (
                    <>
                      <div className="font-medium text-gray-800 text-sm truncate mb-1">
                        {session.title || '新对话'}
                      </div>
                      <div className="text-gray-500 text-xs">
                        {formatDate(session.updated_at || session.created_at)}
                      </div>
                      {(session.message_count || session.file_count) && (
                        <div className="text-gray-500 text-xs">
                          {session.message_count && `${session.message_count}条消息`}
                          {session.message_count && session.file_count && ' '}
                          {session.file_count && `${session.file_count}个文件`}
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))
            )}
        </div>
      </div>
    </div>
  );
};

export default SidebarHistory;