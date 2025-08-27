'use client';

import React from 'react';
import Icon from '../common/Icon';

interface ChartData {
  type: 'bar' | 'line' | 'pie';
  title: string;
  data: any[];
  image?: string;
}

interface ChartPreviewProps {
  charts: ChartData[];
}

const ChartPreview: React.FC<ChartPreviewProps> = ({ charts }) => {
  if (!charts || charts.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <Icon name="barChart" className="text-gray-400" size={24} />
        </div>
        <p className="text-gray-500 text-sm">暂无图表</p>
        <p className="text-gray-400 text-xs mt-1">AI分析生成图表后将在此显示</p>
      </div>
    );
  }

  const getChartIcon = (type: string) => {
    switch (type) {
      case 'bar': return 'barChart';
      case 'line': return 'lineChart';
      case 'pie': return 'pieChart';
      default: return 'barChart';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto space-y-3">
        {charts.map((chart, index) => (
          <div key={`${chart.title}-${index}`} className="border border-gray-200 rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
            <div className="p-3">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-gray-800 truncate flex-1 mr-2">{chart.title}</h4>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded capitalize flex-shrink-0">
                  {chart.type}
                </span>
              </div>
              
              {/* 图片显示区域 - 支持更大的显示面积 */}
              <div className="relative">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg overflow-hidden border border-gray-200">
                  {chart.image ? (
                    <div className="relative group">
                      <img 
                        src={`data:image/png;base64,${chart.image}`} 
                        alt={chart.title}
                        className="w-full h-auto max-h-64 object-contain bg-white"
                        loading="lazy"
                      />
                      {/* 放大按钮 */}
                      <button 
                        className="absolute top-2 right-2 p-1 bg-black bg-opacity-50 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => {
                          const newWindow = window.open('', '_blank');
                          if (newWindow) {
                            newWindow.document.write(`
                              <html>
                                <head><title>${chart.title}</title></head>
                                <body style="margin:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f5f5f5;">
                                  <img src="data:image/png;base64,${chart.image}" alt="${chart.title}" style="max-width:100%; max-height:100%; object-fit:contain;" />
                                </body>
                              </html>
                            `);
                          }
                        }}
                        title="查看大图"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                        </svg>
                      </button>
                    </div>
                  ) : (
                    <div className="h-32 flex items-center justify-center">
                      <div className="text-center">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                          <Icon name={getChartIcon(chart.type)} className="text-blue-600" size={20} />
                        </div>
                        <p className="text-xs text-blue-700 font-medium">{chart.title}</p>
                        <p className="text-xs text-blue-600 mt-1">正在生成图表...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* 图表信息 */}
              <div className="mt-3 pt-2 border-t border-gray-100">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>数据点: {chart.data?.length || 0}</span>
                  <span>{new Date().toLocaleTimeString()}</span>
                </div>
                {chart.image && (
                  <div className="mt-1 text-xs text-green-600">
                    ✅ 图表已生成
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* 提示信息 - 固定在底部 */}
      {charts && charts.length > 0 && (
        <div className="text-xs text-gray-400 text-center pt-2 border-t border-gray-100 flex-shrink-0">
          💡 点击图表右上角的放大镜图标可查看大图
        </div>
      )}
    </div>
  );
};

export default ChartPreview;