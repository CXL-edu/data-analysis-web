'use client';

import React from 'react';
import Icon from '../common/Icon';
import { getButtonClassName } from './styles';

interface SidebarActionsProps {
  isCollapsed: boolean;
}

const SidebarActions: React.FC<SidebarActionsProps> = ({ isCollapsed }) => {
  const handleNewChat = () => {
    // Reset chat messages and clear session
    const event = new CustomEvent('newChat');
    window.dispatchEvent(event);
  };

  return (
    <div className="mb-6">
      {/* Primary Action: New Chat */}
      <button 
        onClick={handleNewChat}
        className={getButtonClassName('primary', isCollapsed, `mb-3 flex items-center justify-center${isCollapsed ? '' : ' space-x-2'}`)}
      >
        {isCollapsed ? (
          <Icon name="newChat" size={20} />
        ) : (
          <>
            <Icon name="newChat" size={16} />
            <span>新建聊天</span>
          </>
        )}
      </button>

      {/* Secondary Action: Knowledge Base */}
      <button className={getButtonClassName('secondary', isCollapsed, 'flex items-center justify-center' + (isCollapsed ? '' : ' space-x-2'))}>
        {isCollapsed ? (
          <Icon name="database" size={20} />
        ) : (
          <>
            <Icon name="database" size={16} />
            <span>知识库</span>
          </>
        )}
      </button>
    </div>
  );
};

export default SidebarActions;
