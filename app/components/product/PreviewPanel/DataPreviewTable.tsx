'use client';

import React from 'react';
import Icon from '../common/Icon';

interface DataRow {
  [key: string]: string | number;
}

interface DataPreviewTableProps {
  data: DataRow[];
}

const DataPreviewTable: React.FC<DataPreviewTableProps> = ({ data }) => {
  if (data.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <Icon name="document" className="text-gray-400" size={24} />
        </div>
        <p className="text-gray-500 text-sm">暂无数据</p>
        <p className="text-gray-400 text-xs mt-1">上传文件后将显示前5行数据</p>
      </div>
    );
  }

  const displayData = data.slice(0, 5);
  const columns = Object.keys(data[0]);

  return (
    <div className="h-full flex flex-col">
      <div className="text-sm text-gray-600 flex justify-between items-center mb-4 flex-shrink-0">
        <span>显示前 {displayData.length} 行，共 {data.length} 行数据</span>
        <span className="text-xs text-gray-500">{columns.length} 列</span>
      </div>
      
      {/* 横向滚动的数据表 */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg bg-white min-h-0">
        <div className="min-w-max">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-gray-50 z-10">
              <tr>
                {columns.map((column, index) => (
                  <th 
                    key={column} 
                    className="px-3 py-2 text-left font-medium text-gray-700 border-b border-r border-gray-200 min-w-[100px] whitespace-nowrap"
                    style={{ minWidth: Math.max(column.length * 8 + 24, 100) }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="truncate">{column}</span>
                      <span className="text-xs text-gray-400 ml-2">#{index + 1}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {displayData.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50 transition-colors">
                  {columns.map((column, colIndex) => (
                    <td 
                      key={`${rowIndex}-${column}`} 
                      className="px-3 py-2 text-gray-700 border-b border-r border-gray-100 whitespace-nowrap"
                      title={String(row[column])} // 显示完整内容的提示
                    >
                      <div className="max-w-[200px] truncate">
                        {row[column] === null || row[column] === undefined ? (
                          <span className="text-gray-400 italic">null</span>
                        ) : (
                          String(row[column])
                        )}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* 滚动提示 - 固定在底部 */}
      {columns.length > 5 && (
        <div className="text-xs text-gray-400 text-center pt-4 flex-shrink-0">
          💡 表格可以横向滚动查看所有 {columns.length} 列数据
        </div>
      )}
    </div>
  );
};

export default DataPreviewTable;