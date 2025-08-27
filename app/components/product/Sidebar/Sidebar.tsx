'use client';

import React, { useState } from 'react';
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
  const [showHistoryItems, setShowHistoryItems] = useState(false);

  // 固定icon尺寸
  const iconSize = 16;

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
        <div className="flex-1 flex flex-col items-center justify-start pt-2">
          {/* Main action buttons - always centered */}
          <div className="space-y-3">
            {/* New Chat Icon */}
            <div className="flex justify-center">
              <button 
                onClick={() => {
                  const event = new CustomEvent('newChat');
                  window.dispatchEvent(event);
                }}
                className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
                title="新建聊天"
              >
                <Icon name="newChat" size={iconSize} />
              </button>
            </div>

            {/* Knowledge Base Icon */}
            <div className="flex justify-center">
              <button 
                className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
                title="知识库"
              >
                <Icon name="database" size={iconSize} />
              </button>
            </div>

            {/* History Icon */}
            <div className="flex justify-center">
              <button 
                onClick={() => setShowHistoryItems(!showHistoryItems)}
                className={`p-2 rounded-lg ${showHistoryItems ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'} transition-colors`}
                title={showHistoryItems ? "隐藏历史记录" : "显示历史记录"}
              >
                <Icon name="history" size={iconSize} />
              </button>
            </div>
          </div>
          
          {/* History items - directly below history button */}
          {showHistoryItems && (
            <div className="space-y-2 pt-2">
              {[
                { id: '1', title: 'merchant_category_code分析' },
                { id: '2', title: '销售数据趋势分析' },
                { id: '3', title: '用户行为分析' }
              ].map((chat) => (
                <div
                  key={chat.id}
                  className="p-1.5 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors flex justify-center"
                  title={chat.title}
                >
                  <Icon name="chat" className="text-gray-600" size={iconSize} />
                </div>
              ))}
            </div>
          )}
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