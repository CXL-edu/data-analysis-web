'use client';

import React, { useState } from 'react';
import DataPreviewTable from './DataPreviewTable';
import ChartPreview from './ChartPreview';
import Icon from '../common/Icon';

interface DataRow {
  [key: string]: string | number;
}

interface ChartData {
  type: 'bar' | 'line' | 'pie';
  title: string;
  data: any[];
}

interface PreviewPanelProps {
  isVisible: boolean;
  onToggleCollapse: () => void;
  data: DataRow[];
  charts: ChartData[];
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({ 
  isVisible, 
  onToggleCollapse, 
  data, 
  charts 
}) => {
  const [activeTab, setActiveTab] = useState<'data' | 'charts'>('data');

  const columns = data && data.length > 0 ? Object.keys(data[0]) : [];

  if (!isVisible) {
    return (
      <div className="h-full bg-white flex items-center justify-center border-l border-gray-200">
        <div className="text-center p-8">
          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Icon name="chevronLeft" className="text-gray-400" size={24} />
          </div>
          <p className="text-gray-500 text-sm mb-2">预览面板已隐藏</p>
          <button
            onClick={onToggleCollapse}
            className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
            title="显示预览面板"
          >
            显示预览
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">实时预览</h3>
          <button
            onClick={onToggleCollapse}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
            title="隐藏预览面板"
          >
            <Icon name="chevronRight" className="text-gray-600" size={20} />
          </button>
        </div>
        
        {/* Tab switcher */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('data')}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'data' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            数据预览
          </button>
          <button
            onClick={() => setActiveTab('charts')}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'charts' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            图表
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'data' ? (
          <DataPreviewTable data={data} />
        ) : (
          <ChartPreview charts={charts} />
        )}
      </div>

      {/* Footer with stats */}
      {data && data.length > 0 && (
        <div className="border-t border-gray-200 p-4">
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex items-center justify-between">
              <span>数据行数:</span>
              <span className="font-medium">{data.length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>列数:</span>
              <span className="font-medium">{columns.length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>图表数:</span>
              <span className="font-medium">{charts?.length || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>最后更新:</span>
              <span className="font-medium">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PreviewPanel;