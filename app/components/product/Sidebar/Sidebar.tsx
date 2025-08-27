'use client';

import React from 'react';
import Link from 'next/link';
import SidebarActions from './SidebarActions';
import SidebarHistory from './SidebarHistory';
import SidebarUserInfo from './SidebarUserInfo';
import SidebarToggle from './SidebarToggle';
import Icon from '../common/Icon';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse }) => {
  return (
    <div className="h-full bg-white flex flex-col transition-all duration-300">
      {/* Header section with logo and toggle */}
      <div className={`${isCollapsed ? 'px-1 py-2' : 'p-4'} flex-shrink-0`}>
        <div className={`flex items-center ${isCollapsed ? 'flex-col space-y-2' : 'justify-between mb-6'}`}>
          {!isCollapsed ? (
            <Link href="/" className="flex items-center space-x-2 min-w-0 flex-1 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                <img src="/favicon.svg" alt="AI数据助手" className="w-8 h-8" />
              </div>
              <span className="text-lg font-semibold text-gray-800 truncate">数源智能</span>
            </Link>
          ) : (
            <Link href="/" className="w-10 h-10 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity">
              <img src="/favicon.svg" alt="AI数据助手" className="w-6 h-6" />
            </Link>
          )}
          <div className="flex-shrink-0">
            <SidebarToggle isCollapsed={isCollapsed} onToggle={onToggleCollapse} />
          </div>
        </div>
        
        {!isCollapsed && <SidebarActions isCollapsed={isCollapsed} />}
      </div>

      {/* Collapsed state: centered icons */}
      {isCollapsed && (
        <div className="flex-1 flex flex-col items-center justify-start pt-2 space-y-3">
          {/* New Chat Icon */}
          <button 
            onClick={() => {
              const event = new CustomEvent('newChat');
              window.dispatchEvent(event);
            }}
            className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
            title="新建聊天"
          >
            <Icon name="newChat" size={16} />
          </button>

          {/* Knowledge Base Icon */}
          <button 
            className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
            title="知识库"
          >
            <Icon name="database" size={16} />
          </button>

          {/* History Icon */}
          <button 
            className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
            title="历史聊天记录"
          >
            <Icon name="history" size={16} />
          </button>
        </div>
      )}

      {/* Expanded state: History section */}
      {!isCollapsed && <SidebarHistory isCollapsed={isCollapsed} />}

      {/* User info section */}
      <SidebarUserInfo isCollapsed={isCollapsed} />
    </div>
  );
};

export default Sidebar;