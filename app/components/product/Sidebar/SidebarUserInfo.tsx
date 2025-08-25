'use client';

import React from 'react';
import Icon from '../common/Icon';

interface SidebarUserInfoProps {
  isCollapsed: boolean;
}

const SidebarUserInfo: React.FC<SidebarUserInfoProps> = ({ isCollapsed }) => {
  return (
    <div className="border-t border-gray-200 p-4">
      <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'}`}>
        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
          <Icon name="user" className="text-gray-600" size={16} />
        </div>
        {!isCollapsed && (
          <div className="min-w-0">
            <div className="text-sm font-medium text-gray-800 truncate">张三</div>
            <div className="text-xs text-gray-500 truncate">zhang.san@example.com</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SidebarUserInfo;