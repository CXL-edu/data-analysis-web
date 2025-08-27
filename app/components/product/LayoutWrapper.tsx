'use client';

import React, { useState, useEffect } from 'react';
import ResizableLayout from './ResizableLayout';
import Sidebar from './Sidebar/Sidebar';
import ChatArea from './ChatArea/ChatArea';
import PreviewPanel from './PreviewPanel/PreviewPanel';
import { apiService, DataRow, ChartData } from './services/api';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';

const LayoutContent: React.FC = () => {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [uploadedData, setUploadedData] = useState<DataRow[]>([]);
  const [charts, setCharts] = useState<ChartData[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { isAuthenticated } = useAuth();

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

  const handleChartGenerated = (chartData: string) => {
    // Handle chart data from streaming responses
    const newChart: ChartData = {
      type: 'bar', // Default type, could be inferred from context
      title: `生成的图表 ${charts.length + 1}`,
      data: [],
      image: chartData
    };
    setCharts(prev => [...prev, newChart]);
  };

  const handleFileUploadComplete = (uploadResponse: any, sessionId: string) => {
    setPreviewVisible(true);
    
    // Set preview data if available
    if (uploadResponse.preview_data) {
      setUploadedData(uploadResponse.preview_data);
    } else {
      setUploadedData([]);
    }
    setCharts([]); // Charts will come from streaming responses
    
    console.log('File uploaded successfully:', uploadResponse.message);
  };

  const handleMockFileUpload = async (file: File) => {
    if (!isBackendConnected) {
      setPreviewVisible(true);
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
    }
  };

  const handleSessionSelect = (newSessionId: string) => {
    setSessionId(newSessionId);
    // Clear current data when switching sessions
    setUploadedData([]);
    setCharts([]);
    setPreviewVisible(false);
  };

  const handleNewSession = () => {
    // Reset state for new session
    setSessionId(null);
    setUploadedData([]);
    setCharts([]);
    setPreviewVisible(false);
    // Trigger new chat event
    window.dispatchEvent(new Event('newChat'));
  };

  const handleSessionCreated = (newSessionId: string) => {
    setSessionId(newSessionId);
  };

  return (
    <ResizableLayout
      leftPanel={
        <Sidebar
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
          currentSessionId={sessionId}
          onSessionSelect={handleSessionSelect}
        />
      }
      centerPanel={
        <ChatArea
          onFileUpload={handleMockFileUpload}
          onFileUploadComplete={handleFileUploadComplete}
          sessionId={sessionId}
          isBackendConnected={isBackendConnected}
          onChartGenerated={handleChartGenerated}
          onSessionCreated={handleSessionCreated}
        />
      }
      rightPanel={
        <PreviewPanel
          isVisible={previewVisible}
          onToggleCollapse={() => setPreviewVisible(!previewVisible)}
          data={uploadedData}
          charts={charts}
        />
      }
      leftInitialWidth={320}
      rightInitialWidth={320}
      leftMinWidth={280}
      rightMinWidth={280}
      leftMaxWidth={500}
      rightMaxWidth={600}
      rightVisible={previewVisible}
      leftCollapsed={sidebarCollapsed}
      onToggleRightPanel={() => setPreviewVisible(true)}
    />
  );
};

// Wrapper component with AuthProvider
const LayoutWrapper: React.FC = () => {
  return (
    <AuthProvider>
      <LayoutContent />
    </AuthProvider>
  );
};

export default LayoutWrapper;