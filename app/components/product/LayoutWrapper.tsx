'use client';

import React, { useState, useEffect } from 'react';
import ResizableLayout from './ResizableLayout';
import Sidebar from './Sidebar/Sidebar';
import ChatArea from './ChatArea/ChatArea';
import PreviewPanel from './PreviewPanel/PreviewPanel';
import { apiService, DataRow, ChartData } from './services/api';

const LayoutWrapper: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [uploadedData, setUploadedData] = useState<DataRow[]>([]);
  const [charts, setCharts] = useState<ChartData[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
    
    // Listen for new chat events
    const handleNewChat = () => {
      setUploadedData([]);
      setCharts([]);
      setSessionId(null);
      setPreviewVisible(false);
    };
    
    window.addEventListener('newChat', handleNewChat);
    
    return () => {
      window.removeEventListener('newChat', handleNewChat);
    };
  }, []);

  const checkBackendConnection = async () => {
    try {
      await apiService.healthCheck();
      setIsBackendConnected(true);
    } catch (error) {
      setIsBackendConnected(false);
      console.warn('Backend connection failed. Using mock data mode.');
    }
  };

  const handleFileUpload = async (file: File) => {
    setPreviewVisible(true);
    
    if (!isBackendConnected) {
      // Fallback to mock data if backend is not connected
      const mockData = [
        { id: 1, name: '示例数据1', value: 100, category: 'A' },
        { id: 2, name: '示例数据2', value: 200, category: 'B' },
        { id: 3, name: '示例数据3', value: 150, category: 'A' },
        { id: 4, name: '示例数据4', value: 300, category: 'C' },
        { id: 5, name: '示例数据5', value: 250, category: 'B' },
      ];
      setUploadedData(mockData);
      
      setTimeout(() => {
        const mockCharts = [
          { type: 'bar' as const, title: '分类统计', data: [] },
          { type: 'line' as const, title: '趋势分析', data: [] }
        ];
        setCharts(mockCharts);
      }, 2000);
      return;
    }

    try {
      // Upload file to backend
      const uploadResponse = await apiService.uploadFile(file);
      setSessionId(uploadResponse.session_id);
      setUploadedData(uploadResponse.preview_data);

      // Generate initial charts
      setTimeout(async () => {
        try {
          if (uploadResponse.columns.length > 0) {
            const numericColumns = uploadResponse.columns.filter(col => 
              uploadResponse.stats.dtypes[col] === 'int64' || 
              uploadResponse.stats.dtypes[col] === 'float64'
            );

            const generatedCharts: ChartData[] = [];

            // Generate histogram for first numeric column
            if (numericColumns.length > 0) {
              const chartResponse = await apiService.generateChart(
                uploadResponse.session_id,
                'histogram',
                numericColumns[0]
              );
              generatedCharts.push({
                type: 'bar',
                title: `${numericColumns[0]} 分布`,
                data: chartResponse.chart_data,
                image: chartResponse.chart_image
              });
            }

            // Generate correlation heatmap if multiple numeric columns
            if (numericColumns.length > 1) {
              const corrResponse = await apiService.generateChart(
                uploadResponse.session_id,
                'correlation'
              );
              generatedCharts.push({
                type: 'line',
                title: '相关性热力图',
                data: corrResponse.chart_data,
                image: corrResponse.chart_image
              });
            }

            setCharts(generatedCharts);
          }
        } catch (error) {
          console.error('Error generating charts:', error);
        }
      }, 1000);

    } catch (error) {
      console.error('Upload failed:', error);
      alert('文件上传失败，请检查后端服务是否启动。');
    }
  };

  return (
    <ResizableLayout
      leftPanel={
        <Sidebar
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      }
      centerPanel={
        <ChatArea
          onFileUpload={handleFileUpload}
          sessionId={sessionId}
          isBackendConnected={isBackendConnected}
        />
      }
      rightPanel={
        <PreviewPanel
          isVisible={true}
          onToggleCollapse={() => setPreviewVisible(!previewVisible)}
          data={uploadedData}
          charts={charts}
        />
      }
      leftInitialWidth={sidebarCollapsed ? 64 : 256}
      rightInitialWidth={320}
      leftMinWidth={sidebarCollapsed ? 64 : 200}
      rightMinWidth={280}
      leftMaxWidth={500}
      rightMaxWidth={600}
      rightVisible={previewVisible}
      leftCollapsed={sidebarCollapsed}
      onToggleRightPanel={() => setPreviewVisible(true)}
    />
  );
};

export default LayoutWrapper;