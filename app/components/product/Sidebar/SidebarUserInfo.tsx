'use client';

import React from 'react';
import Icon from '../common/Icon';
import { useAuth } from '../../../contexts/AuthContext';

interface SidebarUserInfoProps {
  isCollapsed: boolean;
}

const SidebarUserInfo: React.FC<SidebarUserInfoProps> = ({ isCollapsed }) => {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated || !user) {
    return (
      <div className={`border-t border-gray-200 ${isCollapsed ? 'px-1 py-2' : 'p-4'}`}>
        {isCollapsed ? (
          <div className="flex justify-center">
            <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
              <Icon name="user" className="text-gray-600" size={16} />
            </div>
          </div>
        ) : (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
              <Icon name="user" className="text-gray-600" size={16} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium text-gray-800">游客</div>
              <div className="text-xs text-gray-500">未登录</div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`border-t border-gray-200 ${isCollapsed ? 'px-1 py-2' : 'p-4'}`}>
      {isCollapsed ? (
        <div className="flex justify-center">
          <button
            onClick={logout}
            className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center hover:bg-gray-400 transition-colors"
            title={`${user.username} - 点击登出`}
          >
            <Icon name="user" className="text-gray-600" size={16} />
          </button>
        </div>
      ) : (
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
            <Icon name="user" className="text-gray-600" size={16} />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-sm font-medium text-gray-800 truncate">{user.username}</div>
            <div className="text-xs text-gray-500 truncate">{user.email}</div>
          </div>
          <button
            onClick={logout}
            className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded flex-shrink-0"
            title="登出"
          >
            <Icon name="logout" size={14} />
          </button>
        </div>
      )}
    </div>
  );
};

export default SidebarUserInfo;