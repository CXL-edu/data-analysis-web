'use client';

import React from 'react';
import Link from 'next/link';
import SidebarActions from './SidebarActions';
import SidebarHistory from './SidebarHistory';
import SidebarUserInfo from './SidebarUserInfo';
import SidebarToggle from './SidebarToggle';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse }) => {
  return (
    <div className="h-full bg-white flex flex-col transition-all duration-300">
      {/* Header section with logo and toggle */}
      <div className="p-4 flex-shrink-0">
        <div className="flex items-center justify-between mb-6">
          {!isCollapsed ? (
            <Link href="/" className="flex items-center space-x-2 min-w-0 flex-1 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                <img src="/favicon.svg" alt="AI数据助手" className="w-8 h-8" />
              </div>
              <span className="text-lg font-semibold text-gray-800 truncate">数源智能</span>
            </Link>
          ) : (
            <Link href="/" className="w-8 h-8 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity">
              <img src="/favicon.svg" alt="AI数据助手" className="w-8 h-8" />
            </Link>
          )}
          <div className="flex-shrink-0">
            <SidebarToggle isCollapsed={isCollapsed} onToggle={onToggleCollapse} />
          </div>
        </div>
        
        <SidebarActions isCollapsed={isCollapsed} />
      </div>

      {/* History section */}
      <SidebarHistory isCollapsed={isCollapsed} />

      {/* User info section */}
      <SidebarUserInfo isCollapsed={isCollapsed} />
    </div>
  );
};

export default Sidebar;