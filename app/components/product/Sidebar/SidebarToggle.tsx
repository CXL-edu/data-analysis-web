'use client';

import React, { useState } from 'react';
import Icon from '../common/Icon';

interface SidebarToggleProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const SidebarToggle: React.FC<SidebarToggleProps> = ({ isCollapsed, onToggle }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={onToggle}
        className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <div className={`transition-transform ${isCollapsed ? 'rotate-180' : ''}`}>
          <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M5 5H13V19H5V5ZM19 19H15V5H19V19ZM4 3C3.44772 3 3 3.44772 3 4V20C3 20.5523 3.44772 21 4 21H20C20.5523 21 21 20.5523 21 20V4C21 3.44772 20.5523 3 20 3H4ZM7 12L11 8.5V15.5L7 12Z"/>
          </svg>
        </div>
      </button>
      
      {/* 自定义气泡提示 */}
      {showTooltip && (
        <div className="absolute left-full ml-2 top-1/2 transform -translate-y-1/2 z-50">
          <div className="bg-gray-800 text-white text-sm px-2 py-1 rounded shadow-lg whitespace-nowrap">
            {isCollapsed ? "展开侧边栏" : "关闭侧边栏"}
            <div className="absolute right-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-t-4 border-b-4 border-r-4 border-transparent border-r-gray-800"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SidebarToggle;