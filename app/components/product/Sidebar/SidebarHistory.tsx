'use client';

import React, { useState } from 'react';
import Icon from '../common/Icon';

interface ChatHistoryItem {
  id: string;
  title: string;
  date: string;
  dataCount: string;
  modelCount: string;
}

interface SidebarHistoryProps {
  isCollapsed: boolean;
}

const SidebarHistory: React.FC<SidebarHistoryProps> = ({ isCollapsed }) => {
  const [chatHistory] = useState<ChatHistoryItem[]>([
    { id: '1', title: 'merchant_category_code分析', date: '8月24日 18:29', dataCount: '9条数据', modelCount: '3个模型' },
    { id: '2', title: '销售数据趋势分析', date: '8月24日 15:42', dataCount: '156条数据', modelCount: '2个模型' },
    { id: '3', title: '用户行为分析', date: '8月23日 20:15', dataCount: '2341条数据', modelCount: '4个模型' }
  ]);
  const [showHistoryItems, setShowHistoryItems] = useState(false);

  return (
    <div className="flex-1 overflow-y-auto">
      <div className={`${isCollapsed ? 'px-2' : 'px-4'}`}>
        {!isCollapsed ? (
          <div className="text-sm font-medium text-gray-600 mb-4 flex items-center space-x-2">
            <Icon name="history" size={16} />
            <span>历史聊天记录</span>
          </div>
        ) : (
          <button 
            onClick={() => setShowHistoryItems(!showHistoryItems)}
            className="mb-4 flex justify-center w-full p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
            title={showHistoryItems ? "隐藏历史记录" : "显示历史记录"}
          >
            <Icon name="history" size={20} className="text-gray-600" />
          </button>
        )}
        {(!isCollapsed || showHistoryItems) && (
          <div className="space-y-2">
            {chatHistory.map((chat) => (
            <div
              key={chat.id}
              className={`${isCollapsed ? 'p-3' : 'px-3 py-3'} bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors`}
            >
              {isCollapsed ? (
                <div className="flex items-center justify-center">
                  <Icon name="chat" className="text-gray-600" size={20} />
                </div>
              ) : (
                <>
                  <div className="font-medium text-gray-800 text-sm truncate mb-1">{chat.title}</div>
                  <div className="text-gray-500 text-xs">{chat.date}</div>
                  <div className="text-gray-500 text-xs">{chat.dataCount} {chat.modelCount}</div>
                </>
              )}
            </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SidebarHistory;